from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_HYPE = [
    "game-changer",
    "game changer",
    "revolutionary",
    "unlock",
    "supercharge",
    "10x",
    "thrilled",
    "humbled",
    "synergy",
    "disrupt",
]


@dataclass
class Config:
    max_chars: int = 3000
    hook_chars: int = 140
    hook_lines: int = 2
    max_hashtags: int = 3
    max_pdf_mb: int = 100
    max_pages: int = 20
    hype_words: list[str] = field(default_factory=lambda: list(DEFAULT_HYPE))
    blocklist_path: Path | None = None


def load(path: Path | None = None) -> Config:
    """Load `.postlint.toml` (explicit path, else cwd). Missing file gives defaults."""
    p = path if path is not None else Path(".postlint.toml")
    cfg = Config()
    if not p.is_file():
        return cfg
    data = tomllib.loads(p.read_text(encoding="utf-8"))
    int_keys = ("max_chars", "hook_chars", "hook_lines", "max_hashtags", "max_pdf_mb", "max_pages")
    for key in int_keys:
        if key in data:
            setattr(cfg, key, int(data[key]))
    if "hype_words" in data:
        cfg.hype_words = [str(w) for w in data["hype_words"]]
    if "blocklist" in data:
        cfg.blocklist_path = (p.parent / str(data["blocklist"])).resolve()
    return cfg
