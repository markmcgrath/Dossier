# Stream B — Governance Documents

**Estimated effort:** 2–3 hours
**Depends on:** Nothing — can run in parallel with [[01-architecture|Stream A]]
**Blocks:** Nothing directly, but Stream C references these docs
**Reference:** [[../dossier-consolidated-assessment|Consolidated Assessment]] §2.1, §2.5; [[../research/dossier-implementation-plan|Implementation Plan]] §1.1, §1.2

---

## Why This Exists

The skill processes sensitive PII through seven external services and has zero security documentation. Both the deep research report and the gap analysis flagged this as the most critical deficiency. These documents don't change skill behavior — they inform the user and establish contracts for future development.

---

## B.1 — PRIVACY.md

**What:** A governance document mapping every PII data flow, naming external services, and stating user responsibilities.

**Where:** `Dossier/PRIVACY.md` (new file, vault root)

**Sections to include:**

### Data Inventory
Table mapping data types (CV, contact info, salary data, recruiter emails, calendar events, contact lookups, LinkedIn activity, job search queries) to where each flows.

### Per-Service Risk Notes
One subsection per service: Anthropic, Notion (now optional), Gmail, Google Calendar, Apollo, LinkedIn, Indeed/Dice. Each includes what data it receives, retention implications, and mitigations.

**Revision from original plan:** Notion moves from "high risk, always active" to "optional, user-controlled." The risk note should state: "If you never configure Notion, no data ever reaches Notion's servers."

### Threat Model Summary
This was missing from the original implementation plan and added from the consolidated assessment. Four sections:

1. **Assets at risk** — PII, strategy data, OAuth tokens, vault contents
2. **Adversary scenarios** — malware/exfiltration, prompt injection, platform enforcement, supply-chain compromise
3. **Mitigations** — full-disk encryption, content trust boundary, HITL design, token storage in env vars
4. **What Dossier does NOT protect against** — be honest about limits

### Regulatory Notes
Candidate-side tool framing. GDPR, CCPA/CPRA, LinkedIn ToS. Accurate but not alarmist.

### Encryption at Rest
Recommendation for full-disk encryption. Link to OS-specific instructions.

### Data Retention
Forward reference to the retention policy in README.md (added in [[05-advanced#E.4 — Retention Policy]]).

**Acceptance:**
- File exists at vault root
- Covers all 7 external services (with Notion marked as optional)
- Includes threat model section
- Referenced from README.md

---

## B.2 — DATA_CONTRACT.md

**What:** Formal separation of user-owned files from system files, protecting personal data during skill updates.

**Where:** `Dossier/DATA_CONTRACT.md` (new file, vault root)

**Three categories:**

### User Layer — Never Overwritten
`cv.md`, `profile.md`, `config.md`, `stories.md`, `dashboard.md`, and all working folders (`evals/`, `outreach/`, `cover-letters/`, `interview-prep/`, `research/`, `daily/`, `weekly/`, `archive/`).

### System Layer — Updatable
`dossier.skill` (contains SKILL.md + scoring-guide.md), `PRIVACY.md`, `DATA_CONTRACT.md`, `README.md`.

**Revision from original:** The original listed `SKILL.md` and `scoring-guide.md` separately. Since these live inside the `dossier.skill` ZIP package, the contract should reference the package, with a note that extracting and inspecting is possible.

### Derived Files — Created by Skill, Owned by User
Tailored CVs (`cv-[slug]-[date].md`), ATS exports (`cv-[slug]-[date].docx`), negotiation briefs. Once created, the skill only modifies on explicit request.

**Acceptance:**
- File exists at vault root
- Every file and folder in the vault is categorized
- README.md references this document

---

## B.3 — LICENSE

**What:** Add an open-source license so the project is safely reusable.

**Where:** `Dossier/LICENSE` (new file, vault root)

**Recommendation:** MIT. It's the simplest, most permissive, and appropriate for a prompt-based skill that isn't a library or framework. Apache-2.0 is the alternative if patent protection matters, but for a markdown skill file, MIT is sufficient.

**Acceptance:** LICENSE file exists at vault root.

---

## B.4 — Update README.md References

**What:** Add references to PRIVACY.md and DATA_CONTRACT.md from README.md.

**Where:** `README.md` — add a "Governance" section after the existing layout section.

**Content:**
```markdown
## Governance

- [[PRIVACY|PRIVACY.md]] — data flows, per-service risks, threat model, regulatory notes.
- [[DATA_CONTRACT|DATA_CONTRACT.md]] — which files are yours vs. system files.
- `LICENSE` — project license.
```

**Acceptance:** README.md links to both governance docs.

---

## Estimated Breakdown

| Task | Hours |
|------|-------|
| B.1 PRIVACY.md (with threat model) | 1.5 |
| B.2 DATA_CONTRACT.md | 0.5 |
| B.3 LICENSE | 0.1 |
| B.4 README.md references | 0.2 |
| **Total** | **~2.3** |
