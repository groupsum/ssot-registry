---
name: ssot-mcp
description: Route Codex work onto the SSOT MCP control plane instead of direct SSOT registry edits. Use when a task involves SSOT MCP worker campaigns, maturation slices, leases, conflicts, worker events, campaign state, or MCP-governed registry CRUD and CLI delegation. Choose this skill when the user wants pull-only worker execution, honest claim-tier advancement, or lease-aware implementation and evidence flow.
---

# SSOT MCP

Use this skill when the task should stay on the SSOT MCP rail.

## What this skill covers

- Pull-only worker campaigns driven by `claim_next_maturation_slice`
- Lease-aware slice execution and `complete_slice` reporting
- Conflict, expiry, and revocation handling
- SSOT entity repair through MCP-exposed registry CRUD or CLI delegation tools
- Campaign state inspection, worker events, and wake/pause/stop control

## Route by target tier

- Use `$ssot-mcp-t1-worker-campaign` for T1 direct verification work.
- Use `$ssot-mcp-t2-worker-campaign` for T2 robustness verification work.
- Use `$ssot-mcp-t3-worker-campaign` for T3 certification-closure work.

## Operating rules

- Keep SSOT registry mutation on MCP tools only.
- Do not hand-edit `.ssot/registry.json`.
- Do not treat pushed events as work assignment.
- Treat `claim_next_maturation_slice` as the only assignment mechanism.
- Keep runtime, test, and evidence changes inside the lease's allowed paths.
- Report completion honestly through `complete_slice`.

## Minimum MCP loop

1. Claim a slice with `claim_next_maturation_slice`.
2. Inspect the lease with `get_slice_context`.
3. Implement only the allowed runtime, test, and evidence work.
4. Run focused verification.
5. Complete or abandon the slice with precise reporting.

## Worker identity

- Generate one `worker_id` at startup.
- Reuse it for claims, renewals, completion, abandonment, status, and events.
- Prefer `codex-<tier>-<random-hex>` naming.
