from __future__ import annotations

from pathlib import Path

from ssot_registry.guards.claim_closure import evaluate_claim_guard
from ssot_registry.validators.identity import build_index
from .load import load_registry


def evaluate_claims(path: str | Path, claim_id: str | None = None) -> dict[str, object]:
    registry_path, _repo_root, registry = load_registry(path)
    failures: list[str] = []
    index = build_index(registry, failures)

    if claim_id is not None and claim_id not in index["claims"]:
        return {
            "passed": False,
            "registry_path": registry_path.as_posix(),
            "failures": failures + [f"Missing claim {claim_id}"],
            "claims": [],
        }

    selected = (
        [index["claims"][claim_id]]
        if claim_id is not None
        else [index["claims"][entity_id] for entity_id in sorted(index["claims"])]
    )
    reports = [evaluate_claim_guard(claim, index, registry.get("guard_policies", {})) for claim in selected]
    all_failures = failures + [failure for report in reports for failure in report["failures"]]
    return {
        "passed": not all_failures,
        "registry_path": registry_path.as_posix(),
        "failures": sorted(set(all_failures)),
        "claims": reports,
    }
