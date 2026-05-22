from __future__ import annotations

import contextlib
import io
import json
import os
import argparse
from pathlib import Path
from threading import RLock
from typing import Any

from ssot_cli.main import build_parser, main as ssot_cli_main
from ssot_registry.version import __version__ as SSOT_CORE_VERSION
from ssot_registry.api.entity_ops import (
    SECTIONS,
    create_entity,
    delete_entity,
    get_entity,
    link_entities,
    list_entities,
    unlink_entities,
    update_entity,
)
from ssot_registry.control.service import ControlPlane

_PINNED_REPO: Path | None = None
_CLI_LOCK = RLock()
MCP_CLI_ROOT_TOOL_NAME = "ssot_cli__root"


def configure_repo(repo: str | Path | None) -> None:
    global _PINNED_REPO
    _PINNED_REPO = Path(repo).resolve() if repo is not None else None


def resolve_repo(repo: str | None = None) -> Path:
    if _PINNED_REPO is None:
        if repo is None:
            raise ValueError("repo is required unless ssot-mcp is started with --repo")
        return Path(repo).resolve()
    if repo is not None and Path(repo).resolve() != _PINNED_REPO:
        raise ValueError(f"ssot-mcp is pinned to {_PINNED_REPO}; refusing repo {Path(repo).resolve()}")
    return _PINNED_REPO


def _plane(repo: str | None = None) -> ControlPlane:
    return ControlPlane(resolve_repo(repo))


def _notify_registry_updated(repo_root: Path, payload: dict[str, Any]) -> None:
    ControlPlane(repo_root).notify_registry_updated(payload=payload)


def _section_name(section: str) -> str:
    normalized = section.strip().lower().replace("-", "_")
    aliases = {
        "feature": "features",
        "profile": "profiles",
        "test": "tests",
        "claim": "claims",
        "evidence": "evidence",
        "issue": "issues",
        "risk": "risks",
        "boundary": "boundaries",
        "release": "releases",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in SECTIONS:
        raise ValueError(f"unsupported registry section: {section}")
    return normalized


def _matches_query(row: dict[str, Any], query: str) -> bool:
    needle = query.lower()
    haystack = json.dumps(row, sort_keys=True, default=str).lower()
    return needle in haystack


def _cli_root_command(args: list[str]) -> str:
    skip_value_for = {"--output-format", "--output-file"}
    skip_next = False
    for token in args:
        if skip_next:
            skip_next = False
            continue
        if token in skip_value_for:
            skip_next = True
            continue
        if token.startswith("-"):
            continue
        return token
    return ""


def _option_flags(parser: argparse.ArgumentParser) -> list[str]:
    flags: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._HelpAction):
            continue
        for option in action.option_strings:
            if option not in flags:
                flags.append(option)
    return sorted(flags)


def _walk_parser(
    parser: argparse.ArgumentParser,
    path: list[str],
    subcommand_paths: list[str],
    flags_by_path: dict[str, list[str]],
) -> None:
    if path:
        path_key = " ".join(path)
        subcommand_paths.append(path_key)
        flags_by_path[path_key] = _option_flags(parser)

    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child_parser in sorted(action.choices.items()):
            _walk_parser(child_parser, [*path, name], subcommand_paths, flags_by_path)


def _cli_surface() -> dict[str, Any]:
    parser = build_parser(prog="ssot-registry")
    top_level_commands: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            top_level_commands = sorted(action.choices.keys())
            break

    subcommand_paths: list[str] = []
    flags_by_path: dict[str, list[str]] = {}
    _walk_parser(parser, [], subcommand_paths, flags_by_path)
    return {
        "top_level_commands": top_level_commands,
        "subcommand_paths": sorted(subcommand_paths),
        "global_flags": _option_flags(parser),
        "flags_by_path": {key: flags_by_path[key] for key in sorted(flags_by_path)},
    }


