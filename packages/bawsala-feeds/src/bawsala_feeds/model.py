from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field


@dataclass
class Job:
    title: str
    company: str
    url: str
    source: str
    attribution: str
    location: str = ""
    country: str = ""
    remote: bool = False
    posted_at: str = ""
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str = ""
    visa_sponsorship: bool | None = None
    sponsorship_evidence: str = ""
    description: str = ""
    score: float = 0.0
    score_reasons: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        norm = "|".join(re.sub(r"\W+", " ", s.lower()).strip() for s in (self.title, self.company))
        return hashlib.sha1(norm.encode(), usedforsecurity=False).hexdigest()[:12]

    def to_row(self) -> dict[str, object]:
        d = asdict(self)
        d["id"] = self.id
        d["score_reasons"] = "; ".join(self.score_reasons)
        d.pop("description")
        return d


def dedupe(jobs: list[Job]) -> list[Job]:
    """Keep the first job per id (title+company); prefer the one with sponsorship info."""
    best: dict[str, Job] = {}
    for j in jobs:
        cur = best.get(j.id)
        if cur is None or (cur.visa_sponsorship is None and j.visa_sponsorship is not None):
            best[j.id] = j
    return list(best.values())
