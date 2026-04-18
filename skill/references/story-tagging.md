# Interview Story Tagging — Reference

*This file is loaded by the dossier skill on demand. Do not edit without also updating the pointer in SKILL.md.*

Mode 3 (Interview Prep) surfaces the right STAR stories from `stories.md` for a given role by matching the JD's competency signals against each story's `**Tags:**` line. Matches are linked bidirectionally: a `related_stories:` list in the prep artifact's frontmatter, and a `**Used in:**` back-reference added under each matched story in `stories.md`.

## Inputs

- The JD / role description already loaded in Mode 3 context.
- `stories.md` (or `stories.template.md` in the public repo). Each story is an H2 heading (`## Story Title`) with a body containing `**Tags:**` followed by a flat comma-separated tag list.

`stories.md` is **user-layer**. Never reformat stories, never rewrite their bodies, never change tag lists. The only sanctioned write is appending or extending a `**Used in:**` line per the "Back-references" section below.

## Matching procedure

1. From the JD and the target role, extract 3–4 competency signals (e.g. *cross-functional leadership*, *platform migration*, *governance*, *mentoring*). Prefer concrete phrases from the JD's responsibilities and "must-haves"; avoid generic labels.
2. Read `stories.md` and enumerate every `## ` heading as a story. For each, parse the `**Tags:**` line into a lowercased set of trimmed tag strings.
3. Score each story by the number of extracted signals that overlap with its tag set. Overlap matching is substring-friendly and case-insensitive (`leadership` matches `cross-functional-leadership`).
4. Rank by score descending, breaking ties by story order in the file. Take the **top 3–4** stories regardless of minimum overlap count — the ranked list surfaces the best available matches even when the bank is thin.
5. If `stories.md` has fewer than 3 stories, or no story has any overlapping tag, **warn the user once**: "No strongly matching stories in the bank. Consider adding a story covering [signals]." Proceed with whatever matches you have — zero is an acceptable outcome.

## Forward link (prep → stories)

Add `related_stories:` to the prep artifact's frontmatter. It is a YAML list of Obsidian heading wikilinks pointing at the matched stories:

```yaml
related_stories:
  - "[[stories#Multi-Tenant Governance at Scale]]"
  - "[[stories#Cross-Team Data Migration]]"
```

- Heading wikilinks (`[[stories#Heading]]`) resolve inside Obsidian to the specific story, not the whole file.
- Use the story's exact H2 heading text, trimmed, case-preserved. No trailing punctuation.
- If the story has no heading (free-form bullet), fall back to a body-text quote in the prep artifact — do not invent a wikilink.

Echo the list in the prep artifact's `Your Key Talking Points` section with the same wikilinks inline, so the story is one click away during prep.

## Back-references (stories → prep)

For every matched story, propose a `**Used in:**` line addition in `stories.md`. This runs as a single **approval batch** at the end of the Mode 3 flow, not per-story.

Rules:

1. The line goes immediately after the existing `**Tags:**` line of that story. If another line is present (body text), insert a blank line before `**Used in:**`.
2. Format: `**Used in:** [[prep-[slug]-[date]]], [[prep-[other-slug]-[date]]]`.
3. If a `**Used in:**` line already exists for that story, **append** the new wikilink to it (sorted, deduped). Never duplicate, never remove existing entries.
4. Present the full diff to the user before writing — show each story heading, the current `**Used in:**` line (if any), and the proposed line.
5. Get one approval for the whole batch. Either write all or write none.
6. Do not touch any other line in `stories.md`. Do not reformat, re-wrap, or renormalize.
7. Never run back-reference writes outside Mode 3 — other modes that mention `stories.md` (Mode 6, Mode 11) may read but must not mutate.

## Zero-match behavior

If no stories match (bank is empty, tags don't overlap, or stories have no tags):

1. Still write the prep artifact — the prep is useful without stories.
2. Emit the single-line warning named above.
3. Offer to add one or more new story stubs to `stories.md` that cover the missing competencies — but propose them as an explicit batch for user approval, same as back-reference writes. Never silently append to `stories.md`.

## What not to do

- Don't treat story tags as authoritative — they are user-authored, potentially inconsistent, and may use different conventions across stories. Substring + case-insensitive matching is intentional.
- Don't rank stories by recency, length, or any signal other than tag overlap.
- Don't surface more than 4 stories per prep — the goal is the strongest matches, not exhaustive coverage.
- Don't rewrite `stories.md` tag lists, headings, or body text. `**Used in:**` is the only sanctioned mutation.
- Don't write back-references for stories the user rejected during the Mode 3 forward-link approval (if the user declined a specific match, no back-reference for that story).
