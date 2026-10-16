from __future__ import annotations

import re
from pathlib import Path

from postlint.finding import ERROR, Finding

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
INTERNAL_HOST = re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:internal|corp|local|intra|lan)\b", re.I)
TICKET = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d{1,6}\b")


def load_blocklist(path: Path) -> list[tuple[str, re.Pattern[str]]]:
    """One term per line. `#` comments and blank lines ignored. `re:` prefix = regex."""
    terms: list[tuple[str, re.Pattern[str]]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            pattern = re.compile(line[3:], re.I)
        else:
            pattern = re.compile(rf"(?<!\w){re.escape(line)}(?!\w)", re.I)
        terms.append((line, pattern))
    return terms


def mask(term: str) -> str:
    """Show only the first two characters so reports never leak the full blocklist."""
    t = term[3:] if term.startswith("re:") else term
    return t[:2] + "*" * max(len(t) - 2, 1)


def check_blocklist(
    text: str, blocklist: list[tuple[str, re.Pattern[str]]], rule: str, where: str
) -> list[Finding]:
    out = []
    for term, pattern in blocklist:
        if pattern.search(text):
            out.append(Finding(rule, ERROR, f"Blocklisted term found: {mask(term)}", where))
    return out


def check_sensitive_patterns(text: str, where: str = "body") -> list[Finding]:
    """PL006: email addresses, internal hostnames, ticket IDs."""
    out = []
    if EMAIL.search(text):
        out.append(Finding("PL006", ERROR, "Email address in post", where))
    if INTERNAL_HOST.search(text):
        out.append(Finding("PL006", ERROR, "Internal hostname in post", where))
    if TICKET.search(text):
        out.append(Finding("PL006", ERROR, "Ticket-ID-like pattern in post (e.g. ABC-123)", where))
    return out
