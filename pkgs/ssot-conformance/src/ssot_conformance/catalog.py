from __future__ import annotations

from copy import deepcopy


CATALOG_VERSION = "0.2.14.dev1"

FAMILIES = (
    "package-layout",
    "plugin",
    "registry",
    "document",
    "id",
    "spec-adr",
    "feature-spec",
    "proof-chain",
    "boundary-release",
    "scaffold",
    "evidence-output",
    "cli",
)

PROFILE_DEFINITIONS = {
    "all": list(FAMILIES),
    "core": list(FAMILIES),
    **{family: [family] for family in FAMILIES},
}

_FEATURES = {
    "package-layout": [
        ("feat:conformance.package-layout", "SSOT conformance package layout", "Provide the ssot-conformance workspace package structure and package metadata.", ["spc:0524"], ["clm:conformance.package-layout.t2"], ["tst:pytest.conformance.package-layout"]),
    ],
    "plugin": [
        ("feat:conformance.pytest-plugin", "SSOT conformance pytest plugin", "Expose pytest integration for running portable SSOT conformance cases against a target repository.", ["spc:0524"], ["clm:conformance.pytest-plugin.t2"], ["tst:pytest.conformance.pytest-plugin"]),
        ("feat:conformance.case-discovery", "SSOT conformance case discovery", "Discover selected conformance profiles and case families before execution or scaffolding.", ["spc:0524", "spc:0525"], ["clm:conformance.case-discovery.t2"], ["tst:pytest.conformance.pytest-plugin"]),
    ],
    "registry": [
        ("feat:conformance.registry-contract", "Registry conformance contract cases", "Validate registry existence, schema version, required sections, packaged schema conformance, and canonical JSON expectations.", ["spc:0525"], ["clm:conformance.registry-contract.t2"], ["tst:pytest.conformance.registry-contract"]),
    ],
    "document": [
        ("feat:conformance.document-contract", "Document conformance contract cases", "Validate ADR and SPEC document rows, JSON files, hashes, origins, and numbering ranges.", ["spc:0525"], ["clm:conformance.document-contract.t2"], ["tst:pytest.conformance.document-contract"]),
    ],
    "id": [
        ("feat:conformance.id-contract", "Normalized ID conformance contract cases", "Validate normalized entity IDs, reference IDs, and maximum identifier length policy.", ["spc:0525"], ["clm:conformance.id-contract.t2"], ["tst:pytest.conformance.id-contract"]),
    ],
    "spec-adr": [
        ("feat:conformance.spec-adr-contract", "SPEC-to-ADR conformance contract cases", "Validate typed SPEC adr_ids links and derived SPEC-to-ADR graph visibility.", ["spc:0525"], ["clm:conformance.spec-adr-contract.t2"], ["tst:pytest.conformance.spec-adr-contract"]),
    ],
    "feature-spec": [
        ("feat:conformance.feature-spec-contract", "Feature-to-SPEC conformance contract cases", "Validate feature-owned spec_ids links and confirm SPEC entities do not own feature_ids.", ["spc:0525", "spc:0526"], ["clm:conformance.feature-spec-contract.t2"], ["tst:pytest.conformance.feature-spec-contract"]),
    ],
    "proof-chain": [
        ("feat:conformance.proof-chain-contract", "Proof-chain conformance contract cases", "Validate feature, claim, test, and evidence readiness relationships for targeted conformance rows.", ["spc:0525"], ["clm:conformance.proof-chain-contract.t2"], ["tst:pytest.conformance.proof-chain-contract"]),
    ],
    "boundary-release": [
        ("feat:conformance.boundary-release-contract", "Boundary and release conformance contract cases", "Validate frozen boundary and release closure references used for conformance certification.", ["spc:0525"], ["clm:conformance.boundary-release-contract.t2"], ["tst:pytest.conformance.boundary-release-contract"]),
    ],
    "scaffold": [
        ("feat:conformance.scaffold-dry-run", "Conformance scaffold dry-run planning", "Compute missing conformance feature and test rows without mutating the target registry.", ["spc:0526"], ["clm:conformance.scaffold-dry-run.t2"], ["tst:pytest.conformance.scaffold"]),
        ("feat:conformance.scaffold-apply", "Conformance scaffold apply mode", "Create missing conformance feature and test rows through SSOT APIs while preserving validation.", ["spc:0526"], ["clm:conformance.scaffold-apply.t2"], ["tst:pytest.conformance.scaffold"]),
        ("feat:conformance.scaffold-idempotency", "Conformance scaffold idempotency", "Ensure repeated scaffold runs do not duplicate rows or churn stable identifiers.", ["spc:0526"], ["clm:conformance.scaffold-idempotency.t2"], ["tst:pytest.conformance.scaffold"]),
    ],
    "evidence-output": [
        ("feat:conformance.evidence-output", "Conformance evidence output", "Emit machine-readable conformance evidence suitable for registry status synchronization.", ["spc:0526"], ["clm:conformance.evidence-output.t2"], ["tst:pytest.conformance.evidence-output"]),
    ],
    "cli": [
        ("feat:cli.conformance-surface", "CLI conformance command surface", "Expose ssot conformance commands for profile listing, discovery, scaffolding, execution, and evidence handling.", ["spc:0524", "spc:0526"], ["clm:cli.conformance-surface.t2"], ["tst:pytest.cli.conformance-surface"]),
    ],
}

