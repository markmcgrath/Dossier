#!/usr/bin/env python3
"""
run_routing_evals.py — Routing eval harness for the Dossier skill.

Maintainer-side tool. Loads 45 prompts from a golden test-set markdown
file, shells out to `claude -p` (Claude Code CLI in non-interactive print
mode) for each prompt with the bundled SKILL.md as system context, scores
routing decisions against expected outcomes, and writes a markdown report.

Authentication: this script does NOT use the Anthropic SDK or
ANTHROPIC_API_KEY. It invokes the locally-installed `claude` CLI, which
draws from your Claude Code subscription. Make sure `claude` is on PATH
and authenticated before running.

Usage:
    python tools/run_routing_evals.py
        [--skill-md <path>] [--test-set <path>]
        [--report <md>] [--max-prompts <N>]

Options:
    --skill-md       Path to SKILL.md.       Default: skill/SKILL.md
    --test-set       Path to test set.       Default: tests/golden_prompts/routing_test_set.md
    --report         Output report path.     Default: routing-evals-report.md
    --max-prompts N  Evaluate first N only.  Default: 0 (all)

Exit codes:
    0  — completed; accuracy printed and report written. Maintainer
         judges whether the score is acceptable; this script does not
         gate anything.
    2  — environment error (missing files, malformed test set, `claude`
         not on PATH or authentication broken)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SKILL_MD = "skill/SKILL.md"
DEFAULT_TEST_SET = "tests/golden_prompts/routing_test_set.md"
DEFAULT_REPORT = "routing-evals-report.md"
EXPECTED_PROMPT_COUNT = 45
PER_PROMPT_TIMEOUT_S = 120
RETRY_ATTEMPTS = 2

EVAL_INSTRUCTION_PREFIX = (
    "You are evaluating which Claude skill should route a user prompt. "
    "The Dossier skill is the only available candidate; its YAML frontmatter "
    "(what Claude sees when picking a skill to invoke) is shown below. "
    "Given the user prompt sent separately, decide whether Dossier would "
    "trigger and, if so, which mode it would route to.\n\n"
    "Respond ONLY with a valid JSON object of this exact shape:\n"
    '{"would_trigger_dossier": true | false, "mode": "Mode N" | null, '
    '"rationale": "<one sentence>"}\n\n'
    "Rules:\n"
    "- would_trigger_dossier: true if the prompt should activate the "
    "Dossier skill; false otherwise.\n"
    "- mode: the primary mode (e.g. \"Mode 1\", \"Mode 5\") if "
    "would_trigger_dossier is true; null if false. Available modes: 0 "
    "(health check), 1 (offer evaluator), 2 (portal scan), 3 (interview "
    "prep), 4 (company research), 5 (outreach), 6 (cover letter), 7 "
    "(salary negotiation), 8 (LinkedIn browser), 9 (inbox followup), 10 "
    "(calendar ops), 11 (tailored CV), 12 (batch pipeline), 13 (calibration).\n"
    "- rationale: one sentence explaining the routing decision.\n"
    "Do not include code fences, markdown, or any text outside the "
    "JSON object."
)


def extract_frontmatter(skill_md_content):
    """
    Extract the YAML frontmatter (between the first two `---` lines) from
    SKILL.md. This is what Claude actually sees when deciding whether to
    route a prompt to a skill — the body is loaded only AFTER routing
    succeeds. Passing only the frontmatter (~1KB) keeps the system prompt
    well under Windows CreateProcess argv limits (~32KB).
    """
    lines = skill_md_content.splitlines()
    if not lines or lines[0].strip() != "---":
        # No frontmatter; return the whole thing (will fail loud if too big)
        return skill_md_content

    fm_lines = ["---"]
    for line in lines[1:]:
        fm_lines.append(line)
        if line.strip() == "---":
            return "\n".join(fm_lines)

    # Unterminated frontmatter; return what we have
    return "\n".join(fm_lines)


# ---------------------------------------------------------------------------
# Test-set parser (unchanged from API-era harness)
# ---------------------------------------------------------------------------

def parse_test_set(path):
    """
    Parse the routing_test_set.md file into a list of
    (test_id, prompt_text, expected_text) tuples.

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

    in_prompt = False
    in_expected = False

    heading_re = re.compile(r"^###\s+T-(\d{3})")
    bold_field_re = re.compile(r"^\*\*\w")
    blockquote_re = re.compile(r"^>\s?(.*)")

    def flush_entry():
        if current_id is not None and current_prompt_lines and current_expected is not None:
            prompt_text = " ".join(current_prompt_lines).strip()
            results.append((current_id, prompt_text, current_expected.strip()))

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        m = heading_re.match(line)
        if m:
            flush_entry()
            current_id = f"T-{m.group(1)}"
            current_prompt_lines = []
            current_expected = None
            in_prompt = False
            in_expected = False
            continue

        if line.strip() == "---":
            in_prompt = False
            in_expected = False
            continue

        if line.strip() == "**Prompt:**":
            in_prompt = True
            in_expected = False
            continue

        if line.strip().startswith("**Expected (monolithic):**"):
            in_prompt = False
            in_expected = True
            after = line.strip()[len("**Expected (monolithic):**"):].strip()
            current_expected = after if after else ""
            continue

        if line.strip().startswith("**Expected (split):**") or \
                line.strip().startswith("**Rationale:**") or \
                line.strip().startswith("**Category:**"):
            in_prompt = False
            in_expected = False
            continue

        if bold_field_re.match(line.strip()):
            in_prompt = False
            in_expected = False
            continue

        if in_prompt:
            bm = blockquote_re.match(line)
            if bm:
                current_prompt_lines.append(bm.group(1).strip())
            elif line.strip() and not line.strip().startswith(">"):
                in_prompt = False
            continue

        if in_expected and line.strip():
            if current_expected:
                current_expected = current_expected + " " + line.strip()
            else:
                current_expected = line.strip()

    flush_entry()

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
# Expected outcome parser (unchanged)
# ---------------------------------------------------------------------------

