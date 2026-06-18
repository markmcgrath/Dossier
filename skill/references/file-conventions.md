# File Layout & Conventions

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

The Dossier folder is organized so artifacts are queryable locally (via Obsidian + Dataview) and do not accumulate in one flat directory. **Always write artifacts to the correct subfolder** and **always include YAML frontmatter** so Dataview queries work.

### Folder structure

```
Dossier/
├── cv.md                   ← canonical, root
├── profile.md              ← canonical, root
├── README.md               ← conventions reference
├── dashboard.md            ← Dataview pipeline queries
│
├── evals/                  ← eval-[slug]-[date].md       (Mode 1 output)
├── outreach/               ← outreach-[slug]-[date].md   (Mode 5 output)
├── cover-letters/          ← cover-[slug]-[date].md      (Mode 6 output)
├── interview-prep/         ← prep-[slug]-[date].md       (Mode 3 output)
├── research/               ← target-brief-*.md, company research (Mode 4)
├── negotiation/            ← negotiation-[slug]-[date].md (Mode 7 output)
├── daily/                  ← daily-scan-*, leads-*-am/pm, recruiter-triage-*
├── weekly/                 ← pipeline-digest-*, week-ahead-*
├── archive/                ← archived per-company bundles once terminal
│
└── packets/                ← per-application send-ready bundles (Mode 14)
    └── [company-slug]/
        └── [role-slug]/    ← README.md, cv.md/.docx, cover-letter.md/.docx, jd.md
```

### Frontmatter requirements

Every artifact file **must** start with YAML frontmatter. The `type` field is how Dataview distinguishes artifacts.

**Eval files** (`type: eval`):
```yaml
---
type: eval
company: "Company Name"
role: "Role Title"
grade: A            # A | B+ | B | C | D | F
score: 4.5
status: Evaluating  # Evaluating | Applied | Interviewing | Offer | Rejected | Passed | Offer-Declined | Superseded
date: YYYY-MM-DD
location: "Remote"
compensation: "$X–$Y"     # or "Not disclosed"
outcome: Pending          # Pending | No Response | Rejected | Phone Screen | Interview | Offer | Accepted | Withdrawn
legitimacy: Verified      # Verified | Plausible | Suspect | Likely Ghost
notes: "One-sentence recommendation."
# Optional metadata fields — set when the information is available:
source: "Indeed"                     # Indeed | Dice | LinkedIn | Company Careers | Referral | Recruiter Inbound | Other
referral_contact: ""                 # Name of the referrer when source=Referral
application_method: ""               # "Easy Apply" | "Direct" | "Recruiter" | etc.
model: claude-sonnet-4-6             # Which model produced this evaluation
sources: []                          # Data sources consulted: jd_url, apollo, web_search, etc.
---
```

**Outreach files** (`type: outreach`):
```yaml
---
type: outreach
company: "Company Name"
role: "Role Title"
channel: LinkedIn | Email | LinkedIn + Email
date: YYYY-MM-DD
status: drafted        # drafted | sent | replied | no-response
related_eval: "[[eval-[slug]-[date]]]"   # wikilink syntax, not a path
---
```

**Cover letter files** (`type: cover`): same shape as outreach.
**Prep files** (`type: prep`): add `interview_date:`, `interviewers:` (list of names), and `related_stories:` (list of Obsidian heading wikilinks into `stories.md`, e.g. `"[[stories#Story Title]]"`). Story matching and back-reference discipline live in `references/story-tagging.md`.

**Negotiation files** (`type: negotiation`): same base shape as outreach, plus `offer_components:` (free-form summary of base/bonus/equity/etc.) and `walk_away:` (the floor below which the user will decline). Save to `negotiation/negotiation-[slug]-[date].md`.

### Cross-linking rule (for Obsidian graph view)

Obsidian's graph view only follows `[[wikilink]]` syntax — plain file paths in frontmatter are not treated as links. Two rules keep the graph populated:

1. **All `related_*` frontmatter fields use wikilink syntax, in quotes.** Example: `related_eval: "[[eval-acme-corp-2026-04-14]]"`. Not `related_eval: evals/eval-acme-corp-2026-04-14.md`.
2. **Every eval file that has a related outreach, cover letter, or prep doc gets a `## Related` section appended at the bottom**, containing wikilinks to those docs. This creates the return edge so the graph is bidirectional. Example:
   ```
   ---

   ## Related

   - Outreach: [[outreach-acme-corp-2026-04-14]]
   - Cover letter: [[cover-acme-corp-2026-04-14]]
   - Prep: [[prep-acme-corp-2026-04-14]]
   ```
   Update this section whenever a new related artifact is produced. Use file basenames only (no `.md` extension, no folder path) — Obsidian resolves them vault-wide.

### File-first discipline for outreach and cover letters

Outreach messages and cover letters have historically lived only as Gmail drafts, which are volatile — drafts can be sent, edited, or deleted with no permanent record. **Always save the markdown file before creating the Gmail draft**, not after. Flow:

