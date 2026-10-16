# careerkit

Small, offline-first tools for LinkedIn career growth and job search. No LinkedIn automation, no scraping, no credentials.

| Package | Status | Purpose |
|---|---|---|
| [postlint](packages/postlint) | v0.1 | Lint post drafts and PDF carousels before you publish manually |
| [li-metrics](packages/li-metrics) | v0.1 | LinkedIn analytics XLSX to SQLite to weekly report |
| [bawsala-feeds](packages/bawsala-feeds) | v0.1 | Terms-aware job feeds (Arbeitnow, Remotive, Adzuna, Reed) + rule scoring |
| [MCP pre-install checklist](docs/mcp-preinstall-checklist.md) | v0.1 | Vetting checklist before installing any MCP server |

## Terms and guardrails

- Publishing is always manual (LinkedIn's native composer/scheduler). These tools never post, like, comment or message.
- LinkedIn API Terms forbid using the APIs to automate posting; nothing here calls LinkedIn.
- Never commit cookies, tokens, blocklists, drafts or analytics exports. Secrets scanning runs in pre-commit and CI.
- Respect each job source's terms and rate limits (relevant from the feeds milestone).

## Develop

```
uv sync --all-packages
uv run pytest --cov-fail-under=85  # or per package, see CI
uv run ruff check .
pre-commit install
```

MIT licensed.
