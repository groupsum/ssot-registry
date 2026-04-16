from __future__ import annotations

from pathlib import Path

from ssot_registry.util.formatting import render_payload

from .load import load_registry


def export_registry(path: str | Path, output_format: str, output: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)
    extension = output_format if output_format != "df" else "txt"
    output_path = Path(output) if output is not None else repo_root / ".ssot" / "exports" / f"registry.{extension}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_payload(registry, output_format), encoding="utf-8")
    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "output_path": output_path.as_posix(),
        "format": output_format,
    }
