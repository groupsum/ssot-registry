from __future__ import annotations

import argparse
from pathlib import Path

from .generator import generate_python_artifacts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate SSOT Python-side contract metadata artifacts.")
    parser.add_argument(
        "--output-root",
        default=str(Path.cwd() / ".tmp_codegen"),
        help="Directory where generated JSON artifacts should be written.",
    )
    args = parser.parse_args(argv)
    written = generate_python_artifacts(args.output_root)
    for path in written:
        print(path.as_posix())
    return 0
