from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = REPO_ROOT / ".tmp_test_runs"
REPORT_ROOT = REPO_ROOT / "reports" / "benchmarks"
FIXTURE_REPO = REPO_ROOT / "tests" / "fixtures" / "repo_valid"

SSOT_PYTHONPATH_PARTS = [
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-codegen" / "src",
    REPO_ROOT / "pkgs" / "ssot-views" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-cli" / "src",
    REPO_ROOT / "pkgs" / "ssot-tui" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
]
TIGRSTORE_PYTHONPATH_PARTS = [
    Path(r"E:\swarmauri_github\tigrstore\tigrstore\pkgs\tigrstore\src"),
    Path(r"E:\swarmauri_github\tigrstore\tigrstore\pkgs\tigrstore-cli\src"),
    Path(r"E:\swarmauri_github\tigrstore\tigrstore\pkgs\tigrstore-testkit\src"),
    Path(r"E:\swarmauri_github\tigrstore\tigrstore\pkgs\tigrbl-engine-tigrstore\src"),
]

CURRENT_JSON_FEATURE = {
    "implementation_status": "partial",
    "title_prefix": "Bench feature",
}

FILELSM_SELECTIONS = {
    "data_model": "key-value",
    "backend": "local-filesystem",
    "storage_object": "simple-sstable",
    "internal": "flat-records",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "stcs",
}

BLOCKLSM_SELECTIONS = {
    "data_model": "key-value",
    "backend": "local-filesystem",
    "storage_object": "block-sstable",
    "internal": "block-layout",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "stcs",
}

BLOCKLSM_SEGMENTED_WAL_SEGMENT_GC_SELECTIONS = {
    "data_model": "key-value",
    "backend": "local-filesystem",
    "storage_object": "block-sstable",
    "internal": "block-layout",
    "log": "segmented-wal",
    "integrity": "crc32c",
    "compaction_gc": "segment-gc",
}

DOCUMENT_OBJECT_SIMPLE_SELECTIONS = {
    "data_model": "document-object",
    "backend": "local-filesystem",
    "storage_object": "simple-sstable",
    "internal": "flat-records",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "stcs",
}

DOCUMENT_OBJECT_BLOCK_SELECTIONS = {
    "data_model": "document-object",
    "backend": "local-filesystem",
    "storage_object": "block-sstable",
    "internal": "metadata-blocks",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "stcs",
}

METADATA_CONFIG_SIMPLE_SELECTIONS = {
    "data_model": "metadata-config",
    "backend": "local-filesystem",
    "storage_object": "simple-sstable",
    "internal": "flat-records",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "retention-gc",
}

METADATA_CONFIG_BLOCK_SELECTIONS = {
    "data_model": "metadata-config",
    "backend": "local-filesystem",
    "storage_object": "block-sstable",
    "internal": "metadata-blocks",
    "log": "wal",
    "integrity": "crc32c",
    "compaction_gc": "retention-gc",
}

DOCUMENT_OBJECT_SIMPLE_PREFIX_SEQUENCE = {
    "name": "document-object-simple-prefix-seqlatest",
    "selections": DOCUMENT_OBJECT_SIMPLE_SELECTIONS,
    "search": "prefix-search",
    "versioning": "sequence-latest",
}

DOCUMENT_OBJECT_BLOCK_SECONDARY_SEQUENCE = {
    "name": "document-object-block-secondary-seqlatest",
    "selections": DOCUMENT_OBJECT_BLOCK_SELECTIONS,
    "search": "secondary-search",
    "versioning": "sequence-latest",
}

METADATA_CONFIG_SIMPLE_PREFIX_MVCC = {
    "name": "metadata-config-simple-prefix-mvcc",
    "selections": METADATA_CONFIG_SIMPLE_SELECTIONS,
    "search": "prefix-search",
    "versioning": "mvcc",
}

METADATA_CONFIG_BLOCK_SECONDARY_MVCC = {
    "name": "metadata-config-block-secondary-mvcc",
    "selections": METADATA_CONFIG_BLOCK_SELECTIONS,
    "search": "secondary-search",
    "versioning": "mvcc",
}

METADATA_CONFIG_BLOCK_WAL_SEGMENT_GC = {
    "name": "metadata-config-block-wal-segmentgc",
    "selections": {
        "data_model": "metadata-config",
        "backend": "local-filesystem",
        "storage_object": "block-sstable",
        "internal": "metadata-blocks",
        "log": "wal",
        "integrity": "crc32c",
        "compaction_gc": "segment-gc",
    },
    "search": "secondary-search",
    "versioning": "sequence-latest",
}


