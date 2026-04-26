from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - import depends on environment
    import pytest
except ModuleNotFoundError:  # pragma: no cover - import depends on environment
    pytest = None

from .catalog import resolve_selected_families
from .evidence import build_evidence_output, write_evidence_output


def pytest_addoption(parser: Any) -> None:
    group = parser.getgroup("ssot-conformance")
    group.addoption("--ssot-repo-root", action="store", default=".", help="Target repository root for SSOT conformance evaluation.")
    group.addoption(
        "--ssot-conformance-profile",
        action="append",
        default=[],
        help="Conformance profile or family to execute. May be repeated.",
    )
    group.addoption(
        "--ssot-conformance-evidence-output",
        action="store",
        default=None,
        help="Write machine-readable conformance evidence JSON to this path.",
    )


def pytest_configure(config: Any) -> None:
    config._ssot_conformance_reports = []


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    selected_families = set(resolve_selected_families(config.getoption("ssot_conformance_profile")))
    kept: list[Any] = []
    deselected: list[Any] = []
    for item in items:
        family = getattr(item.module, "CONFORMANCE_FAMILY", None)
        if family is None or family in selected_families:
            kept.append(item)
        else:
            deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


if pytest is not None:
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(item: Any, call: Any) -> Any:
        outcome = yield
        report = outcome.get_result()
        if report.when != "call":
            return
        item.config._ssot_conformance_reports.append(
            {
                "nodeid": report.nodeid,
                "family": getattr(item.module, "CONFORMANCE_FAMILY", None),
                "outcome": report.outcome,
            }
        )


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    output = session.config.getoption("ssot_conformance_evidence_output")
    if output is None:
        return
    selected_profiles = session.config.getoption("ssot_conformance_profile") or ["all"]
    selected_families = resolve_selected_families(selected_profiles)
    payload = build_evidence_output(
        repo_root=str(Path(session.config.getoption("ssot_repo_root")).resolve()),
        selected_profiles=list(selected_profiles),
        selected_families=selected_families,
        cases=list(session.config._ssot_conformance_reports),
    )
    write_evidence_output(output, payload)


if pytest is not None:
    @pytest.fixture(scope="session")
    def ssot_repo_root(pytestconfig: Any) -> Path:
        return Path(pytestconfig.getoption("ssot_repo_root")).resolve()


    @pytest.fixture(scope="session")
    def ssot_registry(ssot_repo_root: Path) -> dict[str, object]:
        import json

        return json.loads((ssot_repo_root / ".ssot" / "registry.json").read_text(encoding="utf-8"))
