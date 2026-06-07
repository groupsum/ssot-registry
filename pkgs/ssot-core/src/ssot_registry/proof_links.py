from __future__ import annotations

from typing import Any


Index = dict[str, dict[str, dict[str, Any]]]


def evidence_for_claim(claim_id: str, index: Index) -> list[dict[str, Any]]:
    return [
        evidence
        for evidence in index["evidence"].values()
        if claim_id in evidence.get("claim_ids", [])
    ]


def tests_for_evidence(evidence: dict[str, Any], index: Index) -> list[dict[str, Any]]:
    return [
        test
        for test_id in evidence.get("test_ids", [])
        if (test := index["tests"].get(test_id)) is not None
    ]


def producer_tests_for_claim(claim_id: str, index: Index) -> list[dict[str, Any]]:
    tests: dict[str, dict[str, Any]] = {}
    for evidence in evidence_for_claim(claim_id, index):
        for test in tests_for_evidence(evidence, index):
            tests[str(test["id"])] = test
    return [tests[test_id] for test_id in sorted(tests)]

