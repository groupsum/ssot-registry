# Dispatch Policy (Fail-Closed Safe)

This orchestrator policy is deterministic and guard-first.

## Scheduling rules

1. Default mode: `fail_closed_safe`.
2. Writes are serialized by section.
3. Read-only operations may run in parallel.
4. A write step and read step may run in parallel only when the read scope does not depend on in-flight writes.

## Conflict rules

- Never run two write steps in parallel when they touch the same SSOT section.
- Treat release progression commands as globally exclusive:
  - `release certify`
  - `release promote`
  - `release publish`
- `boundary freeze` is exclusive with all scope-mutation writes.

## Barrier gates

Always stop and evaluate at these barriers:

1. `validate`
2. `registry sync-statuses --dry-run` then `registry sync-statuses`
3. `release certify`
4. `release promote`
5. `release publish`

If any barrier fails:

- mark run state as `blocked`
- capture failures and suggested remediation steps
- do not advance to later stages
- replan from the failed gate only after upstream fixes

## Status convergence

`registry sync-statuses` is mandatory:

- after test/evidence updates
- after release publish

Run order:

1. `registry sync-statuses --dry-run`
2. review proposed changes
3. `registry sync-statuses`
4. `validate --write-report`

## Routing priority

1. If request scope is one entity family: route to that `ssot-<entity>` skill.
2. If request crosses families but stays read-only: route to `ssot-entity-analyze` / `ssot-entity-review`.
3. If request spans freeze/certify/promote/publish or multi-phase lifecycle: route to orchestrated E2E flow (`ssot-e2e-portable-lifecycle` or phase skills).

