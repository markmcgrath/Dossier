# Mode 5: Outreach — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User asks to draft outreach for a specific role, or the eval post-action menu (Mode 1 step 7) leads here.

## Frontmatter Schema

```yaml
type: outreach
company: "Company Name"
role: "Job Title"
channel: "LinkedIn" | "Email" | "LinkedIn + Email"
date: YYYY-MM-DD
status: drafted | sent | replied | no-response | archived
related_eval: "[[eval-company-slug-date]]"
target_titles: ""        # comma-separated list of target recipient titles
sent_date: ""
first_response_date: ""
followup_dates: []
touch_count: 0
```

## Output Template

```
# [Company] Outreach — [Role Title]

## Email Version

**Subject:** [Role title] — quick note

[Body: 150–250 words. Professional tone. Lead with the strategic angle from the eval. Reference a specific company initiative, not generic praise. Close with a clear ask (15-min call).]

---

## LinkedIn Connection-Request Version (<300 chars)

[Short, conversational. Reference the role and one specific credential.]

---

## Follow-up Schedule

| Touch | Channel | Date | Status |
|-------|---------|------|--------|
| 1 — Initial | [LinkedIn/Email] | [send date] | Pending |
| 2 — Follow-up | [Email/LinkedIn] | [send date + 5–7 days] | Pending |
| 3 — Final | [Email] | [Touch 2 + 7–10 days] | Pending |
| Archive | — | [Touch 3 + 14 days] | — |

After 3 touches with no response, archive the outreach. Do not follow up a 4th time.

---

## Notes Before Sending

- [Strategic framing: which narrative to lead with and why]
- [Channel sequencing: LinkedIn first → email follow-up, or vice versa]
- [Any gates or conditions from the eval that must be resolved before sending]
```

## Channel Guidelines

- **LinkedIn connection requests:** Max 300 characters. Conversational. Reference one specific credential + the role.
- **LinkedIn InMails / messages:** Under 150 words. Personalize beyond "I saw your profile" — reference a company project, blog post, or initiative.
- **Email:** 150–300 words. Professional. Quantified proof points. Clear subject line with role title.
- **Multi-channel:** Send LinkedIn first. If no response in 5–7 days, follow up via email. Never send both on the same day.

## Follow-up Cadence Rules

- Touch 1 (initial outreach): day 0
- Touch 2 (follow-up): day 5–7
- Touch 3 (final): day 12–17
- Archive (no further contact): day 26–31
- When updating frontmatter after sending, set `sent_date` to today, increment `touch_count`, and append the next follow-up date to `followup_dates`.