1. Write the outreach / cover letter to the correct subfolder with frontmatter.
2. Then create the Gmail draft using `gmail_create_draft`, copying the message body from the saved file.
3. If the user later tells you they sent it, flip `status: sent` in the frontmatter of the saved file.

The Gmail draft is the delivery mechanism. The markdown file is the record.

### Archive discipline

When a pipeline row reaches a terminal state (Rejected, Passed, Offer-Declined, or >90 days cold), move that company's entire bundle — eval, outreach, cover, prep — into `archive/[company-slug]/`. Update the eval's `status:` frontmatter first. Nothing is deleted; everything stays searchable but out of the active pipeline.

Mode 9 auto-proposes this move in its Application Status Sync batch when it detects a terminal-status transition on an `Applied` or `Interviewing` eval. Repeat archivals of the same company are versioned (`archive/[slug]-v2/`, `-v3/`, …) rather than merged. The `>90 days cold` case is currently manual — it needs date arithmetic not yet implemented. Full procedure, including slug extraction and cross-reference rewriting, lives in `references/terminal-archival.md`.

### Packets

A packet (`packets/[company-slug]/[role-slug]/`) is the send-ready bundle for one application. It is created by Mode 14 (Packet Assembly) and contains tuned submission artifacts derived from the master CV and the role's eval, research, and stories.

**Packet README frontmatter** (`type: packet`):
```yaml
---
type: packet
company: "Company Name"
role: "Role Title"
company_slug: company-slug
role_slug: role-slug
status: Assembling | Ready | Submitted | Archived
send_ready: false
related_eval: "[[eval-company-slug-YYYY-MM-DD]]"
created: YYYY-MM-DD
updated: YYYY-MM-DD
contents:
  cv_md: false
  cv_docx: false
  cover_letter_md: false
  cover_letter_docx: false
  jd_md: false
  prep_md: false
  outreach_md: false
---
```

**Required files in every packet:** `README.md`, `cv.md`, `cv.docx`, `cover-letter.md`, `cover-letter.docx`. A packet is not `send_ready: true` until all five are present, confirmed, and pass the send-ready scan (see `SEND_READY_CONTRACT.md`).

**Cross-linking:** the packet README's `## Related` section links back to the eval, research brief, and outreach draft using Obsidian wikilink syntax. The eval's own `## Related` section gets a `- Packet: [[packets/company-slug/role-slug/README]]` entry added by Mode 14.

**Naming:** company and role slugs follow the same lowercase-hyphen convention as eval slugs. Two roles at the same company each get their own `[role-slug]/` subfolder under the shared `[company-slug]/` directory.

**Legacy artifacts:** `cv-[slug]-[date].md` files at the vault root and `cover-letters/cover-[slug]-[date].md` files predate the packet convention. Their migration target is `packets/[company-slug]/[role-slug]/cv.md` and `cover-letter.md` respectively; migration is a separate manual cleanup, not performed by Mode 14.

**Archive behavior:** when a company reaches a terminal pipeline state, the entire `packets/[company-slug]/` directory is moved to `archive/[company-slug]/packets/` alongside the other company artifacts. Packet `status` is set to `Archived` before the move.

### Time-decay archival for `daily/` and `weekly/`

Daily scans, lead pulses, recruiter triage, pipeline digests, and week-aheads are date-bound artifacts. Apply this trigger to keep those folders scannable:

- When `daily/` exceeds ~60 files, move older-than-current-month into `daily/YYYY-MM/`.
- When `weekly/` exceeds ~26 files, move older files into `weekly/YYYY-Q#/`.
- Dataview queries in `dashboard.md` descend into subfolders automatically, so "recent activity" views keep working.

### Naming

- Company slug: lowercase, hyphen-separated, no punctuation. `acme-corp`, `wayne-enterprises`, `globex-industries`.
- Dates: ISO-8601 (`YYYY-MM-DD`).
- One file per artifact per company per day. If you re-evaluate the same company and role on the same day, version the files using a `-v#` suffix rather than overwriting — see Dedup Check section for details. Cross-day re-evaluations get different date stamps naturally.

## Optional Config Keys

**Additional config keys (optional, all have sensible defaults):**
```yaml
# Email Filtering
# (Use to prevent personal email noise during job search — not a privacy control)
redact_comp: false             # Suppress comp data in Notion rows
gmail_allow_domains: []        # Only process emails from these domains (whitelist)
gmail_deny_domains: []         # Never process from these domains (takes precedence over allow)

# Scoring
scoring_weights: {}            # Override dimension weights. Must sum to 100.

# Portal Scanning (Mode 2 sub-mode)
target_companies: []           # List of companies to scan for new job postings
# Example:
# target_companies:
#   - name: "Anthropic"
#     ats: greenhouse
#     board_token: "anthropic"
#   - name: "Stripe"
#     ats: lever
#     board_token: "stripe"
#   - name: "Startup Co"
#     ats: manual
#     url: "https://startup.co/careers"
# ATS types: greenhouse (API via Greenhouse), lever (browser fallback),
# ashby (browser fallback), manual (user-provided URL).
```
