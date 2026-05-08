#!/usr/bin/env python3
"""
run_routing_evals.py — Routing eval harness for the Dossier skill.

Loads 45 prompts from a golden test-set markdown file, issues one Anthropic
API call per prompt with the bundled SKILL.md as prompt-cached system context,
scores routing decisions against expected outcomes, and writes a markdown
report.  Exits 0 on pass, 1 on below-threshold accuracy, 2 on environment /
input error, 3 on API error after retries.

Usage:
    python run_routing_evals.py <skill_md> <test_set>
        [--model <id>] [--threshold <float>] [--report <md>]
        [--max-prompts <N>]

Arguments:
    skill_md     Path to SKILL.md to evaluate against.  CI passes the
                 extracted-from-ZIP path (e.g. /tmp/built-SKILL.md).
    test_set     Path to routing_test_set.md (golden prompts).

Options:
    --model      Model ID to use.  Default: claude-sonnet-4-7-20260101
    --threshold  Float pass threshold (0–1).  Default: 0.95
    --report     Output path for the markdown report.
                 Default: routing-evals-report.md
    --max-prompts N  Evaluate only the first N prompts (0 = all 45).
                 Useful for local dry-runs.

Exit codes:
    0  — accuracy >= threshold (PASS)
    1  — accuracy < threshold (FAIL; report still written)
    2  — environment error (missing API key, missing input files,
          malformed test set)
    3  — API error after 3 retries with exponential backoff

Authority: ~/.claude/plans/lucky-pondering-dragon.md (Plan 19 Stream B)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import anthropic

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-7-20260101"
DEFAULT_THRESHOLD = 0.95
DEFAULT_REPORT = "routing-evals-report.md"
EXPECTED_PROMPT_COUNT = 45
MAX_RETRIES = 3

EVAL_INSTRUCTION_PREFIX = (
    "You are an expert evaluator for the Dossier job-search skill. "
    "Given the skill manifest above and the user prompt below, determine "
    "whether the Dossier skill would trigger and, if so, which mode it "
    "would use.\n\n"
    "Respond ONLY with a valid JSON object of this exact shape:\n"
    '{"would_trigger_dossier": true | false, "mode": "Mode N" | null, '
    '"rationale": "<one sentence>"}\n\n'
    "Rules:\n"
    "- would_trigger_dossier: true if the prompt should activate the "
    "Dossier skill; false otherwise.\n"
    "- mode: the primary mode (e.g. \"Mode 1\", \"Mode 5\") if "
    "would_trigger_dossier is true; null if false.\n"
    "- rationale: one sentence explaining the routing decision.\n"
    "Do not include code fences, markdown, or any text outside the "
    "JSON object."
)


# ---------------------------------------------------------------------------
# Test-set parser
# ---------------------------------------------------------------------------

def parse_test_set(path):
    """
    Parse the routing_test_set.md file into a list of
    (test_id, prompt_text, expected_text) tuples.

    State machine over markdown lines:
    - Track current T-NNN ID via regex ^### T-(\\d{3}).
    - Within each block, capture blockquoted lines (> ...) after a
      **Prompt:** line.
    - Capture text after **Expected (monolithic):** up to the next bold
      field or --- separator.
    - Skip **Expected (split):** and **Rationale:**.

    Returns a list of tuples; exits 2 if not exactly EXPECTED_PROMPT_COUNT.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        print(f"ERROR: test set not found: {path}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"ERROR: cannot read test set {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    results = []
    current_id = None
    current_prompt_lines = []
    current_expected = None

    # Parser state flags
    in_prompt = False       # currently collecting blockquote lines for prompt
    in_expected = False     # currently collecting expected (monolithic) text

    heading_re = re.compile(r"^###\s+T-(\d{3})")
    bold_field_re = re.compile(r"^\*\*\w")
    blockquote_re = re.compile(r"^>\s?(.*)")

    def flush_entry():
        """Commit the current entry to results if complete."""
        if current_id is not None and current_prompt_lines and current_expected is not None:
            prompt_text = " ".join(current_prompt_lines).strip()
            results.append((current_id, prompt_text, current_expected.strip()))

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        # New T-NNN heading — flush previous entry, reset state
        m = heading_re.match(line)
        if m:
            flush_entry()
            current_id = f"T-{m.group(1)}"
            current_prompt_lines = []
            current_expected = None
            in_prompt = False
            in_expected = False
            continue

        # Section separator --- resets collection flags
        if line.strip() == "---":
            in_prompt = False
            in_expected = False
            continue

        # **Prompt:** marker — start collecting blockquotes
        if line.strip() == "**Prompt:**":
            in_prompt = True
            in_expected = False
            continue

        # **Expected (monolithic):** marker — start collecting expected
        if line.strip().startswith("**Expected (monolithic):**"):
            in_prompt = False
            in_expected = True
            # Inline value on the same line
            after = line.strip()[len("**Expected (monolithic):**"):].strip()
            current_expected = after if after else ""
            continue

        # **Expected (split):** or **Rationale:** — stop collecting expected
        if line.strip().startswith("**Expected (split):**") or \
                line.strip().startswith("**Rationale:**") or \
                line.strip().startswith("**Category:**"):
            in_prompt = False
            in_expected = False
            continue

        # Any other bold field stops collection
        if bold_field_re.match(line.strip()):
            in_prompt = False
            in_expected = False
            continue

        # Collect blockquoted prompt lines
        if in_prompt:
            bm = blockquote_re.match(line)
            if bm:
                current_prompt_lines.append(bm.group(1).strip())
            # Non-blockquote line inside prompt block: stop collecting
            elif line.strip() and not line.strip().startswith(">"):
                in_prompt = False
            continue

        # Collect expected (monolithic) text
        if in_expected and line.strip():
            if current_expected:
                current_expected = current_expected + " " + line.strip()
            else:
                current_expected = line.strip()

    # Flush final entry
    flush_entry()

    # Validate count
    if len(results) != EXPECTED_PROMPT_COUNT:
        found_ids = [r[0] for r in results]
        expected_ids = [f"T-{i:03d}" for i in range(1, EXPECTED_PROMPT_COUNT + 1)]
        missing = [t for t in expected_ids if t not in found_ids]
        extra = [t for t in found_ids if t not in expected_ids]
        msg_parts = [
            f"ERROR: test set parser produced {len(results)} tuples, "
            f"expected {EXPECTED_PROMPT_COUNT}."
        ]
        if missing:
            msg_parts.append(f"  Missing: {missing}")
        if extra:
            msg_parts.append(f"  Extra: {extra}")
        print("\n".join(msg_parts), file=sys.stderr)
        sys.exit(2)

    return results


# ---------------------------------------------------------------------------
# Expected outcome parser
# ---------------------------------------------------------------------------

def parse_expected(test_id, expected_text):
    """
    Parse the expected-outcome string for a single prompt.

    Returns a dict:
        {"would_trigger": bool, "mode": str | None}

    Rules:
    - If expected_text contains "NONE", would_trigger=False, mode=None.
    - T-038 (prompt injection) always expects would_trigger=True (routing
      occurs; the trust boundary is separately documented).
    - If expected_text contains "dossier → Mode N", would_trigger=True,
      primary mode = first "Mode N" found.
    - Compound "Mode N then Mode M" → primary is N.
    """
    if test_id == "T-038":
        # Prompt injection: dossier DOES trigger (JD eval path)
        return {"would_trigger": True, "mode": None}

    upper = expected_text.upper()
    # "NONE" as the primary outcome — check it first.
    # Handles "NONE — dossier should not trigger" (where "dossier" appears
    # as an explanatory noun, not as a trigger indicator).
    if "NONE" in upper:
        # Make sure "NONE" is not used in a negated sense like "NOT NONE".
        # Simple heuristic: if "NONE" appears before any "DOSSIER →" pattern.
        none_pos = upper.find("NONE")
        arrow_pos = upper.find("DOSSIER →")
        if arrow_pos == -1 or none_pos < arrow_pos:
            return {"would_trigger": False, "mode": None}

    # Extract first "Mode N[.M]" occurrence
    mode_match = re.search(r"Mode\s+(\d+(?:\.\d+)?)", expected_text, re.IGNORECASE)
    if mode_match:
        mode_str = f"Mode {mode_match.group(1)}"
        return {"would_trigger": True, "mode": mode_str}

    # "dossier → ..." without a mode number (shouldn't happen, but be safe)
    if "DOSSIER" in upper:
        return {"would_trigger": True, "mode": None}

    return {"would_trigger": False, "mode": None}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score(expected, got):
    """
    Compute credit for a single prompt.

    Args:
        expected: dict with keys 'would_trigger' (bool) and 'mode' (str|None)
        got:      dict with keys 'would_trigger_dossier' (bool) and
                  'mode' (str|None) — parsed from model JSON response

    Returns:
        float: 0.0, 0.5, or 1.0

    Rules:
    - If would_trigger disagrees → 0.0 credit.
    - If would_trigger agrees:
        - If expected mode is None (trigger-only required, e.g. T-038) → 1.0
        - If expected mode agrees with got mode → 1.0
        - If expected mode disagrees → 0.5
    """
    trigger_match = (expected["would_trigger"] == got.get("would_trigger_dossier"))
    if not trigger_match:
        return 0.0

    # Trigger agrees
    if expected["mode"] is None:
        # Only trigger agreement needed (negative cases or T-038)
        return 1.0

    got_mode = got.get("mode")
    if got_mode and _normalize_mode(got_mode) == _normalize_mode(expected["mode"]):
        return 1.0

    return 0.5


def _normalize_mode(mode_str):
    """Normalize mode strings for comparison (e.g. 'Mode 1' == 'Mode 1')."""
    if mode_str is None:
        return None
    return re.sub(r"\s+", " ", mode_str.strip().title())


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------

def call_api_with_retry(client, model, rendered_skill, prompt_text):
    """
    Issue one Anthropic API call for a single prompt, with up to 3 retries.

    Uses prompt caching on rendered_skill_manifest so that the SKILL.md
    content is cached across all 45 calls, reducing cost significantly.

    Returns the model's response text, or exits 3 on repeated failure.
    """
    backoff = [1, 2, 4]
    last_exc = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=400,
                temperature=0,
                system=[
                    {
                        "type": "text",
                        "text": EVAL_INSTRUCTION_PREFIX,
                    },
                    {
                        "type": "text",
                        "text": rendered_skill,
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
                messages=[{"role": "user", "content": prompt_text}],
            )
            # Extract text from the first text block
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""
        except (anthropic.APIError, anthropic.RateLimitError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                wait = backoff[attempt]
                print(
                    f"  [retry {attempt + 1}/{MAX_RETRIES}] API error: {exc}. "
                    f"Waiting {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
        except anthropic.APIConnectionError as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                wait = backoff[attempt]
                print(
                    f"  [retry {attempt + 1}/{MAX_RETRIES}] Connection error: {exc}. "
                    f"Waiting {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)

    print(
        f"ERROR: API call failed after {MAX_RETRIES} retries: {last_exc}",
        file=sys.stderr,
    )
    sys.exit(3)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_report(path, model, timestamp, total_prompts, threshold, accuracy,
                 passed, per_prompt_rows, failures):
    """Write the markdown evaluation report."""
    result_str = "PASS" if passed else "FAIL"
    lines = [
        f"# Routing Evals Report",
        "",
        f"- **Model:** {model}",
        f"- **Timestamp:** {timestamp}",
        f"- **Total prompts:** {total_prompts}",
        f"- **Threshold:** {threshold}",
        f"- **Accuracy:** {accuracy:.3f}",
        f"- **Result:** {'✓ PASS' if passed else '✗ FAIL'}",
        "",
        "## Per-prompt results",
        "",
        "| T-ID | Category | Expected | Got | Credit |",
        "|---|---|---|---|---|",
    ]
    for row in per_prompt_rows:
        lines.append(
            f"| {row['id']} | {row['category']} | {row['expected_str']} | "
            f"{row['got_str']} | {row['credit']} |"
        )

    if failures:
        lines += ["", "## Failures", ""]
        for f in failures:
            lines += [
                f"### {f['id']} — {f['prompt_snippet']}",
                "",
                f"- Expected: {f['expected_str']}",
                f"- Got: {f['got_str']}",
                f"- Model rationale: \"{f['rationale']}\"",
                "",
            ]

    report_text = "\n".join(lines) + "\n"
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(report_text)
    except OSError as exc:
        print(f"WARNING: could not write report to {path}: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Routing eval harness for the Dossier skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  PASS — accuracy >= threshold
  1  FAIL — accuracy < threshold (report still written)
  2  ENV  — missing API key, missing files, or malformed test set
  3  API  — API error after 3 retries
""",
    )
    parser.add_argument("skill_md", help="Path to SKILL.md to evaluate against.")
    parser.add_argument("test_set", help="Path to routing_test_set.md.")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model ID (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help=f"Pass threshold 0–1 (default: {DEFAULT_THRESHOLD})"
    )
    parser.add_argument(
        "--report", default=DEFAULT_REPORT,
        help=f"Output report path (default: {DEFAULT_REPORT})"
    )
    parser.add_argument(
        "--max-prompts", type=int, default=0,
        help="Evaluate only the first N prompts (0 = all). Useful for dry-runs."
    )
    args = parser.parse_args()

    # --- Environment validation ---
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set. "
            "Export it before running the harness.",
            file=sys.stderr,
        )
        sys.exit(2)

    # --- Load SKILL.md ---
    if not os.path.exists(args.skill_md):
        print(f"ERROR: SKILL.md not found: {args.skill_md}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(args.skill_md, encoding="utf-8") as fh:
            rendered_skill = fh.read()
    except OSError as exc:
        print(f"ERROR: cannot read {args.skill_md}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not rendered_skill.strip():
        print(f"ERROR: {args.skill_md} is empty.", file=sys.stderr)
        sys.exit(2)

    # --- Parse test set ---
    prompts = parse_test_set(args.test_set)

    # --- Apply --max-prompts ---
    if args.max_prompts > 0:
        prompts = prompts[: args.max_prompts]
        print(f"Dry-run mode: evaluating {len(prompts)} of {EXPECTED_PROMPT_COUNT} prompts.")

    # --- Set up Anthropic client ---
    client = anthropic.Anthropic(api_key=api_key)

    # --- Run evals ---
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total = len(prompts)
    credits = []
    per_prompt_rows = []
    failures = []

    print(f"Running {total} prompt(s) against model {args.model} ...")

    for i, (test_id, prompt_text, expected_text) in enumerate(prompts, 1):
        print(f"  [{i:2d}/{total}] {test_id} ...", end=" ", flush=True)

        expected = parse_expected(test_id, expected_text)

        # Call the API
        raw_response = call_api_with_retry(client, args.model, rendered_skill, prompt_text)

        # Parse JSON response
        got = None
        try:
            cleaned = raw_response.strip()
            # Strip code fences if model produced them despite instructions
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)
            got = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"[INVALID JSON] response: {raw_response!r}")
            got = {"would_trigger_dossier": None, "mode": None, "rationale": "(invalid JSON)"}

        credit = score(expected, got) if got.get("would_trigger_dossier") is not None else 0.0
        credits.append(credit)

        # Format strings for report
        if expected["would_trigger"]:
            expected_str = f"trigger:true mode:{expected['mode'] or 'any'}"
        else:
            expected_str = "trigger:false"

        got_trigger = got.get("would_trigger_dossier")
        got_mode = got.get("mode")
        if got_trigger:
            got_str = f"trigger:true mode:{got_mode or 'null'}"
        elif got_trigger is False:
            got_str = "trigger:false"
        else:
            got_str = "trigger:invalid"

        # Determine category from test_id
        tid_num = int(test_id.split("-")[1])
        if tid_num <= 20:
            category = "Direct"
        elif tid_num <= 30:
            category = "Indirect"
        elif tid_num <= 38:
            category = "Negative"
        else:
            category = "Ambiguous"

        row = {
            "id": test_id,
            "category": category,
            "expected_str": expected_str,
            "got_str": got_str,
            "credit": credit,
        }
        per_prompt_rows.append(row)

        print(f"credit={credit:.1f} ({got_str})")

        if credit < 1.0:
            snippet = prompt_text[:60] + ("..." if len(prompt_text) > 60 else "")
            failures.append({
                "id": test_id,
                "prompt_snippet": snippet,
                "expected_str": expected_str,
                "got_str": got_str,
                "rationale": got.get("rationale", ""),
                "credit": credit,
            })

    # --- Score ---
    accuracy = sum(credits) / total if total > 0 else 0.0
    passed = accuracy >= args.threshold

    print(f"\nAccuracy: {accuracy:.3f} / threshold: {args.threshold} → "
          f"{'PASS' if passed else 'FAIL'}")

    # --- Write report ---
    write_report(
        args.report,
        model=args.model,
        timestamp=timestamp,
        total_prompts=total,
        threshold=args.threshold,
        accuracy=accuracy,
        passed=passed,
        per_prompt_rows=per_prompt_rows,
        failures=failures,
    )
    print(f"Report written to: {args.report}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
