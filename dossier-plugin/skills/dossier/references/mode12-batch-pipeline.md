# Mode 12: Batch Pipeline — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User provides multiple job descriptions or JD URLs (e.g., "Evaluate these jobs", "batch eval", "rank these listings"), or provides a search result list and asks to filter them.

**What to do:**

Accept a list of job descriptions or URLs, process each through a lightweight Mode 1, and output a ranked digest table for quick decision-making.

**Key constraints:**
- Maximum 10 items per batch (context window limit: the skill is ~1,043 lines; with CV + profile + 10 JDs we approach ~35,000–40,000 tokens, close to practical limits for single turns).
- Lightweight evaluation per item: one-line role summary, score (X.X/5), letter grade, legitimacy tier. Skip CV tailoring, interview probability estimates, and STAR story suggestions.
- Dedup against local `evals/` before evaluating — if a file matching `eval-[company-slug]-*.md` exists for any company in the batch, note it as "Previously evaluated — [grade], [date]" and skip re-evaluation.
- After processing all items, output a ranked digest table with:
  - **Top Picks** section: grades B+ or higher (act on these)
  - **Review** section: grades B or C (maybes)
  - **Skip** section: grades D or below, or Likely Ghost legitimacy (not worth your time)

**Workflow:**

1. **Parse the input.** Determine if the user provided URLs, pasted JDs, or a mixed list. If URLs, fetch each (using web_fetch if needed). If JDs, extract company name and role title from each.

2. **Dedup check.** For each company, search the local `evals/` folder for existing eval files:
   - Run shell command: `find [vault-path]/evals -name "eval-[company-slug]-*.md"`
   - If found, extract grade and date from the file frontmatter (YAML). Record: "Previously evaluated — [grade], [date]. Skipping re-eval."
   - If not found, proceed to step 3.

3. **Lightweight evaluation.** For each item not in dedup:
   - Extract: company name, role title, location (if present), compensation (if disclosed), key responsibilities (bulleted), required skills (bulleted).
   - Read the user's CV and profile once (silently, at the start of the batch).
   - Score the item against Dimensions 1 (Role Match), 2 (Company Quality), 3 (Compensation), and 10 (Strategic Value) only. Skip detailed narrative and dimensional comments — just the final grade.
   - Assess legitimacy tier (Verified, Plausible, Suspect, Likely Ghost) based on red flags: vague JD, generic description, multiple postings for the same role in different variations, weak contact details, etc.
   - Output format per item:
     ```
     [Company] | [Role] | [Location] | [Compensation] | [Score]/5 | [Grade] | [Legitimacy]
     ```

4. **Build the digest table.** Assemble all non-dedup'd items into a single table, sorted by grade (descending), then score (descending). Partition into three sections:
   ```
   ## Batch Digest — [Date] ([N] items evaluated, [M] previously evaluated or skipped)

   ### Top Picks (B+ and above)
   | Company | Role | Location | Comp | Score | Grade | Legitimacy |
   |---------|------|----------|------|-------|-------|------------|
   | [...]   | ...  | ...      | ...  | ...   | ...   | ...        |

   ### Review (B or C)
   | Company | Role | Location | Comp | Score | Grade | Legitimacy |
   |---------|------|----------|------|-------|-------|------------|
   | [...]   | ...  | ...      | ...  | ...   | ...   | ...        |

   ### Skip (D or below, or Likely Ghost)
   | Company | Role | Location | Comp | Score | Grade | Legitimacy |
   |---------|------|----------|------|-------|-------|------------|
   | [...]   | ...  | ...      | ...  | ...   | ...   | ...        |
   ```

5. **Save to vault.** Write the digest to `daily/batch-eval-[YYYY-MM-DD].md` with YAML frontmatter:
   ```yaml
   ---
   type: batch-eval
   date: [YYYY-MM-DD]
   count: [n]
   ---
   ```

6. **Notion sync (optional).** If `notion.enabled: true` in `config.md`, offer to log all evaluated items (non-duped) to Notion:
   - Proposed status: `Batch-Evaluated`
   - Proposed default next step: grade-dependent (Top Picks → "Apply", Review → "Consider", Skip → skip Notion)
   - Show the user a preview of what will be written (count, sample rows). Wait for confirmation before writing.

**Context window note for the user:**

"Batch mode caps at 10 items per session due to context constraints. The skill itself is ~1,043 lines. With your CV, profile, and 10 job descriptions, we're at the practical limit. For larger sets, run multiple batches and the dedup check will prevent re-evaluating items already in your vault."

**Operating principles:**

- **Skim, don't deep-dive.** Lightweight evaluations are fast reads. You can always pull a Top Pick into Mode 1 (full eval) later.
- **Preserve JDs.** If the user wants to keep any JD text, save it as a reference — either in the batch-eval file as a collapsed section, or just tell them where to find it (pasted message, email attachment, etc.).
- **Dedup is a filter, not a block.** If the user explicitly says "re-evaluate this company even though I've seen it before," override dedup and run full Mode 1. Note in the output that a re-eval was requested.
