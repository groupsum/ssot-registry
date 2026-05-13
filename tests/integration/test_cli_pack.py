from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import (
    CLI_SRC_ROOT,
    CODEGEN_SRC_ROOT,
    CONFORMANCE_SRC_ROOT,
    CONTRACTS_SRC_ROOT,
    CORE_SRC_ROOT,
    PACK_CONTRACTS_SRC_ROOT,
    TUI_SRC_ROOT,
    VIEWS_SRC_ROOT,
    run_cli,
    workspace_tempdir,
)


def _write_dist_info(root: Path, *, dist_name: str, version: str, top_level: str) -> None:
    dist_info = root / f"{dist_name.replace('-', '_')}-{version}.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {dist_name}\nVersion: {version}\n",
        encoding="utf-8",
    )
    (dist_info / "top_level.txt").write_text(f"{top_level}\n", encoding="utf-8")


def _run_cli_with_package(package_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath_parts = [
        str(CORE_SRC_ROOT),
        str(CODEGEN_SRC_ROOT),
        str(VIEWS_SRC_ROOT),
        str(CONTRACTS_SRC_ROOT),
        str(PACK_CONTRACTS_SRC_ROOT),
        str(CLI_SRC_ROOT),
        str(TUI_SRC_ROOT),
        str(CONFORMANCE_SRC_ROOT),
        str(package_root),
    ]
    existing = env.get("PYTHONPATH")
    if existing:
        pythonpath_parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    return subprocess.run(
        [sys.executable, "-m", "ssot_registry", *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _write_pack(root: Path) -> str:
    package_name = "cli_governance_pack"
    package_root = root / package_name
    docs_root = package_root / "templates" / "specs"
    docs_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    _write_dist_info(root, dist_name="cli-governance-pack", version="2.0.0", top_level=package_name)
    document = (
        'schema_version: "0.4.0"\n'
        'kind: "spec"\n'
        'id: "spc:5000"\n'
        "number: 5000\n"
        'slug: "cli-pack-spec"\n'
        'title: "CLI Pack Spec"\n'
        'status: "draft"\n'
        'origin: "extension-pack"\n'
        "decision_date: null\n"
        "tags: []\n"
        'summary: "CLI Pack Spec"\n'
        'spec_kind: "governance"\n'
        "adr_ids: []\n"
        "supersedes: []\n"
        "superseded_by: []\n"
        "status_notes: []\n"
        "references: []\n"
        "body: |-\n"
        "  CLI packaged spec.\n"
    )
    document_path = docs_root / "SPEC-5000-cli-pack-spec.yaml"
    document_path.write_text(document, encoding="utf-8", newline="\n")
    sha256 = hashlib.sha256(document_path.read_bytes()).hexdigest()
    (docs_root / "manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "spc:5000",
                    "number": 5000,
                    "slug": "cli-pack-spec",
                    "title": "CLI Pack Spec",
                    "filename": "SPEC-5000-cli-pack-spec.yaml",
                    "target_path": ".ssot/specs/SPEC-5000-cli-pack-spec.yaml",
                    "sha256": sha256,
                    "origin": "extension-pack",
                    "reservation_owner": "extension-pack:cli-governance-pack",
                    "immutable": True,
                    "minimum_schema_version": "0.4.0",
                    "introduced_in": "2.0.0",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                    "kind": "governance",
                    "adr_ids": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "ssot_package_name": "cli-governance-pack",
                "origin": {
                    "id": "pack:cli-governance",
                    "package_name": "cli-governance-pack",
                    "import_name": package_name,
                    "kind": "governance-pack",
                    "title": "CLI Governance Pack",
                    "description": "CLI test governance pack.",
                },
                "compatibility": {
                    "python": ">=3.10,<3.15",
                    "ssot_registry_schema": ">=0.4.0",
                    "ssot_pack_contract": ">=1.0.0",
                },
                "trust": {
                    "trusted_by_default": True,
                    "origin": "extension-pack",
                    "reservation_owner": "extension-pack:cli-governance-pack",
                },
                "documents": {"spec": {"manifest_path": "templates/specs/manifest.json"}},
            }
        ),
        encoding="utf-8",
    )
    return package_name


class CliPackTests(unittest.TestCase):
    def test_pack_inspect_preflight_and_sync(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            repo.mkdir()
            package_name = _write_pack(root)
            init = run_cli("init", str(repo), "--repo-id", "repo:pack-cli", "--repo-name", "pack-cli", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            inspect = _run_cli_with_package(root, "pack", "inspect", package_name)
            self.assertEqual(inspect.returncode, 0, inspect.stderr)
            inspect_payload = json.loads(inspect.stdout)
            self.assertEqual(inspect_payload["metadata"]["origin"]["package_name"], "cli-governance-pack")
            self.assertEqual(inspect_payload["document_counts"], {"spec": 1})

            preflight = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name, "--kind", "spec")
            self.assertEqual(preflight.returncode, 0, preflight.stderr)
            self.assertTrue(json.loads(preflight.stdout)["passed"])

            dry_run = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertEqual(json.loads(dry_run.stdout)["created"], ["spc:5000"])
            self.assertFalse((repo / ".ssot" / "specs" / "SPEC-5000-cli-pack-spec.yaml").exists())

            sync = _run_cli_with_package(root, "pack", "sync", str(repo), package_name)
            self.assertEqual(sync.returncode, 0, sync.stderr)
            self.assertEqual(json.loads(sync.stdout)["created"], ["spc:5000"])
            self.assertTrue((repo / ".ssot" / "specs" / "SPEC-5000-cli-pack-spec.yaml").exists())

            validate = _run_cli_with_package(root, "validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stdout)
            self.assertTrue(json.loads(validate.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
