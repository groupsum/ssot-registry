from __future__ import annotations

from typing import TypedDict


class TestRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    kind: str
    path: str
    feature_ids: list[str]
    claim_ids: list[str]
    evidence_ids: list[str]
