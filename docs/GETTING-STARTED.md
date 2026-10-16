# Getting started (Windows, ~30 min)

Weekly loop and phases live in the Agent Runbook doc; this page is only the tool setup.

1. Install: `pip install uv`, then `uv sync --all-packages` in the repo. Run tools with `uv run <tool>`.
2. **postlint**: put private client names in `private/blocklist.txt` (gitignored), then create `.postlint.toml` with `blocklist = "private/blocklist.txt"`.
   Before every publish: `uv run postlint check drafts/post.md --pdf drafts/deck.pdf`; if PL104 fires, `uv run postlint scrub deck.pdf -o deck.clean.pdf`.
3. **li-metrics** (Fridays): LinkedIn > Analytics > Export (.xlsx), then
   `uv run li-metrics ingest export.xlsx --db private/li.db` and `uv run li-metrics report --db private/li.db --pillars private/posts.csv`.
   If ingest reports 0 rows, share sheet names and header rows (not data) so the parser can be adjusted.
4. **bawsala-feeds**: copy `config.example.yaml` and `rules.example.yaml` into `private/`, set env vars `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `REED_API_KEY`
   (Windows: `setx`), then `uv run bawsala-feeds --config private/config.yaml --out private/out`. Ask Claude to read only `private/out/shortlist.md`.
5. **Schedule** (07:00 and 19:00): Task Scheduler > Create Basic Task > Action: `uv` with arguments
   `run bawsala-feeds --config private/config.yaml --out private/out`, start in the repo folder.
6. **Never** schedule anything that writes to LinkedIn. Publish by hand via the native composer/scheduler.