def mcp_cli_tool_name_for_path(path: str) -> str:
    tokens = [token.strip().lower().replace("-", "_") for token in path.split() if token.strip()]
    if not tokens:
        return MCP_CLI_ROOT_TOOL_NAME
    return "ssot_cli__" + "__".join(tokens)


def _mcp_cli_tool_map(surface: dict[str, Any]) -> dict[str, str]:
    return {path: mcp_cli_tool_name_for_path(path) for path in surface["subcommand_paths"]}


def _is_cli_metadata_request(args: list[str]) -> bool:
    return not args or any(token in {"-h", "--help", "--version"} for token in args)


def _resolve_repo_for_cli(repo: str | None, args: list[str]) -> Path:
    if repo is not None or _PINNED_REPO is not None:
        return resolve_repo(repo)
    if _is_cli_metadata_request(args):
        return Path.cwd()
    return resolve_repo(repo)


def _normalize_mcp_cli_args(args: list[str]) -> tuple[list[str], list[str]]:
    """Normalize delegated CLI calls that are unsafe or ambiguous for MCP workers."""

    if _cli_root_command(args) != "upgrade":
        return list(args), []

    normalized: list[str] = []
    warnings: list[str] = []
    skip_next = False
    saw_sync_docs = False
    for token in args:
        if skip_next:
            skip_next = False
            warnings.append(
                "MCP upgrade ignores --target-version and uses the currently running ssot-mcp binary/runtime instead."
            )
            continue
        if token == "--target-version":
            skip_next = True
            continue
        if token.startswith("--target-version="):
            warnings.append(
                "MCP upgrade ignores --target-version and uses the currently running ssot-mcp binary/runtime instead."
            )
            continue
        if token == "--sync-docs":
            saw_sync_docs = True
        normalized.append(token)

    if not saw_sync_docs:
        normalized.append("--sync-docs")
        warnings.append("MCP upgrade added --sync-docs so packaged ADR/SPEC documents are refreshed with the current runtime.")

    warnings.append(f"MCP upgrade is running with installed ssot-core version {SSOT_CORE_VERSION}.")
    return normalized, warnings


@contextlib.contextmanager
def _cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def claim_next_maturation_slice(
    repo: str | None = None,
    worker_id: str = "",
    campaign_id: str = "",
    target_tier: str = "T2",
    os_user: str | None = None,
    ttl_seconds: int = 1800,
    feature_ids: list[str] | None = None,
    profile_ids: list[str] | None = None,
    boundary_ids: list[str] | None = None,
    max_blockers_per_claim: int = 5,
    auto_scaffold: bool = True,
    feature_limit: int | None = 25,
) -> dict[str, Any]:
    return _plane(repo).claim_next_maturation_slice(
        worker_id=worker_id,
        campaign_id=campaign_id,
        target_tier=target_tier,
        os_user=os_user,
        ttl_seconds=ttl_seconds,
        feature_ids=feature_ids,
        profile_ids=profile_ids,
        boundary_ids=boundary_ids,
        max_blockers_per_claim=max_blockers_per_claim,
        auto_scaffold=auto_scaffold,
        feature_limit=feature_limit,
    )


def renew_lease(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, ttl_seconds: int = 1800) -> dict[str, Any]:
    return _plane(repo).renew_lease(
        worker_id=worker_id,
        lease_id=lease_id,
        fencing_token=fencing_token,
        ttl_seconds=ttl_seconds,
    )


def get_slice_context(repo: str | None = None, lease_id: str = "") -> dict[str, Any]:
    return _plane(repo).get_slice_context(lease_id)


def complete_slice(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, result: dict[str, Any] | None = None) -> dict[str, Any]:
    if result is None:
        result = {}
    return _plane(repo).complete_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, result=result)


