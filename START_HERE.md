# Start Here — Onboarding Script

> **For the user:** Just tell Claude *"Read START_HERE.md and walk me through setup."*
> Claude will follow this script. You'll be asked for your resume and a few targeting
> preferences, and it'll handle the rest. About 5–10 minutes.

---

## For Claude: first-run onboarding

When the user asks you to walk them through setup, follow these steps in order. Do not skip steps. Confirm with the user after each file you create. If the user interrupts to ask something off-script, answer briefly, then return to this playbook.

### Step 1 — Verify the Cowork Project is set up

Before asking for anything, confirm:

- The user is running in a **Cowork Project** in Claude Desktop (not Chat or plain Code mode). Cowork is required because Dossier needs file-write access to the vault folder.
- The Dossier folder is **granted as the Project's file access**. Sanity check: look for `cv.template.md`, `profile.template.md`, and `skill/SKILL.md` inside the project folder.
- `dossier.skill` is **installed via Customize → Skills**.

If any of these is missing, pause and walk the user through fixing it before continuing. Do not try to proceed with setup if the skill isn't attached or if file access isn't granted — the later steps depend on writing files to the vault.

If the user is running on Claude Code mode / CLI instead of Cowork, flag this once: *"Dossier is written for Cowork; some connector-backed modes (Indeed, Dice, Gmail, Calendar, Apollo) may need manual MCP config here. Core evaluation (Mode 1) will work either way."* Then continue.

### Step 2 — Ask for the resume

Ask the user to share their resume in whichever form is easiest:

- Paste the full text into chat
- Share a Google Doc or LinkedIn profile export link
- Attach a PDF or DOCX

If they don't have a current resume handy, offer to help build one — ask a few questions about their last 3–4 roles, key accomplishments, and skills, and construct a baseline from that.

### Step 3 — Generate `cv.md`

Parse the resume into the structure defined in `cv.template.md` (same headings, same order). Write the result to `cv.md` at the root of the vault. Then:

- Show the user the generated file (or a condensed preview if it's long).
- Ask them to flag anything inaccurate or missing.
- Revise until they confirm it's ready.

`cv.md` is the source of truth for capability fit — don't let it ship with errors. Take the time to get it right.

### Step 4 — Ask targeting questions for `profile.md`

Ask the user these questions (adapt phrasing and follow-ups to what they've said so far):

1. What roles are you targeting? (titles, seniority level)
2. What industries or domains? Any hard avoids?
3. Remote, hybrid, or onsite? Which locations?
4. Salary floor and ideal target range?
5. Company size / stage preferences (startup, scaleup, enterprise)?
6. What kind of work energizes you, and what drains you?
7. Any red-flag signals that should tank a role's grade? Examples: mandatory in-office for roles advertised as remote, unpaid take-home assignments, "rockstar" / "we work hard play hard" language, salary below your floor, etc.

If any answer is vague, ask one follow-up. Don't press for more than one.

### Step 5 — Generate `profile.md`

Write the answers into the structure defined in `profile.template.md`. Save as `profile.md` at the root of the vault. Then:

- Show the user the result.
- Confirm the "Roles to Avoid" list, the salary floor, and the match signals are accurate.
- Revise until they confirm.

### Step 6 — Optional: `stories.md`

Mention that `stories.md` is a STAR+R behavioral-interview story bank, best built *as* interviews happen rather than up front. Offer two options:

- Create an empty skeleton from `stories.template.md` now (useful if they want the structure to slot stories into later)
- Skip for now (default — create it when the first interview prep happens)

### Step 7 — Optional: `config.md`

Only bring this up if the user mentions Notion, Gmail, Calendar, or Apollo integrations. If they do, walk them through creating `config.md` from `config.template.md` and filling in their integration IDs. Otherwise, skip — the skill runs fine without `config.md`.

### Step 8 — Run Mode 0

Execute the Mode 0 health check (see `SKILL.md` §"Mode 0: Health Check"). Report the result:

- If all checks pass, say so briefly and move to Step 9.
- If any check fails, surface the specific file or field that's wrong and help the user fix it before moving on.

### Step 9 — Offer the first evaluation

Ask the user to paste a real job description they're actively considering. Then:

1. Run Mode 1 against it.
2. Save the eval to `evals/eval-<company-slug>-<yyyy-mm-dd>.md`.
3. Walk through the grade, the top 2–3 strengths, the top 2–3 concerns, and the one-sentence recommendation.
4. Point out where that file lives in the vault and how future evals will land there automatically.

### First-success criteria

Setup is complete when all of the following are true:

- `cv.md` exists and the user has confirmed it
- `profile.md` exists and the user has confirmed it
- Mode 0 reports clean
- At least one real eval has been saved to `evals/`

Once all four are true, tell the user setup is done and suggest what to ask for next (see "Once setup is done" below).

---

## Troubleshooting during onboarding

**Claude can't see `cv.template.md`, `profile.template.md`, or the `skill/` folder.**
The Dossier folder isn't attached as Project knowledge (vs. being uploaded as a one-off attachment). Have the user re-attach it as Project knowledge in the Claude Project settings.

**The skill's modes aren't triggering.**
`dossier.skill` isn't attached as the Project's skill, or is attached as attachment-knowledge instead. Have the user upload it as a skill in the Project settings.

**Claude asks to write a file but says it doesn't have permission.**
Claude Projects controls file-write access per Project. Have the user enable file-write permissions for the Project, or accept the proposed content in chat and paste it into the file manually.

**Mode 0 fails on missing `cv.md` / `profile.md` even after generation.**
Check that the file was actually written to the vault root, not just displayed in chat. If it was only displayed, re-run the write step explicitly: *"Write that to `cv.md`."*

**Mode 1 returns a grade that feels wildly off.**
The grade is advisory, not authoritative — every eval includes a bias caveat. If the mismatch is systematic, `profile.md` is probably vague. Offer to re-review `profile.md` after 3–5 evals have been run, using the accumulated evals as calibration signal.

---

## Once setup is done

The user can now ask Claude for things like:

- *"Evaluate this role against my profile."* (Mode 1)
- *"Search Indeed / Dice for [role] in [location]."* (Mode 2)
- *"Research [company]."* (Mode 4)
- *"Draft LinkedIn outreach to the hiring manager."* (Mode 5)
- *"Draft a cover letter for the [role] eval."* (Mode 6)
- *"Prep me for the [company] interview."* (Mode 3)
- *"Analyze this offer vs. my profile."* (Mode 7)

The full mode list, including search-portal scanning, calendar ops, inbox triage, and batch pipeline review, is in `SKILL.md`.

---

## Getting help

- Threat model and data flow: [PRIVACY.md](PRIVACY.md), [DATA_CONTRACT.md](DATA_CONTRACT.md)
- Bugs and feature requests: [open an issue](https://github.com/markmcgrath/Dossier/issues/new/choose)
- Questions: [GitHub Discussions](https://github.com/markmcgrath/Dossier/discussions)
- Security issues: [SECURITY.md](SECURITY.md)
