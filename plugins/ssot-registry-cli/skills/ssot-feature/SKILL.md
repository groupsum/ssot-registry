---
name: ssot-feature
description: Manage feature entities with full CLI coverage, including planning, lifecycle transitions, and dependency/claim/test link management.
---

# SSOT Feature

Use this skill for feature-only operations.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Command surface

- `feature create|get|list|update|delete|link|unlink|plan`
- `feature lifecycle set`

## Workflow

1. Inspect feature state and links.
2. Apply roadmap targeting with `feature plan`.
3. Update support state with `feature lifecycle set`.
4. Manage claim/test/dependency links with `feature link`/`feature unlink`.

## Operating rules

- Distinguish planning (`plan`) from support policy (`lifecycle`).
- `feature plan --claim-tier` sets the target assurance tier; it does not mean the feature should only retain one linked claim tier.
- Promotion is additive, not replacement: when a feature moves from `T0` to `T1` or `T1` to `T2`, keep the lower-tier claims linked and add the higher-tier claim plus its proof.
- Do not unlink lower-tier claims just because a higher-tier claim is added. Only unlink claims that are incorrect, obsolete for non-tier reasons, or were linked by mistake.
- If the request includes freeze or release progression, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot feature get . --id feat:demo.login
ssot feature plan . --ids feat:demo.login --horizon current --claim-tier T1 --target-lifecycle-stage active
ssot feature link . --id feat:demo.login --claim-ids clm:demo.login.t0 --test-ids tst:demo.login.smoke
ssot feature link . --id feat:demo.login --claim-ids clm:demo.login.t1 --test-ids tst:demo.login.integration
```
