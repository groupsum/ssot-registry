from __future__ import annotations

import contextlib
import io
import subprocess
from pathlib import Path

from .catalog import resolve_selected_families
from .evidence import build_evidence_output, write_evidence_output

_PLUGIN_MODULE_NAME = "ssot_conformance.plugin"


def run_pytest_cases(
    *,
    repo_root: str | Path,
    profiles: list[str] | None = None,
    evidence_output: str | Path | None = None,
    pytest_args: list[str] | None = None,
) -> dict[str, object]:
    try:
        import pytest
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on test environment
        raise ValueError("pytest is required for `ssot conformance run`; install dev dependencies or use `uv run pytest`") from exc

    import importlib.resources as resources

    resolved_repo_root = Path(repo_root).resolve()
    selected_profiles = profiles or ["all"]
    selected_families = resolve_selected_families(profiles)
    case_root = resources.files("ssot_conformance.cases")
    args = [
        str(case_root),
        "-p",
        _PLUGIN_MODULE_NAME,
        f"--ssot-repo-root={resolved_repo_root}",
    ]
    for profile in selected_profiles:
        args.append(f"--ssot-conformance-profile={profile}")
    if evidence_output is not None:
        args.append(f"--ssot-conformance-evidence-output={evidence_output}")
    args.extend(pytest_args or [])

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        exit_code = pytest.main(args)
    payload: dict[str, object] = {
        "runner": "pytest",
        "passed": exit_code == 0,
        "pytest_exit_code": exit_code,
        "profiles": selected_profiles,
        "families": selected_families,
        "case_root": str(case_root),
    }
    if stdout_buffer.getvalue():
        payload["pytest_stdout"] = stdout_buffer.getvalue()
    if stderr_buffer.getvalue():
        payload["pytest_stderr"] = stderr_buffer.getvalue()
    if evidence_output is not None:
        evidence_path = Path(evidence_output)
        if evidence_path.exists():
            payload["evidence_output"] = evidence_path.as_posix()
        else:
            payload["evidence_output"] = write_evidence_output(
                evidence_path,
                build_evidence_output(
                    repo_root=str(resolved_repo_root),
                    selected_profiles=selected_profiles,
                    selected_families=selected_families,
                    cases=[],
                ),
            )
    return payload


def run_command_suite(
    *,
    repo_root: str | Path,
    profiles: list[str] | None = None,
    evidence_output: str | Path | None = None,
    command: list[str],
) -> dict[str, object]:
    if not command:
        raise ValueError("command runner requires a command after `--command`")

    resolved_repo_root = Path(repo_root).resolve()
    selected_profiles = profiles or ["all"]
    selected_families = resolve_selected_families(profiles)
    result = subprocess.run(
        command,
        cwd=str(resolved_repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    outcome = "passed" if result.returncode == 0 else "failed"
    case = {
        "nodeid": "command-suite",
        "runner": "command",
        "command": list(command),
        "outcome": outcome,
        "returncode": result.returncode,
    }
    if result.stdout:
        case["stdout"] = result.stdout
    if result.stderr:
        case["stderr"] = result.stderr
    payload: dict[str, object] = {
        "runner": "command",
        "passed": result.returncode == 0,
        "command_exit_code": result.returncode,
        "command": list(command),
        "profiles": selected_profiles,
        "families": selected_families,
    }
    if evidence_output is not None:
        payload["evidence_output"] = write_evidence_output(
            evidence_output,
            build_evidence_output(
                repo_root=str(resolved_repo_root),
                selected_profiles=selected_profiles,
                selected_families=selected_families,
                cases=[case],
            ),
        )
    else:
        payload["cases"] = [case]
    return payload
