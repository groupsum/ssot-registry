from __future__ import annotations

from pathlib import Path
from typing import Any

from ssot_registry.api.load import load_registry
from ssot_registry.control.service import ControlPlane
from ssot_registry.maturation.selector import next_maturation_slice

from .tools import resolve_repo


def registry_resource(repo: str | None = None) -> dict[str, Any]:
    _registry_path, _repo_root, registry = load_registry(resolve_repo(repo))
    return registry


def campaign_status_resource(repo: str | None = None, campaign_id: str = "", target_tier: str = "T2") -> dict[str, Any]:
    return ControlPlane(resolve_repo(repo)).get_campaign_status(campaign_id, target_tier=target_tier)


def maturation_queue_resource(repo: str | None = None, target_tier: str = "T2") -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(resolve_repo(repo))
    return {"next_slice": next_maturation_slice(registry, target_tier=target_tier, repo_root=repo_root)}
