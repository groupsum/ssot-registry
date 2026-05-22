from __future__ import annotations

from tests.ssot_scaffold._ssot_mcp_cli_parity import (
    MCP_CLI_ROOT_TOOL_NAME,
    build_surface_and_server,
    live_manifest,
    server_tool_names,
)


def test_ssot_mcp_cli_surface_drift_guard() -> None:
    surface, server = build_surface_and_server()
    manifest = live_manifest()
    names = server_tool_names(server)

    assert surface["global_flags"] == manifest["global_flags"]
    assert surface["top_level_commands"] == manifest["top_level_commands"]
    assert surface["subcommand_paths"] == manifest["subcommand_paths"]
    assert surface["flags_by_path"] == manifest["flags_by_path"]

    assert surface["root_tool_name"] == MCP_CLI_ROOT_TOOL_NAME
    assert MCP_CLI_ROOT_TOOL_NAME in names
    assert set(surface["tool_name_by_path"].values()).issubset(names)
