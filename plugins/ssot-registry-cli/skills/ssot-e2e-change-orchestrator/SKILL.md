---
name: ssot-e2e-change-orchestrator
description: Orchestrate end-to-end SSOT delivery workflows across ADRs, SPECs, features, boundaries, implementation, migration, proof wiring, release certification, promotion, publication, and closure. Use when a request spans multiple lifecycle phases, asks for decision-to-release or decision-to-closure delivery, or includes phrases like ADR + SPEC + features + boundary + freeze, schema change + migration + tests + link everything, certifiably fully featured, or certifiably fully conformant.
---

# SSOT E2E Change Orchestrator

Use this skill when the request spans multiple SSOT phases. Treat this as a deterministic workflow engine with explicit gates, scheduling policy, and replan behavior.

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

## Orchestration loop

1. Classify request intent and identify in-scope entities/phases.
2. Build an execution DAG from `references/capability-map.yaml`.
3. Schedule steps using `references/dispatch-policy.md`:
   - serialize writes
   - parallelize read-only steps where safe
4. Execute steps in topological order with barrier gates.
5. Persist run progress in a structure compatible with `references/run-state-schema.json`.
6. On failure, stop progression, record blocker, and replan from the failed gate.

## Routing rules

- Route single-family requests to per-entity skills:
  - `$ssot-adr`, `$ssot-spec`, `$ssot-feature`, `$ssot-profile`, `$ssot-test`, `$ssot-issue`, `$ssot-claim`, `$ssot-evidence`, `$ssot-risk`, `$ssot-boundary`, `$ssot-release`.
- Use `$ssot-decision-to-scope` for ADR/SPEC + initial feature targeting.
- Use `$ssot-scope-to-frozen-boundary` for target setting through freeze.
- Use `$ssot-implementation-and-migration-delivery` for post-freeze implementation/test delivery.
- Use `$ssot-proof-chain-and-certification` for proof closure and release gates.
- Use `$ssot-e2e-portable-lifecycle` for repeatable, test-framework-agnostic full lifecycle with mandatory status synchronization.
- Keep `$ssot-entity-get/list/review/analyze` as read-oriented wrappers.

## Operating rules

- Default execution mode is fail-closed safe.
- Reject skipped gates unless the user explicitly asks for partial workflow coverage.
- Treat freeze as the point where scope stops changing; after freeze, implementation should satisfy the frozen target instead of rewriting scope.
- If a breaking schema change is requested, require a schema version bump and upgrade-path coverage.
- If the request says "fully featured" or "fully conformant", require docs, targets, freeze, implementation, migration, tests, proof links, and clean release progression.
- Require `registry sync-statuses --dry-run` then `registry sync-statuses` after test/evidence updates and after publish, followed by `validate --write-report`.
- Never continue from failed certify/promote/publish gates.

## Output contract

- State the current phase and the next required gate.
- State which steps ran sequentially vs in parallel and why.
- Call out missing artifacts explicitly: ADRs, SPECs, features, frozen boundary, migrations, tests, claims, evidence, release rows, or closure outputs.
- Prefer fail-closed wording over optimistic assumptions.
- When blocked, provide exact remediation commands and the `resume_from_step`.

## References

- `references/lifecycle-order.md`
- `references/repo-touchpoints.md`
- `references/trigger-phrases.md`
- `references/capability-map.yaml`
- `references/dispatch-policy.md`
- `references/run-state-schema.json`
