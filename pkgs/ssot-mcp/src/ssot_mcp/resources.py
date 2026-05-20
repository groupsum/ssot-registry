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


def campaign_status_resource(repo: str | None = None, campaign_id: str = "") -> dict[str, Any]:
    return ControlPlane(resolve_repo(repo)).get_campaign_status(campaign_id, target_tier="T2")


def maturation_queue_resource(repo: str | None = None) -> dict[str, Any]:
    _registry_path, repo_root, registry = load_registry(resolve_repo(repo))
    return {"next_slice": next_maturation_slice(registry, target_tier="T2", repo_root=repo_root)}