_CLAIMS = {
    "package-layout": [
        ("clm:conformance.package-layout.t2", "Conformance package layout is planned", "The ssot-conformance package layout is tracked as a T2 conformance implementation target.", ["feat:conformance.package-layout"], ["tst:pytest.conformance.package-layout"], ["evd:t2.conformance.package-layout.pytest"]),
    ],
    "plugin": [
        ("clm:conformance.pytest-plugin.t2", "Conformance pytest plugin is planned", "The pytest plugin integration is tracked as a T2 conformance implementation target.", ["feat:conformance.pytest-plugin"], ["tst:pytest.conformance.pytest-plugin"], ["evd:t2.conformance.pytest-plugin.pytest"]),
        ("clm:conformance.case-discovery.t2", "Conformance case discovery is planned", "The conformance profile and case discovery behavior is tracked as a T2 target.", ["feat:conformance.case-discovery"], ["tst:pytest.conformance.pytest-plugin"], ["evd:t2.conformance.pytest-plugin.pytest"]),
    ],
    "registry": [
        ("clm:conformance.registry-contract.t2", "Registry conformance contract is planned", "The registry conformance test family is tracked as a T2 target.", ["feat:conformance.registry-contract"], ["tst:pytest.conformance.registry-contract"], ["evd:t2.conformance.registry-contract.pytest"]),
    ],
    "document": [
        ("clm:conformance.document-contract.t2", "Document conformance contract is planned", "The ADR and SPEC document conformance test family is tracked as a T2 target.", ["feat:conformance.document-contract"], ["tst:pytest.conformance.document-contract"], ["evd:t2.conformance.document-contract.pytest"]),
    ],
    "id": [
        ("clm:conformance.id-contract.t2", "Normalized ID conformance contract is planned", "The normalized ID conformance test family is tracked as a T2 target.", ["feat:conformance.id-contract"], ["tst:pytest.conformance.id-contract"], ["evd:t2.conformance.id-contract.pytest"]),
    ],
    "spec-adr": [
        ("clm:conformance.spec-adr-contract.t2", "SPEC-to-ADR conformance contract is planned", "The SPEC-to-ADR conformance test family is tracked as a T2 target.", ["feat:conformance.spec-adr-contract"], ["tst:pytest.conformance.spec-adr-contract"], ["evd:t2.conformance.spec-adr-contract.pytest"]),
    ],
    "feature-spec": [
        ("clm:conformance.feature-spec-contract.t2", "Feature-to-SPEC conformance contract is planned", "The feature-to-SPEC conformance test family is tracked as a T2 target.", ["feat:conformance.feature-spec-contract"], ["tst:pytest.conformance.feature-spec-contract"], ["evd:t2.conformance.feature-spec-contract.pytest"]),
    ],
    "proof-chain": [
        ("clm:conformance.proof-chain-contract.t2", "Proof-chain conformance contract is planned", "The feature claim test evidence proof-chain conformance family is tracked as a T2 target.", ["feat:conformance.proof-chain-contract"], ["tst:pytest.conformance.proof-chain-contract"], ["evd:t2.conformance.proof-chain-contract.pytest"]),
    ],
    "boundary-release": [
        ("clm:conformance.boundary-release-contract.t2", "Boundary and release conformance contract is planned", "The boundary and release conformance test family is tracked as a T2 target.", ["feat:conformance.boundary-release-contract"], ["tst:pytest.conformance.boundary-release-contract"], ["evd:t2.conformance.boundary-release-contract.pytest"]),
    ],
    "scaffold": [
        ("clm:conformance.scaffold-dry-run.t2", "Conformance scaffold dry-run is planned", "The scaffold dry-run planner is tracked as a T2 target.", ["feat:conformance.scaffold-dry-run"], ["tst:pytest.conformance.scaffold"], ["evd:t2.conformance.scaffold.pytest"]),
        ("clm:conformance.scaffold-apply.t2", "Conformance scaffold apply is planned", "The scaffold apply mutation path is tracked as a T2 target.", ["feat:conformance.scaffold-apply"], ["tst:pytest.conformance.scaffold"], ["evd:t2.conformance.scaffold.pytest"]),
        ("clm:conformance.scaffold-idempotency.t2", "Conformance scaffold idempotency is planned", "The scaffold idempotency behavior is tracked as a T2 target.", ["feat:conformance.scaffold-idempotency"], ["tst:pytest.conformance.scaffold"], ["evd:t2.conformance.scaffold.pytest"]),
    ],
    "evidence-output": [
        ("clm:conformance.evidence-output.t2", "Conformance evidence output is planned", "The conformance evidence output behavior is tracked as a T2 target.", ["feat:conformance.evidence-output"], ["tst:pytest.conformance.evidence-output"], ["evd:t2.conformance.evidence-output.pytest"]),
    ],
    "cli": [
        ("clm:cli.conformance-surface.t2", "CLI conformance surface is planned", "The ssot conformance CLI surface is tracked as a T2 target.", ["feat:cli.conformance-surface"], ["tst:pytest.cli.conformance-surface"], ["evd:t2.cli.conformance-surface.pytest"]),
    ],
}

