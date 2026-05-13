from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir


def _automatic_config_text() -> str:
    return """[policy]
interactive = false
fail_closed = true

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


def _init_repo(repo: Path) -> None:
    result = run_cli(
        "init",
        str(repo),
        "--repo-id",
        f"repo:{repo.name}",
        "--repo-name",
        repo.name,
        "--version",
        "1.0.0",
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)


class RepoLocalConfigurationAndAutomationTests(unittest.TestCase):
    def test_repo_local_toml_file_is_created_during_init(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "config-file-repo"
            repo.mkdir()

            result = run_cli(
                "init",
                str(repo),
                "--repo-id",
                "repo:config-file-repo",
                "--repo-name",
                "config-file-repo",
                "--version",
                "1.0.0",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)

            config_path = repo / ".ssot" / "ssot.toml"
            self.assertEqual(payload["config_path"], config_path.as_posix())
            self.assertTrue(config_path.exists())

    def test_config_surface_show_and_validate_repo_local_config(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "config-surface-repo"
            repo.mkdir()
            _init_repo(repo)

            show = run_cli("config", "show", str(repo))
            self.assertEqual(show.returncode, 0, show.stderr)
            show_payload = json.loads(show.stdout)
            self.assertEqual(show_payload["config"]["sync"]["docs"], "manual")
            self.assertFalse(show_payload["config"]["generation"]["targets"]["graphs"])

            validate = run_cli("config", "validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stderr)
            validate_payload = json.loads(validate.stdout)
            self.assertTrue(validate_payload["passed"], validate_payload)

    def test_invalid_repo_local_config_fails_closed_before_mutation(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "invalid-config-repo"
            repo.mkdir()
            _init_repo(repo)

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

    def test_auto_sync_docs_runs_after_registry_change(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "auto-sync-repo"
            repo.mkdir()
            _init_repo(repo)

            config_path = repo / ".ssot" / "ssot.toml"
            config_path.write_text(_automatic_config_text(), encoding="utf-8", newline="\n")

            result = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.auto-sync",
                "--title",
                "Config auto-sync feature",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)

            sync_payload = payload["automation"]["sync"]
            self.assertIsNotNone(sync_payload, payload)
            self.assertIn("adr", sync_payload)
            self.assertIn("spec", sync_payload)

    def test_auto_validate_and_graph_generation_run_after_registry_change(self) -> None:
        with workspace_tempdir() as temp_dir:
            repo = Path(temp_dir) / "auto-validate-repo"
            repo.mkdir()
            _init_repo(repo)

            config_path = repo / ".ssot" / "ssot.toml"
            config_path.write_text(_automatic_config_text(), encoding="utf-8", newline="\n")

            result = run_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:config.auto-validate",
                "--title",
                "Config auto-validate feature",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)

            self.assertTrue(payload["automation"]["validation"]["passed"], payload)
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


if __name__ == "__main__":
    unittest.main()
