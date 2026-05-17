from .catalog import CATALOG_VERSION, build_catalog_slice, list_profiles, resolve_selected_families
from .discovery import discover_cases
from .evidence import build_evidence_output, write_evidence_output
from .origin import apply_origin_conformance, discover_origin_obligations, list_origin_templates, plan_origin_conformance


def plan_scaffold(*args, **kwargs):
    from .scaffold import plan_scaffold as _plan_scaffold

    return _plan_scaffold(*args, **kwargs)


def apply_scaffold(*args, **kwargs):
    from .scaffold import apply_scaffold as _apply_scaffold

    return _apply_scaffold(*args, **kwargs)

__all__ = [
    "CATALOG_VERSION",
    "build_catalog_slice",
    "list_profiles",
    "resolve_selected_families",
    "discover_cases",
    "build_evidence_output",
    "write_evidence_output",
    "apply_origin_conformance",
    "discover_origin_obligations",
    "list_origin_templates",
    "plan_origin_conformance",
    "plan_scaffold",
    "apply_scaffold",
]
