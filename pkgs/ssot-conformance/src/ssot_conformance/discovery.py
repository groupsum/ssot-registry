from __future__ import annotations

from .catalog import build_catalog_slice


def discover_cases(profiles: list[str] | None = None) -> dict[str, object]:
    catalog = build_catalog_slice(profiles)
    return {
        "passed": True,
        "catalog_version": catalog["catalog_version"],
        "profiles": catalog["profiles"],
        "families": catalog["families"],
        "cases": [
            {
                "id": row["id"],
                "title": row["title"],
                "kind": row["kind"],
                "path": row["path"],
                "feature_ids": row["feature_ids"],
                "claim_ids": row["claim_ids"],
                "evidence_ids": row["evidence_ids"],
            }
            for row in catalog["tests"]
        ],
    }
