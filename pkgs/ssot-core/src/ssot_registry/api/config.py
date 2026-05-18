from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from ssot_registry.util.errors import ValidationError

from .graph import export_graph
from .validate import validate_registry

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib


CONFIG_RELATIVE_PATH = ".ssot/ssot.toml"
_AUTOMATION_MODE_CHOICES = {"manual", "automatic"}
_GRAPH_FORMAT_CHOICES = {"json", "dot", "png", "svg"}

_DEFAULT_CONFIG: dict[str, Any] = {
    "policy": {
        "interactive": False,
        "fail_closed": True,
    },
    "sync": {
        "docs": "manual",
        "templates": "manual",
        "upstream_packages": "manual",
    },
    "validate": {
        "after_registry_change": "automatic",
    },
    "generation": {
        "mode": "manual",
        "formats": ["json"],
        "targets": {
            "graphs": False,
        },
        "graphs": {
            "mode": "manual",
            "formats": ["json"],
            "output_dir": ".ssot/graphs",
            "basename": "registry.graph",
        },
    },
}

_DEFAULT_TEMPLATE = """[policy]
interactive = false
fail_closed = true

[sync]
docs = "manual"
templates = "manual"
upstream_packages = "manual"

[validate]
after_registry_change = "automatic"

[generation]
mode = "manual"
formats = ["json"]

[generation.targets]
graphs = false

[generation.graphs]
mode = "manual"
formats = ["json"]
output_dir = ".ssot/graphs"
basename = "registry.graph"
"""

_AUTOMATION_DEPTH = 0


def _repo_root_from_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_file():
        if candidate.name == "registry.json" and candidate.parent.name == ".ssot":
            return candidate.parent.parent
        if candidate.parent.name == ".ssot":
            return candidate.parent.parent
        return candidate.parent
    if candidate.name == ".ssot":
        return candidate.parent
    return candidate


def _config_path(repo_root: Path) -> Path:
    return repo_root / CONFIG_RELATIVE_PATH


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _expect_table(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key)
    if not isinstance(value, dict):
        raise ValidationError(f"{key} must be a TOML table")
    return value


def _expect_bool(table: dict[str, Any], key: str, *, prefix: str) -> None:
    value = table.get(key)
    if not isinstance(value, bool):
        raise ValidationError(f"{prefix}.{key} must be a boolean")


def _expect_choice(table: dict[str, Any], key: str, choices: set[str], *, prefix: str) -> None:
    value = table.get(key)
    if not isinstance(value, str) or value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValidationError(f"{prefix}.{key} must be one of: {allowed}")


def _expect_string(table: dict[str, Any], key: str, *, prefix: str) -> None:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{prefix}.{key} must be a non-empty string")


def _expect_scalar_string_list(table: dict[str, Any], key: str, choices: set[str] | None = None, *, prefix: str) -> None:
    value = table.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValidationError(f"{prefix}.{key} must be a list of strings")
    if choices is not None:
        invalid = [item for item in value if item not in choices]
        if invalid:
            allowed = ", ".join(sorted(choices))
            raise ValidationError(f"{prefix}.{key} contains unsupported values {invalid}; allowed: {allowed}")


def validate_repo_config_payload(config: dict[str, Any]) -> dict[str, Any]:
    normalized = _deep_merge(_DEFAULT_CONFIG, config)

    policy = _expect_table(normalized, "policy")
    _expect_bool(policy, "interactive", prefix="policy")
    _expect_bool(policy, "fail_closed", prefix="policy")

    sync = _expect_table(normalized, "sync")
    for field_name in ("docs", "templates", "upstream_packages"):
        _expect_choice(sync, field_name, _AUTOMATION_MODE_CHOICES, prefix="sync")

    validate_cfg = _expect_table(normalized, "validate")
    _expect_choice(validate_cfg, "after_registry_change", _AUTOMATION_MODE_CHOICES, prefix="validate")

    generation = _expect_table(normalized, "generation")
    _expect_choice(generation, "mode", _AUTOMATION_MODE_CHOICES, prefix="generation")
    _expect_scalar_string_list(generation, "formats", choices={"json", "yaml", "toml", "md", "dot", "png", "svg"}, prefix="generation")

    targets = _expect_table(generation, "targets")
    _expect_bool(targets, "graphs", prefix="generation.targets")

    graphs = _expect_table(generation, "graphs")
    _expect_choice(graphs, "mode", _AUTOMATION_MODE_CHOICES, prefix="generation.graphs")
    _expect_scalar_string_list(graphs, "formats", choices=_GRAPH_FORMAT_CHOICES, prefix="generation.graphs")
    _expect_string(graphs, "output_dir", prefix="generation.graphs")
    _expect_string(graphs, "basename", prefix="generation.graphs")

    return normalized


