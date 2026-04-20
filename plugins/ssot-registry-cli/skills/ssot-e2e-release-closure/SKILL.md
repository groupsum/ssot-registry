---
name: ssot-e2e-release-closure
description: Compatibility wrapper for older SSOT end-to-end requests that still name release closure directly. Use when a request says ssot-e2e-release-closure or asks for docs-to-release closure in one step, then hand the work to the newer orchestrated workflow stack rooted at ssot-e2e-change-orchestrator.
---

# SSOT E2E Release Closure

Treat this as an alias skill. Do not keep end-to-end logic here. Route the request into the newer layered workflow stack and preserve fail-closed behavior.

## Routing

- For multi-phase delivery, use `$ssot-e2e-change-orchestrator`.
- For ADR, SPEC, and feature planning, use `$ssot-decision-to-scope`.
- For boundary planning and freeze, use `$ssot-scope-to-frozen-boundary`.
- For implementation, migrations, and tests, use `$ssot-implementation-and-migration-delivery`.
- For proof closure and release progression, use `$ssot-proof-chain-and-certification`.

## Operating rules

- Keep this skill as a compatibility bridge for older prompts.
- If the user only wants certify, promote, publish, or closure on an already-frozen target, go directly to `$ssot-proof-chain-and-certification`.
- If the user asks for the full lifecycle, route to `$ssot-e2e-change-orchestrator` and follow canonical order.
