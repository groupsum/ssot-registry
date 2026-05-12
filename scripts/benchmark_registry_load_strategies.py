from __future__ import annotations

import argparse
import json
import shutil
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = REPO_ROOT / ".tmp_test_runs"
REPORT_ROOT = REPO_ROOT / "reports" / "benchmarks"
LOCAL_ORJSON_ROOT = REPO_ROOT / ".tmp_pydeps" / "orjson"

if str(LOCAL_ORJSON_ROOT) not in sys.path and LOCAL_ORJSON_ROOT.exists():
    sys.path.insert(0, str(LOCAL_ORJSON_ROOT))

try:
    import orjson
except ImportError:
    orjson = None

SECTIONS = ("features", "claims", "tests", "evidence")


@dataclass(frozen=True)
class PhaseResult:
    strategy: str
    phase: str
    seconds: float
    operations: int

    @property
    def ms_per_op(self) -> float:
        if self.operations == 0:
            return 0.0
        return (self.seconds * 1000.0) / self.operations


@dataclass(frozen=True)
class Footprint:
    file_count: int
    cumulative_bytes: int


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_stable_json(data), encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_orjson_bytes(data: Any) -> bytes:
    if orjson is None:
        raise RuntimeError("orjson is not installed")
    return orjson.dumps(data, option=orjson.OPT_SORT_KEYS | orjson.OPT_APPEND_NEWLINE)


def _write_orjson(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_stable_orjson_bytes(data))


def _read_orjson(path: Path) -> Any:
    if orjson is None:
        raise RuntimeError("orjson is not installed")
    return orjson.loads(path.read_bytes())


def _safe_id(entity_id: str) -> str:
    return entity_id.replace(":", "__").replace("/", "_")


def _footprint(root: Path) -> Footprint:
    file_count = 0
    cumulative_bytes = 0
    for path in root.rglob("*"):
        if path.is_file():
            file_count += 1
            cumulative_bytes += path.stat().st_size
    return Footprint(file_count=file_count, cumulative_bytes=cumulative_bytes)


def _base_registry() -> dict[str, Any]:
    return {
        "schema_version": "0.3.0",
        "repo": {"id": "repo:benchmark", "name": "benchmark", "version": "0.0.0", "kind": "repo-local"},
        "tooling": {
            "ssot_registry_version": "benchmark",
            "initialized_with_version": "benchmark",
            "last_upgraded_from_version": "benchmark",
        },
        "paths": {
            "ssot_root": ".ssot",
            "schema_root": ".ssot/schemas",
            "adr_root": ".ssot/adr",
            "spec_root": ".ssot/specs",
            "graph_root": ".ssot/graphs",
            "evidence_root": ".ssot/evidence",
            "release_root": ".ssot/releases",
            "report_root": ".ssot/reports",
            "cache_root": ".ssot/cache",
        },
        "program": {"active_boundary_id": "bnd:benchmark", "active_release_id": "rel:benchmark"},
        "guard_policies": {},
        "document_id_reservations": {"adr": [], "spec": []},
        "features": [],
        "profiles": [],
        "tests": [],
        "claims": [],
        "evidence": [],
        "issues": [],
        "risks": [],
        "boundaries": [
            {
                "id": "bnd:benchmark",
                "title": "Benchmark boundary",
                "status": "draft",
                "frozen": False,
                "feature_ids": [],
                "profile_ids": [],
            }
        ],
        "releases": [
            {
                "id": "rel:benchmark",
                "version": "0.0.0",
                "status": "draft",
                "boundary_id": "bnd:benchmark",
                "boundary_ids": ["bnd:benchmark"],
                "claim_ids": [],
                "evidence_ids": [],
            }
        ],
        "adrs": [],
        "specs": [],
    }


def _feature_row(index: int) -> dict[str, Any]:
    feature_id = f"feat:bench.feature-{index:06d}"
    status = "implemented" if index % 5 == 0 else "partial"
    return {
        "id": feature_id,
        "title": f"Benchmark feature {index:06d}",
        "description": (
            "Synthetic benchmark feature row with enough descriptive payload to simulate "
            "real registry growth while remaining targetable and independently linked."
        ),
        "implementation_status": status,
        "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
        "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T1", "target_lifecycle_stage": "active"},
        "spec_ids": [],
        "claim_ids": [f"clm:bench.claim-{index:06d}"],
        "test_ids": [f"tst:bench.test-{index:06d}"],
        "requires": [],
    }


