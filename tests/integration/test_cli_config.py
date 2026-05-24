from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


def _automatic_config_text() -> str:
    return """[policy]
interactive = false
fail_closed = true

[commands.feature.create]
auto_scaffold_proof_graph = true

[sync]
docs = "automatic"
templates = "manual"
upstream_packages = "manual"

[validate]
after_registry_change = "automatic"

[generation]
mode = "automatic"
formats = ["json", "dot"]

[generation.targets]
graphs = true

[generation.graphs]
mode = "automatic"
formats = ["json", "dot"]
output_dir = ".ssot/graphs"
basename = "registry.graph"
"""


class ConfigCliTests(unittest.TestCase):
    def test_init_creates_default_repo_local_config_and_config_commands_work(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "config-repo"
            repo.mkdir()

            init = run_cli("init", str(repo), "--repo-id", "repo:config-repo", "--repo-name", "config-repo", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)
            init_payload = json.loads(init.stdout)
            config_path = repo / ".ssot" / "ssot.toml"
            self.assertEqual(init_payload["config_path"], config_path.as_posix())
            self.assertTrue(config_path.exists())

            show = run_cli("config", "show", str(repo))
            self.assertEqual(show.returncode, 0, show.stderr)
            show_payload = json.loads(show.stdout)
            self.assertTrue(show_payload["config"]["commands"]["feature"]["create"]["auto_scaffold_proof_graph"])
            self.assertEqual(show_payload["config"]["sync"]["docs"], "manual")
            self.assertFalse(show_payload["config"]["generation"]["targets"]["graphs"])

            validate = run_cli("config", "validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stderr)
            validate_payload = json.loads(validate.stdout)
            self.assertTrue(validate_payload["passed"], validate_payload)

    def test_mutation_fails_closed_when_repo_local_config_is_invalid(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "invalid-config-repo"
            repo.mkdir()

            init = run_cli(
                "init",
                str(repo),
                "--repo-id",
                "repo:invalid-config-repo",
                "--repo-name",
                "invalid-config-repo",
                "--version",
                "1.0.0",
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            config_path = repo / ".ssot" / "ssot.toml"
            config_path.write_text(
                _automatic_config_text().replace('docs = "automatic"', 'docs = "eager"'),
                encoding="utf-8",
                newline="\n",
            )

            result = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.invalid",
                "--title",
                "Invalid config feature",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("sync.docs must be one of", result.stdout)

    def test_feature_create_applies_automatic_sync_validate_and_graph_generation(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "automatic-config-repo"
            repo.mkdir()

            init = run_cli(
                "init",
                str(repo),
                "--repo-id",
                "repo:automatic-config-repo",
                "--repo-name",
                "automatic-config-repo",
                "--version",
                "1.0.0",
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            config_path = repo / ".ssot" / "ssot.toml"
            config_path.write_text(_automatic_config_text(), encoding="utf-8", newline="\n")

            result = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.automation",
                "--title",
                "Config automation feature",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["automation"]["validation"]["passed"], payload)
            self.assertIsNotNone(payload["automation"]["sync"], payload)
            self.assertIn("adr", payload["automation"]["sync"])
            self.assertIn("spec", payload["automation"]["sync"])

            graph_outputs = payload["automation"]["generation"]["graphs"]
            self.assertEqual(
                graph_outputs,
                [
                    (repo / ".ssot" / "graphs" / "registry.graph.json").as_posix(),
                    (repo / ".ssot" / "graphs" / "registry.graph.dot").as_posix(),
                ],
            )
            for output_path in graph_outputs:
                self.assertTrue(Path(output_path).exists(), output_path)

    def test_feature_create_uses_repo_local_scaffold_default_and_cli_override_precedence(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "feature-create-config-repo"
            repo.mkdir()

            init = run_cli(
                "init",
                str(repo),
                "--repo-id",
                "repo:feature-create-config-repo",
                "--repo-name",
                "feature-create-config-repo",
                "--version",
                "1.0.0",
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            config_path = repo / ".ssot" / "ssot.toml"
            config_path.write_text(
                _automatic_config_text().replace("auto_scaffold_proof_graph = true", "auto_scaffold_proof_graph = false"),
                encoding="utf-8",
                newline="\n",
            )

            disabled = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.default-off",
                "--title",
                "Config default off feature",
                "--description",
                "should fail closed without scaffold",
                "--implementation-status",
                "partial",
                "--horizon",
                "current",
                "--claim-tier",
                "T2",
            )
            self.assertEqual(disabled.returncode, 1)
            self.assertIn("has no linked claims", disabled.stdout)

            explicit_on = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.explicit-on",
                "--title",
                "Config explicit on feature",
                "--description",
                "explicit CLI enable overrides config disable",
                "--implementation-status",
                "partial",
                "--horizon",
                "current",
                "--claim-tier",
                "T2",
                "--auto-scaffold-proof-graph",
            )
            self.assertEqual(explicit_on.returncode, 0, explicit_on.stderr)
            self.assertIn("\"scaffolded\"", explicit_on.stdout)

            config_path.write_text(_automatic_config_text(), encoding="utf-8", newline="\n")
            explicit_off = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.explicit-off",
                "--title",
                "Config explicit off feature",
                "--description",
                "explicit CLI disable overrides config enable",
                "--implementation-status",
                "partial",
                "--horizon",
                "current",
                "--claim-tier",
                "T2",
                "--no-auto-scaffold-proof-graph",
            )
            self.assertEqual(explicit_off.returncode, 1)
            self.assertIn("has no linked claims", explicit_off.stdout)


if __name__ == "__main__":
    unittest.main()
