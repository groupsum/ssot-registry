---
name: ssot-claim-evidence-linking
description: Create, inspect, update, delete, evaluate, verify, link, and unlink claims and evidence, including their feature and test relationships. Use when Codex needs to connect claims to features, tests, and evidence, adjust claim status or tier, or verify whether proof chains are strong enough for release and certification workflows.
---

# SSOT Claim/Evidence Linking

Use this skill when the user is working on proof chains: what a feature claims, what tests exercise that claim, and what evidence supports it.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Command surface

- Claims: `claim create|get|list|update|delete|link|unlink|evaluate|set-status|set-tier`
- Evidence: `evidence create|get|list|update|delete|link|unlink|verify`
- Companion entity often touched in the same flow: `test link|unlink`

## Workflow

1. Create or inspect the claim first; claims are the assertion layer attached to one or more features.
2. Create or inspect evidence rows with a concrete `--evidence-path` that exists in the repo.
3. Link claims to features, tests, and evidence in one pass when possible so the closure graph is complete.
4. Use `claim evaluate` to inspect whether a claim currently satisfies guards.
5. Use `evidence verify` to check that evidence rows are valid before claiming certification readiness.

## Operating rules

- Keep claim `status` and `tier` distinct; status is lifecycle progress, tier is proof strength.
- Do not change a lower-tier claim into a higher-tier claim in place when each tier needs its own durable proof record. Create a distinct higher-tier claim and preserve the lower-tier claim.
- Promotion is additive, not replacement: when linking `T1` or `T2` claims, keep existing lower-tier claims linked to the feature unless those links are wrong for reasons unrelated to tier progression.
- Evidence should describe an artifact path the repo can actually carry or regenerate.
- When a claim gains or loses supporting evidence, review linked tests at the same time; broken proof chains usually show up as stale links.
- Prefer unlink over delete when historical claim or evidence records should remain visible.
- If the user is trying to certify or publish a target, switch from isolated claim work to `$ssot-proof-chain-and-certification`.
- If the same request also includes ADRs, specs, features, boundaries, freeze, or implementation work, escalate to `$ssot-e2e-change-orchestrator`.

## Example

```powershell
ssot claim create . --id clm:demo.login.t0 --title "Login basic claim" --kind behavior --tier T0
ssot claim create . --id clm:demo.login.t1 --title "Login succeeds" --kind behavior --tier T1
ssot evidence create . --id evd:demo.login.pytest --title "Pytest login run" --kind test_run --evidence-path artifacts/login.json --tier T1
ssot claim link . --id clm:demo.login.t0 --feature-ids feat:demo.login
ssot claim link . --id clm:demo.login.t1 --feature-ids feat:demo.login --test-ids tst:demo.login.unit --evidence-ids evd:demo.login.pytest
ssot evidence verify . --evidence-id evd:demo.login.pytest
ssot claim evaluate . --claim-id clm:demo.login.t1
```

## Source of truth

- `README.md` claim and evidence sections
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0604-claim-statuses.yaml`
- `pkgs/ssot-contracts/src/ssot_contracts/templates/specs/SPEC-0605-claim-tiers.yaml`
