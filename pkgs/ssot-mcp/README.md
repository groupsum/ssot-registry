# ssot-mcp

Optional MCP server for SSOT pull-worker coordination. Workers still pull work
through `claim_next_maturation_slice`; pushed update notifications only wake,
pause, refresh, or stop workers.

Run one pinned server per repository in normal use:

```powershell
ssot-mcp --transport stdio --repo E:\swarmauri_github\ssot-registry
```

Run global/dev mode only when callers must pass an explicit `repo` argument on
every tool/resource call:

```powershell
ssot-mcp --transport stdio --repo-mode explicit
```
