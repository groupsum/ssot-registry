<div align="center">
  <h1>ssot-mcp</h1>
  <p><strong>Optional MCP server for SSOT registry coordination and pull-worker campaigns.</strong></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/ssot-mcp/"><img src="https://img.shields.io/pypi/v/ssot-mcp?label=PyPI%20version" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/ssot-mcp/"><img src="https://img.shields.io/pypi/pyversions/ssot-mcp?label=Python" alt="Supported Python versions" /></a>
  <a href="https://pepy.tech/project/ssot-mcp"><img src="https://static.pepy.tech/badge/ssot-mcp" alt="Downloads" /></a>
  <a href="https://hits.sh/github.com/groupsum/ssot-registry/"><img src="https://hits.sh/github.com/groupsum/ssot-registry.svg?style=flat-square" alt="Repository hits" /></a>
<!-- ssot-schema-badges:start -->
  <img src="https://img.shields.io/badge/schema_version-0.7.0-blue" alt="schema_version 0.7.0" />
  <img src="https://img.shields.io/badge/migration%20coverage-14%2F14-brightgreen" alt="Migration coverage 14/14" />
<!-- ssot-schema-badges:end -->
</div>

`ssot-mcp` is the optional Model Context Protocol server for SSOT.

It lets MCP-capable clients coordinate registry mutations, pull-worker campaigns, leases, worker events, and campaign state through tools backed by [ssot-core](https://pypi.org/project/ssot-core/). The ordinary `.ssot/registry.json`, Python API, and [ssot-cli](https://pypi.org/project/ssot-cli/) workflows do not require this package.

- GitHub: https://github.com/groupsum/ssot-registry

## What this package owns

- The `ssot-mcp` console entry point
- MCP tools, resources, and prompts for optional SSOT control-plane workflows
- Registry entity CRUD and linking tools for MCP clients
- Pull-worker campaign tools for claiming slices, renewing leases, completing slices, abandoning slices, and reading worker events
- In-process delegation to the live `ssot` CLI parser for command coverage that is not yet exposed as a dedicated MCP tool

## When to use this package

Use `ssot-mcp` when you want:

- a Codex or MCP client to mutate SSOT registry entities without hand-editing `.ssot/registry.json`
- workers to pull maturation slices from a shared SSOT registry
- durable worker events and campaign status exposed through MCP tools
- a repo-pinned MCP server for one repository
- an explicit repo-per-call MCP server for development and test harnesses

Use another package when you want:

- [ssot-cli](https://pypi.org/project/ssot-cli/) for complete command-line workflow coverage
- [ssot-core](https://pypi.org/project/ssot-core/) for direct Python API access
- [ssot-registry](https://pypi.org/project/ssot-registry/) for the umbrella install bundle
- [ssot-tui](https://pypi.org/project/ssot-tui/) for terminal browsing

## Install

```bash
python -m pip install ssot-mcp
python -m pip install "ssot-registry[mcp]"
python -m pip install "ssot-registry[all]"
```

For local development:

```bash
python -m pip install -e pkgs/ssot-mcp
```

This package depends on [ssot-core](https://pypi.org/project/ssot-core/) and the official Python MCP runtime. Its SSOT dependency range tracks the current core release train with a compatible `<0.3.0` bound.

## Start the server

Run one pinned server per repository in normal use:

```powershell
ssot-mcp --transport stdio --repo E:\swarmauri_github\ssot-registry
```

Run global development mode only when every tool and resource call must provide an explicit `repo` argument:

```powershell
ssot-mcp --transport stdio --repo-mode explicit
```

See [Codex MCP configuration](../../docs/coordination/codex-mcp.md) for Codex `config.toml` examples.

## Registry write authority

Workers and MCP clients should not hand-edit `.ssot/registry.json`. When a client needs SSOT entity changes, it asks `ssot-mcp` to perform the mutation through registry tools such as:

- `registry_entity_get`
- `registry_entity_list`
- `registry_entity_search`
- `registry_entity_upsert`
- `registry_entity_delete`
- `registry_entity_link`
- `registry_entity_unlink`
- `get_ssot_cli_surface`
- `run_ssot_cli`
- mirrored `ssot_cli__*` tools for each live CLI command path

The structured entity tools use the same core registry mutation APIs as the CLI, validate before saving, and emit `registry_updated` events. `get_ssot_cli_surface` exposes the live parser inventory, `run_ssot_cli` remains the generic delegation fallback, and `ssot-mcp` also registers mirrored `ssot_cli__*` MCP tools for every current CLI command path. Together they keep the CLI and MCP surfaces aligned across global flags, help/version requests, commands, subcommands, command flags, and subcommand flags.

## Pull-worker campaign model

Workers pull work with `claim_next_maturation_slice`. Push notifications may wake, pause, refresh, or stop workers, but they do not assign feature or tier slices.

Useful tools include:

- `claim_next_maturation_slice`
- `get_slice_context`
- `complete_slice`
- `renew_lease`
- `abandon_slice`
- `get_campaign_status`
- `get_worker_events`
- `ack_worker_events`
- `get_conflicts`
- `scaffold_target_claim_wiring`
- `repair_blocked_transition`

`claim_next_maturation_slice` accepts `feature_ids`, `profile_ids`, and `boundary_ids`. Unscoped campaigns consider 25 in-bounds active features by default, and operators can raise `feature_limit` explicitly for broader campaigns. Out-of-bounds features are filtered from assignment and campaign status output.

Auto-scaffolding is enabled by default so `ssot-mcp` attempts target-tier claim, test, and evidence scaffolding before returning a blocked result. When a claim response returns `kind="blocked"`, it includes a top-level `reason` and structured `problem_detail` with recommended MCP tool calls.

## Package relationships

- Package type: optional MCP server package
- Depends on: [ssot-core](https://pypi.org/project/ssot-core/) and the official Python MCP runtime
- Optional via: [ssot-registry](https://pypi.org/project/ssot-registry/) extras `mcp` and `all`
- Related packages: [ssot-cli](https://pypi.org/project/ssot-cli/), [ssot-tui](https://pypi.org/project/ssot-tui/), [ssot-conformance](https://pypi.org/project/ssot-conformance/), [ssot-contracts](https://pypi.org/project/ssot-contracts/)

If you need an MCP server for Codex or another MCP-capable client, install this package. If you only need local command-line registry operations, install [ssot-cli](https://pypi.org/project/ssot-cli/).