_TESTS = {
    "package-layout": [
        ("tst:pytest.conformance.package-layout", "Conformance package layout tests", "tests/unit/test_conformance_package_layout.py", ["feat:conformance.package-layout"], ["clm:conformance.package-layout.t2"], ["evd:t2.conformance.package-layout.pytest"]),
    ],
    "plugin": [
        ("tst:pytest.conformance.pytest-plugin", "Conformance pytest plugin integration tests", "tests/integration/test_conformance_pytest_plugin.py", ["feat:conformance.pytest-plugin", "feat:conformance.case-discovery"], ["clm:conformance.pytest-plugin.t2", "clm:conformance.case-discovery.t2"], ["evd:t2.conformance.pytest-plugin.pytest"]),
    ],
    "registry": [
        ("tst:pytest.conformance.registry-contract", "Registry conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_registry_contract.py", ["feat:conformance.registry-contract"], ["clm:conformance.registry-contract.t2"], ["evd:t2.conformance.registry-contract.pytest"]),
    ],
    "document": [
        ("tst:pytest.conformance.document-contract", "Document conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_document_contract.py", ["feat:conformance.document-contract"], ["clm:conformance.document-contract.t2"], ["evd:t2.conformance.document-contract.pytest"]),
    ],
    "id": [
        ("tst:pytest.conformance.id-contract", "Normalized ID conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_id_contract.py", ["feat:conformance.id-contract"], ["clm:conformance.id-contract.t2"], ["evd:t2.conformance.id-contract.pytest"]),
    ],
    "spec-adr": [
        ("tst:pytest.conformance.spec-adr-contract", "SPEC-to-ADR conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_spec_adr_contract.py", ["feat:conformance.spec-adr-contract"], ["clm:conformance.spec-adr-contract.t2"], ["evd:t2.conformance.spec-adr-contract.pytest"]),
    ],
    "feature-spec": [
        ("tst:pytest.conformance.feature-spec-contract", "Feature-to-SPEC conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_feature_spec_contract.py", ["feat:conformance.feature-spec-contract"], ["clm:conformance.feature-spec-contract.t2"], ["evd:t2.conformance.feature-spec-contract.pytest"]),
    ],
    "proof-chain": [
        ("tst:pytest.conformance.proof-chain-contract", "Proof-chain conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_proof_chain_contract.py", ["feat:conformance.proof-chain-contract"], ["clm:conformance.proof-chain-contract.t2"], ["evd:t2.conformance.proof-chain-contract.pytest"]),
    ],
    "boundary-release": [
        ("tst:pytest.conformance.boundary-release-contract", "Boundary and release conformance contract tests", "pkgs/ssot-conformance/src/ssot_conformance/cases/test_boundary_release_contract.py", ["feat:conformance.boundary-release-contract"], ["clm:conformance.boundary-release-contract.t2"], ["evd:t2.conformance.boundary-release-contract.pytest"]),
    ],
    "scaffold": [
        ("tst:pytest.conformance.scaffold", "Conformance scaffold tests", "tests/unit/test_conformance_scaffold.py", ["feat:conformance.scaffold-dry-run", "feat:conformance.scaffold-apply", "feat:conformance.scaffold-idempotency"], ["clm:conformance.scaffold-dry-run.t2", "clm:conformance.scaffold-apply.t2", "clm:conformance.scaffold-idempotency.t2"], ["evd:t2.conformance.scaffold.pytest"]),
    ],
    "evidence-output": [
        ("tst:pytest.conformance.evidence-output", "Conformance evidence output tests", "tests/unit/test_conformance_evidence_output.py", ["feat:conformance.evidence-output"], ["clm:conformance.evidence-output.t2"], ["evd:t2.conformance.evidence-output.pytest"]),
    ],
    "cli": [
        ("tst:pytest.cli.conformance-surface", "CLI conformance surface tests", "tests/integration/test_cli_conformance.py", ["feat:cli.conformance-surface"], ["clm:cli.conformance-surface.t2"], ["evd:t2.cli.conformance-surface.pytest"]),
    ],
}

