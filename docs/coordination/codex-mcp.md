# Codex MCP Configuration

SSOT MCP is an optional control-plane extension. The core `ssot` CLI and registry remain usable without it.

Codex loads MCP servers from `config.toml`. For this repository, use the trusted project-scoped file at `.codex/config.toml` so the server points at this checkout.

## Repo-pinned server

Use one pinned server per repository for normal work:

```toml
[mcp_servers.ssot]
command = "E:\\swarmauri_github\\ssot-registry\\.venv\\Scripts\\ssot-mcp.exe"
args = ["--transport", "stdio", "--repo", "E:\\swarmauri_github\\ssot-registry"]
cwd = "E:\\swarmauri_github\\ssot-registry"
startup_timeout_sec = 20
tool_timeout_sec = 120
enabled = true
required = true
```

In pinned mode, tool calls may omit `repo`. If a caller passes a different repo, `ssot-mcp` rejects the call. This prevents a worker connected to one project from mutating another registry by accident.

For multiple repositories, configure one named server per repo:

```toml
[mcp_servers.ssot_registry]
command = "E:\\swarmauri_github\\ssot-registry\\.venv\\Scripts\\ssot-mcp.exe"
args = ["--transport", "stdio", "--repo", "E:\\swarmauri_github\\ssot-registry"]
cwd = "E:\\swarmauri_github\\ssot-registry"
enabled = true

[mcp_servers.tigrbl_ssot]
command = "E:\\swarmauri_github\\ssot-registry\\.venv\\Scripts\\ssot-mcp.exe"
args = ["--transport", "stdio", "--repo", "E:\\swarmauri_github\\tigrbl"]
cwd = "E:\\swarmauri_github\\tigrbl"
enabled = true
```

## Explicit repo-per-call mode

Use explicit mode only for global/dev/testing scenarios where every MCP tool/resource call must name the target repo:

```toml
[mcp_servers.ssot_global]
command = "E:\\swarmauri_github\\ssot-registry\\.venv\\Scripts\\ssot-mcp.exe"
args = ["--transport", "stdio", "--repo-mode", "explicit"]
cwd = "E:\\swarmauri_github\\ssot-registry"
startup_timeout_sec = 20
tool_timeout_sec = 120
enabled = true
required = false
```

In explicit mode, calls without `repo` fail. This is useful for development tools that intentionally operate across repos, but it is not the default worker setup.

## Operational notes

- Restart or refresh the Codex tool environment after editing `.codex/config.toml`.
- Use `/mcp` in the Codex TUI to inspect active MCP servers when running in CLI/TUI mode.
- Keep work assignment pull-only: workers obtain slices through `claim_next_maturation_slice`; notifications may wake, pause, refresh, or stop workers but must not assign slices.
- Keep registry ownership clear: `ssot-mcp` writes `.ssot/registry.json`; workers write implementation, test, and evidence paths only through their active leases.

## Registry CRUD through MCP

Workers do not edit `.ssot/registry.json` directly. If a slice needs registry
scaffolding or repair, the worker should call `ssot-mcp` registry tools:

- `get_blocked_transitions`
- `scaffold_target_claim_wiring`
- `repair_blocked_transition`
- `registry_entity_get`
- `registry_entity_list`
- `registry_entity_search`
- `registry_entity_upsert`
- `registry_entity_delete`
- `registry_entity_link`
- `registry_entity_unlink`
- `run_ssot_cli`

Use the structured tools for normal feature, claim, test, evidence, issue,
risk, boundary, profile, and release CRUD. Use `run_ssot_cli` when a registry
operation is already available as a CLI command but does not yet have a
dedicated MCP tool.

## Campaign Scope And Repair

`claim_next_maturation_slice` supports scoped campaigns:

```json
{
  "worker_id": "worker-01",
  "campaign_id": "camp:bucketwarden-brand",
  "target_tier": "T3",
  "feature_ids": ["feat:bucketwarden.brand.asset-registry"],
  "max_blockers_per_claim": 5,
  "feature_limit": 25
}
```

Scopes may be explicit `feature_ids`, `profile_ids`, or `boundary_ids`. The
control plane stores the scope in campaign metadata so later claims and status
checks use the same narrowed feature set. If no scope is supplied, the control
plane considers only the first 25 in-bounds active features by default. Operators
may raise `feature_limit` explicitly for broader campaigns. Out-of-bounds
features are filtered out of worker assignment and campaign status output.

When missing target-tier claim wiring is found, the control plane records a
blocked transition instead of recycling a bad lease. Auto-scaffolding is enabled
by default, so `claim_next_maturation_slice` first attempts to create the missing
target-tier claim/test/evidence wiring before returning a blocked result.
When `kind == "blocked"`, the response includes `reason` and
`problem_detail.recommendations`. Workers should follow those recommendations,
typically by calling `repair_blocked_transition` for each reported `blocked_id`
or `scaffold_target_claim_wiring` for the named feature/tier, then calling
`claim_next_maturation_slice` again. Workers can also inspect blocked records
with `get_blocked_transitions`.
