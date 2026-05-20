# ssot-mcp

Optional MCP server for SSOT pull-worker coordination. Workers still pull work
through `claim_next_maturation_slice`; pushed update notifications only wake,
pause, refresh, or stop workers.

The core `ssot` CLI and `.ssot/registry.json` workflows do not require this
package. Deploy `ssot-mcp` only when a Codex/MCP client should coordinate
campaigns, leases, worker events, and registry writes through MCP tools.

Run one pinned server per repository in normal use:

```powershell
ssot-mcp --transport stdio --repo E:\swarmauri_github\ssot-registry
```

Run global/dev mode only when callers must pass an explicit `repo` argument on
every tool/resource call:

```powershell
ssot-mcp --transport stdio --repo-mode explicit
```

See [Codex MCP configuration](../../docs/coordination/codex-mcp.md) for Codex
`config.toml` examples.

## Registry write authority

Workers must not hand-edit `.ssot/registry.json`. When a worker needs SSOT
entity changes, it asks `ssot-mcp` to perform the mutation through one of the
registry tools:

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
- `get_ssot_cli_surface`
- `run_ssot_cli`

The structured entity tools use the same core registry mutation APIs as the
CLI, validate the registry before saving, and emit `registry_updated` events.
`run_ssot_cli` delegates to the repo-local CLI parser in-process for command
coverage that is not yet exposed as a dedicated MCP tool. It supports global
flags, help/version requests, commands, subcommands, command flags, and
subcommand flags as argv tokens. `get_ssot_cli_surface` returns the live CLI
surface (`global_flags`, `top_level_commands`, `subcommand_paths`, and
`flags_by_path`) so workers can discover the exact supported command shape
before calling `run_ssot_cli`. Help and invalid-argument parser exits are
captured as normal tool results; they must not close the MCP transport.

Campaign claims can also be scoped instead of running over every active
in-bounds feature. `claim_next_maturation_slice` accepts `feature_ids`,
`profile_ids`, and `boundary_ids`; unscoped campaigns consider 25 in-bounds
active features by default, and operators can raise `feature_limit` explicitly
for broader campaigns. Out-of-bounds features are filtered from assignment and
campaign status output. It caps blocker discovery with `max_blockers_per_claim`;
and auto-scaffolding is enabled by default so
`ssot-mcp` attempts target-tier claim/test/evidence scaffolding before returning
a blocked result. Pass `auto_scaffold=false` only when intentionally testing or
observing raw blocked-transition behavior. When a claim response returns
`kind="blocked"`, it includes a top-level `reason` and a structured
`problem_detail` with blocker rows and recommended MCP tool calls such as
`repair_blocked_transition` or `scaffold_target_claim_wiring`; workers should
perform those repairs and then pull again.
