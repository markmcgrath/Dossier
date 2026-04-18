# Mode 2.1: Portal Scan — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User says "scan my target companies", "check for new jobs at [company]", "portal scan", or when Mode 2 is invoked and `target_companies` is configured in `config.md`.

**Prerequisite:** `target_companies` must be defined in `config.md`. If not configured, explain the feature and show the config template:
```yaml
target_companies:
  - name: "Anthropic"
    ats: greenhouse
    board_token: "anthropic"
  - name: "Stripe"
    ats: lever
    board_token: "stripe"
  - name: "Startup Co"
    ats: manual
    url: "https://startup.co/careers"
```

**Rate limiting note:** Portal scanning is session-triggered, not automated. Run once per session. Rapid repeated scans are not recommended.

**What to do:**

For each company in `target_companies`:

**1. Greenhouse ATS** (`ats: greenhouse`):
- Fetch `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true` using `WebFetch`
- Parse the JSON response to extract: job title, department, location, URL, posting date
- Filter to roles matching the user's target role types from `profile.md` (title keywords, seniority level, function)
- Cross-reference against `evals/` — skip any role with an existing eval file in the last 90 days
- Output for new matching roles: title, department, location, URL

**2. Lever, Ashby, or unknown ATS** (`ats: lever | ashby`):
- Fall back to browser automation via Claude in Chrome
- Use standard fallback URLs:
  - Lever: `https://jobs.lever.co/{board_token}`
  - Ashby: `https://jobs.ashbyhq.com/{board_token}`
  - Greenhouse (fallback): `https://boards.greenhouse.io/{board_token}`
- Navigate and use `read_page` or `get_page_text` to extract job listings
- Parse to extract: title, department, location, URL
- Apply the same filtering and dedup logic as Greenhouse

**3. Manual ATS** (`ats: manual` with a `url` field):
- Navigate directly to the provided URL via browser automation
- Extract listings from page text
- Apply the same filtering and dedup logic

**Output structure:**

```
# Portal Scan — [YYYY-MM-DD]

## Summary
- Companies scanned: [N]
- New matching roles found: [N]
- Already evaluated (skipped): [N]

## [Company Name]

**Status:** [N] new role(s) found | No new matching roles | API unreachable (used fallback)

### New Roles
[If roles found, list each as:]
- **[Job Title]** | [Department] | [Location]
  [URL]

[Or if none:]
No new roles matching your target criteria.

### Already Evaluated
[If any evals exist for this company in the last 90 days:]
- [Role Title] — [[eval-slug-date]] | Grade [X], status: [Y]

---

## Next Steps

[If new roles found:]
- **Quick evaluation:** Run Mode 12 (Batch Pipeline) to evaluate all new roles at once
- **Individual evaluation:** Run Mode 1 on any role
- **Skip a role:** Just ignore it — Portal Scan only tracks roles passing your filters

[If no new roles found:]
No action needed. Scan again next session to check for updates.
```

**Save scan results** to `daily/portal-scan-[YYYY-MM-DD].md` with frontmatter:
```yaml
---
type: portal-scan
date: YYYY-MM-DD
companies_scanned: N
new_roles_found: N
ats_types_used: [greenhouse, lever, manual]
---
```

**Error handling:**
- If a company's ATS endpoint is unreachable or returns an error, note it in the output and skip to the next company. Do not halt the entire scan.
- If Greenhouse API returns no jobs, note "No jobs currently posted" rather than treating it as an error.
- If browser automation fails, mention the error but proceed with other companies.
