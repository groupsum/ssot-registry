---
name: ssot-mcp-t1-worker-campaign
description: Use when a Codex worker should participate in an SSOT MCP maturation campaign targeting T1, pull work leases through SSOT MCP, implement direct runtime behavior and project-controlled tests, complete slices honestly, and repeat until T1 completion or structural blockage.
metadata:
  short-description: Pull SSOT MCP slices and deliver T1 direct verification
---

# SSOT MCP T1 Worker Campaign

Use this skill when a Codex worker should participate in an SSOT MCP maturation campaign targeting T1 direct project verification.

## Command discipline

- Do not spend turns rediscovering syntax with `--help` during normal SSOT work. Use the command surface and examples in this skill directly.
- Pick one verified CLI rail for the repo (`ssot`, `ssot-registry`, `ssot-cli`, or `uv run ssot`) and reuse it consistently by substituting that rail into the examples below.
- Only inspect parser or help text when the user explicitly asks about the CLI surface or when observed runtime behavior contradicts the command patterns documented here.
## Operating Model

- Use the local repository for the current Codex session unless the user explicitly provides a different repo path.
- Other workers may be active in the same repository, but you do not need to know how many exist.
- Generate your own unique `worker_id` once at startup with a random suffix, such as `codex-t1-<random-hex>`, and reuse it for every lease, event, completion, abandonment, and status call in this run.
- Target tier is `T1` unless the user explicitly gives a different target.
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
  "worker_id": "codex-t1-<random-hex>",
  "target_tier": "T1",
  "limit": 25,
  "auto_scaffold": true
}
```

If the SSOT MCP server is already pinned to the intended repository, omit `repo`. If the user explicitly provided a repository path, include that path in every SSOT MCP call that accepts `repo`.

2. Inspect context with `get_slice_context` for the returned lease. Confirm feature id, tier transition, required claims/tests/evidence, allowed path roots, forbidden paths, gate requirements, and blocker details.

3. If workable, implement the direct runtime behavior required by the feature and focused project-controlled tests for the expected behavior.

4. Run focused verification, write evidence only inside leased paths, call `complete_slice` accurately, commit only your changes, then claim again.

5. If SSOT wiring is missing, repair it through SSOT MCP registry CRUD or CLI delegation tools. Do not edit `.ssot/registry.json` directly.

6. If blocked, follow `problem_detail` recommendations. Abandon only with a precise reason when the blocker cannot be repaired honestly through available MCP tools.

## T1 Gate Expectation

T1 means the feature directly works and is verified by repeatable project-controlled tests. Do not claim robustness, release certification, or external certification in a T1 slice.

## Events

Use worker events only to wake, pause, refresh, or stop. Do not accept work from notifications.

## Stop Conditions

Stop when campaign status says in-bounds features are T1 complete/verified, SSOT MCP reports no work and campaign complete, repeated blocked responses prove structural queue blockage, or lease/event state requires stopping.

## Final Report

Report worker_id, leases claimed/completed/abandoned, features advanced, tier transitions, files changed, tests run, evidence paths, `complete_slice` results, commits, and blockers.
