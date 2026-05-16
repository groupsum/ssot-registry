from __future__ import annotations

from typing import Any

__all__ = [
    "evaluate_claim_guard",
    "evaluate_claim_tier_gate",
    "evaluate_release_certification_guard",
    "evaluate_release_promotion_guard",
    "evaluate_release_publication_guard",
    "evaluate_feature_lifecycle_transition_guard",
    "apply_status_transition",
    "assert_mutable_document",
    "validate_create_status",
    "validate_transition",
    "apply_supersession",
]


def __getattr__(name: str) -> Any:
    if name == "evaluate_claim_guard":
        from .claim_closure import evaluate_claim_guard

        return evaluate_claim_guard
    if name == "evaluate_claim_tier_gate":
        from .claim_tier_gates import evaluate_claim_tier_gate

        return evaluate_claim_tier_gate
    if name == "evaluate_release_certification_guard":
        from .certification import evaluate_release_certification_guard

        return evaluate_release_certification_guard
    if name == "evaluate_release_promotion_guard":
        from .promotion import evaluate_release_promotion_guard

        return evaluate_release_promotion_guard
    if name == "evaluate_release_publication_guard":
        from .publication import evaluate_release_publication_guard

        return evaluate_release_publication_guard
    if name == "evaluate_feature_lifecycle_transition_guard":
        from .lifecycle import evaluate_feature_lifecycle_transition_guard

        return evaluate_feature_lifecycle_transition_guard
    if name in {"apply_status_transition", "assert_mutable_document", "validate_create_status", "validate_transition"}:
        from . import document_lifecycle

        return getattr(document_lifecycle, name)
    if name == "apply_supersession":
        from .document_supersession import apply_supersession

        return apply_supersession
    raise AttributeError(name)
