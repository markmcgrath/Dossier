# Dossier

[![CI](https://github.com/markmcgrath/Dossier/actions/workflows/ci.yml/badge.svg)](https://github.com/markmcgrath/Dossier/actions/workflows/ci.yml)

Dossier is a structured job search system built on top of Claude Projects.

It combines:

- A reusable Claude skill with defined workflow modes (evaluate, search, research, outreach, prep, negotiate)
    
- A vault-based persistence layer (Obsidian-compatible markdown with frontmatter schemas)
    
- A set of conventions for turning job search into a durable, trackable process instead of ad hoc chats
    

The goal is simple: reduce friction, increase consistency, and make decisions based on your actual profile, not generic AI output.

---

## Recommended setup (Claude-assisted)

This project is designed to be onboarded with Claude.

1. Clone this repository locally
    
2. Open the folder in Claude
    
3. Say:
    

Please read START_HERE.md and guide me through setting up Dossier for my job search.

Claude should then:

- Explain the project structure
    
- Help you create or refine `cv.md` and `profile.md`
    
- Set up your vault
    
- Walk you through workflow modes
    
- Run your first job evaluation
    

---

## What this is

- A structured workflow system for job search
    
- A way to persist AI outputs as reusable artifacts
    
- A method for grounding decisions in your actual profile
    

---

## What this is NOT

- Not an autonomous job application bot
    
- Not a LinkedIn automation tool
    
- Not a scraping or bypass system
    
- Not a generic AI agent framework
    

All external actions remain user-controlled.

---

## Core concepts

- File-first, not chat-first
    
- Persistent artifacts over ephemeral responses
    
- Structured outputs using frontmatter
    
- Explicit workflow modes instead of implicit behavior
    
- Human-in-the-loop for all external actions
    

---

## Project structure

```id="bnsnss"
Dossier/
├── cv.md
├── profile.md
├── stories.md
├── dashboard.md
├── dossier.skill
├── evals/
├── outreach/
├── cover-letters/
├── interview-prep/
├── research/
├── daily/
├── weekly/
├── examples/
└── archive/
```

---

# Dossier Folder Conventions

This folder is the working vault for the Dossier skill. Open it directly in Obsidian (`v1.11.7+`) as a vault — no migration needed, all files are markdown.

## Layout

```
Dossier/
├── cv.md                   # Canonical work history. Source of truth for capability fit.
├── profile.md              # Target archetype, roles to avoid, match signals. Source of truth for desirability fit.
├── stories.md              # STAR+R story bank for behavioral interview prep.
├── dashboard.md            # Dataview queries (live pipeline, unsent outreach, follow-ups due).
├── dossier.skill           # The skill definition. Edit carefully; back up first.
│
├── evals/                  
├── outreach/               
├── cover-letters/          
├── interview-prep/         
├── research/               
├── daily/                  
├── weekly/                 
├── examples/               
└── archive/                
```

---

## Frontmatter conventions

Every artifact file starts with YAML frontmatter so Dataview can query it.

**Eval files:**

```yaml
---
type: eval
company: "Company Name"
role: "Role Title"
grade: A | B+ | B | C | D | F
score: 4.5
status: Evaluating | Applied | Interviewing | Offer | Rejected | Passed
date: YYYY-MM-DD
location: "Remote" | "City, ST" | "Hybrid – City"
compensation: "$X–$Y" | "Not disclosed"
outcome: Pending | No Response | Rejected | Phone Screen | Interview | Offer | Accepted | Withdrawn
legitimacy: Verified | Plausible | Suspect | Likely Ghost
notes: "One-sentence recommendation."
---
```

(Outreach, cover, prep follow same structured pattern)

---

## Time-decay archival

Daily and weekly artifacts are time-bound:

- `daily/` → archive after ~60 files
    
- `weekly/` → archive after ~26 files
    

When Claude detects these thresholds, it moves older files into dated subfolders.

---

## Archive discipline

When a company reaches a terminal state:

1. Create `archive/[company-slug]/`
    
2. Move all related artifacts into it
    
3. Update status before moving
    

Nothing is deleted. Everything remains searchable.

---

## Dataview and frontmatter completeness

Dashboard queries filter on frontmatter fields like `status`, `grade`, `legitimacy`, and `outcome`. If an eval file is missing one of these fields, it will silently drop out of filtered views (e.g., `WHERE legitimacy = "Verified"` excludes files without a `legitimacy` field). Run Mode 0 periodically to catch missing fields. All new evals created via Mode 1 include the full field set automatically.

---

## Data retention

- Active search → keep everything
    
- Archive → permanent storage
    
- Optional cleanup after 12 months (redact compensation)
    
- Stories.md is your most durable asset
    

---

## Naming conventions

- Company slug: lowercase-hyphen format
    
- Dates: YYYY-MM-DD
    
- Versioning: use `-v1`, `-v2` if re-evaluating same day
    

---

## Obsidian setup

1. Open vault
    
2. Enable Dataview plugin
    
3. Open `dashboard.md`
    

---

## Governance

- PRIVACY.md → data flow and risk
    
- DATA_CONTRACT.md → ownership model
    
- LICENSE → MIT
    

---

## Support Matrix

**Supported:**

- Vault-first workflow with local markdown files and Obsidian
- Claude-assisted artifact generation via the Dossier skill
- Obsidian v1.11.7+ with Dataview plugin for dashboard queries
- Python 3.11+ for running the test suite

**Optional:**

- Notion tracker mirroring (vault remains source of truth)
- Gmail, Google Calendar, and Apollo integrations (require MCP connectors)
- LinkedIn browser automation via Claude in Chrome

**Not supported:**

- Autonomous job applications or unsupervised outbound messaging
- Scraping, automation against platform TOS, or CAPTCHA bypassing
- Use without human review of all generated artifacts

---

## Security Model

Dossier is an assistive system, not an autonomous one. These principles are enforced throughout the skill:

1. **Human-in-the-loop.** All external actions (sending emails, submitting applications, posting messages) require explicit user approval. The skill drafts; the user sends.
2. **External content is untrusted.** Job descriptions, recruiter emails, and pasted text may contain prompt injection attempts or misleading claims. The skill's Content Trust Boundary (see SKILL.md) prevents external content from overriding grading criteria or user preferences.
3. **No automatic execution.** The skill never executes instructions found in job postings, emails, or other external content, regardless of how they are phrased.
4. **No credential storage.** API keys, tokens, and passwords must never be stored in vault markdown files. Use environment variables or platform secret stores. The `.gitignore` excludes `config.md` (which may contain Notion IDs) from version control.
5. **User responsibility.** The user owns all data in the vault and all decisions made based on skill output. Model output is advisory, not authoritative.

For the full threat model and data flow documentation, see [PRIVACY.md](PRIVACY.md) and [DATA_CONTRACT.md](DATA_CONTRACT.md).

---

## LLM Safety

Dossier generates evaluations, outreach drafts, and interview prep using Claude. Keep in mind:

- Model output is advisory. Grades, scores, and recommendations reflect pattern-matching against the JD and your CV — they are not authoritative assessments.
- External content (job postings, emails, company descriptions) may contain manipulative or inaccurate claims. The skill flags suspicious signals (see ghost job detection) but cannot guarantee accuracy.
- Always review generated artifacts before acting on them. This applies especially to outreach messages, cover letters, and salary negotiation scripts.
- The skill includes a bias caveat on every evaluation for this reason.

---

## Secrets Handling

Never store API keys, tokens, passwords, or credentials in vault markdown files. This includes `config.md`, eval files, and outreach drafts.

If you need to configure integrations (Notion, Gmail, Calendar), use environment variables or your platform's secret management. The `.gitignore` excludes `config.md` from version control to prevent accidental commits, but the file itself should not contain raw secrets — only identifiers like Notion page IDs.

See [PRIVACY.md](PRIVACY.md) for the full data handling policy.

---

## Source-of-truth model

- Vault = primary source of truth
    
- Notion = optional mirror
    
- If conflict: vault wins
    

---

## Why this exists

Most AI-assisted job searches are stateless and generic.

Dossier is different:

- persistent artifacts instead of disposable chats
    
- schema-driven outputs instead of freeform text
    
- grounding in your actual profile
    

This makes the process:

- repeatable
    
- auditable
    
- improvable over time
    

---

## Status

Early-stage, actively evolving.

Expect iteration and refinement.