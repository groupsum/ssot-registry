from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ssot_registry.control.paths import ensure_allowed_path, repo_relative_path


@dataclass(frozen=True)
class AclCommand:
    argv: tuple[str, ...]
    path: str
    action: str
    worker_user: str


class AclAdapter(Protocol):
    def grant_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]: ...

    def revoke_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]: ...


class AclPolicy:
    def __init__(self, repo_root: str | Path, adapter: AclAdapter | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.adapter = adapter or default_acl_adapter()

    def normalize_roots(self, paths: list[str | Path]) -> list[str]:
        return [ensure_allowed_path(repo_relative_path(self.repo_root, path)) for path in paths]

    def grant_commands(self, worker_user: str, paths: list[str | Path]) -> list[AclCommand]:
        return self.adapter.grant_commands(self.repo_root, worker_user, self.normalize_roots(paths))

    def revoke_commands(self, worker_user: str, paths: list[str | Path]) -> list[AclCommand]:
        return self.adapter.revoke_commands(self.repo_root, worker_user, self.normalize_roots(paths))

    def apply(self, commands: list[AclCommand]) -> None:
        for command in commands:
            subprocess.run(command.argv, check=True)

    def grant(self, worker_user: str, paths: list[str | Path]) -> list[AclCommand]:
        commands = self.grant_commands(worker_user, paths)
        self.apply(commands)
        return commands

    def revoke(self, worker_user: str, paths: list[str | Path]) -> list[AclCommand]:
        commands = self.revoke_commands(worker_user, paths)
        self.apply(commands)
        return commands


class LinuxAclAdapter:
    def grant_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]:
        commands: list[AclCommand] = []
        for path in paths:
            absolute = str(repo_root / path)
            commands.append(AclCommand(("setfacl", "-R", "-m", f"u:{worker_user}:rwX", absolute), path, "grant", worker_user))
            commands.append(AclCommand(("setfacl", "-R", "-d", "-m", f"u:{worker_user}:rwX", absolute), path, "grant-default", worker_user))
        return commands

    def revoke_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]:
        commands: list[AclCommand] = []
        for path in paths:
            absolute = str(repo_root / path)
            commands.append(AclCommand(("setfacl", "-R", "-x", f"u:{worker_user}", absolute), path, "revoke", worker_user))
            commands.append(AclCommand(("setfacl", "-R", "-d", "-x", f"u:{worker_user}", absolute), path, "revoke-default", worker_user))
        return commands


class WindowsAclAdapter:
    def grant_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]:
        commands: list[AclCommand] = []
        for path in paths:
            absolute = str(repo_root / path)
            commands.append(AclCommand(("icacls", absolute, "/grant", f"{worker_user}:(OI)(CI)(M)"), path, "grant", worker_user))
        return commands

    def revoke_commands(self, repo_root: Path, worker_user: str, paths: list[str]) -> list[AclCommand]:
        commands: list[AclCommand] = []
        for path in paths:
            absolute = str(repo_root / path)
            commands.append(AclCommand(("icacls", absolute, "/remove", worker_user), path, "revoke", worker_user))
        return commands


def default_acl_adapter() -> AclAdapter:
    if platform.system().lower().startswith("win"):
        return WindowsAclAdapter()
    return LinuxAclAdapter()