def _pythonpath(parts: list[Path]) -> str:
    existing = os.environ.get("PYTHONPATH")
    values = [str(part) for part in parts]
    if existing:
        values.append(existing)
    return os.pathsep.join(values)


def _run_ssot_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = _pythonpath(SSOT_PYTHONPATH_PARTS)
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from ssot_cli.main import main; raise SystemExit(main())",
            *args,
        ],
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _create_temp_repo() -> Path:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(dir=TEMP_ROOT))
    repo = temp_dir / "repo"
    shutil.copytree(FIXTURE_REPO, repo)
    return repo


@dataclass
class PhaseResult:
    phase: str
    total_seconds: float
    operations: int

    @property
    def ms_per_op(self) -> float:
        if self.operations == 0:
            return 0.0
        return (self.total_seconds * 1000.0) / self.operations


@dataclass(frozen=True)
class FootprintResult:
    file_count: int
    cumulative_bytes: int


@dataclass(frozen=True)
class WorkloadPlan:
    total_instances: int
    feature_count: int
    claim_count: int
    test_count: int
    evidence_count: int


def _directory_footprint(root: Path) -> FootprintResult:
    file_count = 0
    cumulative_bytes = 0
    if not root.exists():
        return FootprintResult(0, 0)
    for path in root.rglob("*"):
        if path.is_file():
            file_count += 1
            cumulative_bytes += path.stat().st_size
    return FootprintResult(file_count, cumulative_bytes)


def _plan_workload(total_instances: int) -> WorkloadPlan:
    if total_instances < 4:
        raise ValueError("total_instances must be at least 4 so feature, claim, test, and evidence families are all used")
    base = total_instances // 4
    remainder = total_instances % 4
    feature_count = base + (1 if remainder >= 1 else 0)
    claim_count = base + (1 if remainder >= 2 else 0)
    test_count = base + (1 if remainder >= 3 else 0)
    evidence_count = base
    return WorkloadPlan(
        total_instances=total_instances,
        feature_count=feature_count,
        claim_count=claim_count,
        test_count=test_count,
        evidence_count=evidence_count,
    )


