from __future__ import annotations

from pathlib import Path

CONFORMANCE_FAMILY = "document"


def test_document_contract(ssot_repo_root, ssot_registry) -> None:
    for section in ("adrs", "specs"):
        for row in ssot_registry[section]:
            path = Path(ssot_repo_root) / row["path"]
            assert path.exists(), row["id"]
            if row["origin"] == "repo-local":
                assert row["number"] >= 1000, row["id"]
            else:
                assert row["number"] < 1000, row["id"]
