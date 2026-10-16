from __future__ import annotations

import yaml

RULES = """Rules (strict):
- Use ONLY facts from the FACTS block. Do not add numbers, percentages, tools, employers, dates or claims that are not in it.
- You may reorder, select, shorten and rephrase. Mirror the job's wording only where it is truthful.
- Keep client/employer-sensitive names anonymous exactly as in FACTS.
- Output: (1) tailored CV in Markdown, (2) a cover note of at most 120 words, (3) a list 'GAPS' of job requirements the facts do not support (do not invent anything for them)."""


def build(facts: dict, title: str, company: str, description: str, max_desc: int = 3000) -> str:
    desc = " ".join(description.split())[:max_desc]
    return (
        f"Tailor my CV for: {title} at {company}.\n\n{RULES}\n\n"
        f"JOB (truncated):\n{desc}\n\nFACTS:\n{yaml.safe_dump(facts, allow_unicode=True, sort_keys=False)}"
    )
