from datetime import date

import httpx
import pytest
from bawsala_feeds import export, scoring
from bawsala_feeds.budget import Budget
from bawsala_feeds.cli import main
from bawsala_feeds.model import Job, dedupe
from bawsala_feeds.runner import run
from bawsala_feeds.sources import adzuna, arbeitnow, reed, remotive

ARB = {
    "data": [
        {
            "title": "QA Lead",
            "company_name": "Acme",
            "url": "https://a/1",
            "location": "Berlin",
            "remote": False,
            "created_at": 1760000000,
            "visa_sponsorship": True,
            "description": "telecom",
        },
        {
            "title": "Intern QA",
            "company_name": "Z",
            "url": "https://a/2",
            "location": "X",
            "remote": True,
            "created_at": None,
            "description": "",
        },
    ]
}
REM = {
    "jobs": [
        {
            "title": "QA Lead",
            "company_name": "Acme",
            "url": "https://r/1",
            "candidate_required_location": "Worldwide",
            "publication_date": "2026-10-01T00:00:00",
            "description": "tmf api testing",
        }
    ]
}
ADZ = {
    "results": [
        {
            "title": "Test Manager",
            "company": {"display_name": "B"},
            "redirect_url": "https://z/1",
            "location": {"display_name": "London"},
            "created": "2026-10-02T00:00:00Z",
            "salary_min": 60000,
            "salary_max": 70000,
            "description": "x",
        }
    ]
}
REED = {
    "results": [
        {
            "jobTitle": "Head of QA",
            "employerName": "C",
            "jobUrl": "https://re/1",
            "locationName": "Leeds",
            "date": "03/10/2026",
            "minimumSalary": 1,
            "maximumSalary": 2,
        },
        {"jobTitle": "T", "employerName": "D", "jobUrl": "u", "locationName": "L", "date": "bad"},
    ]
}


def handler(request: httpx.Request) -> httpx.Response:
    host = request.url.host
    if "arbeitnow" in host:
        return httpx.Response(200, json=ARB)
    if "remotive" in host:
        return httpx.Response(200, json=REM)
    if "adzuna" in host:
        assert request.url.params["app_id"] == "id"
        return httpx.Response(200, json=ADZ)
    if "reed" in host:
        assert request.headers["authorization"].startswith("Basic")
        return httpx.Response(200, json=REED)
    return httpx.Response(500)


@pytest.fixture
def client():
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_sources(client):
    a = arbeitnow.fetch(client, {"visa_only": True}, {})
    assert (
        a[0].visa_sponsorship is True and a[0].posted_at.startswith("2025") and a[1].posted_at == ""
    )
    assert remotive.fetch(client, {"category": "qa"}, {})[0].remote
    z = adzuna.fetch(client, {}, {"ADZUNA_APP_ID": "id", "ADZUNA_APP_KEY": "k"})[0]
    assert z.salary_currency == "GBP" and z.company == "B"
    r = reed.fetch(client, {}, {"REED_API_KEY": "k"})
    assert r[0].posted_at == "2026-10-03" and r[1].posted_at == "bad"


def test_budget_persists(tmp_path):
    p = tmp_path / "b.json"
    b = Budget(p, date(2026, 10, 16))
    for _ in range(4):
        assert b.allow("remotive", 4)
        b.record("remotive")
    assert not Budget(p, date(2026, 10, 16)).allow("remotive", 4)
    assert Budget(p, date(2026, 10, 17)).allow("remotive", 4)


def test_dedupe_and_scoring():
    a = Job("QA Lead", "Acme", "u1", "s", "a")
    b = Job("QA  lead", "ACME", "u2", "s", "a", visa_sponsorship=True)
    assert len(dedupe([a, b])) == 1 and dedupe([a, b])[0].url == "u2"
    rules = {
        "title": {"qa lead": 5},
        "description": {"tmf": 2},
        "location": {"london": 1},
        "remote_bonus": 2,
        "visa_bonus": 3,
        "exclude": ["intern"],
    }
    j = Job(
        "QA Lead",
        "A",
        "u",
        "s",
        "a",
        location="London",
        remote=True,
        visa_sponsorship=True,
        description="TMF",
    )
    assert scoring.score(j, rules).score == 13
    assert scoring.score(Job("Intern", "A", "u", "s", "a"), rules).score == -100
    assert scoring.load_rules(None) == {}


def test_run_end_to_end(tmp_path, client):
    (tmp_path / "rules.yaml").write_text(
        'title: {"qa lead": 5}\nvisa_bonus: 3\nexclude: ["intern"]\n'
    )
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        f"sources:\n  arbeitnow: {{}}\n  remotive: {{}}\n  adzuna: {{}}\n  reed: {{enabled: false}}\n"
        f"  unknown: {{}}\nrules: {tmp_path / 'rules.yaml'}\nshortlist_size: 5\n"
    )
    out = tmp_path / "out"
    jobs = run(cfg, out, client, {"ADZUNA_APP_ID": "id", "ADZUNA_APP_KEY": "k"})
    assert jobs[0].title == "QA Lead" and jobs[0].visa_sponsorship is True
    assert len([j for j in jobs if j.title == "QA Lead"]) == 1  # deduped across sources
    assert "Shortlist" in (out / "shortlist.md").read_text()
    assert (out / "jobs.csv").read_text().startswith("title,")
    for _ in range(5):  # remotive budget of 4/day is enforced
        run(cfg, out, client, {"ADZUNA_APP_ID": "id", "ADZUNA_APP_KEY": "k"})
    assert Budget(out / ".budget.json").used("remotive") == 4


def test_run_skips_missing_key_and_http_error(tmp_path, client):
    cfg = tmp_path / "c.yaml"
    cfg.write_text("sources:\n  adzuna: {}\n  reed: {}\n")
    bad = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    assert run(cfg, tmp_path / "o1", client, {}) == []  # KeyError on missing env
    assert (
        run(
            cfg,
            tmp_path / "o2",
            bad,
            {"REED_API_KEY": "k", "ADZUNA_APP_ID": "i", "ADZUNA_APP_KEY": "k"},
        )
        == []
    )


def test_export_empty(tmp_path):
    export.write_csv([], tmp_path / "e.csv")
    assert (tmp_path / "e.csv").read_text() == ""


def test_cli(tmp_path, capsys):
    assert main(["--config", str(tmp_path / "missing.yaml"), "--out", str(tmp_path)]) == 2
    capsys.readouterr()
