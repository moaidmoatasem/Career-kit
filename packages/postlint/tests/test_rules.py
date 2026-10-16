from postlint import post
from postlint.config import Config, load
from postlint.rules import confidential as conf
from postlint.rules import pdf as pdfr
from postlint.rules import text as txt


def ids(fs):
    return {f.rule for f in fs}


def test_parse_frontmatter_and_plain():
    p = post.parse('---\ntitle: "T"\nlang: ar\n---\nbody here')
    assert p.meta == {"title": "T", "lang": "ar"} and p.body == "body here"
    assert post.parse("just text\r\nmore").body == "just text\nmore"
    assert post.parse("---\nunterminated").body.startswith("---")


def test_length_and_arabic_count():
    cfg = Config(max_chars=10)
    assert "PL001" in ids(txt.check_text("x" * 11, cfg))
    ar = "مرحبا" * 2  # 10 characters, must not be counted as bytes
    assert "PL001" not in ids(txt.check_text(ar, cfg))


def test_hook_hashtags_hype_link():
    cfg = Config()
    body = "a" * 200 + "\n\nBody #a #b #c #d game-changer https://x.io"
    r = ids(txt.check_text(body, cfg))
    assert {"PL002", "PL003", "PL004", "PL007"} <= r
    assert "PL002" in ids(txt.check_text("l1\nl2\nl3\n\nrest", cfg))
    assert ids(txt.check_text("Short hook.\n\nFine.", cfg)) == set()


def test_blocklist(write):
    p = write("bl.txt", "# c\n\nAcmeCorp\nre:proj-\\d+\n")
    bl = conf.load_blocklist(p)
    hit = conf.check_blocklist("we at acmecorp did proj-42", bl, "PL005", "body")
    assert len(hit) == 2
    assert "AcmeCorp" not in hit[0].message and "Ac" in hit[0].message
    assert conf.check_blocklist("AcmeCorporation", bl, "PL005", "body") == []


def test_sensitive_patterns():
    msgs = [f.message for f in conf.check_sensitive_patterns("a@b.com db.corp ABC-123")]
    assert len(msgs) == 3
    assert conf.check_sensitive_patterns("clean text") == []


def test_config_load(write, tmp_path):
    assert load(tmp_path / "none.toml").max_chars == 3000
    p = write(".postlint.toml", 'max_chars = 50\nhype_words = ["wow"]\nblocklist = "bl.txt"\n')
    c = load(p)
    assert c.max_chars == 50 and c.hype_words == ["wow"] and c.blocklist_path.name == "bl.txt"


def test_pdf_rules(make_pdf, mixed_pdf, write):
    cfg = Config(max_pages=1, max_pdf_mb=0)
    d = make_pdf(pages=2, meta={"author": "Me", "title": "T"}, text="secret-sauce")
    bl = conf.load_blocklist(write("b.txt", "secret-sauce\n"))
    r = ids(pdfr.check_pdf(d, cfg, bl))
    assert {"PL101", "PL102", "PL104", "PL105"} <= r
    assert "PL103" in ids(pdfr.check_pdf(mixed_pdf, Config(), []))


def test_scrub_clears_metadata(make_pdf, tmp_path):
    d = make_pdf(meta={"author": "Me", "title": "T"})
    out = tmp_path / "clean.pdf"
    pdfr.scrub(d, out)
    assert "PL104" not in ids(pdfr.check_pdf(out, Config(), []))
