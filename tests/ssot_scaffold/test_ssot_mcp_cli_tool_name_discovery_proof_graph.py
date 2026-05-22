from __future__ import annotations

from ssot_mcp.tools import mcp_cli_tool_name_for_path
from tests.ssot_scaffold._ssot_mcp_cli_parity import build_surface_and_server, server_tool_names


def test_ssot_mcp_cli_tool_name_discovery() -> None:
    surface, server = build_surface_and_server()
    names = server_tool_names(server)

    assert len(surface["tool_name_by_path"]) == len(surface["subcommand_paths"])
    assert len(set(surface["tool_name_by_path"].values())) == len(surface["tool_name_by_path"])

    for path in surface["subcommand_paths"]:
        tool_name = surface["tool_name_by_path"][path]
        assert tool_name == mcp_cli_tool_name_for_path(path)
        assert tool_name in names
