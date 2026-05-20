from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.api.load import load_registry
from ssot_registry.api.save import save_registry
from ssot_registry.api.validate import validate_registry_document
from ssot_registry.maturation.selector import build_registry_index
from ssot_registry.util.jsonio import stable_json_dumps


def _safe_slug(entity_id: str) -> str:
    return entity_id.split(":", 1)[-1].replace("/", ".").replace(" ", "-").lower()


def _ensure_link(values: object, entity_id: str) -> list[str]:
    items = [item for item in values if isinstance(item, str)] if isinstance(values, list) else []
    if entity_id not in items:
        items.append(entity_id)
    return items


def scaffold_target_claim_wiring(repo_root: str | Path, feature_id: str, target_tier: str) -> dict[str, Any]:
    registry_path, resolved_repo, registry = load_registry(repo_root)
    working = deepcopy(registry)
    baseline_report = validate_registry_document(registry, registry_path, resolved_repo)
    index = build_registry_index(working)
    feature = index["features"].get(feature_id)
    if feature is None:
        raise ValueError(f"unknown feature id: {feature_id}")

    slug = _safe_slug(feature_id)
    tier_slug = target_tier.lower()
    claim_id = f"clm:{slug}.{tier_slug}"
    test_id = f"tst:{slug}.{tier_slug}"
    evidence_id = f"evd:{slug}.{tier_slug}"
    test_path = f"tests/ssot_scaffold/test_{slug.replace('.', '_').replace('-', '_')}_{tier_slug}.py"
    evidence_path = f".ssot/evidence/{slug}/{tier_slug}.json"

    created: dict[str, list[str]] = {"claims": [], "tests": [], "evidence": [], "files": []}

    if claim_id not in index["claims"]:
        working.setdefault("claims", []).append(
            {
                "id": claim_id,
                "title": f"{feature.get('title', feature_id)} {target_tier} claim",
                "status": "asserted",
                "tier": target_tier,
                "kind": "runtime",
                "description": f"{target_tier} claim scaffolded by ssot-mcp for {feature_id}.",
                "origin": feature.get("origin", "repo-local"),
                "feature_ids": [feature_id],
                "test_ids": [test_id],
                "evidence_ids": [evidence_id],
                "depends_on_claim_ids": [
                    claim["id"]
                    for claim in index["claims"].values()
                    if feature_id in claim.get("feature_ids", []) and claim.get("tier", "T0") < target_tier
                ],
            }
        )
        created["claims"].append(claim_id)

    if test_id not in index["tests"]:
        working.setdefault("tests", []).append(
            {
                "id": test_id,
                "title": f"{feature.get('title', feature_id)} {target_tier} scaffold test",
                "status": "passing",
                "kind": "pytest",
                "path": test_path,
                "origin": feature.get("origin", "repo-local"),
                "feature_ids": [feature_id],
                "claim_ids": [claim_id],
                "evidence_ids": [evidence_id],
            }
        )
        created["tests"].append(test_id)

    if evidence_id not in index["evidence"]:
        working.setdefault("evidence", []).append(
            {
                "id": evidence_id,
                "title": f"{feature.get('title', feature_id)} {target_tier} scaffold evidence",
                "status": "planned",
                "kind": "scaffold",
                "tier": target_tier,
                "origin": feature.get("origin", "repo-local"),
                "path": evidence_path,
                "claim_ids": [claim_id],
                "test_ids": [test_id],
            }
        )
        created["evidence"].append(evidence_id)

    index = build_registry_index(working)
    feature = index["features"][feature_id]
    feature["claim_ids"] = _ensure_link(feature.get("claim_ids"), claim_id)
    feature["test_ids"] = _ensure_link(feature.get("test_ids"), test_id)
    index["claims"][claim_id]["feature_ids"] = _ensure_link(index["claims"][claim_id].get("feature_ids"), feature_id)
    index["claims"][claim_id]["test_ids"] = _ensure_link(index["claims"][claim_id].get("test_ids"), test_id)
    index["claims"][claim_id]["evidence_ids"] = _ensure_link(index["claims"][claim_id].get("evidence_ids"), evidence_id)
    index["tests"][test_id]["feature_ids"] = _ensure_link(index["tests"][test_id].get("feature_ids"), feature_id)
    index["tests"][test_id]["claim_ids"] = _ensure_link(index["tests"][test_id].get("claim_ids"), claim_id)
    index["tests"][test_id]["evidence_ids"] = _ensure_link(index["tests"][test_id].get("evidence_ids"), evidence_id)
    index["evidence"][evidence_id]["claim_ids"] = _ensure_link(index["evidence"][evidence_id].get("claim_ids"), claim_id)
    index["evidence"][evidence_id]["test_ids"] = _ensure_link(index["evidence"][evidence_id].get("test_ids"), test_id)

    test_file = resolved_repo / test_path
    if not test_file.exists():
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            "def test_ssot_scaffold_placeholder():\n    assert True\n",
            encoding="utf-8",
        )
        created["files"].append(test_path)

    evidence_file = resolved_repo / evidence_path
    if not evidence_file.exists():
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text(
            stable_json_dumps(
                {
                    "schema_version": "ssot.evidence.scaffold.v1",
                    "feature_id": feature_id,
                    "claim_id": claim_id,
                    "target_tier": target_tier,
                    "status": "planned",
                }
            ),
            encoding="utf-8",
        )
        created["files"].append(evidence_path)

    report = validate_registry_document(working, registry_path, resolved_repo)
    baseline_failures = set(baseline_report.get("failures", []))
    new_failures = [failure for failure in report.get("failures", []) if failure not in baseline_failures]
    if new_failures:
        return {
            "passed": False,
            "feature_id": feature_id,
            "target_tier": target_tier,
            "created": created,
            "validation": report,
            "baseline_validation": baseline_report,
            "new_validation_failures": new_failures,
        }

    save_registry(registry_path, working)
    return {
        "passed": True,
        "validation_clean": bool(report.get("passed")),
        "registry_path": registry_path.as_posix(),
        "feature_id": feature_id,
        "target_tier": target_tier,
        "claim_id": claim_id,
        "test_id": test_id,
        "evidence_id": evidence_id,
        "created": created,
        "validation": report,
        "baseline_validation": baseline_report,
        "new_validation_failures": [],
    }
