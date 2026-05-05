# Weekly Trend Report — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** "Weekly trends", "market trends", "what's the market doing", or automatically when generating the weekly pipeline digest and 4+ weeks of scan data exists in `daily/batch-eval-*.md` files.

**What to do:**

Aggregate daily batch-eval data from the past 4+ weeks to identify market patterns: volume trends, grade distribution shifts, role frequency, company hiring activity, salary ranges, and legitimacy distribution.

**Prerequisites:**

- At least 4 full weeks of `daily/batch-eval-*.md` files must exist in the daily folder.
- Each batch-eval file must have frontmatter with `type: batch-eval` and `date`.
- Each batch-eval file should contain a digest table with Company, Role, Score, Grade, and Legitimacy columns.

**Graceful degradation:** If fewer than 4 weeks of data exist, respond with:

"Trend analysis requires 4+ weeks of batch scan data. Keep using Mode 12 to collect batches, and check back when you reach 4 weeks. Current coverage: [N] weeks of data."

**If 4+ weeks exist:**

1. **Volume trend:** Count `daily/batch-eval-*.md` files grouped by week (ISO week calendar). Show:
   - Total unique JDs scanned per week (sum of all `count:` fields in batch-eval frontmatter)
   - Week-over-week growth or decline (% change)
   - Highest-volume week and lowest-volume week

2. **Grade distribution per week:** Extract all grades from all batch-eval digests, grouped by week:
   - % of A grades per week
   - % of B+ grades per week
   - % of B grades per week
   - % of C grades per week
   - % of D grades per week
   - % of F grades per week
   - Signal: Is quality improving (more A/B+) or declining (more C/D/F)?

3. **Role title frequency:** Extract all role titles from all batch-eval digests across all 4 weeks:
   - Top 5 most common role titles by count
   - Top 3 most common keywords (parsed from role titles, e.g., "Senior", "Engineer", "Manager", "Lead")

4. **Company hiring activity:** Extract all company names from all batch-eval digests:
   - Top 10 companies by frequency (companies appearing in the most batch-eval digests)

5. **Salary range trends:** Extract compensation data (if disclosed) from all batch-eval digests, grouped by week:
   - Average salary range per week (e.g., "$120k–$150k" → parse as midpoint, average midpoints)
   - Salary range distribution: % of roles with disclosed compensation vs. undisclosed

6. **Legitimacy distribution per week:** Extract legitimacy tier (Verified, Plausible, Suspect, Likely Ghost) for each item:
   - % Verified per week
   - % Plausible per week
   - % Suspect per week
   - % Likely Ghost per week
   - Signal: Is the market getting more or less trustworthy?

**Output format:**

Save report to `weekly/trend-report-[YYYY-MM-DD].md` with YAML frontmatter:

```yaml
---
type: trend-report
date: [YYYY-MM-DD]
weeks_analyzed: [n]
jds_analyzed: [total count across all weeks]
---
```

Then include sections:

```markdown
## Market Volume

- Week of [date]: [N] JDs scanned (↑5% vs. previous week)
- Week of [date]: [N] JDs scanned
- [...]

**Trend:** [Quality improving/declining/stable]

## Grade Distribution

[Table with week, % A, % B+, % B, % B-, % C, % D, % F]

**Signal:** [Quality improving or declining?]

## Top Role Titles (4-week aggregate)

1. [Title] – [N] postings
2. [Title] – [N] postings
3. [Title] – [N] postings
4. [Title] – [N] postings
5. [Title] – [N] postings

**Keywords:** [Senior, Manager, Engineer, ...] (sorted by frequency)

## Companies Hiring Most Actively

1. [Company] – [N] postings
2. [Company] – [N] postings
3. [Company] – [N] postings
[...]

## Salary Trends

- Week of [date]: avg. midpoint [salary], [X]% disclosed
- Week of [date]: avg. midpoint [salary], [X]% disclosed
- [...]

## Legitimacy Trends

[Table with week, % Verified, % Plausible, % Suspect, % Likely Ghost]

**Signal:** Market trustworthiness [improving/declining/stable]

---

**Interpretation tips:**

- **Volume spike:** A sudden jump in listings could mean your target companies are actively hiring or the market is getting more competitive.
- **Grade decline:** If B+/B ratios drop and C/D spike, the market is flooded with weaker fits — be more selective.
- **Company concentration:** If a few companies dominate the listings, your search may be too narrow. Consider expanding target companies.
- **Legitimacy decline:** A rising % of Suspect / Likely Ghost listings suggests lower-quality job boards or seasonal hiring spam — adjust your sources.
```
