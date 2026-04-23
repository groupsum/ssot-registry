from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from _screenshot_common import (
    DEFAULT_REPO,
    SCREENSHOT_TEXTUAL_THEME,
    TUI_ASSET_ROOT,
    bootstrap_paths,
    display_path,
    save_textual_screenshot_png,
)


bootstrap_paths()


async def capture_tui_screenshots(repo_path: Path, asset_root: Path) -> list[Path]:
    from textual.widgets import Input

    from ssot_tui.app import SsotTuiApp
    from ssot_tui.widgets import EntityTable

    app = SsotTuiApp()
    app.theme = SCREENSHOT_TEXTUAL_THEME
    browser_output = asset_root / "ssot-tui-browser.png"
    adr_output = asset_root / "ssot-tui-adrs.png"
    spec_output = asset_root / "ssot-tui-specs.png"
    validated_output = asset_root / "ssot-tui-validated.png"
    browser_output.parent.mkdir(parents=True, exist_ok=True)

    async def capture_section(section: str, output_path: Path) -> None:
        app.screen._select_section(section)
        await pilot.pause()
        table = app.screen.query_one(EntityTable)
        if table.row_count == 0:
            raise RuntimeError(f"No rows visible in the {section} table for screenshot generation.")
        save_textual_screenshot_png(app, output_path)

    original_cwd = Path.cwd()
    os.chdir(repo_path)
    try:
        async with app.run_test(size=(140, 40)) as pilot:
            input_widget = app.screen.query_one("#repo_path", Input)
            input_widget.value = "."
            app.screen.action_reload_workspace()
            await pilot.pause()
            save_textual_screenshot_png(app, browser_output)
            await capture_section("adrs", adr_output)
            await capture_section("specs", spec_output)
            app.screen.action_validate_workspace()
            await pilot.pause()
            save_textual_screenshot_png(app, validated_output)
    finally:
        os.chdir(original_cwd)
    return [browser_output, adr_output, spec_output, validated_output]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PNG screenshots for the SSOT TUI README.")
    parser.add_argument("--repo", default=str(DEFAULT_REPO), help="Repository path to load in the TUI screenshots.")
    parser.add_argument("--asset-root", default=str(TUI_ASSET_ROOT), help="Directory to write TUI screenshots into.")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    if not repo_path.exists():
        parser.error(f"Repository path does not exist: {repo_path}")

    written = asyncio.run(capture_tui_screenshots(repo_path, Path(args.asset_root).resolve()))
    for path in written:
        print(display_path(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
