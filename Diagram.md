# Dossier System Diagram

This diagram shows how Dossier operates as a file-first, Claude-assisted job search system.

---

## High-Level Flow

```mermaid
flowchart LR
    A[User Input\n(cv.md, profile.md, job description)] --> B[Claude + Dossier Skill]

    B --> C[Artifact Generation\n(eval, outreach, prep)]
    C --> D[Markdown Files with Frontmatter]

    D --> E[Vault (Obsidian or Filesystem)]
    E --> F[Dashboard (Dataview Queries)]

    F --> G[User Decisions\n(apply, outreach, prep, archive)]
```
