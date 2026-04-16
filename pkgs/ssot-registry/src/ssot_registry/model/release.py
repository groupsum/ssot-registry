from __future__ import annotations

from typing import TypedDict


class ReleaseRow(TypedDict, total=False):
    id: str
    version: str
    status: str
    boundary_id: str
    claim_ids: list[str]
    evidence_ids: list[str]
