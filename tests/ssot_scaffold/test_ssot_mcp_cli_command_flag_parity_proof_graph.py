from __future__ import annotations

from tests.ssot_scaffold._ssot_mcp_cli_parity import build_surface_and_server, tool_for_path


def test_ssot_mcp_cli_command_flag_parity() -> None:
    surface, server = build_surface_and_server()

    for path, flags in surface["flags_by_path"].items():
        if not flags:
            continue
        tool = tool_for_path(server, surface, path)
        assert tool is not None
        result = tool.fn(args=["--help"])
        assert result["passed"] is True, path
        assert result["exit_code"] == 0, path
        assert "usage:" in result["stdout"], path
        for flag in flags:
            assert flag in result["stdout"], f"{path} {flag}"
