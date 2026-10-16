import json

from postlint import report
from postlint.cli import main
from postlint.finding import ERROR, Finding

GOOD = "---\ntitle: t\n---\nA clear hook.\n\nSome useful body."


def test_clean_exit0(write, capsys):
    assert main(["check", str(write("p.md", GOOD))]) == 0
    assert "clean" in capsys.readouterr().out


def test_error_exit1_json(write, capsys):
    p = write("p.md", "x" * 3001)
    assert main(["check", str(p), "--format", "json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data["exit_code"] == 1 and data["findings"][0]["rule"] == "PL001"


def test_arabic_post(write, capsys):
    body = "---\nlang: ar\n---\nكيف تختبر نظامًا قبل الإطلاق؟\n\nثلاث نقاط عملية."
    assert main(["check", str(write("ar.md", body)), "--format", "json"]) == 0
    capsys.readouterr()


def test_blocklist_flag_and_pdf(write, make_pdf, capsys):
    bl = write("bl.txt", "Acme\n")
    pdf = make_pdf(text="Acme roadmap", meta={"author": "x"})
    post = str(write("p.md", "About Acme."))
    code = main(["check", post, "--blocklist", str(bl), "--pdf", str(pdf)])
    out = capsys.readouterr().out
    assert code == 1 and "PL005" in out and "PL105" in out and "PL104" in out


def test_config_blocklist(write, capsys):
    write("bl.txt", "Acme\n")
    cfg = write("c.toml", 'blocklist = "bl.txt"\n')
    assert main(["check", str(write("p.md", "Acme")), "--config", str(cfg)]) == 1
    capsys.readouterr()


def test_scrub_cmd(make_pdf, tmp_path, capsys):
    out = tmp_path / "o.pdf"
    assert main(["scrub", str(make_pdf()), "-o", str(out)]) == 0
    assert out.exists()
    capsys.readouterr()


def test_usage_errors(tmp_path, capsys):
    assert main(["check", str(tmp_path / "missing.md")]) == 2
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a pdf")
    assert main(["scrub", str(bad), "-o", str(tmp_path / "o.pdf")]) == 2
    capsys.readouterr()


def test_report_text_summary():
    fs = [Finding("PL001", ERROR, "m", "body"), Finding("PL003", "warning", "w", "body")]
    out = report.render_text(fs)
    assert "1 error(s), 1 warning(s)" in out
