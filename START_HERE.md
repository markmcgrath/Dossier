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

Explain the vault structure (see `README.md` for full layout).

The repository IS the vault — there is no separate template to copy. The user should:

1. Clone this repository
2. Rename `cv.template.md` → `cv.md` and fill in their work history
3. Rename `profile.template.md` → `profile.md` and fill in their targeting preferences
4. Rename `stories.template.md` → `stories.md` (optional, for behavioral interview prep)
5. Rename `config.template.md` → `config.md` and add their Notion tracker IDs (optional)
6. Open the folder in Obsidian as a vault, or work with it via Claude directly

The subfolder structure (`evals/`, `outreach/`, `cover-letters/`, etc.) is already in place.

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

## End state

The user should leave setup with:

- A clear understanding of the system
- A working workflow
- Confidence using Dossier for real job search activity