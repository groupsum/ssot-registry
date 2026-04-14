from __future__ import annotations

from typing import TypedDict


class FeatureRow(TypedDict, total=False):
    id: str
    title: str
    description: str
    implementation_status: str
    lifecycle: dict[str, object]
    plan: dict[str, object]
    claim_ids: list[str]
    test_ids: list[str]
    requires: list[str]
