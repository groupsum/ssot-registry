from __future__ import annotations

from typing import TypedDict


class TestExecutionSuccess(TypedDict, total=False):
    type: str
    expected: int


class TestExecution(TypedDict, total=False):
    mode: str
    argv: list[str]
    cwd: str
    env: dict[str, str]
    timeout_seconds: int
    success: TestExecutionSuccess


class TestRow(TypedDict, total=False):
    id: str
    title: str
    status: str
    kind: str
    path: str
    feature_ids: list[str]
    claim_ids: list[str]
    evidence_ids: list[str]
    execution: TestExecution
