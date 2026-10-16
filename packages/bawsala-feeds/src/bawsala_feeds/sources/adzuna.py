from __future__ import annotations

import httpx

from bawsala_feeds.model import Job

ATTRIBUTION = "Jobs by Adzuna (adzuna.co.uk)"


def fetch(client: httpx.Client, params: dict, env: dict) -> list[Job]:
    country = params.get("country", "gb")
    base = params.get("url", f"https://api.adzuna.com/v1/api/jobs/{country}/search/1")
    q = {
        "app_id": env["ADZUNA_APP_ID"],
        "app_key": env["ADZUNA_APP_KEY"],
        "what": params.get("what", "QA lead"),
        "results_per_page": params.get("limit", 50),
        "content-type": "application/json",
    }
    r = client.get(base, params=q)
    r.raise_for_status()
    out = []
    for d in r.json().get("results", []):
        out.append(
            Job(
                title=d.get("title", ""),
                company=(d.get("company") or {}).get("display_name", ""),
                url=d.get("redirect_url", ""),
                source="adzuna",
                attribution=ATTRIBUTION,
                location=(d.get("location") or {}).get("display_name", ""),
                country=country.upper(),
                posted_at=str(d.get("created", ""))[:10],
                salary_min=d.get("salary_min"),
                salary_max=d.get("salary_max"),
                salary_currency="GBP" if country == "gb" else "",
                description=d.get("description", ""),
            )
        )
    return out
