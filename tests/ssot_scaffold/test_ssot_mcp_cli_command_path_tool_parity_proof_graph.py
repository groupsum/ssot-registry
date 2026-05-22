from __future__ import annotations

from tests.ssot_scaffold._ssot_mcp_cli_parity import (
    MCP_CLI_ROOT_TOOL_NAME,
    build_surface_and_server,
    server_tool_names,
    temp_repo_path,
    tool_for_path,
)


def test_ssot_mcp_cli_command_path_tool_parity() -> None:
    surface, server = build_surface_and_server()
    names = server_tool_names(server)

    assert MCP_CLI_ROOT_TOOL_NAME in names
    assert set(surface["tool_name_by_path"].values()).issubset(names)

    temp_dir, repo = temp_repo_path()
    try:
        for path in ("validate", "feature list", "claim list"):
            tool = tool_for_path(server, surface, path)
            assert tool is not None
            result = tool.fn(repo=str(repo), args=["."])
            assert result["passed"] is True
            assert result["exit_code"] == 0
            assert result["args"] == [*path.split(), "."]
    finally:
        temp_dir.cleanup()
