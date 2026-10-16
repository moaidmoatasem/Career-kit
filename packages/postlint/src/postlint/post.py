from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Post:
    meta: dict[str, str] = field(default_factory=dict)
    body: str = ""


def parse(text: str) -> Post:
    """Parse a post file: optional `---` frontmatter of `key: value` lines, then the body."""
    text = text.lstrip("﻿").replace("\r\n", "\n")
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                meta: dict[str, str] = {}
                for raw in lines[1:i]:
                    if ":" in raw:
                        key, _, value = raw.partition(":")
                        meta[key.strip()] = value.strip().strip("\"'")
                return Post(meta=meta, body="\n".join(lines[i + 1 :]).strip())
    return Post(body=text.strip())