_EVIDENCE = {
    "package-layout": [
        ("evd:t2.conformance.package-layout.pytest", "Package layout pytest evidence", ".ssot/evidence/conformance/conformance-package-layout-pytest.json", ["clm:conformance.package-layout.t2"], ["tst:pytest.conformance.package-layout"]),
    ],
    "plugin": [
        ("evd:t2.conformance.pytest-plugin.pytest", "Pytest plugin integration evidence", ".ssot/evidence/conformance/conformance-pytest-plugin-pytest.json", ["clm:conformance.pytest-plugin.t2", "clm:conformance.case-discovery.t2"], ["tst:pytest.conformance.pytest-plugin"]),
    ],
    "registry": [
        ("evd:t2.conformance.registry-contract.pytest", "Registry contract pytest evidence", ".ssot/evidence/conformance/conformance-registry-contract-pytest.json", ["clm:conformance.registry-contract.t2"], ["tst:pytest.conformance.registry-contract"]),
    ],
    "document": [
        ("evd:t2.conformance.document-contract.pytest", "Document contract pytest evidence", ".ssot/evidence/conformance/conformance-document-contract-pytest.json", ["clm:conformance.document-contract.t2"], ["tst:pytest.conformance.document-contract"]),
    ],
    "id": [
        ("evd:t2.conformance.id-contract.pytest", "ID contract pytest evidence", ".ssot/evidence/conformance/conformance-id-contract-pytest.json", ["clm:conformance.id-contract.t2"], ["tst:pytest.conformance.id-contract"]),
    ],
    "spec-adr": [
        ("evd:t2.conformance.spec-adr-contract.pytest", "SPEC-to-ADR contract pytest evidence", ".ssot/evidence/conformance/conformance-spec-adr-contract-pytest.json", ["clm:conformance.spec-adr-contract.t2"], ["tst:pytest.conformance.spec-adr-contract"]),
    ],
    "feature-spec": [
        ("evd:t2.conformance.feature-spec-contract.pytest", "Feature-to-SPEC contract pytest evidence", ".ssot/evidence/conformance/conformance-feature-spec-contract-pytest.json", ["clm:conformance.feature-spec-contract.t2"], ["tst:pytest.conformance.feature-spec-contract"]),
    ],
    "proof-chain": [
        ("evd:t2.conformance.proof-chain-contract.pytest", "Proof-chain contract pytest evidence", ".ssot/evidence/conformance/conformance-proof-chain-contract-pytest.json", ["clm:conformance.proof-chain-contract.t2"], ["tst:pytest.conformance.proof-chain-contract"]),
    ],
    "boundary-release": [
        ("evd:t2.conformance.boundary-release-contract.pytest", "Boundary and release contract pytest evidence", ".ssot/evidence/conformance/conformance-boundary-release-contract-pytest.json", ["clm:conformance.boundary-release-contract.t2"], ["tst:pytest.conformance.boundary-release-contract"]),
    ],
    "scaffold": [
        ("evd:t2.conformance.scaffold.pytest", "Scaffold pytest evidence", ".ssot/evidence/conformance/conformance-scaffold-pytest.json", ["clm:conformance.scaffold-dry-run.t2", "clm:conformance.scaffold-apply.t2", "clm:conformance.scaffold-idempotency.t2"], ["tst:pytest.conformance.scaffold"]),
    ],
    "evidence-output": [
        ("evd:t2.conformance.evidence-output.pytest", "Evidence output pytest evidence", ".ssot/evidence/conformance/conformance-evidence-output-pytest.json", ["clm:conformance.evidence-output.t2"], ["tst:pytest.conformance.evidence-output"]),
    ],
    "cli": [
        ("evd:t2.cli.conformance-surface.pytest", "CLI conformance surface pytest evidence", ".ssot/evidence/conformance/cli-conformance-surface-pytest.json", ["clm:cli.conformance-surface.t2"], ["tst:pytest.cli.conformance-surface"]),
    ],
}


