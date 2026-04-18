from __future__ import annotations

from typing import TypedDict


class ClaimRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    tier: str
    kind: str
    description: str
    feature_ids: list[str]
    test_ids: list[str]
    evidence_ids: list[str]
