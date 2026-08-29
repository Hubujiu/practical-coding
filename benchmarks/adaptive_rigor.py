"""Adaptive-rigor benchmark adapter for Practical Coding v1.3.

Keeps the v2.0 execution harness intact while changing the classification contract:
Decision is a pre-execution gate; Direct/Debugging/Implementation are execution states;
Retrieval is scored as a minimum-sufficient / maximum-reasonable cost interval.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any


DECISION_STATES = ("CLEAR", "REQUIRED")
EXECUTION_STATES = ("BLOCKED", "DIRECT", "DEBUGGING", "IMPLEMENTATION")
RETRIEVAL_ORDER = ("NONE", "TARGETED", "BOUNDED", "STRUCTURAL")
_RETRIEVAL_INDEX = {name: index for index, name in enumerate(RETRIEVAL_ORDER)}


TRANSITION_CASES = {
    "transition-decision-to-direct": {
        "decision": "CLEAR",
        "execution": "DIRECT",
        "retrieval_min": "TARGETED",
        "retrieval_max": "BOUNDED",
        "prompt": (
            "The earlier storage choice is settled: repository policy requires Python sqlite3. "
            "save_history() is the named function and the existing focused test is sufficient. "
            "Classify the current state now."
        ),
    },
    "transition-decision-to-implementation": {
        "decision": "CLEAR",
        "execution": "IMPLEMENTATION",
        "retrieval_min": "BOUNDED",
        "retrieval_max": "STRUCTURAL",
        "prompt": (
            "The earlier choice is settled: use a dual-read rolling migration. "
            "The producers, readers, rollback surface, and mixed-version storage contract are still unmapped. "
            "Classify the current state now."
        ),
    },
    "transition-debug-to-direct": {
        "decision": "CLEAR",
        "execution": "DIRECT",
        "retrieval_min": "TARGETED",
        "retrieval_max": "BOUNDED",
        "prompt": (
            "The failing test and trace already establish the root cause: parse_bool() does not strip "
            "surrounding whitespace. The shared parser and focused check are known. Classify the current state now."
        ),
    },
    "transition-debug-to-implementation": {
        "decision": "CLEAR",
        "execution": "IMPLEMENTATION",
        "retrieval_min": "BOUNDED",
        "retrieval_max": "STRUCTURAL",
        "prompt": (
            "Diagnosis is complete: invoice leakage comes from checking owner_id without tenant ownership. "
            "However the authoritative tenant authorization boundary, indirect callers, rejection-before-read "
            "contract, and sufficient security evidence are still unmapped. Classify the current state now."
        ),
    },
}


TRANSITION_BEHAVIOR_CASES = {
    "native-transition-decision-to-direct": {
        "prompt": (
            "The storage decision is already settled: repository policy requires Python sqlite3. "
            "save_history() in cli.py is the only affected function and its focused test is sufficient. "
            "Implement it without reopening the settled decision."
        ),
        "files": {
            "cli.py": "import sqlite3\n\ndef save_history(connection, command):\n    pass\n",
        },
        "reasoning_module": None,
        "retrieval": "TARGETED",
    },
    "native-transition-decision-to-implementation": {
        "prompt": (
            "The migration strategy is already settled as dual-read rolling migration. "
            "Before editing, the readers, writers, rollback path, mixed-version guarantees, and authoritative "
            "storage boundary are still unmapped. Determine the safe implementation surface without reopening "
            "the settled strategy choice."
        ),
        "files": {
            "sessions.py": "def encode_session(value):\n    return value\n\ndef decode_session(raw):\n    return raw\n",
        },
        "reasoning_module": "implementation.md",
        "retrieval": "STRUCTURAL",
    },
    "native-transition-debug-to-direct": {
        "prompt": (
            "The failing test and trace already establish the cause: parse_bool() does not strip whitespace. "
            "Fix that known shared parser and run the focused check; do not restart diagnosis."
        ),
        "files": {
            "config.py": (
                "def parse_bool(value):\n"
                "    return value.lower() in {'1', 'true', 'yes'}\n\n"
                "def feature_enabled(env):\n"
                "    return parse_bool(env.get('FEATURE', 'false'))\n"
            ),
        },
        "reasoning_module": None,
        "retrieval": "TARGETED",
    },
    "native-transition-debug-to-implementation": {
        "prompt": (
            "Diagnosis is complete: cross-tenant invoice access comes from checking owner_id without tenant "
            "ownership. The authoritative permission boundary, indirect callers, rejection-before-read invariant, "
            "and sufficient security evidence remain unmapped. Determine the safe implementation surface."
        ),
        "files": {
            "authorization.py": (
                "def owns_record(user, record):\n"
                "    return user['id'] == record['owner_id']\n\n"
                "def can_view_invoice(user, invoice):\n"
                "    return owns_record(user, invoice)\n"
            ),
        },
        "reasoning_module": "implementation.md",
        "retrieval": "STRUCTURAL",
    },
}


def retrieval_bounds(expected: str) -> tuple[str, str]:
    """Map the old exact label to a principled cost interval.

    NONE permits bounded discovery because open decisions may reasonably need repository facts.
    TARGETED permits bounded discovery when the known concept's location is not directly available.
    BOUNDED remains exact: selecting no context is insufficient and structural work is unnecessary.
    STRUCTURAL accepts bounded fallback when no structural backend is available.
    """
    if expected == "NONE":
        return "NONE", "BOUNDED"
    if expected == "TARGETED":
        return "TARGETED", "BOUNDED"
    if expected == "BOUNDED":
        return "BOUNDED", "BOUNDED"
    if expected == "STRUCTURAL":
        return "BOUNDED", "STRUCTURAL"
    raise ValueError(expected)


def _convert_case(old: tuple[str, str, str]) -> dict[str, str]:
    reasoning, retrieval, prompt = old
    if reasoning == "DECISION":
        decision, execution = "REQUIRED", "BLOCKED"
    elif reasoning == "NONE":
        decision, execution = "CLEAR", "DIRECT"
    elif reasoning == "DEBUGGING":
        decision, execution = "CLEAR", "DEBUGGING"
    elif reasoning == "IMPLEMENTATION":
        decision, execution = "CLEAR", "IMPLEMENTATION"
    else:
        raise ValueError(reasoning)
    minimum, maximum = retrieval_bounds(retrieval)
    return {
        "decision": decision,
        "execution": execution,
        "retrieval_min": minimum,
        "retrieval_max": maximum,
        "prompt": prompt,
    }


def parse_rigor_answer(answer: str) -> tuple[str, str, str]:
    match = re.fullmatch(
        r"\s*`?\s*DECISION\s*=\s*(CLEAR|REQUIRED)\s*;\s*"
        r"EXECUTION\s*=\s*(BLOCKED|DIRECT|DEBUGGING|IMPLEMENTATION)\s*;\s*"
        r"RETRIEVAL\s*=\s*(NONE|TARGETED|BOUNDED|STRUCTURAL)\s*`?\s*[.]?\s*",
        answer.upper(),
    )
    return match.groups() if match else ("", "", "")


def score_rigor(spec: dict[str, str], answer: str) -> dict[str, Any]:
    actual_decision, actual_execution, actual_retrieval = parse_rigor_answer(answer)
    decision_ok = actual_decision == spec["decision"]
    execution_ok = actual_execution == spec["execution"]
    state_valid = not (
        (actual_decision == "REQUIRED" and actual_execution != "BLOCKED")
        or (actual_decision == "CLEAR" and actual_execution == "BLOCKED")
    )
    if actual_retrieval in _RETRIEVAL_INDEX:
        actual_index = _RETRIEVAL_INDEX[actual_retrieval]
        min_index = _RETRIEVAL_INDEX[spec["retrieval_min"]]
        max_index = _RETRIEVAL_INDEX[spec["retrieval_max"]]
        retrieval_sufficient = actual_index >= min_index
        retrieval_efficient = actual_index <= max_index
    else:
        retrieval_sufficient = retrieval_efficient = False
    retrieval_ok = retrieval_sufficient and retrieval_efficient
    return {
        "expected_decision": spec["decision"],
        "actual_decision": actual_decision,
        "decision_ok": decision_ok,
        "expected_execution": spec["execution"],
        "actual_execution": actual_execution,
        "execution_ok": execution_ok,
        "state_valid": state_valid,
        "retrieval_min": spec["retrieval_min"],
        "retrieval_max": spec["retrieval_max"],
        "actual_retrieval": actual_retrieval,
        "retrieval_sufficient": retrieval_sufficient,
        "retrieval_efficient": retrieval_efficient,
        "retrieval_ok": retrieval_ok,
        "passed": decision_ok and execution_ok and state_valid and retrieval_ok,
    }


def install(bench: Any) -> None:
    if getattr(bench, "_adaptive_rigor_installed", False):
        return

    bench.DECISION_STATES = DECISION_STATES
    bench.EXECUTION_STATES = EXECUTION_STATES
    bench.RETRIEVAL_MODES = RETRIEVAL_ORDER
    bench.ROUTER_CASES = {name: _convert_case(spec) for name, spec in bench.ROUTER_CASES.items()}
    bench.ROUTER_CASES.update(TRANSITION_CASES)
    bench.BEHAVIOR_CASES.update(TRANSITION_BEHAVIOR_CASES)

    for profile in ("standard", "full"):
        bench.PROFILE_CASES[profile]["router"] = list(bench.ROUTER_CASES)
        bench.PROFILE_CASES[profile]["behavior"] = list(bench.BEHAVIOR_CASES)

    smoke = bench.PROFILE_CASES["smoke"]
    smoke["router"] = [
        "direct-artifact",
        "decision-auth",
        "debug-named-function",
        "verification-risk",
        "transition-debug-to-direct",
    ]

    original_run_cell = bench.run_cell
    original_rescore = bench.rescore_run

    def run_cell(spec: tuple[str, str, str, int], args: Any, sources: dict[str, Path], previous: Path | None, ponytail: Any, eval_homes: dict[str, Path], output: Path) -> dict[str, Any]:
        suite, case, arm, repetition = spec
        if suite != "router":
            return original_run_cell(spec, args, sources, previous, ponytail, eval_homes, output)

        cell = output / "cells" / suite / case / arm / f"r{repetition:03d}"
        cell.mkdir(parents=True, exist_ok=False)
        workspace = cell / "workspace"
        workspace.mkdir()

        case_spec = bench.ROUTER_CASES[case]
        loaded = bench.skill_text(arm, sources, previous, suite=suite)
        prompt = (
            "Classify the current adaptive-rigor state. Return exactly: "
            "DECISION=<CLEAR|REQUIRED>; "
            "EXECUTION=<BLOCKED|DIRECT|DEBUGGING|IMPLEMENTATION>; "
            "RETRIEVAL=<NONE|TARGETED|BOUNDED|STRUCTURAL>. "
            "DECISION=REQUIRED only when an unresolved material choice blocks or materially changes the next safe action; "
            "then EXECUTION must be BLOCKED. Otherwise DECISION=CLEAR. "
            "DIRECT means the Core is sufficient now. DEBUGGING means an observed failure exists and its cause is not evidenced. "
            "IMPLEMENTATION means safe execution is blocked by an unknown contract/invariant, unresolved material risk boundary, "
            "or insufficient evidence for a risky claim. These execution states are alternatives, not sequential stages. "
            "Retrieval describes the cheapest sufficient repository-context cost for the next action: NONE, known TARGETED source, "
            "BOUNDED/ranked discovery, or STRUCTURAL relationship mapping. Classify only; do not use tools or solve it.\n\n"
            "Request: " + case_spec["prompt"] + "\n\n" + loaded
        )
        (cell / "prompt.txt").write_text(prompt, encoding="utf-8")

        env = os.environ.copy()
        env["CODEX_HOME"] = str(eval_homes["default"])
        codex = bench.resolve_codex(args.codex)
        first_out, first_err = cell / "round1.jsonl", cell / "round1.stderr.txt"
        code, timed_out, forced, duration = bench.run_codex(
            bench.codex_command(codex, workspace),
            prompt,
            workspace,
            env,
            first_out,
            first_err,
            args.timeout,
        )
        parsed = bench.parse_transcript(first_out)
        answers = [parsed["answer"]]
        usage = parsed["usage"]
        record: dict[str, Any] = {
            "suite": suite,
            "case": case,
            "arm": arm,
            "repetition": repetition,
            "exit_status": code,
            "timed_out": timed_out,
            "forced_after_completion": forced,
            "duration_seconds": duration,
            "setup_duration_seconds": 0.0,
            "dependency_setup": None,
            "tool_calls": parsed["tool_calls"],
            **usage,
            "workspace": str(workspace),
            "answers": answers,
        }
        infrastructure_error = "timeout" if timed_out else (f"codex exit status {code}" if code and not forced else None)
        if infrastructure_error:
            record.update({"passed": None, "verdict": "indeterminate", "error": infrastructure_error})
        else:
            record.update(score_rigor(case_spec, answers[0]))
            record["verdict"] = "pass" if record["passed"] else "fail"

        (cell / "answer.md").write_text(answers[0] + "\n", encoding="utf-8")
        (cell / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    def rescore_run(run_dir: Path, ponytail: Any) -> None:
        results_path = run_dir / "results.json"
        manifest_path = run_dir / "manifest.json"
        records = json.loads(results_path.read_text(encoding="utf-8"))
        if not any(record.get("suite") == "router" for record in records):
            original_rescore(run_dir, ponytail)
            return

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in records:
            suite, case = record["suite"], record["case"]
            answers = record.get("answers") or []
            if suite == "router":
                record.update(score_rigor(bench.ROUTER_CASES[case], answers[0] if answers else ""))
            elif suite == "decision":
                first = bench.decision_metrics(answers[0]) if answers else bench.decision_metrics("")
                second = bench.decision_metrics(answers[1]) if len(answers) > 1 else {
                    "questions": 999,
                    "recommendations": 0,
                    "has_tradeoff": False,
                    "attempted_implementation": False,
                }
                converged = second["questions"] == 0 and any(
                    term in (answers[-1].lower() if answers else "")
                    for term in bench.DECISION_CASES[case]["expected"]
                )
                passed = (
                    first["questions"] > 0
                    and first["recommendations"] >= first["questions"]
                    and not first["attempted_implementation"]
                    and converged
                    and not second["attempted_implementation"]
                )
                record.update({"first_round": first, "second_round": second, "converged": converged, "passed": passed})
            elif suite == "behavior":
                commands: list[str] = []
                outputs: list[str] = []
                for transcript in sorted(Path(record["workspace"]).parent.glob("round*.jsonl")):
                    parsed = bench.parse_transcript(transcript)
                    commands.extend(parsed["tool_commands"])
                    outputs.extend(parsed["tool_outputs"])
                behavior = bench.BEHAVIOR_CASES[case]
                record.update(
                    bench.behavior_score(
                        commands,
                        behavior["reasoning_module"],
                        outputs,
                        behavior["retrieval"],
                        behavior.get("backend"),
                    )
                )
            elif "workspace" in record:
                workspace = Path(record["workspace"])
                scored = (
                    ponytail.score_workspace(case, record["arm"], bench.MODEL, workspace)
                    if case in ponytail.TASKS
                    else bench.custom_debug_score(case, workspace)
                )
                if case not in ponytail.TASKS:
                    scored.update(ponytail.git_diff_stats(workspace))
                record.update(scored)
                build = record.get("build")
                if build is not None:
                    build["infrastructure_error"] = build.get("infrastructure_error") or bench.build_infrastructure_error(
                        build.get("output_tail", "")
                    )
                if build and build.get("infrastructure_error"):
                    record["passed"] = None
                    record["indeterminate_reason"] = build["infrastructure_error"]
                else:
                    record["passed"] = (
                        scored.get("correct") == 1
                        and scored.get("safe") == 1
                        and (build is None or build.get("passed"))
                    )
            if record.get("error") or record.get("timed_out"):
                record["verdict"] = "indeterminate"
            else:
                record["verdict"] = (
                    "indeterminate"
                    if record.get("passed") is None
                    else ("pass" if record["passed"] else "fail")
                )

        summary = bench.aggregate(records)
        deltas = bench.comparisons(summary)
        rollups = bench.suite_rollups(records)
        rollup_deltas = bench.comparisons(rollups)
        cards = bench.scorecards(summary, rollups)
        results_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        (run_dir / "comparisons.json").write_text(json.dumps(deltas, indent=2) + "\n", encoding="utf-8")
        (run_dir / "rollups.json").write_text(json.dumps(rollups, indent=2) + "\n", encoding="utf-8")
        (run_dir / "rollup-comparisons.json").write_text(json.dumps(rollup_deltas, indent=2) + "\n", encoding="utf-8")
        (run_dir / "scorecards.json").write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
        manifest.update({
            "rescored_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "runner_version": bench.VERSION,
            "runner_sha256": bench.sha256(Path(bench.__file__)),
        })
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        bench.write_report(
            run_dir / "report.md",
            manifest,
            summary,
            deltas,
            float(manifest.get("suite_elapsed_seconds", 0)),
            rollups,
            rollup_deltas,
            cards,
        )
        print(f"rescored {len(records)} cells in {run_dir}")

    bench.parse_router_answer = parse_rigor_answer
    bench.score_rigor = score_rigor
    bench.run_cell = run_cell
    bench.rescore_run = rescore_run
    bench._adaptive_rigor_installed = True