def _claim_row(index: int) -> dict[str, Any]:
    return {
        "id": f"clm:bench.claim-{index:06d}",
        "title": f"Benchmark claim {index:06d}",
        "description": "Synthetic benchmark claim linked to one feature, one test, and one evidence row.",
        "status": "asserted",
        "tier": "T1",
        "kind": "benchmark",
        "feature_ids": [f"feat:bench.feature-{index:06d}"],
        "test_ids": [f"tst:bench.test-{index:06d}"],
        "evidence_ids": [f"evd:bench.evidence-{index:06d}"],
    }


def _test_row(index: int) -> dict[str, Any]:
    return {
        "id": f"tst:bench.test-{index:06d}",
        "title": f"Benchmark test {index:06d}",
        "status": "passing",
        "kind": "pytest",
        "path": f"tests/benchmark/test_feature_{index:06d}.py",
        "feature_ids": [f"feat:bench.feature-{index:06d}"],
        "claim_ids": [f"clm:bench.claim-{index:06d}"],
        "evidence_ids": [f"evd:bench.evidence-{index:06d}"],
    }


def _evidence_row(index: int) -> dict[str, Any]:
    return {
        "id": f"evd:bench.evidence-{index:06d}",
        "title": f"Benchmark evidence {index:06d}",
        "status": "passed",
        "kind": "benchmark",
        "tier": "T1",
        "path": f".ssot/evidence/benchmark/evidence_{index:06d}.json",
        "claim_ids": [f"clm:bench.claim-{index:06d}"],
        "test_ids": [f"tst:bench.test-{index:06d}"],
    }


def build_registry(entity_count: int) -> dict[str, Any]:
    registry = _base_registry()
    for index in range(entity_count):
        registry["features"].append(_feature_row(index))
        registry["claims"].append(_claim_row(index))
        registry["tests"].append(_test_row(index))
        registry["evidence"].append(_evidence_row(index))
    registry["boundaries"][0]["feature_ids"] = [row["id"] for row in registry["features"]]
    registry["releases"][0]["claim_ids"] = [row["id"] for row in registry["claims"]]
    registry["releases"][0]["evidence_ids"] = [row["id"] for row in registry["evidence"]]
    return registry


class SingleJsonStrategy:
    name = "single-json-current"

    def __init__(self, root: Path) -> None:
        self.root = root
        self.registry_path = root / ".ssot" / "registry.json"

    def initialize(self, registry: dict[str, Any]) -> None:
        _write_json(self.registry_path, registry)

    def _load(self) -> dict[str, Any]:
        return _read_json(self.registry_path)

    def _save(self, registry: dict[str, Any]) -> None:
        _write_json(self.registry_path, registry)

    @staticmethod
    def _lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
        return {row["id"]: row for row in registry[section]}

    def create(self) -> None:
        registry = self._load()
        index = len(registry["features"]) + 1_000_000
        registry["features"].append(_feature_row(index))
        self._save(registry)

    def read(self, entity_id: str) -> dict[str, Any]:
        registry = self._load()
        return dict(self._lookup(registry, "features")[entity_id])

    def update(self, entity_id: str) -> None:
        registry = self._load()
        row = self._lookup(registry, "features")[entity_id]
        row["description"] = f"{row['description']} Updated by benchmark."
        self._save(registry)

    def delete(self, entity_id: str) -> None:
        registry = self._load()
        registry["features"] = [row for row in registry["features"] if row["id"] != entity_id]
        self._save(registry)

    def list_features(self) -> list[str]:
        registry = self._load()
        return sorted(row["id"] for row in registry["features"])

    def traverse_children(self, feature_id: str) -> list[dict[str, Any]]:
        registry = self._load()
        features = self._lookup(registry, "features")
        claims = self._lookup(registry, "claims")
        tests = self._lookup(registry, "tests")
        evidence = self._lookup(registry, "evidence")
        feature = features[feature_id]
        rows: list[dict[str, Any]] = [feature]
        rows.extend(claims[claim_id] for claim_id in feature.get("claim_ids", []))
        for test_id in feature.get("test_ids", []):
            test = tests[test_id]
            rows.append(test)
            rows.extend(evidence[evidence_id] for evidence_id in test.get("evidence_ids", []))
        return rows

    def traverse_parents(self, test_id: str) -> list[dict[str, Any]]:
        registry = self._load()
        features = self._lookup(registry, "features")
        claims = self._lookup(registry, "claims")
        tests = self._lookup(registry, "tests")
        evidence = self._lookup(registry, "evidence")
        test = tests[test_id]
        rows: list[dict[str, Any]] = [test]
        rows.extend(features[feature_id] for feature_id in test.get("feature_ids", []))
        rows.extend(claims[claim_id] for claim_id in test.get("claim_ids", []))
        rows.extend(evidence[evidence_id] for evidence_id in test.get("evidence_ids", []))
        return rows

    def search(self, query: str) -> list[str]:
        registry = self._load()
        query_lower = query.lower()
        return [
            row["id"]
            for row in registry["features"]
            if query_lower in row["title"].lower()
            or query_lower in row["description"].lower()
            or query_lower == row["implementation_status"].lower()
        ]


