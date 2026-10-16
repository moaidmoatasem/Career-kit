# MCP pre-install checklist

Run before adding any MCP server to Claude (or another client). Any "no" on 1-4 means do not install.

1. **Source**: repo is public, maintained (commit in last 6 months), license is clear, and you read the tool list.
2. **Auth**: uses official OAuth or scoped API keys. It does NOT ask for browser cookies (e.g. `li_at`), passwords or session tokens.
3. **Terms**: the target service's terms allow this use. For LinkedIn: no scraping, no automated posting/engagement.
4. **Scan**: run an MCP scanner (e.g. Snyk Agent Scan) and review tool descriptions for prompt-injection text.
5. **Scope**: read-only tools preferred; write tools require human approval per call.
6. **Network**: lists which hosts it contacts; nothing unexpected.
7. **Secrets**: keys live in env/secret store, never in the repo or the MCP config committed to git.
8. **Token cost**: count the tools it adds; disable unused ones (every tool description costs context on every turn).
9. **Pin**: pin the version/commit; re-review on upgrade.
10. **Exit**: know how to revoke the token and uninstall.
