# CLAUDE.md

Operating contract for the Dossier vault.

This is a **job search operations workspace** — an Obsidian-compatible markdown vault for managing evaluations, outreach, interview prep, research, and pipeline tracking.

If uncertain about anything below, ask before proceeding.

---

## Key Files

- `profile.md` — target roles, match signals, roles to avoid. **Source of truth for fit.**
- `cv.md` — work history and capabilities. **Source of truth for claims.**
- `README.md` — folder layout, frontmatter schemas, naming conventions, archive rules.
- `dossier.skill` — skill definition. Do not edit without creating a backup first.
- `dashboard.md` — Dataview queries for Obsidian pipeline views.

The vault owns all pipeline state and narrative content. If a Notion tracker is configured, it serves as an optional mirror — the vault is always the source of truth.

---

## How to Work

1. Read `profile.md` and `cv.md` before writing any eval or outreach.
2. Check for existing artifacts for the target company before creating new ones.
3. Follow the naming and frontmatter conventions in `README.md`.
4. Place files in the correct folder. Wrong placement breaks Dataview queries.
5. If a file already exists for the same company + date, version with `-v#` suffix (see SKILL.md dedup rules).

When the task is naturally multi-artifact (a scan that surfaces leads, an eval that flows into outreach), that's fine — don't artificially constrain the workflow.

---

## Integrity Rules

These are non-negotiable:

- **Grade honestly.** If a role is a poor fit, say so. Every eval must include both strengths and concerns. Do not inflate grades or suppress negative signals.
- **Don't fabricate.** Never invent work history, skills, references, or contact information not found in `cv.md` or provided by the user.
- **Draft only.** Outreach and cover letters are drafts. The user decides when and whether to send.
- **Archive, don't delete.** Terminal rows (Rejected, Passed, Offer-Declined, 90+ days cold) go to `archive/[company-slug]/`. Nothing is deleted.

---

## Outreach Standards

- Sound human, not templated.
- Match tone to channel — LinkedIn is conversational, email is professional.
- Never misrepresent the candidate's background.

---

## Safety

- No credentials, API keys, or passwords in vault files.
- Do not include sensitive personal data unless the user provides it.
- Redact sensitive information if encountered in job descriptions or emails.

---

## When to Pause and Ask

- The user asks to modify `dossier.skill` (back up first).
- A company has existing artifacts and the new request might conflict with them.
- Vault structure changes are implied but not stated.

Don't over-escalate. Making a judgment call on a borderline grade is your job, not the user's.

---

## Prohibited

- Inflating grades or hiding concerns.
- Fabricating history, skills, or references.
- Reorganizing the vault without approval.
- Editing `dossier.skill` without a backup.
- Creating files outside the established folder structure.
- Deleting files.

---

End of CLAUDE.md