def parse_expected(test_id, expected_text):
    """
    Parse the expected-outcome string for a single prompt.
    Returns {"would_trigger": bool, "mode": str | None}.
    """
    if test_id == "T-038":
        return {"would_trigger": True, "mode": None}

    upper = expected_text.upper()
    if "NONE" in upper:
        none_pos = upper.find("NONE")
        arrow_pos = upper.find("DOSSIER →")
        if arrow_pos == -1 or none_pos < arrow_pos:
            return {"would_trigger": False, "mode": None}

    mode_match = re.search(r"Mode\s+(\d+(?:\.\d+)?)", expected_text, re.IGNORECASE)
    if mode_match:
        mode_str = f"Mode {mode_match.group(1)}"
        return {"would_trigger": True, "mode": mode_str}

    if "DOSSIER" in upper:
        return {"would_trigger": True, "mode": None}

    return {"would_trigger": False, "mode": None}


# ---------------------------------------------------------------------------
# Scoring (unchanged)
# ---------------------------------------------------------------------------

def score(expected, got):
    """
    Compute credit (0.0, 0.5, or 1.0) for a single prompt.
    """
    trigger_match = (expected["would_trigger"] == got.get("would_trigger_dossier"))
    if not trigger_match:
        return 0.0

    if expected["mode"] is None:
        return 1.0

    got_mode = got.get("mode")
    if got_mode and _normalize_mode(got_mode) == _normalize_mode(expected["mode"]):
        return 1.0

    return 0.5


def _normalize_mode(mode_str):
    if mode_str is None:
        return None
    return re.sub(r"\s+", " ", mode_str.strip().title())


# ---------------------------------------------------------------------------
# Claude Code CLI invocation
# ---------------------------------------------------------------------------

def _extract_assistant_text(data):
    """
    Walk the JSON shape returned by `claude -p --output-format json` and
    extract the assistant's response text. Per claude-code-guide the field
    is typically "result"; fall back to messages-array shapes if absent.
    """
    if isinstance(data, dict):
        if isinstance(data.get("result"), str):
            return data["result"]
        # Newer/older shapes — walk best-effort
        msgs = data.get("messages") or []
        for msg in reversed(msgs):
            content = msg.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        return block.get("text", "")
        # Last-ditch: scan top-level string fields for what looks like JSON
        for key in ("output", "response", "text", "content"):
            if isinstance(data.get(key), str):
                return data[key]
    return ""


