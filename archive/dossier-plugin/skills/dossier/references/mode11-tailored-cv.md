# Mode 11: Tailored CV — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

**Trigger:** User asks to tailor their CV for a specific role, or follows up after a Mode 1 evaluation with "tailor my CV" or "generate a CV version for this." Also triggered as an optional step at the end of Mode 1 when the evaluation grades B or higher.

**The core principle:** The master `cv.md` is never touched. This mode produces a *disposable export* — a role-specific version that emphasizes different proof points, reorders experience, and mirrors JD language where it's genuinely accurate. The goal is not to fabricate — it's to choose the most relevant true things and surface them prominently.

**Inputs required:**
1. The job description (from a recent Mode 1 evaluation or pasted directly)
2. `Dossier/cv.md` — the master CV
3. `Dossier/profile.md` — for positioning and keyword guidance

**Step 1: Extract what the JD cares most about.**
From the JD, identify the top 5–7 requirements in priority order — not just the listed skills, but what the role clearly *depends on*. For a data modeling role this might be: dimensional modeling methodology → semantic layer ownership → multi-source reconciliation → Power BI expertise → SQL depth → stakeholder communication. Weight them by how prominently they appear in the JD.

**Step 2: Map requirements to CV evidence.**
For each JD requirement, find the strongest matching evidence in `cv.md`. Be specific: not "has SQL experience" but a concrete, named project that demonstrates the skill at the right scope and scale. Flag which requirements have strong evidence (2+ specific examples), adequate evidence (1 example), and thin/missing evidence (acknowledge the gap rather than hide it).

**Step 3: Build the tailored version.**

Apply these changes to produce the tailored CV:

- **Reorder experience bullets within each role** — the bullet that best matches the JD's top requirement moves to position 1. De-prioritize bullets that are irrelevant to this role (move to bottom or trim if space is tight).
- **Reorder the Skills section** — group skills so the ones most prominent in the JD appear first within their category. Don't add skills that aren't in the master CV.
- **Swap in JD-specific terminology where it's accurate.** If the JD uses a specific term for something the CV describes differently — and the two terms genuinely mean the same thing in context — use the JD's term. If the JD names a methodology or framework the candidate has actually used, surface that term explicitly even if the master CV phrases it more generically. Never swap in terminology the CV cannot support.
- **Surface the Short Summary** (from `profile.md`) as a 2-sentence professional summary at the top of the CV, tuned to this specific role. Lead with the dimension the JD cares most about.
- **Do not invent, inflate, or fabricate. This is the hardest rule and the most commonly broken one.**
  - Never create sections that don't exist in `cv.md`. If `cv.md` has no "Key Accomplishments" section, the tailored CV has no "Key Accomplishments" section. If `cv.md` has no "Highlights" or "Summary of Qualifications," neither does the tailored version.
  - Never write a new accomplishment bullet with specific metrics. Every bullet in the tailored CV must exist verbatim or as a direct reframe of a bullet in `cv.md`. If you want to write "Reduced report delivery time by 40%," that exact figure must be traceable to a line in `cv.md`. If it's not there, the bullet doesn't go in.
  - Before writing any bullet you're not sure about, ask: "Can I point to the line in cv.md this came from?" If the answer is no, cut it.
  - The cover letter (Mode 6) is the right place to address gaps in narrative. The CV should only make accurate, traceable claims.
- **Keep the same visual structure** as `cv.md` — same sections, same formatting conventions. The tailored version should look like a well-maintained CV, not a remix. Do not add new sections.

**Step 4: Write the Change Summary (mandatory — do not skip).**
After the CV content, append the following section to the same file. This section is always included — it helps the user understand what changed and informs any cover letter drafted afterward. Do not put it in a separate file.

```
---

## What Changed (vs. master cv.md)
*This section is for reference only — remove before submitting the CV.*

- **Professional summary:** [added for this role / not present in master]
- **Reordered bullets in:** [list each role where bullets were reordered, and what moved to position 1]
- **Terminology swaps:** [e.g. "data model" → "semantic layer" in 3 places — only list genuine swaps]
- **Skills section reordered:** [yes/no — which skill groups moved up and why]
- **Bullets trimmed or de-prioritized:** [list bullets removed or moved down, with reason]
- **Gaps not covered:** [JD requirements with thin or no CV evidence — these should inform the cover letter's narrative]
```

**Step 5: Save the file.**
Write to `Dossier/cv-[company-slug]-[YYYY-MM-DD].md` with the `## What Changed` section already appended. Tell the user the filename, remind them the master `cv.md` is unchanged, and note that the What Changed section should be removed before submitting.

Offer: "Want me to draft a cover letter for this role too? Mode 6 can use this tailored version as its base."

**Step 6: Offer ATS-safe docx export (optional).**

After saving the markdown CV, offer to generate an ATS-safe `.docx` file:

"Want me to generate an ATS-friendly Word version of this CV? I can produce a single-column, plain-text layout that parses cleanly through most applicant tracking systems."

**If the user accepts:**

1. Use the docx skill to generate the `.docx` file: invoke it with the formatted markdown CV content (ATS-safe version), specifying single-column layout, standard fonts, and `.docx` output format.
2. Generate a `.docx` file with these ATS compatibility rules applied:
   - Single-column layout — no tables, text boxes, graphics, or columns
   - Standard fonts only: Arial, Calibri, or Times New Roman (11–12pt body, 14pt headers)
   - Standard section headers: "Professional Summary", "Experience", "Education", "Skills", "Certifications"
   - Name and contact info in document body, not header/footer
   - Plain dashes or dots for bullets (• or -)
   - Standard date format: "Jan 2022 – Present" or "2022–2024"
   - Strip the "What Changed" section (that's user-facing only, not for ATS submission)
3. Save as `Dossier/cv-[company-slug]-[YYYY-MM-DD].docx` — parallel to the markdown file.
4. Append a keyword match score (user-facing, not in the docx):
   ```
   ATS Keyword Match: X/10 requirements explicitly present
   Missing: [requirements not found in document text]
   ```
5. Note: "Ready to submit. Remember to remove the master cv.md 'What Changed' section from any submitted copy if you copy-paste from markdown."
