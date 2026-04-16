from __future__ import annotations

from importlib import import_module
from collections.abc import Callable
from typing import Any


def _load_cli_symbol(name: str) -> Any:
    try:
        cli_main = import_module("ssot_cli.main")
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.split(".", 1)[0] == "ssot_cli":
            raise RuntimeError(
                "CLI compatibility shims live in the ssot-cli package. Install ssot-cli to use the command surface."
            ) from exc
        raise
    return getattr(cli_main, name)


def build_parser(*args: Any, **kwargs: Any) -> Any:
    builder = _load_cli_symbol("build_parser")
    return builder(*args, **kwargs)


def main(argv: list[str] | None = None) -> int:
    entrypoint = _load_cli_symbol("main")
    return entrypoint(argv)


def __getattr__(name: str) -> Callable[..., Any]:
    if name.startswith("register_"):
        return _load_cli_symbol(name)
    raise AttributeError(name)


__all__ = [
    "build_parser",
    "main",
]
