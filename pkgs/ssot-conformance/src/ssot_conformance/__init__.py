from .catalog import CATALOG_VERSION, list_profiles, resolve_selected_families
from .discovery import discover_cases
from .evidence import build_evidence_output, write_evidence_output


def run_pytest_cases(*args, **kwargs):
    from .runner import run_pytest_cases as _run_pytest_cases

    return _run_pytest_cases(*args, **kwargs)


def run_command_suite(*args, **kwargs):
    from .runner import run_command_suite as _run_command_suite

    return _run_command_suite(*args, **kwargs)


def plan_scaffold(*args, **kwargs):
    from .scaffold import plan_scaffold as _plan_scaffold

    return _plan_scaffold(*args, **kwargs)


def apply_scaffold(*args, **kwargs):
    from .scaffold import apply_scaffold as _apply_scaffold

    return _apply_scaffold(*args, **kwargs)

__all__ = [
    "CATALOG_VERSION",
    "list_profiles",
    "resolve_selected_families",
    "discover_cases",
    "build_evidence_output",
    "write_evidence_output",
    "run_pytest_cases",
    "run_command_suite",
    "plan_scaffold",
    "apply_scaffold",
]
