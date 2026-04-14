from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ssot_registry.graph.export_dot import build_graph_dot
from ssot_registry.graph.export_json import build_graph_json
from ssot_registry.util.jsonio import save_json

from .load import load_registry


_IMAGE_FORMATS = {"png", "svg"}


def _render_dot_image(dot_text: str, output_path: Path, image_format: str) -> None:
    dot_bin = shutil.which("dot")
    if dot_bin is None:
        raise ValueError("Graphviz 'dot' binary is required for image export but was not found in PATH")
    process = subprocess.run(
        [dot_bin, f"-T{image_format}", "-o", output_path.as_posix()],
        input=dot_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or "unknown error"
        raise ValueError(f"dot image export failed: {detail}")


def export_graph(path: str | Path, output_format: str, output: str | None = None) -> dict[str, object]:
    registry_path, repo_root, registry = load_registry(path)

    if output_format == "json":
        artifact = build_graph_json(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / "registry.graph.json"
        save_json(output_path, artifact)
    elif output_format == "dot":
        artifact = build_graph_dot(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / "registry.graph.dot"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(artifact, encoding="utf-8")
    elif output_format in _IMAGE_FORMATS:
        dot_text = build_graph_dot(registry)
        output_path = Path(output) if output is not None else repo_root / ".ssot" / "graphs" / f"registry.graph.{output_format}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _render_dot_image(dot_text, output_path, output_format)
    else:
        raise ValueError(f"Unsupported graph format: {output_format}")

    return {
        "passed": True,
        "registry_path": registry_path.as_posix(),
        "output_path": output_path.as_posix(),
        "format": output_format,
    }
