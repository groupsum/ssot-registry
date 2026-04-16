from __future__ import annotations

from typing import TypedDict


class BoundaryRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    frozen: bool
    feature_ids: list[str]
    profile_ids: list[str]
