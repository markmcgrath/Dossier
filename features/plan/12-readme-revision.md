# README Revision Plan

Scope: open-source `README.md` (the public-facing file). The main-vault README mirrors the open-source version per CLAUDE.md propagation rules, so changes flow outward.

---

## 1. Rewrite the opening hook

**Current problem.** The first paragraph buries the value proposition behind mechanics ("Paste a job description…"). A new reader should immediately understand what Dossier does and why it's worth trying.

**Proposed revision.**

- Lead with the outcome: *"Dossier turns your job search into a structured, repeatable system — grounded in your actual work history, not generic AI output."*
- Follow with the three headline features: profile-grounded evaluation, outreach drafting in the user's voice, and persistent markdown artifacts the user owns.
- Remove "Paste a job description" from the hook. Pasting a JD is one way to trigger an eval, but Dossier also accepts URLs, email forwards, and search-mode scans. The hook shouldn't imply a single input method.
- Replace "Built for people running 10–30 active applications" with language like "Built for people juggling multiple active applications" — avoids an arbitrary range that might exclude lighter or heavier searchers.

---

## 2. Update the "How it works" Mermaid diagram

**Current diagram.**

```
User Input (cv.md, profile.md, job description) → Claude + Skill → Artifact Generation → Markdown Files → Vault → Dashboard → User Decisions
```

**Issues.**

- "User Input" box lists "job description" as if it's always required up front. In search mode the user provides targeting criteria, not a JD.
- The flow is strictly linear; it doesn't show the feedback loop (user decisions feed back into the vault, which informs future evals).
- Missing: optional integrations (Notion mirror, Gmail triage, Calendar prep blocks) that are now part of the system.

**Proposed revision.**

- Rename the first node to something like "User + Profile (cv.md, profile.md)" to emphasize the profile grounding.
- Add a second entry point: "Job Input (JD, URL, search criteria)" feeding into the skill.
- Add a feedback arrow from "User Decisions" back to the vault to show the iterative nature.
- Optionally add a dashed branch for "Optional Integrations (Notion, Gmail, Calendar)" off the vault node — keeps it visible but clearly secondary.

---

## 3. Fix "Who is this for?" section

**Current text:** "Are working on 10+ applications a week and can't keep track of them."

**Issues.**

- "10+ applications a week" is a specific volume that may not match all users. Some people are running 5 carefully targeted applications; they still benefit.
- "Have access to Claude Projects" — the system now runs on Cowork, not Claude Projects.

**Proposed revision.**

- Replace the volume qualifier: "Are managing multiple active applications and want to stay organized."
- Update the platform reference to Cowork (already partially done in Quick Start but inconsistent here).

---

## 4. Resolve Claude Projects → Cowork inconsistency

**Current state.** The file mentions "Claude Projects" in the opening description (line 2 of main vault README) and in the "Who is this for" section. The Quick Start section correctly says "Claude Cowork." This creates confusion about which runtime is actually needed.

**Proposed revision.**

- Global find-and-replace: "Claude Projects" → "Claude Cowork" (or just "Cowork") everywhere in both READMEs.
- In the main vault README line 2, change "built on top of Claude Projects" → "built on top of Claude Cowork."
- Keep the Support Matrix section as-is (it already says Cowork).

---

## 5. Decide on scheduling coverage

**Question:** Should the README cover Cowork scheduled tasks (daily scans, follow-up reminders, etc.)?

**Recommendation: No — keep it out of README; confirm START_HERE covers it.**

- README is a project overview and quick-start guide. Scheduling is a power-user feature that adds cognitive load for new readers.
- START_HERE currently does NOT mention scheduling either. A short section should be added to START_HERE (or a linked "Advanced Features" doc) covering: what can be scheduled, how to set it up, and what the user should expect.
- README can include a one-line mention under "Core concepts" or a "What's possible" list: "Optional: schedule recurring scans and follow-up reminders via Cowork scheduled tasks." Link to START_HERE or a dedicated doc for details.

**Action items:**

1. Add a "Going further" or "Advanced features" section to START_HERE.md that covers scheduling, Notion sync, Gmail triage, and Calendar integration.
2. Add a single bullet to README under Core Concepts or a new "Optional integrations" line.

---

## 6. Tighten "What this is / What this is NOT"

These sections exist in both READMEs. The open-source version integrates them well. The main-vault README has them as flat bullet lists that could be folded into the rewritten opening or removed as redundant with the open-source copy.

**Proposed revision.**

- Main vault: remove the standalone "What this is" / "What this is NOT" sections. They duplicate the open-source README and the CLAUDE.md integrity rules.
- Open-source: keep as-is (they serve a discoverability purpose for GitHub visitors).

---

## 7. Remove "Paste a job description" implication throughout

Anywhere the README implies the only input is a pasted JD, soften to reflect the actual input methods:

- Pasted JD text
- URL to a job posting
- Search criteria (title, location, etc.) for scan mode
- Forwarded recruiter email

This mainly affects the opening hook (item 1) and the Mermaid diagram (item 2).

---

## Execution order

1. Items 1 + 3 + 4 (opening, who-is-this-for, Projects→Cowork) — can be done in one pass.
2. Item 2 (Mermaid diagram) — requires testing the rendering.
3. Item 7 (JD-paste language) — sweep after the above are done.
4. Item 5 (scheduling in START_HERE) — separate file edit.
5. Item 6 (main vault cleanup) — after open-source is finalized.
6. Propagate open-source README → main vault README per CLAUDE.md sync rules.

---

## Files affected

- `open-source/README.md` (primary edit target)
- `README.md` (main vault — sync from open-source)
- `START_HERE.md` (add scheduling / advanced features section)
- `open-source/START_HERE.md` (propagate)
