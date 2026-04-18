from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from _screenshot_common import DEFAULT_REPO, TUI_ASSET_ROOT, bootstrap_paths, display_path


bootstrap_paths()


async def capture_tui_screenshots(repo_path: Path, asset_root: Path) -> list[Path]:
    from textual.widgets import Input

    from ssot_tui.app import SsotTuiApp

    app = SsotTuiApp()
    browser_output = asset_root / "ssot-tui-browser.png"
    validated_output = asset_root / "ssot-tui-validated.png"
    browser_output.parent.mkdir(parents=True, exist_ok=True)
    async with app.run_test(size=(140, 40)) as pilot:
        input_widget = app.screen.query_one("#repo_path", Input)
        input_widget.value = str(repo_path)
        app.screen.action_reload_workspace()
        await pilot.pause()
        app.save_screenshot(filename=browser_output.name, path=str(browser_output.parent))
        app.screen.action_validate_workspace()
        await pilot.pause()
        app.save_screenshot(filename=validated_output.name, path=str(validated_output.parent))
    return [browser_output, validated_output]


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
