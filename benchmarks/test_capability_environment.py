from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from benchmarks import capability_environment as cap


HERE = Path(__file__).resolve().parent


class CapabilityManifestTests(unittest.TestCase):
    def test_checked_in_manifest_is_fail_closed_and_unmeasured(self) -> None:
        manifest = cap.load_manifest(HERE / "capability_manifest.json")
        self.assertEqual(
            set(manifest["required_roles"]),
            {"ranked_retrieval", "graph_retrieval", "execution_output"},
        )
        self.assertFalse(manifest["measurement_contract"]["setup_included_in_comparison"])
        self.assertFalse(manifest["measurement_contract"]["setup_token_estimate"])
        self.assertEqual(
            manifest["measurement_contract"]["measured_phase_starts"],
            "after_workspace_prepare",
        )

    def test_manifest_rejects_missing_required_provider_role(self) -> None:
        manifest = json.loads((HERE / "capability_manifest.json").read_text(encoding="utf-8"))
        manifest["providers"] = manifest["providers"][:-1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(cap.CapabilityManifestError):
                cap.load_manifest(path)

    def test_manifest_rejects_setup_entering_comparison(self) -> None:
        manifest = json.loads((HERE / "capability_manifest.json").read_text(encoding="utf-8"))
        manifest["measurement_contract"]["setup_included_in_comparison"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(cap.CapabilityManifestError):
                cap.load_manifest(path)

    def test_manifest_rejects_invalid_provider_version_regex(self) -> None:
        manifest = json.loads((HERE / "capability_manifest.json").read_text(encoding="utf-8"))
        manifest["providers"][0]["version_regex"] = "["
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(cap.CapabilityManifestError):
                cap.load_manifest(path)


class CapabilityPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = cap.load_manifest(HERE / "capability_manifest.json")

    def test_missing_binary_fails_before_benchmark(self) -> None:
        with self.assertRaisesRegex(cap.MissingCapabilityError, "zg"):
            cap.preflight(
                self.manifest,
                which=lambda binary: None if binary == "zg" else f"/fake/bin/{binary}",
            )

    @staticmethod
    def _probe_output(command) -> str:
        binary = Path(command[0]).name
        return {
            "zg": "zg 0.2.0",
            "codebase-memory-mcp": "codebase-memory-mcp 0.10.8",
            "rtk": "rtk 0.47.0",
        }[binary]

    def test_all_providers_are_probed(self) -> None:
        commands: list[list[str]] = []

        def runner(command, cwd, env, timeout):
            commands.append(list(command))
            return subprocess.CompletedProcess(command, 0, stdout=self._probe_output(command), stderr="")

        report = cap.preflight(
            self.manifest,
            runner=runner,
            which=lambda binary: f"/fake/bin/{binary}",
        )
        self.assertFalse(report["included_in_comparison"])
        self.assertEqual(len(report["provider_probes"]), 3)
        self.assertEqual({item["role"] for item in report["provider_probes"]}, set(self.manifest["required_roles"]))
        self.assertTrue(all(command[0].startswith("/fake/bin/") for command in commands))
        self.assertTrue(all(item["observed_version_output"] for item in report["provider_probes"]))
        self.assertFalse(cap.contains_token_key(report))

    def test_unapproved_provider_version_fails_before_benchmark(self) -> None:
        def runner(command, cwd, env, timeout):
            output = self._probe_output(command)
            if Path(command[0]).name == "zg":
                output = "zg 0.1.0"
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

        with self.assertRaisesRegex(cap.MissingCapabilityError, "unapproved version"):
            cap.preflight(
                self.manifest,
                runner=runner,
                which=lambda binary: f"/fake/bin/{binary}",
            )


class WorkspaceSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = cap.load_manifest(HERE / "capability_manifest.json")

    @staticmethod
    def _preflight(manifest):
        return {
            "manifest_sha256": cap.manifest_fingerprint(manifest),
            "resolved_executables": {
                "zg": "/fake/zg",
                "codebase-memory-mcp": "/fake/codebase-memory-mcp",
                "rtk": "/fake/rtk",
                "git": "/fake/git",
                "node": "/fake/node",
                "npm": "/fake/npm",
                "java": "/fake/java",
                "mvn": "/fake/mvn",
            },
        }

    def test_setup_is_separate_clean_and_has_no_token_field(self) -> None:
        commands: list[list[str]] = []
        observed_cache_dirs: list[str] = []

        def runner(command, cwd, env, timeout):
            commands.append(list(command))
            observed_cache_dirs.append(env.get("CBM_CACHE_DIR", ""))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cell" / "workspace"
            shared_cbm_cache = Path(directory) / "shared-cbm-cache"
            (workspace / ".git" / "info").mkdir(parents=True)
            report = cap.prepare_workspace(
                workspace,
                "personal-progress",
                self.manifest,
                self._preflight(self.manifest),
                runner=runner,
                base_env={"PRACTICAL_BENCHMARK_CBM_CACHE_DIR": str(shared_cbm_cache)},
            )
            self.assertFalse(report["included_in_comparison"])
            self.assertTrue(report["measurement_begins_after_report"])
            self.assertEqual(len(report["provider_setup"]), 3)
            self.assertEqual(len(report["provider_warmup"]), 2)
            self.assertEqual(report["repository_warmup"], [])
            self.assertFalse(cap.contains_token_key(report))
            self.assertTrue(all(observed_cache_dirs))
            self.assertEqual({str(shared_cbm_cache.resolve())}, set(observed_cache_dirs))
            self.assertEqual(report["cbm_cache_cohort"], str(shared_cbm_cache.resolve()))
            exclude = (workspace / ".git" / "info" / "exclude").read_text(encoding="utf-8")
            self.assertIn(".zvec-grep/", exclude)
            self.assertTrue(any(command[:2] == ["/fake/zg", "index"] for command in commands))
            self.assertTrue(any(command[:2] == ["/fake/zg", "query"] for command in commands))

    def test_repository_warmup_is_executed_before_measurement(self) -> None:
        commands: list[list[str]] = []

        def runner(command, cwd, env, timeout):
            commands.append(list(command))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cell" / "workspace"
            (workspace / ".git" / "info").mkdir(parents=True)
            report = cap.prepare_workspace(
                workspace,
                "cover-atelier",
                self.manifest,
                self._preflight(self.manifest),
                runner=runner,
                base_env={},
            )
            self.assertEqual(len(report["repository_warmup"]), 2)
            self.assertIn(["/fake/npm", "ci", "--no-audit", "--no-fund"], commands)
            self.assertFalse(cap.contains_token_key(report))

    def test_default_environment_does_not_create_per_cell_cbm_cohorts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cell" / "workspace"
            additions = cap.workspace_environment(workspace, {})
            self.assertNotIn("CBM_CACHE_DIR", additions)
            self.assertIn("PRACTICAL_CAPABILITY_STATE", additions)

    def test_failed_provider_setup_aborts(self) -> None:
        def runner(command, cwd, env, timeout):
            if command[0] == "/fake/codebase-memory-mcp":
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="index failed")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cell" / "workspace"
            (workspace / ".git" / "info").mkdir(parents=True)
            with self.assertRaisesRegex(cap.CapabilitySetupError, "index failed"):
                cap.prepare_workspace(
                    workspace,
                    "personal-progress",
                    self.manifest,
                    self._preflight(self.manifest),
                    runner=runner,
                    base_env={},
                )

    def test_stale_preflight_receipt_is_rejected(self) -> None:
        stale = copy.deepcopy(self._preflight(self.manifest))
        stale["manifest_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "cell" / "workspace"
            (workspace / ".git" / "info").mkdir(parents=True)
            with self.assertRaisesRegex(cap.CapabilitySetupError, "does not match"):
                cap.prepare_workspace(workspace, "personal-progress", self.manifest, stale)


if __name__ == "__main__":
    unittest.main()