def call_claude_cli(user_prompt, system_prompt, claude_path):
    """
    Issue one `claude -p` invocation. Up to RETRY_ATTEMPTS attempts.
    Returns the model's response text. Exits 2 if `claude` is missing
    or repeatedly fails (treated as environment error since this is a
    maintainer-side tool — the CLI failing is not an API outage to retry
    around indefinitely).

    Flag choices:
      --system-prompt <inline>     replaces the default system prompt;
                                   isolates from CLAUDE.md auto-discovery,
                                   default tool prompts, etc.
      --disable-slash-commands     don't load skills (parent project's
                                   skills/MCP context cannot bleed in)
      --strict-mcp-config + ""     no MCP servers
      --output-format json         structured response in `result` field

    Note: `--bare` is intentionally NOT used — it disables OAuth/keychain
    auth and forces ANTHROPIC_API_KEY, which defeats the point of using
    Claude Code subscription.

    `claude_path` is the absolute path to the `claude` executable
    (resolved once via shutil.which at startup) so subprocess.run works
    on Windows where `claude` is a .cmd shim that argv-style execve
    doesn't resolve.
    """
    cmd = [
        claude_path, "-p", user_prompt,
        "--system-prompt", system_prompt,
        "--disable-slash-commands",
        "--strict-mcp-config",
        "--mcp-config", "",
        "--output-format", "json",
    ]

    last_err = ""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=PER_PROMPT_TIMEOUT_S,
            )
        except FileNotFoundError:
            print(
                "ERROR: `claude` CLI not found on PATH. Install Claude Code "
                "and ensure `claude` is invokable.",
                file=sys.stderr,
            )
            sys.exit(2)
        except subprocess.TimeoutExpired:
            last_err = f"timeout after {PER_PROMPT_TIMEOUT_S}s"
            continue

        if result.returncode != 0:
            last_err = f"exit={result.returncode} stderr={result.stderr.strip()[:200]}"
            continue

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # `claude -p` returned non-JSON despite --output-format json — surface raw
            return result.stdout.strip()

        text = _extract_assistant_text(data)
        if text:
            return text
        last_err = f"could not extract assistant text from response keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}"

    print(
        f"ERROR: `claude -p` failed after {RETRY_ATTEMPTS} attempts. Last error: {last_err}",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_report(path, timestamp, total_prompts, accuracy,
                 per_prompt_rows, failures):
    """Write the markdown evaluation report."""
    lines = [
        "# Routing Evals Report",
        "",
        f"- **Timestamp:** {timestamp}",
        f"- **Total prompts:** {total_prompts}",
        f"- **Accuracy:** {accuracy:.3f}",
        f"- **Failures:** {len(failures)}",
        "",
        "_Note: this is a maintainer-side report. The harness does not gate "
        "publication. Score acceptability is the maintainer's judgment._",
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
        description="Routing eval harness for the Dossier skill (maintainer-side, uses `claude -p`).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Completed (regardless of accuracy)
  2  Environment error (missing files, malformed test set, missing `claude` CLI)
""",
    )
    parser.add_argument(
        "--skill-md", default=DEFAULT_SKILL_MD,
        help=f"Path to SKILL.md (default: {DEFAULT_SKILL_MD})"
    )
    parser.add_argument(
        "--test-set", default=DEFAULT_TEST_SET,
        help=f"Path to routing test set (default: {DEFAULT_TEST_SET})"
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
    claude_path = shutil.which("claude")
    if claude_path is None:
        print(
            "ERROR: `claude` CLI not on PATH. Install Claude Code and ensure "
            "`claude` is invokable.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not os.path.exists(args.skill_md):
        print(f"ERROR: SKILL.md not found: {args.skill_md}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(args.skill_md, encoding="utf-8") as fh:
            skill_md_content = fh.read()
    except OSError as exc:
        print(f"ERROR: cannot read {args.skill_md}: {exc}", file=sys.stderr)
        sys.exit(2)

    if not skill_md_content.strip():
        print(f"ERROR: {args.skill_md} is empty.", file=sys.stderr)
        sys.exit(2)

    # --- Parse test set ---
    prompts = parse_test_set(args.test_set)

    if args.max_prompts > 0:
        prompts = prompts[: args.max_prompts]
        print(f"Dry-run mode: evaluating {len(prompts)} of {EXPECTED_PROMPT_COUNT} prompts.")

    # --- Build the system prompt (eval prefix + SKILL.md frontmatter only) ---
    # Pass ONLY the YAML frontmatter, not the full SKILL.md body.
    # Routing decisions are made on the description; the body loads only
    # AFTER a routing decision is made. This also keeps the system prompt
    # ~1KB instead of ~30KB, fitting comfortably under Windows
    # CreateProcess argv limits.
    skill_frontmatter = extract_frontmatter(skill_md_content)
    system_prompt = (
        EVAL_INSTRUCTION_PREFIX
        + "\n\n---\n\nDossier skill frontmatter (what Claude sees when routing):\n\n"
        + skill_frontmatter
    )

    # --- Run evals ---
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total = len(prompts)
    credits = []
    per_prompt_rows = []
    failures = []

    print(f"Running {total} prompt(s) via `claude -p` ...")

    for i, (test_id, prompt_text, expected_text) in enumerate(prompts, 1):
        print(f"  [{i:2d}/{total}] {test_id} ...", end=" ", flush=True)

        expected = parse_expected(test_id, expected_text)
        raw_response = call_claude_cli(prompt_text, system_prompt, claude_path)

        got = None
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned)
            got = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"[INVALID JSON] response: {raw_response!r}")
            got = {"would_trigger_dossier": None, "mode": None, "rationale": "(invalid JSON)"}

        credit = score(expected, got) if got.get("would_trigger_dossier") is not None else 0.0
        credits.append(credit)

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
    print(f"\nAccuracy: {accuracy:.3f}  ({len(failures)} failure(s))")

    # --- Write report ---
    write_report(
        args.report,
        timestamp=timestamp,
        total_prompts=total,
        accuracy=accuracy,
        per_prompt_rows=per_prompt_rows,
        failures=failures,
    )
    print(f"Report written to: {args.report}")

    sys.exit(0)


if __name__ == "__main__":
    main()
