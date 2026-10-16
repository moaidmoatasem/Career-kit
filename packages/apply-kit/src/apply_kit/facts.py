from __future__ import annotations

from pathlib import Path

import yaml


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("facts file must be a YAML mapping")
    return data


def corpus(data: object) -> str:
    """Flatten every claim in the facts file into one lowercase searchable text.

    `anonymize` and `extra_vocabulary` are policy lists, not claims, so they are excluded."""
    parts: list[str] = []

    def walk(x: object) -> None:
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif x is not None:
            parts.append(str(x))

    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if k not in ("anonymize", "extra_vocabulary")}
    walk(data)
    return "\n".join(parts).lower()
