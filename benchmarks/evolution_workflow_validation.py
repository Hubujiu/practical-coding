#!/usr/bin/env python3
"""Score the explicit WikiSkill-inspired maintenance workflow contract.

This benchmark is deterministic and intentionally does not measure runtime coding
quality. Runtime quality remains covered by the tree benchmark. This suite verifies
that maintenance skills are isolated from automatic routing and that the proposer
contract cannot accept a candidate without a frozen, same-evidence non-regression gate.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SESSION_SKILL = ROOT / "evolution/skills/session-to-wiki/SKILL.md"
EVOLVE_SKILL = ROOT / "evolution/skills/evolve-skill/SKILL.md"
TOPOLOGY = HERE / "tree_topology.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_name(text: str) -> str | None:
    match = re.search(r"(?ms)^---\s*$.*?^name:\s*([^\n]+?)\s*$.*?^---\s*$", text)
    return match.group(1).strip().strip('"\'') if match else None


def contains_all(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return all(term.lower() in lower for term in terms)


def checks() -> list[tuple[str, Callable[[], bool]]]:
    session = read(SESSION_SKILL) if SESSION_SKILL.is_file() else ""
    evolve = read(EVOLVE_SKILL) if EVOLVE_SKILL.is_file() else ""
    topology = json.loads(read(TOPOLOGY)) if TOPOLOGY.is_file() else {}
    automatic_refs = {
        spec.get("reference")
        for spec in topology.get("automatic_nodes", {}).values()
        if isinstance(spec, dict)
    }
    automatic_children = {
        child
        for spec in topology.get("automatic_nodes", {}).values()
        if isinstance(spec, dict)
        for child in spec.get("children", [])
    }

    return [
        ("session skill exists", lambda: SESSION_SKILL.is_file()),
        ("evolve skill exists", lambda: EVOLVE_SKILL.is_file()),
        ("session skill has standalone name", lambda: frontmatter_name(session) == "session-to-wiki"),
        ("evolve skill has standalone name", lambda: frontmatter_name(evolve) == "evolve-skill"),
        ("session activation is explicit-only", lambda: contains_all(session, ["explicit", "outside the automatic runtime router tree"])),
        ("evolve activation is explicit-only", lambda: contains_all(evolve, ["explicit", "outside the automatic coding router tree"])),
        ("session writes immutable raw receipt first", lambda: contains_all(session, ["immutable receipt", "evolution/raw/sessions/", "before consolidating"])),
        ("session sanitizes and avoids transcript storage", lambda: contains_all(session, ["sanitize", "never copy the full transcript", "secrets"])),
        ("session reads wiki before consolidation", lambda: contains_all(session, ["read the current wiki before consolidating", "evolution/wiki/index.md"])),
        ("session deduplicates mechanisms", lambda: contains_all(session, ["update an existing mechanism", "create a new page only"])),
        ("session cannot mutate runtime skill", lambda: contains_all(session, ["must not edit `skill.md`", "stop before runtime mutation"])),
        ("evolver reads wiki index and impact history first", lambda: contains_all(evolve, ["evolution/wiki/index.md", "evolution/wiki/skill-impact.md", "first"])),
        ("evolver proposes one atomic target", lambda: contains_all(evolve, ["one atomic proposal", "one runtime skill/node/boundary"])),
        ("hypothesis frozen before candidate validation", lambda: contains_all(evolve, ["freeze the hypothesis", "before seeing candidate validation"])),
        ("benchmark frozen before runtime patch", lambda: contains_all(evolve, ["benchmark before applying the runtime patch", "positive case", "boundary/negative case"])),
        ("baseline runs before candidate", lambda: contains_all(evolve, ["run the baseline on the frozen benchmark", "exact commit/ref"])),
        ("baseline and candidate use same evidence", lambda: contains_all(evolve, ["same model, harness, repetitions, cases, and scorer"])),
        ("scorer fixes invalidate both arms", lambda: contains_all(evolve, ["invalidate both affected results", "rerun baseline and candidate from scratch"])),
        ("quality cannot regress", lambda: contains_all(evolve, ["not lower than baseline", "quality regression"])),
        ("indeterminate gate cannot accept", lambda: contains_all(evolve, ["gate is indeterminate", "revert the runtime candidate"])),
        ("rejection preserves wiki knowledge", lambda: contains_all(evolve, ["keep valid raw receipts/wiki knowledge", "rejected"])),
        ("impact tracker records accepted outcome", lambda: contains_all(evolve, ["evolution/wiki/skill-impact.md", "accepted"])),
        ("maintenance skills absent from automatic refs", lambda: "evolution/skills/session-to-wiki/SKILL.md" not in automatic_refs and "evolution/skills/evolve-skill/SKILL.md" not in automatic_refs),
        ("maintenance skills absent from automatic child names", lambda: "session-to-wiki" not in automatic_children and "evolve-skill" not in automatic_children),
        ("wiki index exists", lambda: (ROOT / "evolution/wiki/index.md").is_file()),
        ("wiki log exists", lambda: (ROOT / "evolution/wiki/log.md").is_file()),
        ("skill impact tracker exists", lambda: (ROOT / "evolution/wiki/skill-impact.md").is_file()),
        ("raw session receipt exists", lambda: (ROOT / "evolution/raw/sessions/2026-09-01-wikiskill-maintenance.md").is_file()),
    ]


def evaluate() -> dict[str, object]:
    rows = []
    for name, predicate in checks():
        try:
            passed = bool(predicate())
            error = None
        except Exception as exc:  # benchmark should report malformed inputs, not hide them
            passed = False
            error = f"{type(exc).__name__}: {exc}"
        rows.append({"check": name, "passed": passed, "error": error})
    passed = sum(row["passed"] is True for row in rows)
    total = len(rows)
    return {
        "schema_version": 1,
        "benchmark": "evolution-workflow-contract",
        "passed": passed,
        "total": total,
        "score": passed / total if total else 0.0,
        "checks": rows,
        "note": "Deterministic maintenance-contract benchmark; runtime coding quality is gated separately by tree validation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="require a perfect contract score")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate()
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if args.self_test and report["score"] != 1.0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
