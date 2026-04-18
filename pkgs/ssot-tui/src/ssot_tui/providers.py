from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ssot_registry.api import get_document, list_entities, load_registry, validate_registry
from ssot_registry.api.documents import list_documents

from .presentations import SECTION_TO_COMMAND
from .state import ValidationSummary


@dataclass(slots=True)
class BridgeCommand:
    label: str
    command: list[str]
    cwd: str | None = None


class WorkspaceProvider:
    def resolve_startup_repo(self, path: str | Path) -> str:
        return self.resolve_preferred_repo(path)

    def resolve_preferred_repo(self, path: str | Path) -> str:
        return self.resolve_preferred_registry_path(path).parent.parent.as_posix()

    def resolve_preferred_registry_path(self, path: str | Path) -> Path:
        candidate = Path(path).expanduser()
        if candidate.name == "registry.json" and candidate.parent.name == ".ssot" and candidate.is_file():
            return candidate
        if candidate.name == ".ssot":
            direct = candidate / "registry.json"
            if direct.is_file():
                return direct
        direct = candidate / ".ssot" / "registry.json"
        if direct.is_file():
            return direct

        repo_boundary = self._nearest_git_boundary(candidate)
        roots = [candidate, *candidate.parents]
        if repo_boundary is not None:
            bounded_roots: list[Path] = []
            for root in roots:
                bounded_roots.append(root)
                if root == repo_boundary:
                    break
            ancestor_match: Path | None = None
            for root in bounded_roots:
                registry_path = root / ".ssot" / "registry.json"
                if registry_path.is_file():
                    ancestor_match = registry_path
            if ancestor_match is not None:
                return ancestor_match
            search_root = candidate if candidate.is_dir() else candidate.parent
            descendants = self._descendant_candidates(search_root)
            if descendants:
                return descendants[0]
            raise FileNotFoundError(
                "Unable to locate .ssot/registry.json from "
                f"{candidate}. Provide the repository root, the .ssot directory, "
                "the registry.json file, or any path inside a repository that contains .ssot/registry.json."
            )

        for root in roots:
            registry_path = root / ".ssot" / "registry.json"
            if registry_path.is_file():
                return registry_path

        search_root = candidate if candidate.is_dir() else candidate.parent
        descendants = self._descendant_candidates(search_root)
        if descendants:
            return descendants[0]

        raise FileNotFoundError(
            "Unable to locate .ssot/registry.json from "
            f"{candidate}. Provide the repository root, the .ssot directory, "
            "the registry.json file, or any path inside a repository that contains .ssot/registry.json."
        )

    def _nearest_git_boundary(self, path: Path) -> Path | None:
        for root in [path, *path.parents]:
            if (root / ".git").exists():
                return root
        return None

    def _descendant_candidates(self, search_root: Path) -> list[Path]:
        return sorted(
            (
                registry_path
                for registry_path in search_root.rglob("registry.json")
                if registry_path.parent.name == ".ssot" and registry_path.is_file()
            ),
            key=lambda registry_path: (len(registry_path.relative_to(search_root).parts), registry_path.as_posix()),
        )

    def build_validation_summary(self, validation: dict[str, Any]) -> ValidationSummary:
        failures = [str(item) for item in validation.get("failures", [])]
        warnings = [str(item) for item in validation.get("warnings", [])]
        section_failures: dict[str, int] = {}
        for failure in failures:
            prefix = failure.split(".", 1)[0]
            if prefix in SECTION_TO_COMMAND or prefix in {"adrs", "specs"}:
                section_failures[prefix] = section_failures.get(prefix, 0) + 1
        return ValidationSummary(
            passed=bool(validation.get("passed")),
            failure_count=len(failures),
            warning_count=len(warnings),
            failures=failures,
            warnings=warnings,
            last_checked_label="Just now",
            section_failures=section_failures,
        )

    def validate(self, path: str | Path) -> ValidationSummary:
        return self.build_validation_summary(validate_registry(path))


class BridgeActionProvider:
    def build_open_path_command(self, path: str | Path) -> BridgeCommand:
        target = Path(path).as_posix()
        if os.name == "nt":
            return BridgeCommand(label="open path", command=["explorer", target], cwd=None)
        if sys.platform == "darwin":
            return BridgeCommand(label="open path", command=["open", target], cwd=None)
        return BridgeCommand(label="open path", command=["xdg-open", target], cwd=None)

    def build_reveal_path_command(self, path: str | Path) -> BridgeCommand:
        target = Path(path)
        if os.name == "nt":
            return BridgeCommand(label="reveal path", command=["explorer", "/select,", target.as_posix()], cwd=None)
        if sys.platform == "darwin":
            return BridgeCommand(label="reveal path", command=["open", "-R", target.as_posix()], cwd=None)
        return BridgeCommand(label="reveal path", command=["xdg-open", target.parent.as_posix()], cwd=None)

    def build_cli_validate_command(self, repo_path: str | Path) -> BridgeCommand:
        return BridgeCommand(
            label="validate repo",
            command=[sys.executable, "-m", "ssot_cli.main", "validate", str(repo_path)],
            cwd=Path(repo_path).as_posix(),
        )

    def build_cli_list_command(self, repo_path: str | Path, section: str) -> BridgeCommand:
        command_name = SECTION_TO_COMMAND[section]
        return BridgeCommand(
            label=f"list {section}",
            command=[sys.executable, "-m", "ssot_cli.main", command_name, "list", str(repo_path)],
            cwd=Path(repo_path).as_posix(),
        )

    def build_cli_get_command(self, repo_path: str | Path, section: str, entity_id: str) -> BridgeCommand:
        command_name = SECTION_TO_COMMAND[section]
        id_flag = "--id" if section not in {"adrs", "specs"} else "--id"
        return BridgeCommand(
            label=f"get {entity_id}",
            command=[sys.executable, "-m", "ssot_cli.main", command_name, "get", str(repo_path), id_flag, entity_id],
            cwd=Path(repo_path).as_posix(),
        )

    def run(self, bridge_command: BridgeCommand) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        cwd = bridge_command.cwd
        if cwd is not None:
            repo_root = Path(cwd).resolve()
            src_paths = [
                repo_root / "pkgs" / "ssot-cli" / "src",
                repo_root / "pkgs" / "ssot-core" / "src",
                repo_root / "pkgs" / "ssot-contracts" / "src",
                repo_root / "pkgs" / "ssot-codegen" / "src",
                repo_root / "pkgs" / "ssot-views" / "src",
            ]
            env["PYTHONPATH"] = os.pathsep.join([str(path) for path in src_paths] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        return subprocess.run(bridge_command.command, cwd=cwd, env=env, capture_output=True, text=True, check=False)

    def preview_cli_read(self, repo_path: str | Path, section: str, entity_id: str | None = None) -> str:
        if section in {"adrs", "specs"}:
            kind = "adr" if section == "adrs" else "spec"
            if entity_id is None:
                return _preview_json(list_documents(repo_path, kind))
            try:
                return _preview_json(get_document(repo_path, kind, entity_id))
            except ValueError:
                return f"{entity_id} not found in {section}"
        if entity_id is None:
            payload = list_entities(repo_path, section)
            return _preview_json(payload)
        _, _, registry = load_registry(repo_path)
        for row in registry.get(section, []):
            if isinstance(row, dict) and row.get("id") == entity_id:
                return _preview_json(row)
        return f"{entity_id} not found in {section}"


def _preview_json(value: object) -> str:
    return str(value) if isinstance(value, str) else __import__("json").dumps(value, indent=2, sort_keys=True)
