from __future__ import annotations

import argparse
from typing import Any

from . import resources, tools


def _make_cli_mirror_tool(path: str):
    prefix = path.split()

    def cli_mirror_tool(
        repo: str | None = None,
        global_args: list[str] | None = None,
        args: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run one fixed ssot-registry command path through MCP.

        `global_args` are inserted before the fixed command path so callers can
        supply root-level flags such as `--output-format`.
        `args` are appended after the fixed command path for command and
        subcommand flags plus positional arguments.
        """

        argv: list[str] = []
        if global_args:
            argv.extend(global_args)
        argv.extend(prefix)
        if args:
            argv.extend(args)
        return tools.run_ssot_cli(repo=repo, args=argv)

    cli_mirror_tool.__name__ = tools.mcp_cli_tool_name_for_path(path)
    return cli_mirror_tool


def _register_cli_mirror_tools(mcp: Any) -> None:
    surface = tools.get_ssot_cli_surface()
    mcp.tool(
        name=tools.MCP_CLI_ROOT_TOOL_NAME,
        title="ssot-registry root",
        description="Mirror of the root ssot-registry CLI surface through MCP. Pass argv tokens after `ssot-registry` in `args`.",
    )(tools.run_ssot_cli)

    for path in surface["subcommand_paths"]:
        flags = surface["flags_by_path"].get(path, [])
        flags_text = ", ".join(f"`{flag}`" for flag in flags) if flags else "none"
        mcp.tool(
            name=surface["tool_name_by_path"][path],
            title=f"ssot-registry {path}",
            description=(
                f"Mirror of `ssot-registry {path}` through MCP. "
                f"Supported path-local flags: {flags_text}. "
                "Pass root/global flags in `global_args` and path-local flags or positionals in `args`."
            ),
        )(_make_cli_mirror_tool(path))


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised when optional dependency is absent.
        raise RuntimeError("ssot-mcp requires the official `mcp` Python package. Install the ssot-mcp extra/package.") from exc

    mcp = FastMCP("ssot-mcp")

    mcp.tool()(tools.claim_next_maturation_slice)
    mcp.tool()(tools.renew_lease)
    mcp.tool()(tools.get_slice_context)
    mcp.tool()(tools.complete_slice)
    mcp.tool()(tools.abandon_slice)
    mcp.tool()(tools.get_campaign_status)
    mcp.tool()(tools.get_ssot_cli_surface)
    mcp.tool()(tools.get_worker_events)
    mcp.tool()(tools.ack_worker_events)
    mcp.tool()(tools.get_conflicts)
    mcp.tool()(tools.get_blocked_transitions)
    mcp.tool()(tools.scaffold_target_claim_wiring)
    mcp.tool()(tools.repair_blocked_transition)
    mcp.tool()(tools.repair_blocked_transitions)
    mcp.tool()(tools.registry_entity_get)
    mcp.tool()(tools.registry_entity_list)
    mcp.tool()(tools.registry_entity_search)
    mcp.tool()(tools.registry_entity_upsert)
    mcp.tool()(tools.registry_entity_delete)
    mcp.tool()(tools.registry_entity_link)
    mcp.tool()(tools.registry_entity_unlink)
    mcp.tool()(tools.run_ssot_cli)
    _register_cli_mirror_tools(mcp)

    mcp.resource("ssot://registry/{repo}")(resources.registry_resource)
    mcp.resource("ssot://campaign/{repo}/{campaign_id}")(resources.campaign_status_resource)
    mcp.resource("ssot://maturation-queue/{repo}")(resources.maturation_queue_resource)

    return mcp


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the optional SSOT pull-worker MCP server.")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--repo", default=None, help="Pin this MCP server instance to one SSOT repository root.")
    parser.add_argument(
        "--repo-mode",
        choices=["explicit"],
        default=None,
        help="Run as a global/dev server where every tool call must pass an explicit repo argument.",
    )
    args = parser.parse_args(argv)
    if args.repo is not None and args.repo_mode is not None:
        parser.error("--repo and --repo-mode explicit are mutually exclusive")
    if args.repo is None and args.repo_mode != "explicit":
        parser.error("choose either --repo <path> for a pinned server or --repo-mode explicit for dev/testing")
    tools.configure_repo(args.repo)
    server = build_server()
    server.run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
