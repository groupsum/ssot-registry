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
