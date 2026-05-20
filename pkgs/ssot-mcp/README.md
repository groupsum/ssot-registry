# ssot-mcp

Optional MCP server for SSOT pull-worker coordination. Workers still pull work
through `claim_next_maturation_slice`; pushed update notifications only wake,
pause, refresh, or stop workers.
