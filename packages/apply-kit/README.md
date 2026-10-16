# apply-kit

Application copilot that **never submits anything**. You apply; it prepares and keeps you honest.

```
apply-kit tailor --title "QA Lead" --company Acme --desc-file job.txt   # compact prompt for Claude
apply-kit check tailored.md                                              # truth check vs facts
apply-kit add --title "QA Lead" --company Acme --source reed --cv lead   # log after you submit
apply-kit status 3 interview ; apply-kit due ; apply-kit funnel --by source
```
- `private/facts.yaml` (gitignored; see `facts.example.yaml`) is the only allowed source of claims.
- Truth check errors: TC001 number/percentage/year not in facts, TC002 tool not in facts, TC003 anonymized client name present.
- Ledger = SQLite in `private/`. Funnel by source or CV variant shows what actually gets replies.
- Keep `private/` out of git. This package ships code only.
