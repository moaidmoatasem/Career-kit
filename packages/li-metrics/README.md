# li-metrics

Turn LinkedIn's creator-analytics `.xlsx` export (Analytics > Export, up to 365 days) into a SQLite history and a weekly report.
No LinkedIn API, no credentials.

```
li-metrics ingest export.xlsx --db li-metrics.db
li-metrics report --db li-metrics.db [--end 2026-10-16] [--pillars posts.csv]
```

Ingest is idempotent (re-importing overlapping exports overwrites the same days/posts). The reader maps columns by header name
(Date, Impressions, Engagements, New followers, Post URL) and ignores the rest, because LinkedIn does not document the layout.
If an export is not recognised, open an issue with the sheet names and header rows only (no data).
`posts.csv` (`url,pillar`) is maintained by you and enables the best-pillar line.
