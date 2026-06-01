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


def _write_shared_id_pack(root: Path, *, package_name: str, dist_name: str, pack_id: str) -> str:
    package_root = root / package_name
    adr_root = package_root / "templates" / "adr"
    spec_root = package_root / "templates" / "specs"
    adr_root.mkdir(parents=True)
    spec_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    _write_dist_info(root, dist_name=dist_name, version="2.0.0", top_level=package_name)

    adr_doc = (
        'schema_version: "0.4.0"\n'
        'kind: "adr"\n'
        'id: "adr:0001"\n'
        "number: 1\n"
        'slug: "shared-adr"\n'
        f'title: "{dist_name} Shared ADR"\n'
        'status: "accepted"\n'
        'origin: "extension-pack"\n'
        "decision_date: null\n"
        "tags: []\n"
        f'summary: "{dist_name} Shared ADR"\n'
        "supersedes: []\n"
        "superseded_by: []\n"
        "status_notes: []\n"
        "references: []\n"
        "body: |-\n"
        f"  {dist_name} ADR body.\n"
    )
    adr_path = adr_root / "ADR-0001-shared-adr.yaml"
    adr_path.write_text(adr_doc, encoding="utf-8", newline="\n")
    spec_doc = (
        'schema_version: "0.4.0"\n'
        'kind: "spec"\n'
        'id: "spc:0001"\n'
        "number: 1\n"
        'slug: "shared-spec"\n'
        f'title: "{dist_name} Shared SPEC"\n'
        'status: "draft"\n'
        'origin: "extension-pack"\n'
        "decision_date: null\n"
        "tags: []\n"
        f'summary: "{dist_name} Shared SPEC"\n'
        'spec_kind: "governance"\n'
        'adr_ids: ["adr:0001"]\n'
        "supersedes: []\n"
        "superseded_by: []\n"
        "status_notes: []\n"
        "references: []\n"
        "body: |-\n"
        f"  {dist_name} SPEC body.\n"
    )
    spec_path = spec_root / "SPEC-0001-shared-spec.yaml"
    spec_path.write_text(spec_doc, encoding="utf-8", newline="\n")
    (adr_root / "manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "adr:0001",
                    "number": 1,
                    "slug": "shared-adr",
                    "title": f"{dist_name} Shared ADR",
                    "filename": adr_path.name,
                    "target_path": f".ssot/adr/{adr_path.name}",
                    "sha256": hashlib.sha256(adr_path.read_bytes()).hexdigest(),
                    "origin": "extension-pack",
                    "reservation_owner": f"extension-pack:{dist_name}",
                    "immutable": True,
                    "minimum_schema_version": "0.4.0",
                    "introduced_in": "2.0.0",
                    "status": "accepted",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    (spec_root / "manifest.json").write_text(
        json.dumps(
            [
                {
                    "id": "spc:0001",
                    "number": 1,
                    "slug": "shared-spec",
                    "title": f"{dist_name} Shared SPEC",
                    "filename": spec_path.name,
                    "target_path": f".ssot/specs/{spec_path.name}",
                    "sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest(),
                    "origin": "extension-pack",
                    "reservation_owner": f"extension-pack:{dist_name}",
                    "immutable": True,
                    "minimum_schema_version": "0.4.0",
                    "introduced_in": "2.0.0",
                    "status": "draft",
                    "supersedes": [],
                    "superseded_by": [],
                    "status_notes": [],
                    "kind": "governance",
                    "adr_ids": ["adr:0001"],
                }
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "ssot_package_name": dist_name,
                "origin": {
                    "id": pack_id,
                    "package_name": dist_name,
                    "import_name": package_name,
                    "kind": "governance-pack",
                    "title": f"{dist_name} Pack",
                    "description": "Shared-id test governance pack.",
                },
                "compatibility": {
                    "python": ">=3.10,<3.15",
                    "ssot_registry_schema": ">=0.4.0",
                    "ssot_pack_contract": ">=1.0.0",
                },
                "trust": {
                    "trusted_by_default": True,
                    "origin": "extension-pack",
                    "reservation_owner": f"extension-pack:{dist_name}",
                },
                "documents": {
                    "adr": {"manifest_path": "templates/adr/manifest.json"},
                    "spec": {"manifest_path": "templates/specs/manifest.json"},
                },
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
            dry_run_payload = json.loads(dry_run.stdout)
            created_id = dry_run_payload["created"][0]
            self.assertTrue(created_id.startswith("spc:pack.cli-governance.5000"))
            self.assertFalse((repo / ".ssot" / "specs" / "SPEC-5000-cli-pack-spec.yaml").exists())

            sync = _run_cli_with_package(root, "pack", "sync", str(repo), package_name)
            self.assertEqual(sync.returncode, 0, sync.stderr)
            self.assertEqual(json.loads(sync.stdout)["created"], [created_id])
            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
            spec = next(row for row in registry["specs"] if row["id"] == created_id)
            self.assertEqual(spec["source_pack_id"], "pack:cli-governance")
            self.assertEqual(spec["source_package_name"], "cli-governance-pack")
            self.assertEqual(spec["source_document_kind"], "spec")
            self.assertEqual(spec["source_document_id"], "spc:5000")
            self.assertNotIn("raw_manifest_row", spec)
            self.assertNotIn("source_minimum_schema_version", spec)
            self.assertNotIn("minimum_schema_version", spec)
            self.assertTrue((repo / spec["path"]).exists())

            validate = _run_cli_with_package(root, "validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stdout)
            self.assertTrue(json.loads(validate.stdout)["passed"])

    def test_shared_pack_document_ids_materialize_per_pack_and_features_link_to_pack_spec(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            repo.mkdir()
            alpha = _write_shared_id_pack(root, package_name="alpha_governance_pack", dist_name="alpha-governance-pack", pack_id="pack:alpha")
            beta = _write_shared_id_pack(root, package_name="beta_governance_pack", dist_name="beta-governance-pack", pack_id="pack:beta")
            init = run_cli("init", str(repo), "--repo-id", "repo:pack-shared-ids", "--repo-name", "pack-shared-ids", "--version", "1.0.0")
            self.assertEqual(init.returncode, 0, init.stderr)

            alpha_sync = _run_cli_with_package(root, "pack", "sync", str(repo), alpha, "--all")
            self.assertEqual(alpha_sync.returncode, 0, alpha_sync.stderr)
            beta_sync = _run_cli_with_package(root, "pack", "sync", str(repo), beta, "--all")
            self.assertEqual(beta_sync.returncode, 0, beta_sync.stderr)

            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
            source_adrs = {row["source_pack_id"]: row for row in registry["adrs"] if row.get("source_document_id") == "adr:0001"}
            source_specs = {row["source_pack_id"]: row for row in registry["specs"] if row.get("source_document_id") == "spc:0001"}
            self.assertEqual(set(source_adrs), {"pack:alpha", "pack:beta"})
            self.assertEqual(set(source_specs), {"pack:alpha", "pack:beta"})
            self.assertNotEqual(source_specs["pack:alpha"]["id"], source_specs["pack:beta"]["id"])
            self.assertEqual(source_specs["pack:alpha"]["adr_ids"], [source_adrs["pack:alpha"]["id"]])
            self.assertEqual(source_specs["pack:beta"]["adr_ids"], [source_adrs["pack:beta"]["id"]])

            feature = _run_cli_with_package(
                root,
                "feature",
                "create",
                str(repo),
                "--id",
                "feat:pack.alpha.spec.consumer",
                "--title",
                "Alpha pack SPEC consumer",
                "--description",
                "Regression feature that references a materialized pack SPEC.",
                "--origin",
                "repo-local",
                "--horizon",
                "backlog",
                "--spec-ids",
                source_specs["pack:alpha"]["id"],
            )
            self.assertEqual(feature.returncode, 0, feature.stderr)
            validate = _run_cli_with_package(root, "validate", str(repo))
            self.assertEqual(validate.returncode, 0, validate.stdout)
            registry = json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))
            feature_row = next(row for row in registry["features"] if row["id"] == "feat:pack.alpha.spec.consumer")
            self.assertEqual(feature_row["spec_ids"], [source_specs["pack:alpha"]["id"]])


if __name__ == "__main__":
    unittest.main()
