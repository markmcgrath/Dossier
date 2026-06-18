# Send-Ready Document Contract

*This file is loaded by the dossier skill on demand. Do not edit without also
updating the pointer in SKILL.md and the machine-readable config at
skill/references/send_ready_config.json.*

A send-ready document is one that can be forwarded to a hiring manager,
recruiter, or other external party without further editing. It contains no
scaffolding, no internal notes, no reviewer commentary, no placeholders, and
no draft markers of any kind. The validator at `.github/scripts/sendready_scan.py`
enforces this contract on every PR.

## Document classes in scope

### 1. Tuned CV (`document_class: tuned_cv`)

Files matching: `packets/**/cv.md`, `cv-*.md`

A tuned CV is a role-specific export derived from the master `cv.md`. It
contains only the sections below (in any order). Every other heading is a
hard failure.

**Allowed headings (case-insensitive, `#` or `##` prefix):**

- Name (the H1 at the top — no `##` required; a bare `# Full Name` line counts)
- Professional Summary
- Summary
- Skills
- Experience
- Professional Experience
- Work Experience
- Employment History
- Education
- Selected Projects
- Selected Architecture Projects
- Architecture Projects
- Projects
- Certifications
- Selected Projects / Certifications
- Earlier Career

No other `##`-level headings are permitted. In particular, the following heading
is a hard failure and must be stripped before the document is sent:

- `What Changed` (or `What Changed (vs. master cv.md)` or any variant)

The `What Changed` section is internal scaffolding produced by Mode 11. Mode 11
instructs the user to remove it before submitting; the validator enforces that
instruction mechanically.

### 2. Cover Letter (`document_class: cover_letter`)

Files matching: `packets/**/cover-letter.md`, `cover-letters/*.md`

A cover letter has no required heading structure — it is prose. The validator
does not check section headings for cover letters. It applies only the global
banned-content ruleset below.

### 3. General Outbound (`document_class: outbound`)

Any other `.md` file explicitly passed to the validator on the command line.
Applies only the global banned-content ruleset; no section-allowlist check.

---

## Global Banned-Content Ruleset

The following patterns are **hard failures** in the body of any send-ready
document (frontmatter is exempt). A file containing any of these may not be
marked `send_ready: true` and must not be sent.

### Category A: Internal scaffolding markers

| Pattern | Description |
| --- | --- |
| `<!-- ... -->` | HTML comment of any kind |
| Lines starting with `NOTE:` or `Note:` or `NOTE ` | Inline note prefix |
| Lines starting with `Q:` or `Q.` | Inline question prefix |
| Lines starting with `TODO` or `FIXME` or `XXX` | Developer task markers |
| The word `DRAFT` as a standalone token on a line | Draft stamp |
| Lines starting with `>` (blockquote) | Blockquotes used as reviewer asides |
| `## What Changed` (or `## What Changed (`) | Trailing change-summary section |

### Category B: Placeholder brackets

| Pattern | Description |
| --- | --- |
| `[COMPANY]`, `[ROLE]`, `[DATE]`, or any `[ALL CAPS]` token | Unfilled template slots |
| `[add ...]` or `[insert ...]` or `[your ...]` | Instruction placeholders |
| `[TBD]` or `[TK]` or `[placeholder]` | Explicit placeholder words |
| Any `[` ... `]` pair where the interior is 3+ uppercase letters | Generic unfilled slot |

### Category C: Reviewer commentary words

The following words trigger a warning (not a hard failure) when they appear
as a standalone sentence or at the start of a line. They are common in
review-cycle drafts but can appear legitimately in body text (e.g., a cover
letter that describes a `memo` the candidate authored).

| Word | Trigger condition |
| --- | --- |
| `memo` | Line starts with `Memo:` or `MEMO:` |
| `placeholder` | Appears anywhere in body |
| `reviewer` | Line starts with `Reviewer:` |
| `see note` | Phrase appears anywhere in line |
| `per your comment` | Phrase appears in line |
| `action item` | Line starts with `Action item:` or `Action Item:` |

### Category D: Trailing question lines

A line that ends with `?` AND is not inside a quoted passage (i.e., not inside
`>` blockquote) AND is not a rhetorical question in a known sentence pattern is
a warning. Exact detection: the validator flags lines where the stripped line
ends with `?` and the line is fewer than 120 characters (long rhetorical
questions in cover-letter prose are unlikely to be internal questions; short
question lines almost always are).

---

## Hard failures vs. warnings

**Hard failure (exit 1):** Categories A and B. The document must not be sent.

**Warning (exit 0 by default, exit 1 with `--strict`):** Categories C and D.

---

## Frontmatter exemption

YAML frontmatter (the block between the opening `---` and the closing `---`) is
not checked for banned content. Frontmatter fields like `notes:` in an eval file
are valid vault metadata, not document body content. The validator strips
frontmatter before scanning.

---

## What Changed exemption for the master cv.md

The master `cv.md` is not a send-ready document and is never validated as one.
Only files matching the send-ready glob patterns are checked. The master is
explicitly excluded.