class OrjsonSingleJsonStrategy(SingleJsonStrategy):
    name = "single-json-orjson"

    def initialize(self, registry: dict[str, Any]) -> None:
        _write_orjson(self.registry_path, registry)

    def _load(self) -> dict[str, Any]:
        return _read_orjson(self.registry_path)

    def _save(self, registry: dict[str, Any]) -> None:
        _write_orjson(self.registry_path, registry)


class ShardedIndexStrategy:
    name = "sharded-index-recommended"

    def __init__(self, root: Path) -> None:
        self.root = root
        self.registry_path = root / ".ssot" / "registry.json"
        self.cache_root = root / ".ssot" / "cache" / "registry-store"
        self.index_path = self.cache_root / "registry.index.json"

    def initialize(self, registry: dict[str, Any]) -> None:
        _write_json(self.registry_path, registry)
        index: dict[str, Any] = {
            "sections": {section: {} for section in SECTIONS},
            "implemented_feature_ids": [],
        }
        for section in SECTIONS:
            section_root = self.cache_root / "entities" / section
            for row in registry[section]:
                entity_id = row["id"]
                entity_path = section_root / f"{_safe_id(entity_id)}.json"
                _write_json(entity_path, row)
                metadata = self._metadata_for_row(section, row, entity_path)
                index["sections"][section][entity_id] = metadata
                if section == "features" and row.get("implementation_status") == "implemented":
                    index["implemented_feature_ids"].append(entity_id)
        index["implemented_feature_ids"].sort()
        _write_json(self.index_path, index)

    def _load_index(self) -> dict[str, Any]:
        return _read_json(self.index_path)

    def _save_index(self, index: dict[str, Any]) -> None:
        _write_json(self.index_path, index)

    def _entity_path(self, section: str, entity_id: str) -> Path:
        return self.cache_root / "entities" / section / f"{_safe_id(entity_id)}.json"

    def _metadata_for_row(self, section: str, row: dict[str, Any], entity_path: Path) -> dict[str, Any]:
        metadata = {
            "path": entity_path.relative_to(self.root).as_posix(),
            "title": row.get("title", ""),
        }
        for field_name in ("description", "implementation_status", "feature_ids", "claim_ids", "test_ids", "evidence_ids"):
            if field_name in row:
                metadata[field_name] = row[field_name]
        return metadata

    def _read_entity(self, index: dict[str, Any], section: str, entity_id: str) -> dict[str, Any]:
        relative = index["sections"][section][entity_id]["path"]
        return _read_json(self.root / relative)

    def create(self) -> None:
        index = self._load_index()
        row_index = len(index["sections"]["features"]) + 1_000_000
        row = _feature_row(row_index)
        entity_path = self._entity_path("features", row["id"])
        _write_json(entity_path, row)
        index["sections"]["features"][row["id"]] = self._metadata_for_row("features", row, entity_path)
        if row.get("implementation_status") == "implemented":
            index["implemented_feature_ids"] = sorted({*index["implemented_feature_ids"], row["id"]})
        self._save_index(index)

    def read(self, entity_id: str) -> dict[str, Any]:
        index = self._load_index()
        return self._read_entity(index, "features", entity_id)

    def update(self, entity_id: str) -> None:
        index = self._load_index()
        row = self._read_entity(index, "features", entity_id)
        row["description"] = f"{row['description']} Updated by benchmark."
        entity_path = self.root / index["sections"]["features"][entity_id]["path"]
        _write_json(entity_path, row)
        index["sections"]["features"][entity_id] = self._metadata_for_row("features", row, entity_path)
        self._save_index(index)

    def delete(self, entity_id: str) -> None:
        index = self._load_index()
        relative = index["sections"]["features"][entity_id]["path"]
        del index["sections"]["features"][entity_id]
        index["implemented_feature_ids"] = [value for value in index["implemented_feature_ids"] if value != entity_id]
        (self.root / relative).unlink(missing_ok=True)
        self._save_index(index)

    def list_features(self) -> list[str]:
        index = self._load_index()
        return sorted(index["sections"]["features"])

    def traverse_children(self, feature_id: str) -> list[dict[str, Any]]:
        index = self._load_index()
        feature_meta = index["sections"]["features"][feature_id]
        rows = [self._read_entity(index, "features", feature_id)]
        rows.extend(self._read_entity(index, "claims", claim_id) for claim_id in feature_meta.get("claim_ids", []))
        for test_id in feature_meta.get("test_ids", []):
            test = self._read_entity(index, "tests", test_id)
            rows.append(test)
            rows.extend(self._read_entity(index, "evidence", evidence_id) for evidence_id in test.get("evidence_ids", []))
        return rows

    def traverse_parents(self, test_id: str) -> list[dict[str, Any]]:
        index = self._load_index()
        test_meta = index["sections"]["tests"][test_id]
        rows = [self._read_entity(index, "tests", test_id)]
        rows.extend(self._read_entity(index, "features", feature_id) for feature_id in test_meta.get("feature_ids", []))
        rows.extend(self._read_entity(index, "claims", claim_id) for claim_id in test_meta.get("claim_ids", []))
        rows.extend(self._read_entity(index, "evidence", evidence_id) for evidence_id in test_meta.get("evidence_ids", []))
        return rows

    def search(self, query: str) -> list[str]:
        index = self._load_index()
        if query == "implemented":
            return list(index["implemented_feature_ids"])
        query_lower = query.lower()
        return [
            entity_id
            for entity_id, row in index["sections"]["features"].items()
            if query_lower in str(row.get("title", "")).lower()
            or query_lower in str(row.get("description", "")).lower()
            or query_lower == str(row.get("implementation_status", "")).lower()
        ]


