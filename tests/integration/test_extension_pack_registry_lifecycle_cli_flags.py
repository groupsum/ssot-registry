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


def _document(document_id: str, number: int, slug: str, title: str) -> str:
    return (
        'schema_version: "0.4.0"\n'
        'kind: "spec"\n'
        f'id: "{document_id}"\n'
        f"number: {number}\n"
        f'slug: "{slug}"\n'
        f'title: "{title}"\n'
        'status: "draft"\n'
        'origin: "extension-pack"\n'
        "decision_date: null\n"
        "tags: []\n"
        f'summary: "{title}"\n'
        'spec_kind: "governance"\n'
        "adr_ids: []\n"
        "supersedes: []\n"
        "superseded_by: []\n"
        "status_notes: []\n"
        "references: []\n"
        "body: |-\n"
        f"  {title} body.\n"
    )


def _write_pack(
    root: Path,
    *,
    package_name: str = "cli_governance_pack",
    dist_name: str = "cli-governance-pack",
    version: str = "2.0.0",
    trusted: bool = True,
    entries: list[dict[str, object]] | None = None,
) -> str:
    package_root = root / package_name
    docs_root = package_root / "templates" / "specs"
    docs_root.mkdir(parents=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    _write_dist_info(root, dist_name=dist_name, version=version, top_level=package_name)
    manifest_rows = []
    for entry in entries or [{"id": "spc:5000", "number": 5000, "slug": "cli-pack-spec", "title": "CLI Pack Spec"}]:
        filename = f"SPEC-{int(entry['number']):04d}-{entry['slug']}.yaml"
        document_path = docs_root / filename
        document_path.write_text(
            _document(str(entry["id"]), int(entry["number"]), str(entry["slug"]), str(entry["title"])),
            encoding="utf-8",
            newline="\n",
        )
        manifest_rows.append(
            {
                "id": entry["id"],
                "number": entry["number"],
                "slug": entry["slug"],
                "title": entry["title"],
                "filename": filename,
                "target_path": f".ssot/specs/{filename}",
                "sha256": hashlib.sha256(document_path.read_bytes()).hexdigest(),
                "origin": "extension-pack",
                "reservation_owner": f"extension-pack:{dist_name}",
                "immutable": True,
                "minimum_schema_version": entry.get("minimum_schema_version", "0.4.0"),
                "introduced_in": version,
                "status": "draft",
                "supersedes": [],
                "superseded_by": [],
                "status_notes": [],
                "kind": "governance",
                "adr_ids": [],
            }
        )
    (docs_root / "manifest.json").write_text(json.dumps(manifest_rows), encoding="utf-8")
    (package_root / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "ssot_package_name": dist_name,
                "origin": {
                    "id": f"pack:{dist_name}",
                    "package_name": dist_name,
                    "import_name": package_name,
                    "kind": "governance-pack",
                    "title": "CLI Governance Pack",
                    "description": "CLI test governance pack.",
                },
                "compatibility": {"python": ">=3.10,<3.15", "ssot_registry_schema": ">=0.4.0", "ssot_pack_contract": ">=1.0.0"},
                "trust": {"trusted_by_default": trusted, "origin": "extension-pack", "reservation_owner": f"extension-pack:{dist_name}"},
                "documents": {"spec": {"manifest_path": "templates/specs/manifest.json"}},
            }
        ),
        encoding="utf-8",
    )
    return package_name


