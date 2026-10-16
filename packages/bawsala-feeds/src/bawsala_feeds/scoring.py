from __future__ import annotations

from pathlib import Path

import yaml

from bawsala_feeds.model import Job


def load_rules(path: Path | None) -> dict:
    if path and path.is_file():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def score(job: Job, rules: dict) -> Job:
    """Deterministic scoring. rules: title/description: {term: weight}, location: {term: weight},
    remote_bonus, visa_bonus, exclude: [terms] (any hit -> score forced to -100)."""
    title, desc, loc = job.title.lower(), job.description.lower(), job.location.lower()
    total, reasons = 0.0, []
    for term in rules.get("exclude", []):
        if term.lower() in title:
            job.score, job.score_reasons = -100.0, [f"excluded: {term}"]
            return job
    for term, w in (rules.get("title") or {}).items():
        if term.lower() in title:
            total += w
            reasons.append(f"title:{term}({w:+g})")
    for term, w in (rules.get("description") or {}).items():
        if term.lower() in desc:
            total += w
            reasons.append(f"desc:{term}({w:+g})")
    for term, w in (rules.get("location") or {}).items():
        if term.lower() in loc:
            total += w
            reasons.append(f"loc:{term}({w:+g})")
    if job.remote and rules.get("remote_bonus"):
        total += rules["remote_bonus"]
        reasons.append(f"remote({rules['remote_bonus']:+g})")
    if job.visa_sponsorship and rules.get("visa_bonus"):
        total += rules["visa_bonus"]
        reasons.append(f"visa({rules['visa_bonus']:+g})")
    job.score, job.score_reasons = total, reasons
    return job
