---
name: ssot-feature-crud
description: Create, inspect, update, delete, plan, link, unlink, and set lifecycle for SSOT features. Use when Codex needs to manage targetable features, adjust planning horizon or target claim tier, wire dependencies, or retire/replacement-link features through the CLI instead of hand-editing the registry.
---

# SSOT Feature CRUD

Use this skill for feature-centered SSOT operations. Features are the targetable unit for planning, evaluation, and release scope, so keep their plan and lifecycle fields coherent with linked claims and tests.

## Command surface

- `feature create|get|list|update|delete|link|unlink|plan|lifecycle set`
- Use `feature link` and `feature unlink` for graph edges instead of mutating arrays by hand.

## Workflow

1. Inspect the feature with `feature get` or `feature list` before mutation when current links or lifecycle are unknown.
2. Create the feature with stable `feat:` IDs and a clear title.
3. Set planning fields with `feature plan` when the user is changing horizon, slot, target lifecycle stage, or target claim tier.
4. Use `feature lifecycle set` for support-state transitions such as active, deprecated, or retired; include notes and replacement feature IDs when relevant.
5. Use `feature link` or `unlink` to connect claims, tests, dependencies, issues, risks, and supporting documents after the feature row exists.

## Operating rules

- Distinguish planning from lifecycle: horizon answers when the feature is targeted; lifecycle answers its support state.
- Prefer `feature plan` for roadmap changes and `feature lifecycle set` for policy/support changes.
- When retiring a feature, supply `--replacement-feature-id` if there is a successor and keep the old feature rather than deleting it.
- Prefer delete only for mistaken rows that should not remain in history.
- If the user asks whether a feature is release-ready, escalate into claim/test/evidence checks or the E2E release-closure skill.

## Examples

```powershell
ssot feature create . --id feat:demo.login --title "User login"
ssot feature plan . --ids feat:demo.login --horizon current --claim-tier T1 --target-lifecycle-stage active
ssot feature lifecycle set . --ids feat:demo.login --stage active --note "Initial rollout"
ssot feature link . --id feat:demo.login --claim-ids clm:demo.login.t1 --test-ids tst:demo.login.unit
```

## Source of truth

- `README.md` feature section
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0603-feature-lifecycle.yaml`
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0611-planning-horizons.yaml`
