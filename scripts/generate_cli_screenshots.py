from __future__ import annotations

import argparse
from pathlib import Path

from _screenshot_common import CLI_ASSET_ROOT, bootstrap_paths, display_path, render_help, write_text_screenshot_png


bootstrap_paths()


def capture_cli_screenshots(asset_root: Path) -> list[Path]:
    screenshots = (
        (asset_root / "ssot-cli-help.png", []),
        (asset_root / "ssot-cli-boundary-help.png", ["boundary", "--help"]),
    )
    written: list[Path] = []
    for output_path, argv in screenshots:
        write_text_screenshot_png(output_path, render_help(list(argv)))
        written.append(output_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PNG screenshots for the SSOT CLI README.")
    parser.add_argument("--asset-root", default=str(CLI_ASSET_ROOT), help="Directory to write CLI screenshots into.")
    args = parser.parse_args()

    written = capture_cli_screenshots(Path(args.asset_root).resolve())
    for path in written:
        print(display_path(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
