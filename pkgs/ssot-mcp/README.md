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
