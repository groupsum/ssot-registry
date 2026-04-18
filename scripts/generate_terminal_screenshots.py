from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _screenshot_common import CLI_ASSET_ROOT, DEFAULT_REPO, PROJECT_ROOT, TUI_ASSET_ROOT, bootstrap_paths
from generate_cli_screenshots import capture_cli_screenshots
from generate_tui_screenshots import capture_tui_screenshots


bootstrap_paths()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PNG screenshots for the SSOT CLI and TUI READMEs.")
    parser.add_argument("--repo", default=str(DEFAULT_REPO), help="Repository path to load in the TUI screenshots.")
    parser.add_argument("--cli-asset-root", default=str(CLI_ASSET_ROOT), help="Directory to write CLI screenshots into.")
    parser.add_argument("--tui-asset-root", default=str(TUI_ASSET_ROOT), help="Directory to write TUI screenshots into.")
    parser.add_argument("--cli-only", action="store_true", help="Generate only CLI screenshots.")
    parser.add_argument("--tui-only", action="store_true", help="Generate only TUI screenshots.")
    args = parser.parse_args()

    if args.cli_only and args.tui_only:
        parser.error("--cli-only and --tui-only are mutually exclusive")

    repo_path = Path(args.repo).resolve()
    cli_asset_root = Path(args.cli_asset_root).resolve()
    tui_asset_root = Path(args.tui_asset_root).resolve()
    if not repo_path.exists():
        parser.error(f"Repository path does not exist: {repo_path}")

    written: list[Path] = []
    if not args.tui_only:
        written.extend(capture_cli_screenshots(cli_asset_root))
    if not args.cli_only:
        import asyncio

        written.extend(asyncio.run(capture_tui_screenshots(repo_path, tui_asset_root)))

    for path in written:
        print(path.resolve().relative_to(PROJECT_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