class CachedShardedIndexStrategy(ShardedIndexStrategy):
    name = "cached-sharded-index-recommended"

    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self._index_cache: dict[str, Any] | None = None
        self._entity_cache: dict[str, dict[str, Any]] = {}

    def initialize(self, registry: dict[str, Any]) -> None:
        super().initialize(registry)
        self._index_cache = None
        self._entity_cache = {}

    def _load_index(self) -> dict[str, Any]:
        if self._index_cache is None:
            self._index_cache = _read_json(self.index_path)
        return self._index_cache

    def _save_index(self, index: dict[str, Any]) -> None:
        self._index_cache = index
        _write_json(self.index_path, index)

    def _read_entity(self, index: dict[str, Any], section: str, entity_id: str) -> dict[str, Any]:
        relative = index["sections"][section][entity_id]["path"]
        cached = self._entity_cache.get(relative)
        if cached is None:
            cached = _read_json(self.root / relative)
            self._entity_cache[relative] = cached
        return dict(cached)

    def create(self) -> None:
        index = self._load_index()
        row_index = len(index["sections"]["features"]) + 1_000_000
        row = _feature_row(row_index)
        entity_path = self._entity_path("features", row["id"])
        _write_json(entity_path, row)
        relative = entity_path.relative_to(self.root).as_posix()
        self._entity_cache[relative] = row
        index["sections"]["features"][row["id"]] = self._metadata_for_row("features", row, entity_path)
        if row.get("implementation_status") == "implemented":
            index["implemented_feature_ids"] = sorted({*index["implemented_feature_ids"], row["id"]})
        self._save_index(index)

    def update(self, entity_id: str) -> None:
        index = self._load_index()
        row = self._read_entity(index, "features", entity_id)
        row["description"] = f"{row['description']} Updated by benchmark."
        entity_path = self.root / index["sections"]["features"][entity_id]["path"]
        _write_json(entity_path, row)
        relative = entity_path.relative_to(self.root).as_posix()
        self._entity_cache[relative] = row
        index["sections"]["features"][entity_id] = self._metadata_for_row("features", row, entity_path)
        self._save_index(index)

    def delete(self, entity_id: str) -> None:
        index = self._load_index()
        relative = index["sections"]["features"][entity_id]["path"]
        del index["sections"]["features"][entity_id]
        index["implemented_feature_ids"] = [value for value in index["implemented_feature_ids"] if value != entity_id]
        self._entity_cache.pop(relative, None)
        (self.root / relative).unlink(missing_ok=True)
        self._save_index(index)


