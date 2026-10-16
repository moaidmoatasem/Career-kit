from __future__ import annotations

import re

from postlint.config import Config
from postlint.finding import ERROR, INFO, WARNING, Finding

HASHTAG = re.compile(r"(?<!\w)#\w+", re.UNICODE)
URL = re.compile(r"https?://\S+|www\.\S+", re.I)


def check_text(body: str, cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    if len(body) > cfg.max_chars:
        out.append(
            Finding("PL001", ERROR, f"Body is {len(body)} chars (max {cfg.max_chars})", "body")
        )

    hook = body.split("\n\n", 1)[0].strip()
    hook_lines = [ln for ln in hook.split("\n") if ln.strip()]
    if len(hook) > cfg.hook_chars or len(hook_lines) > cfg.hook_lines:
        out.append(
            Finding(
                "PL002",
                WARNING,
                f"Hook is {len(hook)} chars / {len(hook_lines)} lines "
                f"(aim for <= {cfg.hook_chars} chars, <= {cfg.hook_lines} lines)",
                "hook",
            )
        )

    tags = HASHTAG.findall(body)
    if len(tags) > cfg.max_hashtags:
        out.append(
            Finding("PL003", WARNING, f"{len(tags)} hashtags (max {cfg.max_hashtags})", "body")
        )

    lowered = body.lower()
    for word in cfg.hype_words:
        if word.lower() in lowered:
            out.append(Finding("PL004", WARNING, f"Hype word: '{word}'", "body"))

    if URL.search(body):
        msg = "External link in body (consider putting it in a comment)"
        out.append(Finding("PL007", INFO, msg, "body"))
    return out
