from __future__ import annotations

from typing import TypedDict


class ProfileRow(TypedDict, total=False):
    id: str
    title: str
    description: str
    status: str
    kind: str
    feature_ids: list[str]
    profile_ids: list[str]
    claim_tier: str | None
    evaluation: dict[str, object]
