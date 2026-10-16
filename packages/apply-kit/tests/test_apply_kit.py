from datetime import date

import pytest
from apply_kit import facts as F
from apply_kit import ledger, prompt, truthcheck
from apply_kit.cli import main

FACTS = {
    "anonymize": ["Acme"],
    "extra_vocabulary": ["FooTool"],
    "experience": [
        {"facts": ["Built QA team to 13 engineers using Selenium and Jira", "2020 to 2022"]}
    ],
}


@pytest.fixture
def facts_file(tmp_path):
    p = tmp_path / "facts.yaml"
    p.write_text(
        "anonymize: [Acme]\nextra_vocabulary: [FooTool]\nsummary: 'QA team of 13 using Selenium, 8+ years'\n",
        encoding="utf-8",
    )
    return p


def codes(text):
    return {i.rule for i in truthcheck.check(text, FACTS)}


def test_truthcheck():
    assert codes("Built a team of 13 with Selenium and Jira in 2021") == {
        "TC001"
    }  # 2021 not in facts
    assert codes("Team of 13, Selenium, 2020") == set()
    assert "TC001" in codes("reduced defects by 15%")
    assert "TC002" in codes("used Cypress daily")
    assert "TC002" in codes("used FooTool daily")
    assert "TC003" in codes("worked for ACME on payments")
    assert "TC002" not in codes("Javaland and Pythonic")  # whole words only


def test_prompt_and_facts(tmp_path, facts_file):
    data = F.load(facts_file)
    out = prompt.build(data, "QA Lead", "X", "word " * 2000)
    assert "Use ONLY facts" in out and len(out) < 6000
    bad = tmp_path / "bad.yaml"
    bad.write_text("- a\n- b\n")
    with pytest.raises(ValueError):
        F.load(bad)
    assert "13" in F.corpus(data)


def test_ledger(tmp_path):
    con = ledger.connect(tmp_path / "l.db")
    a = ledger.add(con, "QA Lead", "A", source="reed", cv_variant="lead", today=date(2026, 10, 1))
    b = ledger.add(con, "SDET", "B", source="reed", today=date(2026, 10, 10))
    ledger.set_status(con, a, "interview", "phone screen")
    assert [r[0] for r in ledger.due(con, date(2026, 10, 20))] == [b]
    assert ledger.funnel(con)[0][:2] == ("reed", 2)
    assert ledger.funnel(con, "cv_variant")
    with pytest.raises(ValueError):
        ledger.set_status(con, a, "bogus")
    with pytest.raises(ValueError):
        ledger.set_status(con, 999, "offer")
    with pytest.raises(ValueError):
        ledger.funnel(con, "x")


def test_cli(tmp_path, facts_file, capsys):
    db = str(tmp_path / "a.db")
    base = ["--facts", str(facts_file), "--db", db]
    good = tmp_path / "good.md"
    good.write_text("Team of 13 using Selenium")
    bad = tmp_path / "bad.md"
    bad.write_text("Cut bugs 40% at Acme")
    assert main([*base, "check", str(good)]) == 0
    assert main([*base, "check", str(bad)]) == 1
    job = tmp_path / "job.txt"
    job.write_text("Lead QA")
    assert main([*base, "tailor", "--title", "T", "--company", "C", "--desc-file", str(job)]) == 0
    assert main([*base, "add", "--title", "T", "--company", "C", "--source", "s"]) == 0
    assert main([*base, "status", "1", "replied"]) == 0
    assert main([*base, "due"]) == 0
    assert main([*base, "funnel"]) == 0
    assert main([*base, "status", "99", "offer"]) == 2
    capsys.readouterr()
