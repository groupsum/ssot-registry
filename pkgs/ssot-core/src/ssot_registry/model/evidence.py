from __future__ import annotations

from typing import TypedDict


class EvidenceRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    kind: str
    tier: str
    path: str
    claim_ids: list[str]
    test_ids: list[str]
