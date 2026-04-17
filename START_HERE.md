# Start Here

Extended setup walkthrough for Dossier. For the 4-step version, see the [Quick start in README.md](README.md#quick-start). This doc goes deeper with troubleshooting.

---

## Before you begin

You'll need:

- A **Claude** account with access to **Claude Projects** (the skill runs inside a Claude Project)
- **Git** to clone the repository
- A text editor — any will do; [Obsidian](https://obsidian.md) is optimized for this vault but optional
- (Optional) **Python 3.11+** if you want to run the test suite locally

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/markmcgrath/Dossier.git
cd Dossier
```

---

## Step 2 — Create your personal files from the templates

The repo ships with `.template.md` versions of every file that contains personal data. Your real versions are gitignored — they never leave your machine unless you explicitly copy them somewhere.

```bash
cp cv.template.md cv.md           # your work history
cp profile.template.md profile.md # your targeting preferences
cp stories.template.md stories.md # (optional) STAR+R behavioral stories
cp config.template.md config.md   # (optional) Notion / MCP integration IDs
```

Then open each file in your editor and fill it in.

**Minimum viable setup:** you need `cv.md` and `profile.md` to get useful output. Everything else is optional.

**If you don't have a resume in markdown yet:** paste your existing resume (PDF, LinkedIn export, Google Doc) into Claude and say *"Convert this to the format in cv.template.md."* You'll get a clean `cv.md` draft.

---

## Step 3 — Load Dossier into Claude Projects

1. Create a new Claude Project (or pick an existing one).
2. Add this folder as **Project knowledge**. Claude will index the markdown files so it can reference `cv.md`, `profile.md`, your existing evals, etc.
3. Upload `dossier.skill` as a **skill** in the same Project.

The skill is a ZIP bundle containing `SKILL.md` + `references/*.md`. Claude loads these automatically once the skill is attached.

---

## Step 4 — Run your first evaluation

Paste any job description into Claude and ask for an evaluation. Example prompt:

> Please evaluate this role against my profile.
>
> [paste JD here]

What Claude will do:

1. Run Mode 0 (health check) to confirm your `cv.md` and `profile.md` are loaded.
2. Run Mode 1 (evaluation) — reads the JD, scores it against your profile across 10 dimensions, assigns a letter grade (A / B+ / B / C / D / F), flags legitimacy risk (Verified / Plausible / Suspect / Likely Ghost), and writes a structured artifact to `evals/eval-<company>-<date>.md`.
3. Show you the grade, the key strengths/concerns, and a one-sentence recommendation.

**What "first success" looks like:**

- `cv.md` and `profile.md` exist and are populated
- `evals/eval-<your-first-company>-<today>.md` exists with a grade and frontmatter
- You can open the eval file in any text editor and read the structured report

If all three are true, onboarding is complete.

---

## Available workflow modes

Once setup is done, these are the main things to ask Claude for:

| Mode | What to ask for |
|---|---|
| **Evaluate** | *"Evaluate this role."* — grades fit against your profile |
| **Search** | *"Search Indeed / Dice for [role]."* — finds roles, evaluates them in bulk |
| **Research** | *"Research [company]."* — company background, interviewers, competitors |
| **Outreach** | *"Draft LinkedIn outreach to [recruiter / hiring manager]."* — personalized messages |
| **Cover letter** | *"Draft a cover letter for the [role] eval."* — reuses the eval as context |
| **Prep** | *"Prep me for the [company] interview."* — role-specific prep doc with likely questions |
| **Negotiate** | *"Analyze this offer vs. my profile."* — salary / equity / leverage analysis |

All modes write artifacts to the corresponding folder (`outreach/`, `cover-letters/`, `interview-prep/`, etc.) with consistent frontmatter so Dataview can query them.

---

## (Optional) Verify the skill is installed correctly

Run the test suite to confirm everything is wired up:

```bash
DOSSIER_VAULT="$(pwd)" python -m pytest tests/ -v
```

You should see 43 passed, 4 skipped. If anything fails, the error message will name the file and line that's wrong — see [tests/README.md](tests/README.md) for how to interpret common failures.

---

## Troubleshooting

**Claude doesn't seem to know about `cv.md` or `profile.md`.**
Check that the folder is added as Project knowledge (Step 3). Upload-as-attachment doesn't give the skill access; the folder must be Project-level knowledge.

**Mode 1 produces the wrong grade.**
The grade is advisory, not authoritative — see the bias caveat in every eval. If it's systematically off, your `profile.md` may be vague. Try running *"Review my profile.md and suggest improvements based on the last 5 evals."*

**Claude asks to edit a file but doesn't have permission.**
Claude Projects controls file write access. You may need to grant permission per-session, or accept the proposed change and paste it into the file yourself.

**Nothing writes to `evals/` / `outreach/` / etc.**
Check that the folder exists (it should, with a `.gitkeep` in it). Claude may be giving you the draft in chat instead of creating a file; ask explicitly *"write this to evals/ as a proper artifact."*

**Test suite fails with `SKILL.md not found in ZIP`.**
The skill ZIP is out of sync with `skill/`. Re-download the repo or repack `dossier.skill` from the `skill/` folder.

---

## Design principles

- **File-first, not chat-first** — every interaction produces a persistent artifact
- **Structured outputs** — YAML frontmatter makes everything queryable
- **Explicit workflows over implicit behavior** — named modes instead of guessed intent
- **Human-in-the-loop** — the skill never sends or applies for you
- **Your data, your vault** — no cloud sync required

---

## Getting help

- Detailed docs and the threat model: [PRIVACY.md](PRIVACY.md), [DATA_CONTRACT.md](DATA_CONTRACT.md)
- Bugs or feature requests: [open an issue](https://github.com/markmcgrath/Dossier/issues/new/choose)
- Questions or discussion: [GitHub Discussions](https://github.com/markmcgrath/Dossier/discussions)
- Security issues: [SECURITY.md](SECURITY.md)
