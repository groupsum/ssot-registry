---
name: ssot-mcp-t1-worker-campaign
description: Execute SSOT MCP pull-worker maturation work targeting T1. Use when Codex should claim leases through SSOT MCP, implement direct runtime behavior, add repeatable project-controlled tests, produce evidence in leased paths, and complete slices honestly without hand-editing the SSOT registry.
---

# SSOT MCP T1 Worker Campaign

Use this skill for T1 direct verification slices.

## Defaults

- Generate one `worker_id` such as `codex-t1-<random-hex>`.
- Use the local repo unless the user explicitly provides another repo path.
- Use `target_tier: T1`.
- Use `limit: 25`.
- Use `auto_scaffold: true`.

## Hard rules

- Use SSOT MCP for all SSOT registry reads and writes.
- Do not hand-edit `.ssot/registry.json`.
- Do not accept work from notifications.
- Do not claim success without passing tests and honest evidence.
- Commit only your own runtime, test, and evidence changes.

## Worker loop

1. Claim work with `claim_next_maturation_slice`.
2. Inspect the lease with `get_slice_context`.
3. Confirm feature id, tier transition, claims, tests, evidence, allowed paths, forbidden paths, gates, and blockers.
4. Implement direct runtime behavior.
5. Implement focused project-controlled tests for the expected behavior.
6. Run focused verification.
7. Write evidence only inside leased paths.
8. Call `complete_slice` with accurate changed paths, tests run, evidence paths, requested tier, result, and notes.
9. Claim again unless campaign state or lease state says stop.

## T1 standard

T1 means the feature directly works under repeatable project-controlled verification. Do not claim T2 robustness or T3 certification from this skill.
