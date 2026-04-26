from __future__ import annotations

from pathlib import Path

from ssot_registry.util.jcs import dump_jcs_json


def build_evidence_output(
    *,
    repo_root: str,
    selected_profiles: list[str],
    selected_families: list[str],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "total": len(cases)}
    for row in cases:
        outcome = str(row.get("outcome", "unknown"))
        if outcome in summary:
            summary[outcome] += 1
    return {
        "kind": "ssot-conformance-evidence",
        "repo_root": repo_root,
        "profiles": selected_profiles,
        "families": selected_families,
        "summary": summary,
        "cases": cases,
    }


def write_evidence_output(path: str | Path, payload: dict[str, object]) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_jcs_json(payload), encoding="utf-8")
    return target.as_posix()
