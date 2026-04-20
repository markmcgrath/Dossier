# Features — Planning & Research Archive

This folder is the working record behind Dossier: research notes, architecture specs, staged implementation plans, risk registers, and release-hardening execution. It exists on purpose — the finished artifacts in `skill/`, `tests/`, and the root docs are the *output*, and everything here is the *reasoning that produced them*.

If you're just trying to *use* Dossier, skip this folder and start at [`README.md`](../README.md) and [`START_HERE.md`](../START_HERE.md).

If you're evaluating how this project was built, pick a starting point:

- **`plan/README.md`** — stream-by-stream implementation plan. Numbered `00-` through `09-` map to actual shipped work.
- **`research/deep-research-report.md`** — external audit against NIST AI RMF, OWASP LLM Top 10, and relevant prompt-injection literature.
- **`research/dossier-gap-analysis.md`** and **`dossier-consolidated-assessment.md`** — self-critique and reconciliation against the external audit.
- **`vault-first-architecture-spec.md`** — the architectural pivot from Notion-centric to vault-first.
- **`plan/07-risks.md`** — the risk register tracked through implementation.

Documents may supersede each other as the project evolved; the `Supersedes:` lines at the top of each doc point at predecessors. The `git log` is authoritative for chronology.
