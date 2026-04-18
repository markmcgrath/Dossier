# START HERE

This file is the onboarding guide for both:
- You (the user)
- Claude (acting as your setup assistant)

---

## If you are a user

After opening this repository in Claude, say:

> Please read START_HERE.md and guide me through setting up Dossier for my job search.

Claude should then walk you through everything step by step.

---

## If you are Claude

When a user asks for help setting up this project, follow this process:

### 1. Understand the project

- Read `README.md`
- Read this file (`START_HERE.md`)
- Summarize the system briefly:
  - what it is
  - how it works
  - what the user will get out of it

Keep it concise.

---

### 2. Check required inputs

Confirm whether the user has:

- `cv.md` (their resume in markdown form)
- `profile.md` (their role targeting and positioning)

If missing:
- Ask for them
- Help generate them from user input

---

### 3. Set up the vault

Explain the vault structure:

- evals/
- outreach/
- cover-letters/
- interview-prep/
- research/
- daily/
- weekly/
- archive/
- dashboard.md

Then:
- Ask the user where they want to store their vault (local folder or Obsidian).
- The repo root already mirrors the vault structure — the eight folders above and `dashboard.md` are present. Tell the user they can either (a) use the cloned repo in place as their vault, or (b) copy those folders and `dashboard.md` to a separate vault location along with `cv.template.md`, `profile.template.md`, `stories.template.md`, and `config.template.md` (renamed to drop `.template`).

---

### 4. Explain workflow modes

Briefly explain the available modes:

- evaluate: assess job fit
- search: find relevant roles
- research: analyze companies and roles
- outreach: generate tailored messages
- prep: create interview materials
- negotiate: analyze offers

Do not over-explain. Keep it practical.

---

### 5. Run first workflow (required)

Ask the user for a job description.

Then:
- Run an evaluation
- Produce a structured artifact
- Show how it would be stored in the vault

This is the first success moment.

---

### 6. Reinforce usage pattern

Explain how the system should be used going forward:

- Each interaction produces artifacts
- Artifacts are saved, not discarded
- Decisions should be based on accumulated outputs
- The system improves over time with better inputs

---

### 7. Boundaries and safety

Make it clear:

- No automated applications
- No scraping or bypassing platform rules
- All outreach and decisions are user-reviewed
- This is an assistive system, not an autonomous one

---

## Design principles

- File-first, not chat-first
- Persistent state via markdown artifacts
- Structured outputs using frontmatter
- Explicit workflows over implicit behavior
- User owns all data and decisions

---

## First success looks like

The user should have:

- A working `cv.md`
- A working `profile.md`
- A vault folder structure
- One completed job evaluation artifact

If those exist, onboarding is complete.

---

## If something fails

- Identify the missing piece (files, structure, or understanding)
- Fix that piece directly
- Do not continue until the system is usable

---

## Going further (after setup)

Once the vault is working and you've completed your first eval, these optional features can level up your workflow:

### Scheduled tasks

Cowork supports scheduled tasks that run automatically on an interval. Useful Dossier schedules include:

- **Daily job scan** — search for new postings matching your profile and surface them as candidates for evaluation.
- **Follow-up reminders** — flag applications where outreach was sent but no response has come in after a set number of days.
- **Weekly pipeline review** — generate a weekly summary of active applications, status changes, and next actions.

To set one up, tell Claude:

> Set up a daily scheduled task that searches for new Senior BI Engineer roles and saves candidates to evals/.

Claude will configure the schedule via Cowork's scheduled-tasks system. You can list, edit, or remove schedules at any time.

### Optional integrations

These are mirrors — the vault remains the source of truth.

- **Notion** — sync your pipeline to a Notion database for visual board views and sharing with an accountability partner.
- **Gmail** — triage recruiter emails directly from your inbox; Claude drafts replies as vault artifacts.
- **Google Calendar** — create prep-block calendar events before interviews with links to your prep artifacts.

Each integration is configured in `config.md`. See the skill's Mode 0 (health check) output for current integration status.

---

## End state

The user should leave setup with:

- A clear understanding of the system
- A working workflow
- Confidence using Dossier for real job search activity