def ensure_repo_config(path: str | Path, *, overwrite: bool = False) -> dict[str, Any]:
    repo_root = _repo_root_from_path(path)
    repo_root.mkdir(parents=True, exist_ok=True)
    config_path = _config_path(repo_root)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existed = config_path.exists()

    if existed and not overwrite:
        payload = load_repo_config(path)
        return {
            "passed": True,
            "config_path": payload["config_path"],
            "created": False,
            "overwritten": False,
            "config": payload["config"],
        }

    config_path.write_text(_DEFAULT_TEMPLATE, encoding="utf-8", newline="\n")
    payload = load_repo_config(path)
    return {
        "passed": True,
        "config_path": payload["config_path"],
        "created": not existed,
        "overwritten": existed and overwrite,
        "config": payload["config"],
    }


def load_repo_config(path: str | Path) -> dict[str, Any]:
    repo_root = _repo_root_from_path(path)
    config_path = _config_path(repo_root)
    if not config_path.exists():
        raise FileNotFoundError(f"Repo-local SSOT config not found: {config_path.as_posix()}")
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValidationError("Repo-local SSOT config must decode to a TOML table")
    normalized = validate_repo_config_payload(raw)
    return {
        "passed": True,
        "repo_root": repo_root.as_posix(),
        "config_path": config_path.as_posix(),
        "config": normalized,
    }


def validate_repo_config(path: str | Path) -> dict[str, Any]:
    payload = load_repo_config(path)
    return {
        "passed": True,
        "repo_root": payload["repo_root"],
        "config_path": payload["config_path"],
        "config": payload["config"],
    }


def run_repo_automation(path: str | Path) -> dict[str, Any]:
    global _AUTOMATION_DEPTH

    try:
        payload = load_repo_config(path)
    except FileNotFoundError as exc:
        return {
            "passed": True,
            "config_path": str(exc).removeprefix("Repo-local SSOT config not found: "),
            "skipped": True,
            "sync": None,
            "validation": None,
            "generation": {
                "graphs": [],
            },
        }
    config = payload["config"]
    results: dict[str, Any] = {
        "passed": True,
        "config_path": payload["config_path"],
        "skipped": False,
        "sync": None,
        "validation": None,
        "generation": {
            "graphs": [],
        },
    }
    if _AUTOMATION_DEPTH > 0:
        results["skipped"] = True
        return results

    _AUTOMATION_DEPTH += 1
    try:
        if config["sync"]["docs"] == "automatic":
            from .documents import sync_all_documents

            results["sync"] = sync_all_documents(path)

        if config["validate"]["after_registry_change"] == "automatic":
            validation = validate_registry(path)
            if not validation["passed"] and config["policy"]["fail_closed"]:
                raise ValidationError("Repo-local automation validation failed after registry change")
            results["validation"] = validation

        graph_cfg = config["generation"]["graphs"]
        if config["generation"]["targets"]["graphs"] and graph_cfg["mode"] == "automatic":
            repo_root = Path(payload["repo_root"])
            for output_format in graph_cfg["formats"]:
                output_path = repo_root / graph_cfg["output_dir"] / f"{graph_cfg['basename']}.{output_format}"
                graph_result = export_graph(path=path, output_format=output_format, output=output_path.as_posix())
                results["generation"]["graphs"].append(graph_result["output_path"])
    finally:
        _AUTOMATION_DEPTH -= 1

    return results
