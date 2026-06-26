---
name: ssot-mcp-t2-worker-campaign
description: Execute SSOT MCP pull-worker maturation work targeting T2 robustness verification. Use when Codex should claim leases through SSOT MCP, harden existing behavior with negative, edge, concurrency, failure, idempotency, compatibility, security, or recovery coverage, and complete slices honestly with distinct T2 evidence.
---

# SSOT MCP T2 Worker Campaign

Use this skill for T2 robustness slices.

## Defaults

- Generate one `worker_id` such as `codex-t2-<random-hex>`.
- Use the local repo unless the user explicitly provides another repo path.
- Use `target_tier: T2`.
- Use `limit: 25`.
- Use `auto_scaffold: true`.

## Hard rules

- Keep all SSOT registry mutation on SSOT MCP tools.
- Do not hand-edit `.ssot/registry.json`.
- Do not treat notifications as assignment.
- Do not reuse T1 evidence as if it were T2 evidence.
- Commit only your own runtime, test, and evidence changes.

## Worker loop

1. Claim work with `claim_next_maturation_slice`.
2. Inspect the lease with `get_slice_context`.
3. Confirm T1 support, robustness dimensions, gates, allowed paths, forbidden paths, and blockers.
4. Harden the runtime behavior where the lease permits it.
5. Implement focused robustness tests across applicable dimensions.
6. Run focused verification.
7. Write distinct T2 evidence inside leased paths.
8. Call `complete_slice` with accurate changed paths, tests run, evidence paths, requested tier, result, and notes.
9. Claim again unless campaign or lease state says stop.

## T2 standard

T2 means the feature robustly works across declared project-controlled dimensions. Cover only dimensions that are honestly applicable to the slice and supported by evidence.
