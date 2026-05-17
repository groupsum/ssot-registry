from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
for path in (
    REPO_ROOT / "pkgs" / "ssot-core" / "src",
    REPO_ROOT / "pkgs" / "ssot-contracts" / "src",
    REPO_ROOT / "pkgs" / "ssot-conformance" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ssot_conformance.origin import (  # noqa: E402
    GENERATED_MARKER,
    apply_origin_conformance,
    discover_origin_obligations,
    list_origin_templates,
    plan_origin_conformance,
    render_origin_test,
)
from tests.helpers import temp_repo_from_fixture  # noqa: E402


def _repo(request: pytest.FixtureRequest) -> Path:
    temp_dir = temp_repo_from_fixture("repo_valid")
    request.addfinalizer(temp_dir.cleanup)
    return Path(temp_dir.name) / "repo"


def _registry(repo: Path) -> dict[str, object]:
    return json.loads((repo / ".ssot" / "registry.json").read_text(encoding="utf-8"))


def test_origin_template_catalog_lists_adr_and_spec_templates() -> None:
    assert {row["id"] for row in list_origin_templates()} == {"origin-adr-compliance", "origin-spec-compliance"}


def test_origin_template_renderer_outputs_deterministic_file(request: pytest.FixtureRequest) -> None:
    obligation = discover_origin_obligations(_repo(request), kinds=["adr"])[0]
    assert render_origin_test(obligation) == render_origin_test(obligation)
    assert render_origin_test(obligation).startswith(GENERATED_MARKER)


def test_origin_template_metadata_embeds_stable_links(request: pytest.FixtureRequest) -> None:
    rendered = render_origin_test(discover_origin_obligations(_repo(request), kinds=["spec"])[0])
    metadata_line = next(line for line in rendered.splitlines() if line.startswith("# ssot-conformance-metadata: "))
    metadata = json.loads(metadata_line.split(": ", 1)[1])
    assert metadata["template_id"] == "origin-spec-compliance"
    assert metadata["feature_id"].startswith("feat:origin.spec.")
    assert metadata["test_id"].startswith("tst:pytest.origin.spec.")


def test_origin_template_idempotency_preserves_existing_rows(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    first = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    second = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    assert first["created"]["features"]
    assert second["created"]["features"] == []
    assert set(second["unchanged"]["features"]) == set(first["created"]["features"])


def test_origin_template_conflict_guard_refuses_local_edits(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)
    target = repo / result["created"]["files"][0]
    target.write_text("def test_local_edit():\n    assert True\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Refusing to overwrite"):
        apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)


def test_origin_template_dry_run_reports_without_mutation(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    plan = plan_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    assert plan["missing"]["features"]
    assert not (repo / plan["generated_files"][0]["path"]).exists()


def test_downstream_origin_obligation_discovery_finds_adrs_and_specs(request: pytest.FixtureRequest) -> None:
    kinds = {row["kind"] for row in discover_origin_obligations(_repo(request))}
    assert kinds == {"adr", "spec"}


def test_downstream_origin_row_generation_creates_feature_and_test_rows(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    registry = _registry(repo)
    feature_ids = {row["id"] for row in registry["features"]}
    test_ids = {row["id"] for row in registry["tests"]}
    assert set(result["created"]["features"]).issubset(feature_ids)
    assert set(result["created"]["tests"]).issubset(test_ids)


def test_downstream_origin_claim_evidence_opt_in_creates_rows(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)
    assert result["created"]["claims"]
    assert result["created"]["evidence"]


def test_downstream_origin_test_file_generation_writes_files(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    assert all((repo / path).exists() for path in result["created"]["files"])


def test_downstream_origin_execution_metadata_populates_command_contract(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)
    tests = {row["id"]: row for row in _registry(repo)["tests"]}
    execution = tests[result["created"]["tests"][0]]["execution"]
    assert execution["mode"] == "command"
    assert execution["argv"][:3] == ["python", "-m", "pytest"]


def test_origin_adr_compliance_tests_are_generated(request: pytest.FixtureRequest) -> None:
    result = apply_origin_conformance(_repo(request), kinds=["adr"], include_claims=True, include_evidence=True)
    assert all("/test_adr_" in f"/{path}" for path in result["created"]["files"])


def test_origin_spec_compliance_tests_are_generated(request: pytest.FixtureRequest) -> None:
    result = apply_origin_conformance(_repo(request), kinds=["spec"], include_claims=True, include_evidence=True)
    assert all("/test_spec_" in f"/{path}" for path in result["created"]["files"])


def test_origin_compliance_evidence_output_is_machine_readable(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["adr"], include_claims=True, include_evidence=True)
    payload = json.loads((repo / result["report_path"]).read_text(encoding="utf-8"))
    assert payload["passed"] is True
    assert payload["obligation_count"] == len(result["obligations"])


def test_origin_compliance_report_summarizes_created_rows(request: pytest.FixtureRequest) -> None:
    repo = _repo(request)
    result = apply_origin_conformance(repo, kinds=["spec"], include_claims=True, include_evidence=True)
    payload = json.loads((repo / result["report_path"]).read_text(encoding="utf-8"))
    assert payload["created"]["features"] == result["created"]["features"]
    assert payload["generated_files"]
