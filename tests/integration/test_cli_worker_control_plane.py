from __future__ import annotations

import json
from pathlib import Path

from tests.helpers import run_cli, workspace_tempdir
from tests.unit.test_worker_control_plane import _registry, _write_registry


def test_worker_control_plane_cli_claims_and_lists_slice() -> None:
    temp_dir = workspace_tempdir()
    try:
        repo = Path(temp_dir.name) / "repo"
        repo.mkdir()
        _write_registry(repo, _registry(repo, t1_ready=False, t2_ready=False))

        claim = run_cli(
            "worker",
            "claim-next",
            str(repo),
            "--worker-id",
            "worker-01",
            "--campaign-id",
            "camp:test",
        )
        assert claim.returncode == 0, claim.stderr
        payload = json.loads(claim.stdout)
        assert payload["kind"] == "lease_granted"
        lease_id = payload["lease"]["lease_id"]

        leases = run_cli("leases", "list", str(repo), "--status", "active")
        assert leases.returncode == 0, leases.stderr
        lease_payload = json.loads(leases.stdout)
        assert [lease["lease_id"] for lease in lease_payload["leases"]] == [lease_id]

        status = run_cli("campaign", "status", str(repo), "--campaign-id", "camp:test")
        assert status.returncode == 0, status.stderr
        assert json.loads(status.stdout)["active_lease_count"] == 1

        events = run_cli("worker", "events", str(repo), "--worker-id", "worker-01")
        assert events.returncode == 0, events.stderr
        assert any(event["kind"] == "maturation_lease_acquired" for event in json.loads(events.stdout)["events"])
    finally:
        temp_dir.cleanup()


def test_worker_control_plane_cli_ack_renew_and_bad_sequences() -> None:
    temp_dir = workspace_tempdir()
    try:
        repo = Path(temp_dir.name) / "repo"
        repo.mkdir()
        _write_registry(repo, _registry(repo, t1_ready=False, t2_ready=False))

        claim = run_cli(
            "worker",
            "claim-next",
            str(repo),
            "--worker-id",
            "worker-01",
            "--campaign-id",
            "camp:test",
            "--ttl-seconds",
            "30",
        )
        assert claim.returncode == 0, claim.stderr
        lease = json.loads(claim.stdout)["lease"]

        duplicate = run_cli("worker", "claim-next", str(repo), "--worker-id", "worker-02", "--campaign-id", "camp:test")
        assert duplicate.returncode == 0, duplicate.stderr
        assert json.loads(duplicate.stdout)["kind"] == "no_work"

        renew = run_cli(
            "worker",
            "renew",
            str(repo),
            "--worker-id",
            "worker-01",
            "--lease-id",
            lease["lease_id"],
            "--fencing-token",
            str(lease["fencing_token"]),
        )
        assert renew.returncode == 0, renew.stderr

        stale = run_cli(
            "worker",
            "renew",
            str(repo),
            "--worker-id",
            "worker-01",
            "--lease-id",
            lease["lease_id"],
            "--fencing-token",
            "999",
        )
        assert stale.returncode == 1
        assert "stale fencing token" in json.loads(stale.stdout)["error"]

        events = json.loads(run_cli("worker", "events", str(repo), "--worker-id", "worker-01").stdout)["events"]
        ack = run_cli(
            "worker",
            "ack-events",
            str(repo),
            "--worker-id",
            "worker-01",
            "--event-ids",
            *[str(event["event_id"]) for event in events],
            "--action",
            "integration-ack",
        )
        assert ack.returncode == 0, ack.stderr
        assert json.loads(ack.stdout)["action"] == "integration-ack"

        missing = run_cli("leases", "inspect", str(repo), "--lease-id", "lease:missing")
        assert missing.returncode == 1
        assert "unknown lease" in json.loads(missing.stdout)["error"]
    finally:
        temp_dir.cleanup()
