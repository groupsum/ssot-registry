---
name: ssot-e2e-change-orchestrator
description: Orchestrate end-to-end SSOT delivery workflows across ADRs, SPECs, features, boundaries, implementation, migration, proof wiring, release certification, promotion, publication, and closure. Use when a request spans multiple lifecycle phases, asks for decision-to-release or decision-to-closure delivery, or includes phrases like ADR + SPEC + features + boundary + freeze, schema change + migration + tests + link everything, certifiably fully featured, or certifiably fully conformant.
---

# SSOT E2E Change Orchestrator

Use this skill when the request spans multiple SSOT phases. Keep the flow in canonical order and hand work to narrower workflow or worker skills instead of improvising a one-off sequence.

## Canonical order

1. Decision and scope definition
2. ADR and SPEC authoring or sync
3. Feature creation and target setting
4. Boundary creation and freeze
5. Implementation and migration delivery
6. Claim, test, and evidence closure
7. Release creation and certification
8. Promotion and publication
9. Closure verification

## Routing rules

- Use `$ssot-decision-to-scope` for ADR, SPEC, and initial feature work.
- Use `$ssot-scope-to-frozen-boundary` for target-setting through boundary freeze.
- Use `$ssot-implementation-and-migration-delivery` for schema, code, migration, and test delivery after freeze.
- Use `$ssot-proof-chain-and-certification` for proof wiring, release certify, promote, publish, and closure checks.
- Use `$ssot-e2e-portable-lifecycle` when the request explicitly requires a repeatable, portable, test-framework-agnostic full lifecycle with automated status synchronization.
- Use the narrower CRUD or linking skills only for local substeps inside a single phase.

## Operating rules

- Reject skipped gates unless the user explicitly asks for a partial workflow.
- Treat freeze as the point where scope stops changing; after freeze, implementation should satisfy the frozen target instead of rewriting scope.
- If a breaking schema change is requested, require a schema version bump and upgrade-path coverage.
- If the request says "fully featured" or "fully conformant", require docs, targets, freeze, implementation, migration, tests, proof links, and clean release progression.
- Escalate to the repo-specific references before giving implementation guidance.

## Output contract

- State the current phase and the next required gate.
- Call out missing artifacts explicitly: ADRs, SPECs, features, frozen boundary, migrations, tests, claims, evidence, release rows, or closure outputs.
- Prefer fail-closed wording over optimistic assumptions.

## References

- `references/lifecycle-order.md`
- `references/repo-touchpoints.md`
- `references/trigger-phrases.md`
