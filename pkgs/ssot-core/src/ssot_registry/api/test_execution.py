from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ssot_registry.util.jcs import dump_jcs_json

from .load import load_registry
from .profile_resolution import resolve_boundary_feature_ids


def _row_lookup(registry: dict[str, Any], section: str) -> dict[str, dict[str, Any]]:
    return {
        row["id"]: row
        for row in registry.get(section, [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _validate_execution_contract(test: dict[str, Any]) -> dict[str, Any]:
    execution = test.get("execution")
    test_id = str(test.get("id", "<missing>"))
    if not isinstance(execution, dict):
        raise ValueError(f"Test {test_id} is not runnable; missing execution metadata")
    if execution.get("mode") != "command":
        raise ValueError(f"Test {test_id} execution.mode must be 'command'")
    argv = execution.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item.strip() for item in argv):
        raise ValueError(f"Test {test_id} execution.argv must be a non-empty list of strings")
    cwd = execution.get("cwd")
    if not isinstance(cwd, str) or not cwd.strip():
        raise ValueError(f"Test {test_id} execution.cwd must be a non-empty string")
    env = execution.get("env")
    if not isinstance(env, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in env.items()):
        raise ValueError(f"Test {test_id} execution.env must be a string-to-string object")
    timeout_seconds = execution.get("timeout_seconds")
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError(f"Test {test_id} execution.timeout_seconds must be a positive integer")
    success = execution.get("success")
    if not isinstance(success, dict):
        raise ValueError(f"Test {test_id} execution.success must be an object")
    if success.get("type") != "exit_code":
        raise ValueError(f"Test {test_id} execution.success.type must be 'exit_code'")
    expected = success.get("expected")
    if not isinstance(expected, int):
        raise ValueError(f"Test {test_id} execution.success.expected must be an integer")
    return execution


def _resolve_command_cwd(repo_root: Path, cwd: str, *, test_id: str) -> Path:
    relative = Path(cwd)
    if relative.is_absolute():
        raise ValueError(f"Test {test_id} execution.cwd must be repo-relative")
    target = (repo_root / relative).resolve()
    if repo_root not in {target, *target.parents}:
        raise ValueError(f"Test {test_id} execution.cwd must stay within the repo root")
    return target


def _write_evidence_output(path: str | Path, payload: dict[str, Any]) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_jcs_json(payload), encoding="utf-8")
    return target.as_posix()


def _build_evidence_payload(
    *,
    repo_root: Path,
    target: dict[str, Any],
    resolved_test_ids: list[str],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "total": len(cases)}
    for case in cases:
        outcome = str(case.get("outcome", "unknown"))
        if outcome in summary:
            summary[outcome] += 1
    return {
        "kind": "ssot-conformance-evidence",
        "repo_root": repo_root.as_posix(),
        "profiles": [],
        "families": [],
        "target": target,
        "resolved_test_ids": list(resolved_test_ids),
        "summary": summary,
        "cases": cases,
    }


def _resolve_tests_from_ids(registry: dict[str, Any], test_ids: list[str]) -> list[dict[str, Any]]:
    tests = _row_lookup(registry, "tests")
    missing = [test_id for test_id in test_ids if test_id not in tests]
    if missing:
        raise ValueError(f"Unknown test ids: {', '.join(sorted(missing))}")
    return [tests[test_id] for test_id in _dedupe_preserve(test_ids)]


def _resolve_tests_for_spec(registry: dict[str, Any], spec_id: str) -> tuple[list[str], list[dict[str, Any]]]:
    specs = _row_lookup(registry, "specs")
    if spec_id not in specs:
        raise ValueError(f"Unknown spec id: {spec_id}")
    feature_ids = [
        row["id"]
        for row in registry.get("features", [])
        if isinstance(row, dict) and spec_id in row.get("spec_ids", [])
    ]
    resolved_test_ids: list[str] = []
    for row in registry.get("features", []):
        if isinstance(row, dict) and row.get("id") in feature_ids:
            resolved_test_ids.extend(row.get("test_ids", []))
    return feature_ids, _resolve_tests_from_ids(registry, resolved_test_ids)


def _resolve_tests_for_boundary(registry: dict[str, Any], boundary_id: str | None) -> tuple[str, list[str], list[dict[str, Any]]]:
    boundaries = _row_lookup(registry, "boundaries")
    if boundary_id is None:
        program = registry.get("program", {})
        if not isinstance(program, dict):
            raise ValueError("Registry program section is malformed")
        active_boundary_id = program.get("active_boundary_id")
        if not isinstance(active_boundary_id, str) or not active_boundary_id.strip():
            raise ValueError("Registry program.active_boundary_id is missing")
        boundary_id = active_boundary_id
    boundary = boundaries.get(boundary_id)
    if boundary is None:
        raise ValueError(f"Unknown boundary id: {boundary_id}")
    index = {
        "features": _row_lookup(registry, "features"),
        "profiles": _row_lookup(registry, "profiles"),
    }
    feature_ids = list(resolve_boundary_feature_ids(boundary, index))
    resolved_test_ids: list[str] = []
    for row in registry.get("features", []):
        if isinstance(row, dict) and row.get("id") in feature_ids:
            resolved_test_ids.extend(row.get("test_ids", []))
    return boundary_id, feature_ids, _resolve_tests_from_ids(registry, resolved_test_ids)


def _run_test_cases(
    *,
    repo_root: Path,
    target: dict[str, Any],
    tests: list[dict[str, Any]],
    evidence_output: str | Path | None,
    dry_run: bool,
) -> dict[str, Any]:
    resolved_tests = [
        {
            "id": row["id"],
            "title": row["title"],
            "kind": row["kind"],
            "path": row["path"],
            "execution": row.get("execution"),
        }
        for row in tests
    ]
    if dry_run:
        return {
            "passed": True,
            "dry_run": True,
            "target": target,
            "resolved_tests": resolved_tests,
        }

    execution_specs = {row["id"]: _validate_execution_contract(row) for row in tests}
    cases: list[dict[str, Any]] = []
    for row in tests:
        test_id = str(row["id"])
        execution = execution_specs[test_id]
        command = list(execution["argv"])
        if command and command[0] == "python":
            command[0] = sys.executable
        command_cwd = _resolve_command_cwd(repo_root, str(execution["cwd"]), test_id=test_id)
        env = os.environ.copy()
        env.update(execution["env"])
        expected_exit = int(execution["success"]["expected"])
        timeout_seconds = int(execution["timeout_seconds"])

        case = {
            "nodeid": test_id,
            "test_id": test_id,
            "title": row["title"],
            "kind": row["kind"],
            "path": row["path"],
            "runner": "command",
            "command": command,
            "cwd": Path(execution["cwd"]).as_posix(),
            "expected_exit_code": expected_exit,
        }
        try:
            result = subprocess.run(
                command,
                cwd=str(command_cwd),
                env=env,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            case["returncode"] = result.returncode
            case["outcome"] = "passed" if result.returncode == expected_exit else "failed"
            if result.stdout:
                case["stdout"] = result.stdout
            if result.stderr:
                case["stderr"] = result.stderr
        except subprocess.TimeoutExpired as exc:
            case["returncode"] = None
            case["outcome"] = "failed"
            case["stderr"] = f"Command timed out after {timeout_seconds} seconds"
            if exc.stdout:
                case["stdout"] = exc.stdout
            if exc.stderr:
                case["stderr_detail"] = exc.stderr
        except FileNotFoundError as exc:
            case["returncode"] = None
            case["outcome"] = "failed"
            case["stderr"] = str(exc)
        cases.append(case)

    resolved_test_ids = [row["id"] for row in tests]
    evidence_payload = _build_evidence_payload(
        repo_root=repo_root,
        target=target,
        resolved_test_ids=resolved_test_ids,
        cases=cases,
    )
    passed = evidence_payload["summary"]["failed"] == 0
    payload: dict[str, Any] = {
        "passed": passed,
        "dry_run": False,
        "target": target,
        "resolved_tests": resolved_tests,
        "summary": evidence_payload["summary"],
    }
    if evidence_output is not None:
        payload["evidence_output"] = _write_evidence_output(evidence_output, evidence_payload)
    else:
        payload["cases"] = cases
    return payload


def run_resolved_test_rows(
    repo_root: str | Path,
    *,
    target: dict[str, Any],
    tests: list[dict[str, Any]],
    evidence_output: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    return _run_test_cases(
        repo_root=Path(repo_root).resolve(),
        target=target,
        tests=tests,
        evidence_output=evidence_output,
        dry_run=dry_run,
    )


def run_tests(
    path: str | Path,
    *,
    test_ids: list[str],
    evidence_output: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(path)
    tests = _resolve_tests_from_ids(registry, test_ids)
    return _run_test_cases(
        repo_root=repo_root,
        target={"kind": "test", "ids": [row["id"] for row in tests]},
        tests=tests,
        evidence_output=evidence_output,
        dry_run=dry_run,
    )


def run_spec_tests(
    path: str | Path,
    *,
    spec_id: str,
    evidence_output: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(path)
    feature_ids, tests = _resolve_tests_for_spec(registry, spec_id)
    return _run_test_cases(
        repo_root=repo_root,
        target={"kind": "spec", "id": spec_id, "feature_ids": feature_ids},
        tests=tests,
        evidence_output=evidence_output,
        dry_run=dry_run,
    )


def run_boundary_tests(
    path: str | Path,
    *,
    boundary_id: str | None = None,
    evidence_output: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(path)
    resolved_boundary_id, feature_ids, tests = _resolve_tests_for_boundary(registry, boundary_id)
    return _run_test_cases(
        repo_root=repo_root,
        target={"kind": "boundary", "id": resolved_boundary_id, "feature_ids": feature_ids},
        tests=tests,
        evidence_output=evidence_output,
        dry_run=dry_run,
    )