def _time_phase(strategy: Any, phase: str, operations: int, func: Any) -> PhaseResult:
    start = time.perf_counter()
    func()
    return PhaseResult(strategy=strategy.name, phase=phase, seconds=time.perf_counter() - start, operations=operations)


def run_strategy(strategy: Any, *, entity_count: int, sample_count: int) -> tuple[list[PhaseResult], Footprint]:
    feature_ids = [f"feat:bench.feature-{index:06d}" for index in range(sample_count)]
    test_ids = [f"tst:bench.test-{index:06d}" for index in range(sample_count)]
    delete_id = f"feat:bench.feature-{entity_count + 1_000_000:06d}"

    phases = [
        _time_phase(strategy, "create", 1, strategy.create),
        _time_phase(strategy, "read", sample_count, lambda: [strategy.read(entity_id) for entity_id in feature_ids]),
        _time_phase(strategy, "update", sample_count, lambda: [strategy.update(entity_id) for entity_id in feature_ids]),
        _time_phase(strategy, "delete", 1, lambda: strategy.delete(delete_id)),
        _time_phase(strategy, "list", 1, strategy.list_features),
        _time_phase(
            strategy,
            "traverse_children",
            sample_count,
            lambda: [strategy.traverse_children(entity_id) for entity_id in feature_ids],
        ),
        _time_phase(
            strategy,
            "traverse_parents",
            sample_count,
            lambda: [strategy.traverse_parents(entity_id) for entity_id in test_ids],
        ),
        _time_phase(strategy, "search", 1, lambda: strategy.search("implemented")),
    ]
    return phases, _footprint(strategy.root / ".ssot")


def _aggregate(runs: list[list[PhaseResult]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str], list[PhaseResult]] = {}
    for run in runs:
        for phase in run:
            by_key.setdefault((phase.strategy, phase.phase), []).append(phase)
    rows: list[dict[str, Any]] = []
    for (strategy, phase), values in sorted(by_key.items()):
        seconds = [value.seconds for value in values]
        ms_per_op = [value.ms_per_op for value in values]
        rows.append(
            {
                "strategy": strategy,
                "phase": phase,
                "operations": values[0].operations,
                "median_seconds": statistics.median(seconds),
                "median_ms_per_op": statistics.median(ms_per_op),
                "min_seconds": min(seconds),
                "max_seconds": max(seconds),
            }
        )
    return rows


def _median_footprint(values: list[Footprint]) -> Footprint:
    file_counts = sorted(value.file_count for value in values)
    byte_counts = sorted(value.cumulative_bytes for value in values)
    mid = len(values) // 2
    return Footprint(file_count=file_counts[mid], cumulative_bytes=byte_counts[mid])


