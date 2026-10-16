from __future__ import annotations

from datetime import UTC, datetime

import httpx

from bawsala_feeds.model import Job

URL = "https://www.arbeitnow.com/api/job-board-api"
ATTRIBUTION = "Jobs via Arbeitnow (arbeitnow.com)"


def fetch(client: httpx.Client, params: dict, env: dict) -> list[Job]:
    r = client.get(
        params.get("url", URL),
        params={"visa_sponsorship": "true"} if params.get("visa_only") else None,
    )
    r.raise_for_status()
    out = []
    for d in r.json().get("data", []):
        ts = d.get("created_at")
        posted = datetime.fromtimestamp(ts, UTC).date().isoformat() if ts else ""
        visa = d.get("visa_sponsorship")
        out.append(
            Job(
                title=d.get("title", ""),
                company=d.get("company_name", ""),
                url=d.get("url", ""),
                source="arbeitnow",
                attribution=ATTRIBUTION,
                location=d.get("location", ""),
                remote=bool(d.get("remote")),
                posted_at=posted,
                visa_sponsorship=visa if isinstance(visa, bool) else None,
                sponsorship_evidence="arbeitnow visa_sponsorship flag" if visa else "",
                description=d.get("description", ""),
            )
        )
    return out
