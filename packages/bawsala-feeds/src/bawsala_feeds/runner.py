from __future__ import annotations

import os
from pathlib import Path

import httpx
import yaml

from bawsala_feeds import export, scoring
from bawsala_feeds.budget import Budget
from bawsala_feeds.model import Job, dedupe
from bawsala_feeds.sources import DAILY_LIMITS, adzuna, arbeitnow, reed, remotive

REGISTRY = {
    "arbeitnow": arbeitnow.fetch,
    "remotive": remotive.fetch,
    "adzuna": adzuna.fetch,
    "reed": reed.fetch,
}


def run(
    config_path: Path, out_dir: Path, client: httpx.Client | None = None, env: dict | None = None
) -> list[Job]:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    env = env if env is not None else dict(os.environ)
    out_dir.mkdir(parents=True, exist_ok=True)
    budget = Budget(out_dir / ".budget.json")
    client = client or httpx.Client(timeout=20, headers={"User-Agent": "bawsala-feeds/0.1"})
    jobs: list[Job] = []
    for name, params in (cfg.get("sources") or {}).items():
        params = params or {}
        if name not in REGISTRY or not params.get("enabled", True):
            continue
        if not budget.allow(name, DAILY_LIMITS[name]):
            print(f"bawsala-feeds: {name}: daily budget used, skipping")
            continue
        try:
            budget.record(name)
            jobs += REGISTRY[name](client, params, env)
        except (httpx.HTTPError, KeyError) as exc:
            print(f"bawsala-feeds: {name}: skipped ({type(exc).__name__}: {exc})")
    rules = scoring.load_rules(Path(cfg["rules"]) if cfg.get("rules") else None)
    jobs = [scoring.score(j, rules) for j in dedupe(jobs)]
    jobs.sort(key=lambda j: j.score, reverse=True)
    export.write_csv(jobs, out_dir / "jobs.csv")
    export.write_shortlist(jobs, out_dir / "shortlist.md", int(cfg.get("shortlist_size", 15)))
    return jobs
