from __future__ import annotations

from tests.ssot_scaffold._ssot_mcp_cli_parity import build_surface_and_server, temp_repo_path, tool_for_path


def test_ssot_mcp_cli_subcommand_flag_parity() -> None:
    surface, server = build_surface_and_server()
    temp_dir, repo = temp_repo_path()
    try:
        invalid_flag = "--unknown-ssot-parity-flag"
        for path in surface["subcommand_paths"]:
            if " " not in path:
                continue
            tool = tool_for_path(server, surface, path)
            assert tool is not None
            result = tool.fn(repo=str(repo), args=[invalid_flag])
            assert result["passed"] is False, path
            assert result["exit_code"] != 0, path
            combined = result["stdout"] + result["stderr"]
            assert "usage:" in combined, path
            assert (
                invalid_flag in combined
                or "the following arguments are required" in combined
                or "one of the arguments" in combined
                or "invalid choice" in combined
            ), path
    finally:
        temp_dir.cleanup()
