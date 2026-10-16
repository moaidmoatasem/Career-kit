# bawsala-feeds

Pluggable job-feed fetchers with deterministic, rule-based scoring. Zero LLM tokens; Claude only reads the small `shortlist.md`.

```
cp config.example.yaml config.yaml && cp rules.example.yaml rules.yaml
bawsala-feeds --config config.yaml --out out
```
Outputs `out/jobs.csv` (normalized schema incl. `source`, `attribution`, `visa_sponsorship`, `sponsorship_evidence`, `score_reasons`) and `out/shortlist.md`.

## Terms and guardrails
- Terms are enforced in code: Remotive max 4 calls/day (persisted in `out/.budget.json`); attribution string kept on every row.
- This repo ships **code only**. Do not publish or redistribute fetched job data (Remotive forbids passing jobs to third-party sites).
- Keys via env vars (`ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `REED_API_KEY`); never commit them.
- Egypt/Gulf boards (Wuzzuf, Bayt, NaukriGulf) and LinkedIn have no public API: use email alerts, not scrapers.
- Arbeitnow's UK endpoint: set `url:` under `sources.arbeitnow` once you confirm the path in their docs.
