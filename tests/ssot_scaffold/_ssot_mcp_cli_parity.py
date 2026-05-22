from __future__ import annotations

from pathlib import Path

from scripts.generate_cli_surface_manifest import generate_manifest
from ssot_mcp.server import build_server
from ssot_mcp.tools import MCP_CLI_ROOT_TOOL_NAME, get_ssot_cli_surface
from tests.helpers import temp_repo_from_fixture


def build_surface_and_server():
    return get_ssot_cli_surface(), build_server()


def server_tool_names(server) -> set[str]:
    return {tool.name for tool in server._tool_manager.list_tools()}


def tool_for_path(server, surface: dict[str, object], path: str):
    tool_name = surface["tool_name_by_path"][path]
    return server._tool_manager.get_tool(tool_name)


def live_manifest() -> dict[str, object]:
    return generate_manifest()


def temp_repo_path() -> tuple[object, Path]:
    temp_dir = temp_repo_from_fixture("repo_valid")
    return temp_dir, Path(temp_dir.name) / "repo"


__all__ = [
    "MCP_CLI_ROOT_TOOL_NAME",
    "build_surface_and_server",
    "live_manifest",
    "server_tool_names",
    "temp_repo_path",
    "tool_for_path",
]
