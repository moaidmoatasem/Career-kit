from pathlib import Path

import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas


@pytest.fixture
def make_pdf(tmp_path):
    def _make(name="deck.pdf", pages=2, size=(1080, 1350), text="Hello deck", meta=None):
        path = tmp_path / name
        c = canvas.Canvas(str(path), pagesize=size, invariant=True)
        if meta:
            c.setAuthor(meta.get("author", ""))
            c.setTitle(meta.get("title", ""))
        for _ in range(pages):
            c.drawString(50, 50, text)
            c.showPage()
        c.save()
        return path

    return _make


@pytest.fixture
def mixed_pdf(tmp_path):
    w = PdfWriter()
    w.add_blank_page(100, 100)
    w.add_blank_page(200, 300)
    p = tmp_path / "mixed.pdf"
    with p.open("wb") as fh:
        w.write(fh)
    return p


@pytest.fixture
def write(tmp_path):
    def _w(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _w