def _print_table(rows: list[dict[str, Any]], footprints: dict[str, Footprint]) -> None:
    rendered = []
    for row in rows:
        footprint = footprints[row["strategy"]]
        rendered.append(
            {
                "strategy": row["strategy"],
                "phase": row["phase"],
                "ops": row["operations"],
                "median_s": f"{row['median_seconds']:.6f}",
                "median_ms_per_op": f"{row['median_ms_per_op']:.3f}",
                "file_count": footprint.file_count,
                "cumulative_bytes": footprint.cumulative_bytes,
            }
        )
    headers = ("strategy", "phase", "ops", "median_s", "median_ms_per_op", "file_count", "cumulative_bytes")
    widths = {header: len(header) for header in headers}
    for row in rendered:
        for header in headers:
            widths[header] = max(widths[header], len(str(row[header])))
    print("  ".join(header.ljust(widths[header]) for header in headers))
    print("  ".join("-" * widths[header] for header in headers))
    for row in rendered:
        print("  ".join(str(row[header]).ljust(widths[header]) for header in headers))


def _write_report(
    *,
    entity_count: int,
    sample_count: int,
    repeats: int,
    registry_bytes: int,
    rows: list[dict[str, Any]],
    footprints: dict[str, Footprint],
    output: Path | None,
) -> Path:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = output
    if report_path is None:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        report_path = REPORT_ROOT / f"benchmark_registry_load_strategies_{stamp}.json"
    payload = {
        "generated_at": datetime.now().isoformat(),
        "cwd": REPO_ROOT.as_posix(),
        "entity_count_per_family": entity_count,
        "sample_count": sample_count,
        "repeats": repeats,
        "initial_registry_bytes": registry_bytes,
        "orjson_available": orjson is not None,
        "strategies": {
            name: {"file_count": fp.file_count, "cumulative_bytes": fp.cumulative_bytes}
            for name, fp in footprints.items()
        },
        "rows": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark single-file registry loading against a sharded entity cache plus compact index."
    )
    parser.add_argument("--entities", type=int, default=1_000, help="Rows per entity family to generate.")
    parser.add_argument("--samples", type=int, default=50, help="Rows touched by read/update/traversal phases.")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--json-report", type=Path, default=None)
    parser.add_argument("--strategy", action="append", default=None)
    args = parser.parse_args()

    if args.entities < 2:
        raise ValueError("--entities must be at least 2")
    if args.samples < 1 or args.samples >= args.entities:
        raise ValueError("--samples must be at least 1 and smaller than --entities")

    registry = build_registry(args.entities)
    registry_bytes = len(_stable_json(registry).encode("utf-8"))
    strategy_types = [SingleJsonStrategy]
    if orjson is not None:
        strategy_types.append(OrjsonSingleJsonStrategy)
    strategy_types.extend([ShardedIndexStrategy, CachedShardedIndexStrategy])
    if args.strategy:
        allowed = set(args.strategy)
        strategy_types = [strategy_type for strategy_type in strategy_types if strategy_type.name in allowed]
        if not strategy_types:
            raise ValueError(f"no strategies matched --strategy values: {sorted(allowed)!r}")

    all_runs: list[list[PhaseResult]] = []
    footprint_runs: dict[str, list[Footprint]] = {}
    for _ in range(args.repeats):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(dir=TEMP_ROOT))
        try:
            for strategy_type in strategy_types:
                root = temp_dir / strategy_type.name
                strategy = strategy_type(root)
                strategy.initialize(registry)
                phases, footprint = run_strategy(strategy, entity_count=args.entities, sample_count=args.samples)
                all_runs.append(phases)
                footprint_runs.setdefault(strategy.name, []).append(footprint)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    rows = _aggregate(all_runs)
    footprints = {name: _median_footprint(values) for name, values in footprint_runs.items()}
    _print_table(rows, footprints)
    report_path = _write_report(
        entity_count=args.entities,
        sample_count=args.samples,
        repeats=args.repeats,
        registry_bytes=registry_bytes,
        rows=rows,
        footprints=footprints,
        output=args.json_report,
    )
    print()
    print(f"initial_registry_bytes  {registry_bytes}")
    print(f"json_report             {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