class SsotCliRunner:
    name = "ssot-cli-current-json"

    def run_once(self, workload: WorkloadPlan) -> tuple[list[PhaseResult], FootprintResult]:
        repo = _create_temp_repo()
        try:
            feature_ids = [f"feat:bench.{index:04d}" for index in range(workload.feature_count)]
            results = [
                self._create(repo, feature_ids),
                self._read(repo, feature_ids),
                self._update(repo, feature_ids),
                self._list(repo),
            ]
            claim_ids, test_ids = self._prepare_graph(repo, workload, feature_ids)
            results.extend(
                [
                    self._traverse_children(repo, feature_ids),
                    self._traverse_parents(repo, test_ids),
                    self._search(repo),
                ]
            )
            return results, _directory_footprint(repo / ".ssot")
        finally:
            shutil.rmtree(repo.parent, ignore_errors=True)

    def _create(self, repo: Path, ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            result = _run_ssot_cli(
                "feature",
                "create",
                str(repo),
                "--id",
                entity_id,
                "--title",
                f"{CURRENT_JSON_FEATURE['title_prefix']} {entity_id}",
                "--implementation-status",
                CURRENT_JSON_FEATURE["implementation_status"],
            )
            if result.returncode != 0:
                raise RuntimeError(f"feature create failed for {entity_id}: {result.stderr}")
        return PhaseResult("create", time.perf_counter() - start, len(ids))

    def _read(self, repo: Path, ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            result = _run_ssot_cli("feature", "get", str(repo), "--id", entity_id)
            if result.returncode != 0:
                raise RuntimeError(f"feature get failed for {entity_id}: {result.stderr}")
            payload = json.loads(result.stdout)
            if payload["id"] != entity_id:
                raise RuntimeError(f"feature get returned unexpected id: {payload}")
        return PhaseResult("read", time.perf_counter() - start, len(ids))

    def _update(self, repo: Path, ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            result = _run_ssot_cli(
                "feature",
                "update",
                str(repo),
                "--id",
                entity_id,
                "--title",
                f"Updated {entity_id}",
            )
            if result.returncode != 0:
                raise RuntimeError(f"feature update failed for {entity_id}: {result.stderr}")
        return PhaseResult("update", time.perf_counter() - start, len(ids))

    def _list(self, repo: Path) -> PhaseResult:
        start = time.perf_counter()
        result = _run_ssot_cli("feature", "list", str(repo))
        if result.returncode != 0:
            raise RuntimeError(f"feature list failed: {result.stderr}")
        payload = json.loads(result.stdout)
        if not isinstance(payload, list):
            raise RuntimeError("feature list did not return a list")
        return PhaseResult("list", time.perf_counter() - start, 1)

    def _prepare_graph(self, repo: Path, workload: WorkloadPlan, feature_ids: list[str]) -> tuple[list[str], list[str]]:
        claim_ids: list[str] = []
        evidence_ids: list[str] = []
        test_ids: list[str] = []
        feature_count = len(feature_ids)
        claim_count = workload.claim_count
        test_count = workload.test_count
        for index in range(claim_count):
            feature_id = feature_ids[index % feature_count]
            claim_id = f"clm:bench.{index:04d}"
            claim_ids.append(claim_id)

            claim_result = _run_ssot_cli(
                "claim",
                "create",
                str(repo),
                "--id",
                claim_id,
                "--title",
                f"Bench claim {claim_id}",
                "--status",
                "proposed",
                "--tier",
                "T1",
                "--kind",
                "conformance",
                "--feature-ids",
                feature_id,
            )
            if claim_result.returncode != 0:
                raise RuntimeError(
                    f"claim create failed for {claim_id}: {claim_result.stderr or claim_result.stdout}"
                )

        for index in range(workload.evidence_count):
            claim_id = claim_ids[index % claim_count]
            evidence_id = f"evd:bench.{index:04d}"
            evidence_ids.append(evidence_id)
            evidence_relpath = Path(".ssot") / "evidence" / "bundles" / f"evd__bench_{index:04d}.json"
            (repo / evidence_relpath).parent.mkdir(parents=True, exist_ok=True)
            (repo / evidence_relpath).write_text("{}", encoding="utf-8")
            evidence_result = _run_ssot_cli(
                "evidence",
                "create",
                str(repo),
                "--id",
                evidence_id,
                "--title",
                f"Bench evidence {evidence_id}",
                "--status",
                "planned",
                "--kind",
                "bundle",
                "--tier",
                "T1",
                "--evidence-path",
                str(evidence_relpath).replace("\\", "/"),
                "--claim-ids",
                claim_id,
            )
            if evidence_result.returncode != 0:
                raise RuntimeError(
                    f"evidence create failed for {evidence_id}: {evidence_result.stderr or evidence_result.stdout}"
                )

        for index in range(test_count):
            feature_id = feature_ids[index % feature_count]
            claim_id = claim_ids[index % claim_count]
            evidence_id = evidence_ids[index % len(evidence_ids)]
            test_id = f"tst:bench.{index:04d}"
            test_ids.append(test_id)
            test_relpath = Path("tests") / f"test_bench_{index:04d}.py"
            (repo / test_relpath).parent.mkdir(parents=True, exist_ok=True)
            (repo / test_relpath).write_text("# bench fixture\n", encoding="utf-8")
            test_result = _run_ssot_cli(
                "test",
                "create",
                str(repo),
                "--id",
                test_id,
                "--title",
                f"Bench test {test_id}",
                "--status",
                "planned",
                "--kind",
                "pytest",
                "--test-path",
                str(test_relpath).replace("\\", "/"),
                "--feature-ids",
                feature_id,
                "--claim-ids",
                claim_id,
                "--evidence-ids",
                evidence_id,
            )
            if test_result.returncode != 0:
                raise RuntimeError(
                    f"test create failed for {test_id}: {test_result.stderr or test_result.stdout}"
                )

            claim_link = _run_ssot_cli(
                "claim",
                "link",
                str(repo),
                "--id",
                claim_id,
                "--test-ids",
                test_id,
            )
            if claim_link.returncode != 0:
                raise RuntimeError(
                    f"claim link failed for {claim_id}: {claim_link.stderr or claim_link.stdout}"
                )

            evidence_link = _run_ssot_cli(
                "evidence",
                "link",
                str(repo),
                "--id",
                evidence_id,
                "--test-ids",
                test_id,
            )
            if evidence_link.returncode != 0:
                raise RuntimeError(
                    f"evidence link failed for {evidence_id}: {evidence_link.stderr or evidence_link.stdout}"
                )

            feature_link = _run_ssot_cli(
                "feature",
                "link",
                str(repo),
                "--id",
                feature_id,
                "--claim-ids",
                claim_id,
                "--test-ids",
                test_id,
            )
            if feature_link.returncode != 0:
                raise RuntimeError(
                    f"feature link failed for {feature_id}: {feature_link.stderr or feature_link.stdout}"
                )
        return claim_ids, test_ids

    def _traverse_children(self, repo: Path, feature_ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for feature_id in feature_ids:
            feature = self._get_cli_entity("feature", repo, feature_id)
            for claim_id in feature.get("claim_ids", []):
                self._get_cli_entity("claim", repo, claim_id)
            for test_id in feature.get("test_ids", []):
                test = self._get_cli_entity("test", repo, test_id)
                for evidence_id in test.get("evidence_ids", []):
                    self._get_cli_entity("evidence", repo, evidence_id)
        return PhaseResult("traverse_children", time.perf_counter() - start, len(feature_ids))

    def _traverse_parents(self, repo: Path, test_ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for test_id in test_ids:
            test = self._get_cli_entity("test", repo, test_id)
            for feature_id in test.get("feature_ids", []):
                self._get_cli_entity("feature", repo, feature_id)
            for claim_id in test.get("claim_ids", []):
                self._get_cli_entity("claim", repo, claim_id)
            for evidence_id in test.get("evidence_ids", []):
                self._get_cli_entity("evidence", repo, evidence_id)
        return PhaseResult("traverse_parents", time.perf_counter() - start, len(test_ids))

    def _get_cli_entity(self, family: str, repo: Path, entity_id: str) -> dict[str, Any]:
        result = _run_ssot_cli(family, "get", str(repo), "--id", entity_id)
        if result.returncode != 0:
            raise RuntimeError(f"{family} get failed for {entity_id}: {result.stderr}")
        payload = json.loads(result.stdout)
        if payload["id"] != entity_id:
            raise RuntimeError(f"{family} get returned unexpected id: {payload}")
        return payload

    def _search(self, repo: Path) -> PhaseResult:
        start = time.perf_counter()
        result = _run_ssot_cli("feature", "list", str(repo))
        if result.returncode != 0:
            raise RuntimeError(f"feature list failed during search: {result.stderr}")
        payload = json.loads(result.stdout)
        matches = [row for row in payload if row.get("implementation_status") == "implemented"]
        if not matches:
            raise RuntimeError("search did not return any implemented features")
        return PhaseResult("search", time.perf_counter() - start, 1)


class CompiledTigrstoreRunner:
    def __init__(
        self,
        name: str,
        selections: dict[str, str],
        *,
        search_slug: str = "none",
        versioning_slug: str = "latest-only",
    ) -> None:
        self.name = name
        self.selections = selections
        self.search_slug = search_slug
        self.versioning_slug = versioning_slug
        self._sequence_latest_state: dict[str, Any] = {}
        self._bench_timestamp = 0
        self._runtime_root: Path | None = None

    def run_once(self, workload: WorkloadPlan) -> tuple[list[PhaseResult], FootprintResult]:
        self._sequence_latest_state = {}
        self._bench_timestamp = 0
        engine = self._build_engine()
        try:
            feature_ids = [f"feat:bench.{index:04d}" for index in range(workload.feature_count)]
            payloads = {
                entity_id: json.dumps(
                    {
                        "model": "Feature",
                        "id": entity_id,
                        "title": f"Bench feature {entity_id}",
                        "implementation_status": "partial",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                for entity_id in feature_ids
            }
            results = [
                self._create(engine, feature_ids, payloads),
                self._read(engine, feature_ids),
                self._update(engine, feature_ids, payloads),
                self._list(engine),
            ]
            test_ids = self._prepare_graph(engine, workload, feature_ids)
            results.extend(
                [
                    self._traverse_children(engine, feature_ids),
                    self._traverse_parents(engine, test_ids),
                    self._search(engine),
                ]
            )
            footprint_root = self._runtime_root / ".tigrstore" if self._runtime_root is not None else TEMP_ROOT
            return results, _directory_footprint(footprint_root)
        finally:
            if self._runtime_root is not None:
                shutil.rmtree(self._runtime_root.parent, ignore_errors=True)
                self._runtime_root = None

    def _build_engine(self) -> Any:
        sys.path[:0] = [str(path) for path in TIGRSTORE_PYTHONPATH_PARTS if str(path) not in sys.path]
        from tigrbl_engine_tigrstore import build_tigrstore_engine

        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(dir=TEMP_ROOT))
        self._runtime_root = temp_dir / "store"
        self._runtime_root.mkdir(parents=True, exist_ok=True)
        mapping = {
            "name": self.name,
            "root": str(self._runtime_root),
            "namespace": "bench",
            "strict": True,
            "selections": dict(self.selections),
            "lookup": "memtable-lookup",
            "filter_index": "bloom-filter",
            "secondary": "secondary-lsm-index",
            "storage_object_option": self.selections["storage_object"],
            "integrity_layers": (self.selections["integrity"],),
            "search": self.search_slug,
            "versioning": self.versioning_slug,
            "compaction": self.selections["compaction_gc"],
            "log": self.selections["log"],
        }
        engine, _factory = build_tigrstore_engine(mapping=mapping)
        if engine.compiled_store is None:
            raise RuntimeError("compiled_store was not attached to engine")
        return engine

    def _create(self, engine: Any, ids: list[str], payloads: dict[str, bytes]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            self._put_compiled_entity(
                engine,
                "features",
                entity_id,
                json.loads(payloads[entity_id].decode("utf-8")),
            )
        return PhaseResult("create", time.perf_counter() - start, len(ids))

    def _read(self, engine: Any, ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            self._get_compiled_entity(engine, "features", entity_id)
        return PhaseResult("read", time.perf_counter() - start, len(ids))

    def _update(self, engine: Any, ids: list[str], payloads: dict[str, bytes]) -> PhaseResult:
        start = time.perf_counter()
        for entity_id in ids:
            doc = json.loads(payloads[entity_id].decode("utf-8"))
            doc["implementation_status"] = "implemented"
            self._put_compiled_entity(engine, "features", entity_id, doc)
        return PhaseResult("update", time.perf_counter() - start, len(ids))

    def _list(self, engine: Any) -> PhaseResult:
        start = time.perf_counter()
        rows = tuple(self._load_store(engine).get("Feature", {}).values())
        return PhaseResult("list", time.perf_counter() - start, 1)

    def _prepare_graph(self, engine: Any, workload: WorkloadPlan, feature_ids: list[str]) -> list[str]:
        claim_ids: list[str] = []
        evidence_ids: list[str] = []
        test_ids: list[str] = []
        feature_count = len(feature_ids)
        for index in range(workload.claim_count):
            feature_id = feature_ids[index % feature_count]
            claim_id = f"clm:bench.{index:04d}"
            claim_ids.append(claim_id)
            self._put_compiled_entity(
                engine,
                "claims",
                claim_id,
                {
                    "model": "Claim",
                    "id": claim_id,
                    "title": f"Bench claim {claim_id}",
                    "status": "proposed",
                    "tier": "T1",
                    "kind": "conformance",
                    "feature_ids": [feature_id],
                    "test_ids": [],
                    "evidence_ids": [],
                },
            )
        for index in range(workload.evidence_count):
            claim_id = claim_ids[index % len(claim_ids)]
            evidence_id = f"evd:bench.{index:04d}"
            evidence_ids.append(evidence_id)
            self._put_compiled_entity(
                engine,
                "evidences",
                evidence_id,
                {
                    "model": "Evidence",
                    "id": evidence_id,
                    "title": f"Bench evidence {evidence_id}",
                    "status": "planned",
                    "kind": "bundle",
                    "tier": "T1",
                    "claim_ids": [claim_id],
                    "test_ids": [],
                    "path": f".ssot/evidence/bundles/evd__bench_{index:04d}.json",
                },
            )
            claim = self._get_compiled_entity(engine, "claims", claim_id)
            claim["evidence_ids"] = sorted({*claim.get("evidence_ids", []), evidence_id})
            self._put_compiled_entity(engine, "claims", claim_id, claim)
        for index in range(workload.test_count):
            feature_id = feature_ids[index % feature_count]
            claim_id = claim_ids[index % len(claim_ids)]
            evidence_id = evidence_ids[index % len(evidence_ids)]
            test_id = f"tst:bench.{index:04d}"
            test_ids.append(test_id)
            self._put_compiled_entity(
                engine,
                "tests",
                test_id,
                {
                    "model": "Test",
                    "id": test_id,
                    "title": f"Bench test {test_id}",
                    "status": "planned",
                    "kind": "pytest",
                    "path": f"tests/test_bench_{index:04d}.py",
                    "feature_ids": [feature_id],
                    "claim_ids": [claim_id],
                    "evidence_ids": [evidence_id],
                },
            )
            claim = self._get_compiled_entity(engine, "claims", claim_id)
            claim["test_ids"] = [test_id]
            self._put_compiled_entity(engine, "claims", claim_id, claim)
            evidence = self._get_compiled_entity(engine, "evidences", evidence_id)
            evidence["test_ids"] = sorted({*evidence.get("test_ids", []), test_id})
            self._put_compiled_entity(engine, "evidences", evidence_id, evidence)
            feature = self._get_compiled_entity(engine, "features", feature_id)
            feature["claim_ids"] = sorted({*feature.get("claim_ids", []), claim_id})
            feature["test_ids"] = sorted({*feature.get("test_ids", []), test_id})
            self._put_compiled_entity(engine, "features", feature_id, feature)
        return test_ids

    def _traverse_children(self, engine: Any, feature_ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for feature_id in feature_ids:
            feature = self._get_compiled_entity(engine, "features", feature_id)
            for claim_id in feature.get("claim_ids", []):
                self._get_compiled_entity(engine, "claims", claim_id)
            for test_id in feature.get("test_ids", []):
                test = self._get_compiled_entity(engine, "tests", test_id)
                for evidence_id in test.get("evidence_ids", []):
                    self._get_compiled_entity(engine, "evidences", evidence_id)
        return PhaseResult("traverse_children", time.perf_counter() - start, len(feature_ids))

    def _traverse_parents(self, engine: Any, test_ids: list[str]) -> PhaseResult:
        start = time.perf_counter()
        for test_id in test_ids:
            test = self._get_compiled_entity(engine, "tests", test_id)
            for feature_id in test.get("feature_ids", []):
                self._get_compiled_entity(engine, "features", feature_id)
            for claim_id in test.get("claim_ids", []):
                self._get_compiled_entity(engine, "claims", claim_id)
            for evidence_id in test.get("evidence_ids", []):
                self._get_compiled_entity(engine, "evidences", evidence_id)
        return PhaseResult("traverse_parents", time.perf_counter() - start, len(test_ids))

    def _entity_key(self, family: str, entity_id: str) -> str:
        return f"entity/{family}/{entity_id}"

    def _put_compiled_entity(self, engine: Any, family: str, entity_id: str, doc: dict[str, Any]) -> None:
        from tigrstore.versioning import SequenceLatest

        compiled = engine.compiled_store
        payload = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")
        key = self._entity_key(family, entity_id)
        self._bench_timestamp += 1
        timestamp = self._bench_timestamp
        if self.versioning_slug == "mvcc":
            compiled.versioning.put(key, payload, timestamp)
        elif self.versioning_slug == "sequence-latest":
            state = self._sequence_latest_state
            current = state.get(key)
            next_sequence = 1 if current is None else current.sequence + 1
            state[key] = SequenceLatest(next_sequence, payload)
        store = self._load_store(engine)
        model_name = self._family_model_name(family)
        store.setdefault(model_name, {})[entity_id] = json.loads(payload.decode("utf-8"))
        engine.persist_namespace_store("bench", store)
        compiled.filter_index.add(key)
        compiled.secondary_index.add("family", family, entity_id)
        if family == "features":
            status = str(doc.get("implementation_status", ""))
            if status:
                compiled.secondary_index.add("implementation_status", status, entity_id)
        self._search_add(compiled, key, entity_id, doc)

    def _get_compiled_entity(self, engine: Any, family: str, entity_id: str) -> dict[str, Any]:
        compiled = engine.compiled_store
        key = self._entity_key(family, entity_id)
        payload = None
        if self.versioning_slug == "mvcc":
            payload = compiled.versioning.get(key)
        elif self.versioning_slug == "sequence-latest":
            current = self._sequence_latest_state.get(key)
            payload = None if current is None else current.value
        if payload is None:
            store = self._load_store(engine)
            model_name = self._family_model_name(family)
            value = store.get(model_name, {}).get(entity_id)
            if value is None:
                raise RuntimeError(f"compiled lookup missed {key}")
            return deepcopy(value)
        return json.loads(payload.decode("utf-8"))

    def _load_store(self, engine: Any) -> dict[str, dict[str, object]]:
        return engine.load_namespace_store("bench")

    @staticmethod
    def _family_model_name(family: str) -> str:
        return {"features": "Feature", "claims": "Claim", "tests": "Test", "evidences": "Evidence"}[family]

    def _search_add(self, compiled: Any, key: str, entity_id: str, doc: dict[str, Any]) -> None:
        if self.search_slug == "prefix-search" and hasattr(compiled.search, "add"):
            compiled.search.add(key)
            return
        if self.search_slug == "secondary-search":
            field_values = compiled.search.field_values
            field_values.setdefault("family", {}).setdefault("features", set())
            if key.startswith("entity/features/"):
                field_values["family"]["features"].add(entity_id)
                status = str(doc.get("implementation_status", ""))
                if status:
                    field_values.setdefault("implementation_status", {}).setdefault(status, set()).add(entity_id)

    def _search(self, engine: Any) -> PhaseResult:
        start = time.perf_counter()
        compiled = engine.compiled_store
        if self.search_slug == "prefix-search":
            rows = compiled.search.search("entity/features/")
        elif self.search_slug == "secondary-search":
            rows = compiled.search.search("implementation_status", "implemented")
        else:
            rows = compiled.secondary_index.lookup("implementation_status", "implemented")
        if not rows:
            raise RuntimeError("search returned no rows")
        return PhaseResult("search", time.perf_counter() - start, 1)


def _aggregate(results: list[list[PhaseResult]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[PhaseResult]] = {}
    for run in results:
        for phase in run:
            grouped.setdefault(phase.phase, []).append(phase)
    summary: dict[str, dict[str, float]] = {}
    for phase_name, phase_runs in grouped.items():
        totals = [phase.total_seconds for phase in phase_runs]
        ms_per_op = [phase.ms_per_op for phase in phase_runs]
        summary[phase_name] = {
            "median_seconds": statistics.median(totals),
            "median_ms_per_op": statistics.median(ms_per_op),
            "min_seconds": min(totals),
            "max_seconds": max(totals),
            "operations": phase_runs[0].operations,
        }
    return summary


def _aggregate_footprints(results: list[FootprintResult]) -> FootprintResult:
    if not results:
        return FootprintResult(0, 0)
    file_counts = sorted(result.file_count for result in results)
    byte_counts = sorted(result.cumulative_bytes for result in results)
    midpoint = len(results) // 2
    if len(results) % 2 == 1:
        return FootprintResult(file_counts[midpoint], byte_counts[midpoint])
    return FootprintResult(
        (file_counts[midpoint - 1] + file_counts[midpoint]) // 2,
        (byte_counts[midpoint - 1] + byte_counts[midpoint]) // 2,
    )


def _print_table(rows: list[dict[str, object]]) -> None:
    headers = ("contender", "phase", "ops", "median_s", "median_ms_per_op", "file_count", "cumulative_bytes")
    widths = {header: len(header) for header in headers}
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(str(row[header])))
    line = "  ".join(header.ljust(widths[header]) for header in headers)
    print(line)
    print("  ".join("-" * widths[header] for header in headers))
    for row in rows:
        print("  ".join(str(row[header]).ljust(widths[header]) for header in headers))


def _write_json_report(
    *,
    workload: WorkloadPlan,
    repeats: int,
    rows: list[dict[str, object]],
    output_path: Path | None,
) -> Path:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = output_path
    if report_path is None:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        report_path = REPORT_ROOT / f"benchmark_ssot_cli_vs_tigrstore_{stamp}.json"
    report = {
        "generated_at": datetime.now().isoformat(),
        "cwd": str(REPO_ROOT),
        "repeats": repeats,
        "workload": {
            "total_instances": workload.total_instances,
            "feature_count": workload.feature_count,
            "claim_count": workload.claim_count,
            "test_count": workload.test_count,
            "evidence_count": workload.evidence_count,
        },
        "rows": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=int, default=100)
    parser.add_argument("--entities", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--json-report", type=Path, default=None)
    parser.add_argument("--strategy", action="append", default=None)
    args = parser.parse_args()
    total_instances = args.instances if args.entities is None else args.entities
    workload = _plan_workload(total_instances)

    contenders = [
        SsotCliRunner(),
        CompiledTigrstoreRunner("filelsm-based", FILELSM_SELECTIONS),
        CompiledTigrstoreRunner("blocklsm-based", BLOCKLSM_SELECTIONS),
        CompiledTigrstoreRunner(
            "blocklsm-segmentedwal-segmentgc",
            BLOCKLSM_SEGMENTED_WAL_SEGMENT_GC_SELECTIONS,
        ),
        CompiledTigrstoreRunner("document-object-simple", DOCUMENT_OBJECT_SIMPLE_SELECTIONS),
        CompiledTigrstoreRunner("document-object-block", DOCUMENT_OBJECT_BLOCK_SELECTIONS),
        CompiledTigrstoreRunner("metadata-config-simple", METADATA_CONFIG_SIMPLE_SELECTIONS),
        CompiledTigrstoreRunner("metadata-config-block", METADATA_CONFIG_BLOCK_SELECTIONS),
        CompiledTigrstoreRunner(
            METADATA_CONFIG_BLOCK_WAL_SEGMENT_GC["name"],
            METADATA_CONFIG_BLOCK_WAL_SEGMENT_GC["selections"],
            search_slug=METADATA_CONFIG_BLOCK_WAL_SEGMENT_GC["search"],
            versioning_slug=METADATA_CONFIG_BLOCK_WAL_SEGMENT_GC["versioning"],
        ),
        CompiledTigrstoreRunner(
            DOCUMENT_OBJECT_SIMPLE_PREFIX_SEQUENCE["name"],
            DOCUMENT_OBJECT_SIMPLE_PREFIX_SEQUENCE["selections"],
            search_slug=DOCUMENT_OBJECT_SIMPLE_PREFIX_SEQUENCE["search"],
            versioning_slug=DOCUMENT_OBJECT_SIMPLE_PREFIX_SEQUENCE["versioning"],
        ),
        CompiledTigrstoreRunner(
            DOCUMENT_OBJECT_BLOCK_SECONDARY_SEQUENCE["name"],
            DOCUMENT_OBJECT_BLOCK_SECONDARY_SEQUENCE["selections"],
            search_slug=DOCUMENT_OBJECT_BLOCK_SECONDARY_SEQUENCE["search"],
            versioning_slug=DOCUMENT_OBJECT_BLOCK_SECONDARY_SEQUENCE["versioning"],
        ),
        CompiledTigrstoreRunner(
            METADATA_CONFIG_SIMPLE_PREFIX_MVCC["name"],
            METADATA_CONFIG_SIMPLE_PREFIX_MVCC["selections"],
            search_slug=METADATA_CONFIG_SIMPLE_PREFIX_MVCC["search"],
            versioning_slug=METADATA_CONFIG_SIMPLE_PREFIX_MVCC["versioning"],
        ),
        CompiledTigrstoreRunner(
            METADATA_CONFIG_BLOCK_SECONDARY_MVCC["name"],
            METADATA_CONFIG_BLOCK_SECONDARY_MVCC["selections"],
            search_slug=METADATA_CONFIG_BLOCK_SECONDARY_MVCC["search"],
            versioning_slug=METADATA_CONFIG_BLOCK_SECONDARY_MVCC["versioning"],
        ),
    ]
    if args.strategy:
        allowed = set(args.strategy)
        contenders = [contender for contender in contenders if contender.name in allowed]
        if not contenders:
            raise SystemExit(f"no contenders matched --strategy values: {sorted(allowed)!r}")

    all_rows: list[dict[str, object]] = []
    for contender in contenders:
        runs = [contender.run_once(workload) for _ in range(args.repeats)]
        phase_runs = [phases for phases, _footprint in runs]
        footprints = [footprint for _phases, footprint in runs]
        summary = _aggregate(phase_runs)
        footprint = _aggregate_footprints(footprints)
        for phase_name in ("create", "read", "update", "list", "traverse_children", "traverse_parents", "search"):
            phase = summary[phase_name]
            all_rows.append(
                {
                    "contender": contender.name,
                    "phase": phase_name,
                    "ops": phase["operations"],
                    "median_s": f"{phase['median_seconds']:.6f}",
                    "median_ms_per_op": f"{phase['median_ms_per_op']:.3f}",
                    "file_count": footprint.file_count,
                    "cumulative_bytes": footprint.cumulative_bytes,
                }
            )

    _print_table(all_rows)
    report_path = _write_json_report(
        workload=workload,
        repeats=args.repeats,
        rows=all_rows,
        output_path=args.json_report,
    )
    print()
    print(f"json_report  {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
