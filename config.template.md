# Dossier — Configuration

Per-user settings read by the `dossier` skill. Fill in the values below,
save as `config.md` at the root of your Dossier folder, and the skill
will pick them up on its next run.

Everything here is optional. If a value is missing or left as its
placeholder, the skill skips the feature that depends on it and falls back
to markdown-only behavior.

---

## Notion Tracker (Optional)

Create a new Notion database with these columns: Company (title), Role (text), Grade (select: A/B/C/D/F), Score (number), Status (select: Evaluating/Applied/Interviewing/Offer/Rejected/Passed), Date (date), Location (text), Compensation (text), Job URL (URL), Notes (text). Then paste its IDs below.

```yaml
# --- Notion Mirror (optional) ---
notion:
  enabled: false                            # Set to true to enable Notion sync
  data_source_id: "<your-notion-data-source-id>"
  parent_page_url: "<your-notion-parent-page-url>"
  tracker_url: "<your-notion-tracker-url>"
  sync_compensation: false                  # Set to true to sync salary data to Notion
```

**How to find these in Notion:**

- Open your duplicated tracker page in Notion.
- Click Share → Copy link. That's your `notion_tracker_url`.
- The ID at the end of that URL (a 32-character hex string) is also
  typically the `notion_parent_page_url` target.
- The `notion_data_source_id` is the database ID for the tracker view.
  If you're unsure, ask Claude to help find it after connecting Notion:
  *"Find the data source ID for my Dossier tracker in Notion."*

If any of these values are missing or still set to the placeholder text,
the skill will log evaluations to `evals/` as markdown only and mention
this once per session.

---

## Optional preferences

Uncomment and set any of the following to override skill defaults.

```yaml
# Default location to apply to job searches when the user doesn't specify.
# default_search_location: "Remote"

# Cap on the number of results returned by Mode 2 (Job Search).
# job_search_result_cap: 8

# Whether to offer the day-7 follow-up reminder automatically for grade
# B+ and higher evaluations. Default: true.
# auto_offer_followup_reminder: true

# Word-count ceiling for cover letters (Mode 6). Hard limit — drafts
# exceeding this are compressed before saving. Default: 400.
# cover_letter_word_cap: 400
```

---

## Notes

- This file is plain markdown with fenced YAML blocks. The skill parses
  the YAML blocks; everything else is documentation for you.
- Do not commit this file to a public repo once filled in — the IDs are
  tied to your Notion workspace. The repo's `.gitignore` already excludes
  `config.md`; keep it that way.
- If you rotate or re-duplicate your Notion tracker, update the values
  here and the skill will pick up the new tracker on the next run.
