from __future__ import annotations

import unittest
from pathlib import Path

from benchmarks import dependency_tree_validation as dependency
from benchmarks import retrieval_trace
from benchmarks import retrieval_validation as retrieval
from benchmarks import tree_validation as base


HERE = Path(__file__).resolve().parent


class RetrievalTopologyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.topology = base.load_topology(HERE / "tree_topology.json")
        cls.nodes = dependency._retrieval_nodes(cls.topology)

    def test_retrieval_tree_is_a_single_progressive_local_path(self) -> None:
        self.assertEqual(self.topology["retrieval_tree"]["root"], "retrieval")
        self.assertEqual(self.nodes["retrieval"]["children"], ["direct"])
        self.assertEqual(self.nodes["direct"]["children"], ["discovery"])
        self.assertEqual(self.nodes["discovery"]["children"], ["evidence"])
        self.assertEqual(self.nodes["evidence"]["children"], ["structural"])
        self.assertEqual(self.nodes["structural"]["children"], [])

    def test_canonical_trace_modes_match_declared_nodes(self) -> None:
        declared = {spec["trace_mode"] for spec in self.nodes.values()}
        self.assertEqual(declared, set(dependency.CANONICAL_RETRIEVAL_MODES))
        self.assertEqual(
            tuple(self.topology["retrieval_trace_modes"]),
            dependency.CANONICAL_RETRIEVAL_MODES,
        )

    def test_none_has_no_loaded_retrieval_policy_prefix(self) -> None:
        self.assertEqual(dependency.retrieval_reference_prefix(self.topology, "NONE"), [])
        self.assertEqual(retrieval.retrieval_declared_prefix(self.topology, "NONE"), [])

    def test_r2_requires_a_complete_loaded_reference_prefix(self) -> None:
        self.assertEqual(
            dependency.retrieval_reference_prefix(self.topology, "R2_EVIDENCE"),
            [
                "references/retrieval/skill.md",
                "references/retrieval/direct.md",
                "references/retrieval/discovery.md",
                "references/retrieval/evidence.md",
            ],
        )

    def test_declared_prefix_preserves_case_sensitive_skill_path(self) -> None:
        self.assertEqual(
            retrieval.retrieval_declared_prefix(self.topology, "R1_DISCOVERY"),
            [
                "references/retrieval/SKILL.md",
                "references/retrieval/direct.md",
                "references/retrieval/discovery.md",
            ],
        )

    def test_structural_is_the_only_leaf(self) -> None:
        leaves = {name for name, spec in self.nodes.items() if not spec["children"]}
        self.assertEqual(leaves, {"structural"})

    def test_provider_names_are_not_retrieval_nodes(self) -> None:
        self.assertTrue({"zg", "zvec-grep", "codebase-memory-mcp", "rtk"}.isdisjoint(self.nodes))


class CanonicalTraceParserTests(unittest.TestCase):
    def test_digit_bearing_retrieval_stage_is_parsed(self) -> None:
        trace = retrieval_trace.parse_trace(
            "TREE_TRACE path=core>debugging retrieval=R2_EVIDENCE manual=none "
            "refs=references/retrieval/SKILL.md,references/retrieval/direct.md"
        )
        self.assertEqual(trace["path"], ["core", "debugging"])
        self.assertEqual(trace["retrieval"], "R2_EVIDENCE")


class RetrievalReferenceObservationTests(unittest.TestCase):
    def test_observed_references_preserve_progressive_command_order(self) -> None:
        observed = retrieval_trace.observed_references(
            [
                "Get-Content references/retrieval/SKILL.md",
                "Get-Content references/retrieval/direct.md",
                "Get-Content references/retrieval/discovery.md",
            ]
        )
        self.assertEqual(
            observed,
            [
                "references/retrieval/skill.md",
                "references/retrieval/direct.md",
                "references/retrieval/discovery.md",
            ],
        )

    def test_repeated_reference_is_deduplicated_without_reordering(self) -> None:
        observed = retrieval_trace.observed_references(
            [
                "cat references/retrieval/SKILL.md references/retrieval/direct.md",
                "cat references/retrieval/SKILL.md",
            ]
        )
        self.assertEqual(
            observed,
            ["references/retrieval/skill.md", "references/retrieval/direct.md"],
        )


class MeasuredSetupGuardTests(unittest.TestCase):
    def test_forbidden_setup_commands_are_detected(self) -> None:
        for command in (
            "zg index --embedding local/potion-code-16m-v2",
            "codebase-memory-mcp cli index_repository --repo-path .",
            "rtk init -g --codex",
            "npm ci",
            "npm install",
        ):
            with self.subTest(command=command):
                self.assertRegex(command, dependency.SETUP_COMMAND_RE)

    def test_normal_provider_queries_and_requested_builds_are_not_setup(self) -> None:
        for command in (
            'zg query --human "where is login restored" --limit 5',
            "codebase-memory-mcp cli trace_path --project workspace --function-name run",
            "rtk git diff",
            "mvn -pl ai-example/ai-example-memory/ai-example-spring-ai-memory -am compile",
            "npm test -- src/lib/exportFilename.test.ts",
        ):
            with self.subTest(command=command):
                self.assertIsNone(dependency.SETUP_COMMAND_RE.search(command))


class ProviderUsageDetectionTests(unittest.TestCase):
    def test_absolute_provider_paths_are_detected(self) -> None:
        usage = retrieval._provider_usage(
            [
                "/usr/local/bin/zg query --human auth --limit 5",
                r"C:\tools\rtk.exe git diff",
                "/opt/cbm/codebase-memory-mcp cli list_projects",
            ]
        )
        self.assertEqual(
            usage,
            {"zvec-grep": True, "codebase-memory-mcp": True, "rtk": True},
        )


class RetrievalCeilingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.topology = base.load_topology(HERE / "tree_topology.json")

    def test_current_only_runs_adaptive_plus_all_five_ceilings(self) -> None:
        specs = retrieval.build_specs(1, current_only=True, selected_cases={"pp-known-contract"})
        self.assertEqual(
            {variant for _, variant, _ in specs},
            {"adaptive", *(f"retrieval-cap:{stage}" for stage in retrieval.STAGES)},
        )

    def test_provider_availability_is_owned_by_retrieval_stage(self) -> None:
        self.assertEqual(retrieval.allowed_provider_ids("R0_DIRECT"), {"rtk"})
        self.assertEqual(retrieval.allowed_provider_ids("R1_DISCOVERY"), {"rtk", "zvec-grep"})
        self.assertEqual(
            retrieval.allowed_provider_ids("R3_STRUCTURAL"),
            {"rtk", "zvec-grep", "codebase-memory-mcp"},
        )

    def test_deeper_provider_use_is_a_ceiling_violation(self) -> None:
        usage = {"rtk": False, "zvec-grep": True, "codebase-memory-mcp": False}
        self.assertTrue(retrieval.provider_ceiling_violation(usage, "R0_DIRECT"))
        self.assertFalse(retrieval.provider_ceiling_violation(usage, "R1_DISCOVERY"))

    def test_ceiling_instruction_uses_real_paths(self) -> None:
        instruction = retrieval.retrieval_ceiling_instruction(self.topology, "R0_DIRECT")
        self.assertIn("references/retrieval/SKILL.md", instruction)
        self.assertNotIn("references/retrieval/skill.md", instruction)


if __name__ == "__main__":
    unittest.main()
