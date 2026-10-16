from __future__ import annotations

from collections.abc import Callable

import httpx

from bawsala_feeds.model import Job

# A source is fetch(client, params, env) -> list[Job]. DAILY_LIMITS enforces each source's terms.
Fetch = Callable[[httpx.Client, dict, dict], list[Job]]

DAILY_LIMITS = {"remotive": 4, "arbeitnow": 48, "adzuna": 200, "reed": 200}
