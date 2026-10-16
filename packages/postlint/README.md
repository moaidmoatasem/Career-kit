# postlint

Pre-publish linter for LinkedIn posts and PDF carousels. Offline, one dependency (`pypdf`).

```
postlint check post.md [--pdf deck.pdf] [--blocklist terms.txt] [--format text|json]
postlint scrub deck.pdf -o deck.clean.pdf
```

Exit codes: `0` clean/warnings, `1` at least one error, `2` usage or I/O error.

| Rule | Check | Severity |
|---|---|---|
| PL001 | Body over 3,000 characters | error |
| PL002 | Hook over ~140 chars or 2 lines | warning |
| PL003 | More than 3 hashtags | warning |
| PL004 | Hype words (configurable) | warning |
| PL005 | Blocklist hit in body | error |
| PL006 | Email, internal hostname, ticket ID | error |
| PL007 | External link in body | info |
| PL101 | PDF over 100 MB | error |
| PL102 | More than 20 pages | warning |
| PL103 | Mixed page sizes | error |
| PL104 | PDF metadata present (`postlint scrub` fixes) | error |
| PL105 | Blocklist hit in PDF text | error |

Post file: optional `---` frontmatter (`title`, `pillar`, `format`, `lang`, `slot`, `link`), then the body.
Blocklist file: one term per line, `#` comments, `re:` prefix for regex. Matches are case-insensitive whole words and
reports only show the first two letters of a hit. Keep the blocklist private; never commit it.
Config: `.postlint.toml` (`max_chars`, `hook_chars`, `hook_lines`, `max_hashtags`, `max_pdf_mb`, `max_pages`,
`hype_words`, `blocklist`).

Pre-commit: `repos: - repo: <this repo>` with hook id `postlint`.
