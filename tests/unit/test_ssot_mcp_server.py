from __future__ import annotations

import pytest

from ssot_mcp.server import build_server, main
from ssot_mcp.tools import MCP_CLI_ROOT_TOOL_NAME, get_ssot_cli_surface
from tests.helpers import temp_repo_from_fixture


def test_server_requires_repo_or_explicit_repo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: None)

    with pytest.raises(SystemExit):
        main(["--transport", "stdio"])


def test_server_rejects_repo_with_explicit_mode(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: None)

    with pytest.raises(SystemExit):
        main(["--transport", "stdio", "--repo", str(tmp_path), "--repo-mode", "explicit"])


def test_server_accepts_explicit_repo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeServer:
        def __init__(self) -> None:
            self.transport = None

        def run(self, transport: str) -> None:
            self.transport = transport

    server = FakeServer()
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: server)

    assert main(["--transport", "stdio", "--repo-mode", "explicit"]) == 0
    assert server.transport == "stdio"


def test_server_build_registers_mcp_resources() -> None:
    assert build_server() is not None


def test_server_build_registers_cli_mirror_tools() -> None:
    server = build_server()
    surface = get_ssot_cli_surface()
    tool_names = {tool.name for tool in server._tool_manager.list_tools()}

    assert MCP_CLI_ROOT_TOOL_NAME in tool_names
    for path, tool_name in surface["tool_name_by_path"].items():
        assert tool_name in tool_names, path


def test_server_cli_mirror_tool_executes_fixed_path() -> None:
    temp_dir = temp_repo_from_fixture("repo_valid")
    try:
        repo = temp_dir.name + "\\repo"
        server = build_server()
        surface = get_ssot_cli_surface()
        tool = server._tool_manager.get_tool(surface["tool_name_by_path"]["validate"])
        assert tool is not None

        result = tool.fn(repo=repo, args=["."])

        assert result["passed"] is True
        assert result["exit_code"] == 0
        assert result["args"] == ["validate", "."]
    finally:
        temp_dir.cleanup()
