from __future__ import annotations

from datetime import datetime

import httpx

from bawsala_feeds.model import Job

URL = "https://www.reed.co.uk/api/1.0/search"
ATTRIBUTION = "Jobs via Reed.co.uk"


def _date(s: str) -> str:
    try:
        return datetime.strptime(s, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return s


def fetch(client: httpx.Client, params: dict, env: dict) -> list[Job]:
    r = client.get(
        params.get("url", URL),
        params={
            "keywords": params.get("what", "QA lead"),
            "resultsToTake": params.get("limit", 50),
        },
        auth=(env["REED_API_KEY"], ""),
    )
    r.raise_for_status()
    out = []
    for d in r.json().get("results", []):
        out.append(
            Job(
                title=d.get("jobTitle", ""),
                company=d.get("employerName", ""),
                url=d.get("jobUrl", ""),
                source="reed",
                attribution=ATTRIBUTION,
                location=d.get("locationName", ""),
                country="GB",
                posted_at=_date(str(d.get("date", ""))),
                salary_min=d.get("minimumSalary"),
                salary_max=d.get("maximumSalary"),
                salary_currency="GBP",
                description=d.get("jobDescription", ""),
            )
        )
    return out
