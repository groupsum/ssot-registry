---
name: ssot-mcp-t2-worker-campaign
description: Use when a Codex worker should participate in an SSOT MCP maturation campaign targeting T2, pull work leases through SSOT MCP, harden runtime behavior with robustness/failure/edge/negative/race/security tests, complete slices honestly, and repeat until T2 completion or structural blockage.
metadata:
  short-description: Pull SSOT MCP slices and deliver T2 robustness verification
---

# SSOT MCP T2 Worker Campaign

Use this skill when a Codex worker should participate in an SSOT MCP maturation campaign targeting T2 robust project verification.

## Operating Model

- Use the local repository for the current Codex session unless the user explicitly provides a different repo path.
- Other workers may be active in the same repository, but you do not need to know how many exist.
- Generate your own unique `worker_id` once at startup with a random suffix, such as `codex-t2-<random-hex>`, and reuse it for every lease, event, completion, abandonment, and status call in this run.
- Target tier is `T2` unless the user explicitly gives a different target.
- Use `limit: 25` by default unless the user explicitly gives a different limit.
- Use `auto_scaffold: true` by default.

## Hard Rules

- Use the SSOT MCP only for SSOT registry reads/writes.
- Do not hand-edit `.ssot/registry.json`.
- Do not directly CRUD SSOT entities by editing files.
- If registry/entity changes are needed, request them through SSOT MCP tools, including registry CRUD / CLI delegation tools exposed by the MCP.
- Work assignment is pull-only. Only `claim_next_maturation_slice` grants work.
- Never treat pushed events or status output as an assignment.
- Commit only your own runtime/test/evidence changes.
- Do not revert or rewrite work from other agents.

## Worker Loop

1. Claim work with `claim_next_maturation_slice` through SSOT MCP.

Use this shape:

```json
{
  "repo": "<LOCAL_REPO_OR_USER_PROVIDED_REPO>",
  "worker_id": "codex-t2-<random-hex>",
  "target_tier": "T2",
  "limit": 25,
  "auto_scaffold": true
}
```

If the SSOT MCP server is already pinned to the intended repository, omit `repo`. If the user explicitly provided a repository path, include that path in every SSOT MCP call that accepts `repo`.

2. Inspect context with `get_slice_context` for the returned lease. Confirm feature id, tier transition, required claims/tests/evidence, allowed path roots, forbidden paths, gate requirements, source T1 support, robustness dimensions, and blocker details.

3. If workable, harden the runtime behavior and implement focused robustness tests. Cover applicable negative cases, edge cases, state variation, compatibility, concurrency, security abuse, performance envelope, failure recovery, idempotency, regression, fuzz, property, or mutation dimensions.

4. Run focused verification, write evidence only inside leased paths, call `complete_slice` accurately, commit only your changes, then claim again.

5. If SSOT wiring is missing, repair it through SSOT MCP registry CRUD or CLI delegation tools. Do not edit `.ssot/registry.json` directly.

6. If blocked, follow `problem_detail` recommendations. Abandon only with a precise reason when the blocker cannot be repaired honestly through available MCP tools.

## T2 Gate Expectation

T2 means the feature robustly works across declared project-controlled robustness dimensions. T2 evidence must be distinct from T1 evidence and should record the exercised dimensions and source T1 support. Do not claim release certification or external certification in a T2 slice.

## Events

Use worker events only to wake, pause, refresh, or stop. Do not accept work from notifications.

## Stop Conditions

Stop when campaign status says in-bounds features are T2 complete/robustly verified, SSOT MCP reports no work and campaign complete, repeated blocked responses prove structural queue blockage, or lease/event state requires stopping.

## Final Report

Report worker_id, leases claimed/completed/abandoned, features advanced, robustness dimensions covered, tier transitions, files changed, tests run, evidence paths, `complete_slice` results, commits, and blockers.