class ExtensionPackRegistryLifecycleCliFlagTests(unittest.TestCase):
    def test_pack_cli_flags_cover_all_manifest_resolved_reservations_pin_trust_yes_dry_run_and_no_sync(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            repo.mkdir()
            package_name = _write_pack(root)
            self.assertEqual(run_cli("init", str(repo), "--repo-id", "repo:pack-flags", "--repo-name", "pack-flags", "--version", "1.0.0").returncode, 0)

            inspect = _run_cli_with_package(root, "pack", "inspect", package_name, "--manifest")
            self.assertEqual(inspect.returncode, 0, inspect.stderr)
            self.assertIn("documents", json.loads(inspect.stdout))

            preflight = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name, "--all", "--manifest", "--resolved", "--pin", "2.0.0")
            self.assertEqual(preflight.returncode, 0, preflight.stderr)
            preflight_payload = json.loads(preflight.stdout)
            self.assertTrue(preflight_payload["passed"])
            self.assertEqual(preflight_payload["pin"], "2.0.0")
            resolved_id = preflight_payload["resolved"][0]["id"]
            resolved_path = preflight_payload["resolved"][0]["target_path"]
            self.assertTrue(resolved_id.startswith("spc:pack.cli-governance-pack.5000"))
            self.assertEqual(preflight_payload["resolved"][0]["source_document_id"], "spc:5000")

            dry_run = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--dry-run", "--resolved")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertFalse((repo / resolved_path).exists())

            no_sync = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--no-sync")
            self.assertEqual(no_sync.returncode, 0, no_sync.stderr)
            self.assertTrue(json.loads(no_sync.stdout)["no_sync"])
            self.assertFalse((repo / resolved_path).exists())

            sync = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--all", "--trust", "--yes", "--reservations")
            self.assertEqual(sync.returncode, 0, sync.stderr)
            sync_payload = json.loads(sync.stdout)
            self.assertTrue(sync_payload["trusted_operator_approved"])
            self.assertTrue(sync_payload["yes"])
            self.assertEqual(sync_payload["created"], [resolved_id])
            self.assertEqual(sync_payload["reservations"][0]["owner"], "extension-pack:cli-governance-pack")

    def test_pack_preflight_detects_conflicts_missing_artifacts_schema_pin_and_trust_failures(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            repo.mkdir()
            package_name = _write_pack(root, trusted=False)
            self.assertEqual(run_cli("init", str(repo), "--repo-id", "repo:pack-conflicts", "--repo-name", "pack-conflicts", "--version", "1.0.0").returncode, 0)

            trust = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name, "--trusted-only")
            self.assertEqual(trust.returncode, 1)
            self.assertIn("not trusted by default", trust.stdout)

            pin = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name, "--pin", "9.9.9")
            self.assertEqual(pin.returncode, 1)
            self.assertIn("pinned version", pin.stdout)

            manifest = root / package_name / "templates" / "specs" / "manifest.json"
            rows = json.loads(manifest.read_text(encoding="utf-8"))
            rows.append({**rows[0], "id": "spc:5001"})
            manifest.write_text(json.dumps(rows), encoding="utf-8")
            conflict = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name)
            self.assertEqual(conflict.returncode, 1)
            self.assertIn("duplicate spec manifest number", conflict.stdout)

            rows = json.loads(manifest.read_text(encoding="utf-8"))[:1]
            rows[0]["minimum_schema_version"] = "99.0.0"
            manifest.write_text(json.dumps(rows), encoding="utf-8")
            schema = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name)
            self.assertEqual(schema.returncode, 1)
            self.assertIn("requires schema", schema.stdout)

            rows[0]["minimum_schema_version"] = "0.4.0"
            rows[0]["filename"] = "missing.yaml"
            manifest.write_text(json.dumps(rows), encoding="utf-8")
            missing = _run_cli_with_package(root, "pack", "preflight", str(repo), package_name)
            self.assertEqual(missing.returncode, 1)
            self.assertIn("missing", missing.stdout.lower())

    def test_pack_prune_stale_removes_detached_extension_pack_documents_only_when_requested(self) -> None:
        with workspace_tempdir() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            repo.mkdir()
            package_name = _write_pack(root, entries=[{"id": "spc:5000", "number": 5000, "slug": "cli-pack-spec", "title": "CLI Pack Spec"}])
            self.assertEqual(run_cli("init", str(repo), "--repo-id", "repo:pack-prune", "--repo-name", "pack-prune", "--version", "1.0.0").returncode, 0)
            sync = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--resolved")
            self.assertEqual(sync.returncode, 0)
            sync_payload = json.loads(sync.stdout)
            synced_id = sync_payload["created"][0]
            synced_path = sync_payload["resolved"][0]["target_path"]

            package_root = root / package_name
            docs_root = package_root / "templates" / "specs"
            for child in docs_root.glob("SPEC-5000-*.yaml"):
                child.unlink()
            (docs_root / "manifest.json").write_text(json.dumps([]), encoding="utf-8")

            retained = _run_cli_with_package(root, "pack", "sync", str(repo), package_name)
            self.assertEqual(retained.returncode, 0, retained.stderr)
            self.assertEqual(json.loads(retained.stdout)["stale"], [synced_id])
            self.assertTrue((repo / synced_path).exists())

            pruned = _run_cli_with_package(root, "pack", "sync", str(repo), package_name, "--prune-stale")
            self.assertEqual(pruned.returncode, 0, pruned.stderr)
            self.assertEqual(json.loads(pruned.stdout)["pruned"], [synced_id])
            self.assertFalse((repo / synced_path).exists())


if __name__ == "__main__":
    unittest.main()
