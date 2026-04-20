from __future__ import annotations

import argparse
from pathlib import Path

from ssot_registry.api import validate_registry
from ssot_registry.util.jsonio import save_json


def register_validate(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate",
        help="Check registry integrity and guard compliance.",
        description="Validate an SSOT repository or registry file and report schema, linkage, and guard failures.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository root or registry file to validate.")
    parser.add_argument("--write-report", action="store_true", help="Write the validation report under `.ssot/reports` for later review.")
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
