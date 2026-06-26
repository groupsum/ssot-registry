---
name: ssot-mcp-t3-worker-campaign
description: Execute SSOT MCP pull-worker maturation work targeting T3 certification closure. Use when Codex should claim leases through SSOT MCP, deliver runtime, tests, evidence, and certification-closure work within leased paths, satisfy release, boundary, or profile gates where applicable, and complete slices honestly without direct SSOT registry edits.
---

# SSOT MCP T3 Worker Campaign

Use this skill for T3 certification-closure slices.

## Defaults

- Generate one `worker_id` such as `codex-t3-<random-hex>`.
- Use the local repo unless the user explicitly provides another repo path.
- Use `target_tier: T3`.
- Use `limit: 25`.
- Use `auto_scaffold: true`.

## Hard rules

- Keep SSOT registry reads and writes on SSOT MCP tools.
- Do not hand-edit `.ssot/registry.json`.
- Do not accept work from notifications.
- Do not over-claim certification or closure without real supporting evidence.
- Commit only your own runtime, test, and evidence changes.

## Worker loop

1. Claim work with `claim_next_maturation_slice`.
2. Inspect the lease with `get_slice_context`.
3. Confirm required claims, tests, evidence, release or boundary gates, allowed paths, forbidden paths, and blockers.
4. Implement or harden runtime and test work required for honest T3 completion.
5. Run focused verification.
6. Write evidence only inside leased paths.
7. Use MCP registry CRUD or CLI delegation tools if proof-chain wiring is missing.
8. Call `complete_slice` with accurate changed paths, tests run, evidence paths, requested tier, result, and notes.
9. Claim again unless campaign or lease state says stop.

## T3 standard

T3 means the slice has enough honest support for certification-closure expectations that apply to that feature tranche. Do not claim broader release completion than the lease and evidence actually support.
