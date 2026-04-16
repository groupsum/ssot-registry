from __future__ import annotations

from typing import TypedDict


class IssueRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    severity: str
    description: str
    plan: dict[str, object]
    feature_ids: list[str]
    claim_ids: list[str]
    test_ids: list[str]
    evidence_ids: list[str]
    risk_ids: list[str]
    release_blocking: bool
