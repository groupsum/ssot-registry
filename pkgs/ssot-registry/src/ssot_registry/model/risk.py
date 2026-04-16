from __future__ import annotations

from typing import TypedDict


class RiskRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    severity: str
    description: str
    feature_ids: list[str]
    claim_ids: list[str]
    test_ids: list[str]
    evidence_ids: list[str]
    issue_ids: list[str]
    release_blocking: bool
