from __future__ import annotations

from pathlib import Path

import pytest

from ssot_registry.acl.policy import AclPolicy, LinuxAclAdapter, WindowsAclAdapter
from ssot_registry.acl.wrapper import main as acl_wrapper_main
from ssot_registry.control.events import format_sse_event
from ssot_registry.guards.completion import evaluate_completion_guard
from ssot_registry.watch.git_status import parse_porcelain_v2_z
from ssot_registry.watch.observer import classify_changed_paths

from .test_worker_control_plane import _registry


def test_acl_policy_generates_linux_and_windows_commands(tmp_path: Path) -> None:
    linux = AclPolicy(tmp_path, adapter=LinuxAclAdapter())
    linux_commands = linux.grant_commands("worker01", ["src/a"])
    assert linux_commands[0].argv[:4] == ("setfacl", "-R", "-m", "u:worker01:rwX")
    assert linux_commands[1].argv[:5] == ("setfacl", "-R", "-d", "-m", "u:worker01:rwX")

    windows = AclPolicy(tmp_path, adapter=WindowsAclAdapter())
    windows_commands = windows.grant_commands("worker01", ["src/a"])
    assert windows_commands[0].argv[:3] == ("icacls", str(tmp_path / "src/a"), "/grant")

    with pytest.raises(ValueError, match="forbidden"):
        linux.grant_commands("worker01", [".ssot/control/state.sqlite"])
    with pytest.raises(ValueError, match="path escapes"):
        linux.grant_commands("worker01", [tmp_path.parent / "outside"])


def test_acl_wrapper_dry_run_and_invalid_path_exit(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = acl_wrapper_main(["grant", str(tmp_path), "worker01", "src/a", "--dry-run"])
    assert exit_code == 0
    assert "worker01" in capsys.readouterr().out

    with pytest.raises(ValueError, match="forbidden"):
        acl_wrapper_main(["grant", str(tmp_path), "worker01", ".ssot/registry.json", "--dry-run"])


def test_completion_guard_rejects_unleased_and_forbidden_paths(tmp_path: Path) -> None:
    registry = _registry(tmp_path, t1_ready=True, t2_ready=False)
    lease = {
        "lease_id": "lease:test",
        "feature_id": "feat:control.worker",
        "to_tier": "T1",
        "path_roots": ["tests/control", ".ssot/evidence/control/worker"],
    }
    result = {
        "changed_paths": ["src/outside.py", ".ssot/registry.json"],
        "tests_run": [{"command": "pytest", "exit_code": 0}],
        "evidence_paths": [".ssot/evidence/control/worker/t1.json"],
        "requested_tier": "T1",
    }

    report = evaluate_completion_guard(registry, lease, result, repo_root=tmp_path)

    assert report["passed"] is False
    assert "completion changed_paths must be under active lease roots" in report["failures"]
    assert "completion changed_paths must not include forbidden paths" in report["failures"]


def test_completion_guard_rejects_missing_outputs_and_unknown_tier_claim(tmp_path: Path) -> None:
    registry = _registry(tmp_path, t1_ready=True, t2_ready=False)
    lease = {
        "lease_id": "lease:test",
        "feature_id": "feat:control.worker",
        "to_tier": "T2",
        "path_roots": ["tests/control", ".ssot/evidence/control/worker"],
    }
    result = {
        "changed_paths": ["tests/control/test_worker.py"],
        "tests_run": [{"command": "pytest", "exit_code": 0}],
        "evidence_paths": [".ssot/evidence/control/worker/missing.json"],
        "requested_tier": "T2",
    }

    report = evaluate_completion_guard(registry, lease, result, repo_root=tmp_path)

    assert report["passed"] is False
    assert "completion evidence_paths must exist" in report["failures"]
    assert any("T2 gate requires passed linked evidence" in failure for failure in report["failures"])


def test_completion_guard_accepts_leased_paths_and_tier_gate(tmp_path: Path) -> None:
    registry = _registry(tmp_path, t1_ready=True, t2_ready=False)
    lease = {
        "lease_id": "lease:test",
        "feature_id": "feat:control.worker",
        "to_tier": "T1",
        "path_roots": ["tests/control", ".ssot/evidence/control/worker"],
    }
    result = {
        "changed_paths": ["tests/control/test_worker.py", ".ssot/evidence/control/worker/t1.json"],
        "tests_run": [{"command": "pytest", "exit_code": 0}],
        "evidence_paths": [".ssot/evidence/control/worker/t1.json"],
        "requested_tier": "T1",
    }

    report = evaluate_completion_guard(registry, lease, result, repo_root=tmp_path)

    assert report["passed"] is True
    assert report["checks"]["tier_gate_passed"] is True


def test_repo_watch_classifies_authorized_and_forbidden_paths() -> None:
    scan = classify_changed_paths(
        ["src/a/file.py", "src/b/file.py", ".ssot/registry.json"],
        [{"lease_id": "lease:a", "worker_id": "worker-01", "campaign_id": "camp:test", "feature_id": "feat:a", "path": "src/a"}],
    )

    assert scan.authorized_paths == ["src/a/file.py"]
    assert scan.out_of_lease_paths == ["src/b/file.py"]
    assert scan.forbidden_paths == [".ssot/registry.json"]


def test_repo_watch_classifies_control_and_git_as_forbidden() -> None:
    scan = classify_changed_paths(
        [".ssot/control/state.sqlite", ".git/index", "docs/readme.md"],
        [],
    )

    assert scan.forbidden_paths == [".git/index", ".ssot/control/state.sqlite"]
    assert scan.out_of_lease_paths == ["docs/readme.md"]


def test_git_status_parser_and_sse_format() -> None:
    output = b"1 .M N... 100644 100644 100644 abc abc src/a.py\0? tests/new.py\0"
    assert parse_porcelain_v2_z(output) == ["src/a.py", "tests/new.py"]

    rendered = format_sse_event({"event_id": 7, "kind": "registry_updated", "payload": {"ok": True}})
    assert rendered.startswith("id: 7\nevent: registry_updated\n")
    assert rendered.endswith("\n\n")