def list_profiles() -> list[dict[str, object]]:
    profiles = []
    for profile_name, families in PROFILE_DEFINITIONS.items():
        profiles.append(
            {
                "profile": profile_name,
                "families": list(families),
                "case_count": sum(len(_TESTS[family]) for family in families),
            }
        )
    return profiles


def resolve_selected_families(profiles: list[str] | None = None) -> list[str]:
    if not profiles:
        return list(PROFILE_DEFINITIONS["all"])
    selected: list[str] = []
    for profile in profiles:
        if profile not in PROFILE_DEFINITIONS:
            raise ValueError(f"Unknown conformance profile: {profile}")
        for family in PROFILE_DEFINITIONS[profile]:
            if family not in selected:
                selected.append(family)
    return selected


def _feature_row(values: tuple[str, str, str, list[str], list[str], list[str]]) -> dict[str, object]:
    feature_id, title, description, spec_ids, claim_ids, test_ids = values
    return {
        "id": feature_id,
        "title": title,
        "description": description,
        "implementation_status": "absent",
        "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
        "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
        "spec_ids": list(spec_ids),
        "claim_ids": list(claim_ids),
        "test_ids": list(test_ids),
        "requires": [],
    }


def _claim_row(values: tuple[str, str, str, list[str], list[str], list[str]]) -> dict[str, object]:
    claim_id, title, description, feature_ids, test_ids, evidence_ids = values
    return {
        "id": claim_id,
        "title": title,
        "status": "proposed",
        "tier": "T2",
        "kind": "conformance",
        "description": description,
        "feature_ids": list(feature_ids),
        "test_ids": list(test_ids),
        "evidence_ids": list(evidence_ids),
    }


def _test_row(values: tuple[str, str, str, list[str], list[str], list[str]]) -> dict[str, object]:
    test_id, title, path, feature_ids, claim_ids, evidence_ids = values
    return {
        "id": test_id,
        "title": title,
        "status": "planned",
        "kind": "pytest",
        "path": path,
        "feature_ids": list(feature_ids),
        "claim_ids": list(claim_ids),
        "evidence_ids": list(evidence_ids),
    }


def _evidence_row(values: tuple[str, str, str, list[str], list[str]]) -> dict[str, object]:
    evidence_id, title, path, claim_ids, test_ids = values
    return {
        "id": evidence_id,
        "title": title,
        "status": "planned",
        "kind": "pytest",
        "tier": "T2",
        "path": path,
        "claim_ids": list(claim_ids),
        "test_ids": list(test_ids),
    }


def build_catalog_slice(profiles: list[str] | None = None) -> dict[str, object]:
    families = resolve_selected_families(profiles)
    payload = {
        "catalog_version": CATALOG_VERSION,
        "profiles": profiles or ["all"],
        "families": families,
        "features": [],
        "claims": [],
        "tests": [],
        "evidence": [],
    }
    for family in families:
        payload["features"].extend(_feature_row(values) for values in _FEATURES[family])
        payload["claims"].extend(_claim_row(values) for values in _CLAIMS[family])
        payload["tests"].extend(_test_row(values) for values in _TESTS[family])
        payload["evidence"].extend(_evidence_row(values) for values in _EVIDENCE[family])
    return deepcopy(payload)
