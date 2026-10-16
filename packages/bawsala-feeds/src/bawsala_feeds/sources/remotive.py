from __future__ import annotations

import httpx

from bawsala_feeds.model import Job

URL = "https://remotive.com/api/remote-jobs"
ATTRIBUTION = "Source: Remotive (remotive.com)"


def fetch(client: httpx.Client, params: dict, env: dict) -> list[Job]:
    q = {k: params[k] for k in ("category", "search", "limit") if k in params}
    r = client.get(params.get("url", URL), params=q)
    r.raise_for_status()
    out = []
    for d in r.json().get("jobs", []):
        out.append(
            Job(
                title=d.get("title", ""),
                company=d.get("company_name", ""),
                url=d.get("url", ""),
                source="remotive",
                attribution=ATTRIBUTION,
                location=d.get("candidate_required_location", ""),
                remote=True,
                posted_at=str(d.get("publication_date", ""))[:10],
                description=d.get("description", ""),
            )
        )
    return out
