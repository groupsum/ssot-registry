from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.api import validate_registry
from ssot_registry.util.jsonio import save_json


def register_validate(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("validate", help="Validate a registry file or repository root.")
    parser.add_argument("path", nargs="?", default=".", help="Registry file path or repository root.")
    parser.add_argument("--write-report", action="store_true", help="Write validation report under .ssot/reports.")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> dict[str, object]:
    report = validate_registry(args.path)
    if args.write_report:
        path = Path(args.path)
        repo_root = path if path.is_dir() else path.parent.parent
        output_path = repo_root / ".ssot" / "reports" / "validation.report.json"
        save_json(output_path, report)
        report["report_path"] = output_path.as_posix()
    return report
