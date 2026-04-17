# Dossier

[![CI](https://github.com/markmcgrath/Dossier/actions/workflows/ci.yml/badge.svg)](https://github.com/markmcgrath/Dossier/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Dossier is a Claude-powered job-search operations system. Paste a job description; it grades the role against **your** profile, drafts outreach in **your** voice, and stores everything as markdown in a local vault you own — not a SaaS dashboard.

Built for people running 10–30 active applications at a time who want to apply strategically rather than mass-blast resumes. Generic ATS scoring and one-size-fits-all tracker apps don't know your career; Dossier does, because it reads `cv.md` and `profile.md` as the source of truth for fit. Evals, outreach drafts, interview prep, and company research all land in versionable markdown with YAML frontmatter, queryable by Obsidian Dataview or any text tool. Nothing is sent automatically — every outreach message is a draft you decide to send.

## How it works

```mermaid
flowchart LR
    A[User Input<br/>cv.md, profile.md,<br/>job description] --> B[Claude + Dossier Skill]
    B --> C[Artifact Generation<br/>eval, outreach, prep]
    C --> D[Markdown Files<br/>with Frontmatter]
    D --> E[Vault<br/>Obsidian or Filesystem]
    E --> F[Dashboard<br/>Dataview Queries]
    F --> G[User Decisions<br/>apply, outreach, prep, archive]
```

## Who is this for?

**Use Dossier if you…**

- Are working on 10+ applications a week and can't keep track of them
- Want grading tied to your actual work history, not generic ATS keywords
- Own your outreach and don't want an agent emailing on your behalf
- Already keep notes in markdown (bonus if you use Obsidian + Dataview)
- Have access to Claude Projects and are comfortable installing a skill

**Dossier isn't for you if you…**

- Want fully automated applications or mass-blast tooling
- Prefer a polished cloud SaaS over a local file-based workflow
- Don't have access to Claude

## How Dossier differs

| Tool | Your data lives | Grades against your profile | Auto-apply | Cost |
|---|---|---|---|---|
| Spreadsheet | Local | ❌ | ❌ | Free |
| Notion tracker | Notion cloud | ❌ | ❌ | Free–$10/mo |
| Teal / Huntr | Vendor cloud | Generic rubric | ❌ | $0–$30/mo |
| LinkedIn Jobs | LinkedIn | ❌ | Easy Apply | Free |
| **Dossier** | **Your local vault** | **Yes — against cv.md + profile.md** | **No (by design)** | **Free + Claude subscription** |

## Quick start

Three actions. Everything else — parsing your resume into `cv.md`, building `profile.md` from a short Q&A, running the first eval — is handled by Claude.

1. **Get the files.** Clone the repo, or download the ZIP from GitHub and extract it.

   ```bash
   git clone https://github.com/markmcgrath/Dossier.git
   ```

2. **Create a Claude Project.**
   - Add the Dossier folder as **Project knowledge**
   - Upload `dossier.skill` as the project's skill

3. **Tell Claude to walk you through setup.**

   > Read START_HERE.md and walk me through setup.

   Claude will ask for your resume (paste it, link a Google Doc, or attach a PDF), then a handful of targeting questions. About 5–10 minutes. At the end you'll have a populated vault and a first evaluation saved to `evals/`.

For what happens during that walkthrough and how to recover if it gets stuck, see [START_HERE.md](START_HERE.md).

## What this is NOT

- Not an autonomous application bot
- Not a LinkedIn automation tool
- Not a scraping or bypass system
- Not a generic AI agent framework

All external actions remain user-controlled.

## Core concepts

- **File-first, not chat-first.** Every interaction produces a persistent markdown artifact, not a throwaway chat.
- **Structured outputs.** YAML frontmatter lets Dataview (and any other tool) query the vault like a database.
- **Explicit workflow modes.** 14 named modes (Evaluate, Search, Outreach, Prep, …) instead of implicit chat behavior.
- **Human-in-the-loop.** The skill drafts; you decide to send.
- **Your data, your vault.** No cloud sync required. Notion, Gmail, and Calendar integrations are optional mirrors.

## Project structure

```
Dossier/
├── cv.md                   # Your work history. Source of truth for capability fit.
├── profile.md              # Target archetype, roles to avoid, match signals.
├── stories.md              # STAR+R story bank for behavioral interviews.
├── dashboard.md            # Dataview queries (live pipeline, unsent outreach, due follow-ups).
├── dossier.skill           # The skill ZIP. Edit via skill/ and repack.
│
├── evals/                  # Per-role evaluations
├── outreach/               # Recruiter / hiring-manager messages (drafts)
├── cover-letters/          # Cover letter drafts
├── interview-prep/         # Role-specific prep artifacts
├── research/               # Company / person research notes
├── daily/                  # Daily journals
├── weekly/                 # Weekly pipeline reviews
├── examples/               # Reference artifacts (fictional companies)
└── archive/                # Terminal (rejected, declined, 90+ days cold) applications
```

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

Outreach, cover, and prep files follow the same structured pattern. See [examples/](examples/) for complete reference artifacts.

## Vault discipline

**Time-decay archival.** `daily/` and `weekly/` are rolling logs:

- `daily/` → archive after ~60 files
- `weekly/` → archive after ~26 files

When Claude detects these thresholds, it moves older files into dated subfolders.

**Terminal archival.** When a company reaches a terminal state (Rejected, Passed, Offer-Declined, or 90+ days cold), create `archive/[company-slug]/` and move all related artifacts into it. Update `status` before moving. Nothing is deleted; everything remains searchable.

**Naming.** Company slug is `lowercase-hyphen`; dates are `YYYY-MM-DD`; use `-v1`, `-v2` suffixes when re-evaluating the same role on the same day.

**Dataview completeness.** Dashboard queries filter on `status`, `grade`, `legitimacy`, and `outcome`. If a file is missing one of these fields, it silently drops out of filtered views. Mode 0 (health check) surfaces missing fields. Files created by Mode 1 onward include the full field set automatically.

## Obsidian setup (optional)

1. Open the folder as an Obsidian vault (v1.11.7+)
2. Enable the Dataview plugin
3. Open `dashboard.md`

Obsidian isn't required — the vault works fine as plain markdown in any editor — but Dataview gives you live pipeline views for free.

## Security & privacy

Dossier is an assistive system, not an autonomous one. Key principles:

1. **Human-in-the-loop.** All external actions (sending emails, submitting applications, posting messages) require explicit user approval. The skill drafts; the user sends.
2. **External content is untrusted.** Job descriptions, recruiter emails, and pasted text may contain prompt-injection attempts or misleading claims. The skill's Content Trust Boundary (see `SKILL.md`) prevents external content from overriding grading criteria or user preferences.
3. **No automatic execution.** The skill never executes instructions found in job postings, emails, or other external content.
4. **No credential storage.** API keys, tokens, and passwords must never be stored in vault files. `.gitignore` excludes `config.md` (which may hold Notion IDs) from version control.
5. **User responsibility.** Model output is advisory, not authoritative. Always review generated artifacts before acting on them.

For the full threat model, data-flow diagram, and per-service risk analysis, see [PRIVACY.md](PRIVACY.md) and [DATA_CONTRACT.md](DATA_CONTRACT.md). To report a security issue, see [SECURITY.md](SECURITY.md).

## Support matrix

**Supported**

- Vault-first workflow with local markdown files
- Claude-assisted artifact generation via the Dossier skill
- Obsidian v1.11.7+ with Dataview plugin for dashboard queries
- Python 3.11 and 3.12 for running the test suite

**Optional**

- Notion tracker mirroring (vault remains source of truth)
- Gmail, Google Calendar, and Apollo integrations (require MCP connectors)
- LinkedIn browser automation via Claude in Chrome

**Not supported**

- Autonomous job applications or unsupervised outbound messaging
- Scraping or automation against platform TOS
- Use without human review of generated artifacts

## Documentation

- [START_HERE.md](START_HERE.md) — extended setup walkthrough
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute, maintainer hook setup
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — contributor conduct
- [PRIVACY.md](PRIVACY.md) — threat model and data-flow analysis
- [DATA_CONTRACT.md](DATA_CONTRACT.md) — what's yours, what's generated, what updates
- [SECURITY.md](SECURITY.md) — vulnerability disclosure policy
- [CHANGELOG.md](CHANGELOG.md) — release history and known limitations
- [Diagram.md](Diagram.md) — standalone architecture diagram
- [tests/README.md](tests/README.md) — how the test suite works

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Open an issue before investing time in anything non-trivial so we can discuss the approach. All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Support

- **Bugs / feature requests:** [open an issue](https://github.com/markmcgrath/Dossier/issues/new/choose)
- **Questions / discussion:** [GitHub Discussions](https://github.com/markmcgrath/Dossier/discussions)
- **Security issues:** see [SECURITY.md](SECURITY.md) — please do not file public issues for vulnerabilities

## Acknowledgments

Dossier is built on top of work that made it possible:

- [Claude](https://claude.com/) — the underlying LLM and skill runtime
- [Obsidian](https://obsidian.md/) — the optional markdown editor the vault is optimized for
- [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) — the Obsidian plugin powering the dashboard queries
- The [Keep a Changelog](https://keepachangelog.com/) and [Contributor Covenant](https://www.contributor-covenant.org/) projects for the governance formats

## License

MIT — see [LICENSE](LICENSE).
