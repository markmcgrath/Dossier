# Mode 13: Calibration Report — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User asks "How accurate are my evaluations?", "calibration report", "check my scoring", or proactively when the vault has 50+ evaluations or 3+ months of evaluation activity.

**What to do:**

Analyze the correlation between evaluation grades and actual outcomes to detect scoring drift and identify which dimensions best predict advancement.

1. **Data collection:** Scan `evals/` for all files with a non-Pending `outcome` field (check frontmatter). Collect: `grade`, `score`, `outcome`, and all 10 dimension scores.

2. **Minimum threshold:** If fewer than 15 outcomes exist, respond: "Not enough outcomes yet — update outcomes via Mode 9 and check back when you have at least 15." Stop here.

3. **Grade-to-outcome correlation:** For each grade band (A, B+, B, B-, C, D, F), compute:
   - Total evals in that band
   - % reaching Interview+ outcomes (Phone Screen, Interview, Offer, Accepted)
   - % reaching Offer+ outcomes (Offer, Accepted)
   - % No Response
   - % Rejected

4. **Predictive check:** A well-calibrated system shows monotonically decreasing interview rate from A→F. Flag any breaks in this pattern (e.g., B-grade evals advancing more often than A-grade). This suggests scoring drift or miscalibration.

5. **Dimension analysis:** For each of the 10 dimensions, compare average score in Interview+ outcomes vs. No Response/Rejected outcomes. Identify which dimensions most strongly predict advancement (highest deltas). List the top 3.

6. **Scoring drift:** Compute mean composite score per calendar month (from eval `date:` field). Flag if the rolling mean has shifted 0.5+ points over time, suggesting grade inflation or deflation.

**Output format — use this structure:**

```
# Calibration Report — [date]

## Summary

[1–2 sentences: overall calibration health]

## Grade-to-Outcome Correlation

| Grade | N | Interview+ % | Offer+ % | No Response % | Rejected % |
|-------|---|--------------|----------|---------------|------------|
| A     | 5 | 80% | 40% | 0% | 20% |
| B+    | 8 | 62% | 25% | 25% | 13% |
| B     | 12 | 50% | 17% | 25% | 33% |
| B-    | 9 | 40% | 13% | 30% | 38% |
| C     | 10 | 30% | 10% | 40% | 50% |
| D     | 6 | 17% | 0% | 50% | 83% |
| F     | 4 | 0% | 0% | 75% | 25% |

## Predictive Dimensions

Top 3 dimensions by predictive power (highest delta between Interview+ and No Response/Rejected):

1. [Dimension name] — [avg score Interview+] vs. [avg score No Response] (+[delta] point advantage for advances)
2. ...
3. ...

## Scoring Drift

Mean composite score per month:

- [Month 1]: 3.2
- [Month 2]: 3.4
- ...

[Assessment: "Stable" or "Drifting [direction] by [amount] points over [timeframe]"]

## Calibration Assessment

[2–3 sentences: is the monotonic drop intact? Which dimensions are carrying weight? Any concerning drift?]
```

**Output:** Save report to `weekly/calibration-report-[date].md` with YAML frontmatter:
```yaml
type: calibration
date: [date]
evals_analyzed: [n]
```

**Edge case:** If `weekly/` directory doesn't exist, note the intended path and let the user create it or ask whether to place it in the Dossier root instead.