def abandon_slice(repo: str | None = None, worker_id: str = "", lease_id: str = "", fencing_token: int = 0, reason: str = "") -> dict[str, Any]:
    return _plane(repo).abandon_slice(worker_id=worker_id, lease_id=lease_id, fencing_token=fencing_token, reason=reason)


def get_campaign_status(repo: str | None = None, campaign_id: str = "", target_tier: str = "T2", feature_limit: int | None = None) -> dict[str, Any]:
    return _plane(repo).get_campaign_status(campaign_id, target_tier=target_tier, feature_limit=feature_limit)


def get_worker_events(
    repo: str | None = None,
    worker_id: str | None = None,
    campaign_id: str | None = None,
    after_event_id: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    return _plane(repo).get_worker_events(
        worker_id=worker_id,
        campaign_id=campaign_id,
        after_event_id=after_event_id,
        limit=limit,
    )


def ack_worker_events(repo: str | None = None, worker_id: str = "", event_ids: list[int] | None = None, action: str = "processed") -> dict[str, Any]:
    if event_ids is None:
        event_ids = []
    return _plane(repo).ack_worker_events(worker_id=worker_id, event_ids=event_ids, action=action)


def get_conflicts(repo: str | None = None, status: str | None = "open") -> dict[str, Any]:
    return _plane(repo).get_conflicts(status=status)


def get_ssot_cli_surface(repo: str | None = None) -> dict[str, Any]:
    if repo is not None or _PINNED_REPO is not None:
        _resolve_repo_for_cli(repo, ["--help"])
    surface = _cli_surface()
    return {
        "passed": True,
        **surface,
        "root_tool_name": MCP_CLI_ROOT_TOOL_NAME,
        "tool_name_by_path": _mcp_cli_tool_map(surface),
    }


def get_blocked_transitions(repo: str | None = None, campaign_id: str | None = None, status: str | None = "open") -> dict[str, Any]:
    return {"passed": True, "blocked_transitions": _plane(repo).store.get_blocked_transitions(campaign_id=campaign_id, status=status)}


def scaffold_target_claim_wiring(repo: str | None = None, feature_id: str = "", target_tier: str = "T1") -> dict[str, Any]:
    return _plane(repo).scaffold_target_claim_wiring(feature_id=feature_id, target_tier=target_tier)


def repair_blocked_transition(repo: str | None = None, blocked_id: str = "") -> dict[str, Any]:
    return _plane(repo).repair_blocked_transition(blocked_id=blocked_id)


def repair_blocked_transitions(
    repo: str | None = None,
    campaign_id: str | None = None,
    feature_ids: list[str] | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    return _plane(repo).repair_blocked_transitions(campaign_id=campaign_id, feature_ids=feature_ids, limit=limit)


def registry_entity_get(repo: str | None = None, section: str = "", entity_id: str = "") -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    return {"passed": True, "section": resolved_section, "entity": get_entity(repo_root, resolved_section, entity_id)}


def registry_entity_list(
    repo: str | None = None,
    section: str = "",
    ids: list[str] | None = None,
    origin: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    rows = list_entities(repo_root, resolved_section, ids=ids, origin=origin)
    total = len(rows)
    limited = rows[max(offset, 0) : max(offset, 0) + max(limit, 0)]
    return {"passed": True, "section": resolved_section, "total": total, "offset": offset, "limit": limit, "entities": limited}


def registry_entity_search(repo: str | None = None, section: str = "", query: str = "", limit: int = 100, offset: int = 0) -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    rows = [row for row in list_entities(repo_root, resolved_section) if _matches_query(row, query)]
    total = len(rows)
    limited = rows[max(offset, 0) : max(offset, 0) + max(limit, 0)]
    return {"passed": True, "section": resolved_section, "query": query, "total": total, "offset": offset, "limit": limit, "entities": limited}


def registry_entity_upsert(repo: str | None = None, section: str = "", entity: dict[str, Any] | None = None) -> dict[str, Any]:
    if entity is None:
        entity = {}
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    entity_id = entity.get("id")
    if not isinstance(entity_id, str) or not entity_id:
        raise ValueError("entity.id is required")
    try:
        existing = get_entity(repo_root, resolved_section, entity_id)
    except ValueError:
        result = create_entity(repo_root, resolved_section, entity)
        action = "create"
    else:
        result = update_entity(repo_root, resolved_section, entity_id, entity)
        action = "update"
        result["previous_entity"] = existing
    _notify_registry_updated(repo_root, {"source": "ssot-mcp", "tool": "registry_entity_upsert", "section": resolved_section, "entity_id": entity_id, "action": action})
    return result


def registry_entity_delete(repo: str | None = None, section: str = "", entity_id: str = "") -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    result = delete_entity(repo_root, resolved_section, entity_id)
    _notify_registry_updated(repo_root, {"source": "ssot-mcp", "tool": "registry_entity_delete", "section": resolved_section, "entity_id": entity_id})
    return result


def registry_entity_link(repo: str | None = None, section: str = "", entity_id: str = "", links: dict[str, list[str]] | None = None) -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    result = link_entities(repo_root, resolved_section, entity_id, links or {})
    _notify_registry_updated(repo_root, {"source": "ssot-mcp", "tool": "registry_entity_link", "section": resolved_section, "entity_id": entity_id, "links": links or {}})
    return result


def registry_entity_unlink(repo: str | None = None, section: str = "", entity_id: str = "", links: dict[str, list[str]] | None = None) -> dict[str, Any]:
    repo_root = resolve_repo(repo)
    resolved_section = _section_name(section)
    result = unlink_entities(repo_root, resolved_section, entity_id, links or {})
    _notify_registry_updated(repo_root, {"source": "ssot-mcp", "tool": "registry_entity_unlink", "section": resolved_section, "entity_id": entity_id, "links": links or {}})
    return result


def run_ssot_cli(repo: str | None = None, args: list[str] | None = None) -> dict[str, Any]:
    """Run the SSOT CLI in-process against the resolved repo root.

    The server changes cwd to the target repo for the duration of the call so
    normal CLI commands using the default `.` path operate on the MCP-selected
    registry. Arguments are argv tokens after `ssot`.
    """

    original_args = list(args or [])
    normalized_args, normalization_warnings = _normalize_mcp_cli_args(original_args)
    repo_root = _resolve_repo_for_cli(repo, normalized_args)
    argv = list(normalized_args)
    metadata_request = _is_cli_metadata_request(argv)
    if "--output-format" not in argv and not metadata_request:
        argv = ["--output-format", "json", *argv]
    stdout = io.StringIO()
    stderr = io.StringIO()
    with _CLI_LOCK:
        with _cwd(repo_root), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exit_code = ssot_cli_main(argv)
            except SystemExit as exc:
                code = exc.code
                exit_code = int(code) if isinstance(code, int) else 1
    stdout_text = stdout.getvalue()
    stderr_text = stderr.getvalue()
    try:
        payload: Any = json.loads(stdout_text) if stdout_text.strip() else None
    except json.JSONDecodeError:
        payload = stdout_text
    mutating_roots = {
        "init",
        "upgrade",
        "config",
        "adr",
        "spec",
        "feature",
        "profile",
        "test",
        "issue",
        "claim",
        "evidence",
        "risk",
        "boundary",
        "release",
        "registry",
    }
    command = _cli_root_command(original_args)
    if exit_code == 0 and command in mutating_roots:
        _notify_registry_updated(repo_root, {"source": "ssot-mcp", "tool": "run_ssot_cli", "args": original_args, "normalized_args": normalized_args})
    return {
        "passed": exit_code == 0,
        "exit_code": exit_code,
        "args": original_args,
        "normalized_args": normalized_args,
        "warnings": normalization_warnings,
        "output": payload,
        "stdout": stdout_text,
        "stderr": stderr_text,
    }
