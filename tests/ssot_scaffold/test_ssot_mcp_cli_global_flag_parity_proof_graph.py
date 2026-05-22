from __future__ import annotations

from tests.ssot_scaffold._ssot_mcp_cli_parity import build_surface_and_server, temp_repo_path, tool_for_path


def test_ssot_mcp_cli_global_flag_parity() -> None:
    surface, server = build_surface_and_server()
    root_tool = server._tool_manager.get_tool(surface["root_tool_name"])
    assert root_tool is not None

    version = root_tool.fn(args=["--version"])
    assert version["passed"] is True
    assert "ssot-registry" in version["stdout"]

    help_result = root_tool.fn(args=["--help"])
    assert help_result["passed"] is True
    for flag in surface["global_flags"]:
        assert flag in help_result["stdout"]

    temp_dir, repo = temp_repo_path()
    try:
        validate_tool = tool_for_path(server, surface, "validate")
        assert validate_tool is not None
        result = validate_tool.fn(repo=str(repo), global_args=["--output-format", "json"], args=["."])
        assert result["passed"] is True
        assert isinstance(result["output"], dict)
        assert result["output"]["passed"] is True

        output_file = repo / "mirrored-global-flags.json"
        feature_list_tool = tool_for_path(server, surface, "feature list")
        assert feature_list_tool is not None
        output_result = feature_list_tool.fn(
            repo=str(repo),
            global_args=["--output-file", str(output_file)],
            args=["."],
        )
        assert output_result["passed"] is True
        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8").strip()
    finally:
        temp_dir.cleanup()
