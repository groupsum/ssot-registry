from __future__ import annotations

import argparse
import asyncio
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-cli" / "assets"
TUI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-tui" / "assets"
DEFAULT_REPO = PROJECT_ROOT / "examples" / "minimal-repo"


def _bootstrap_paths() -> None:
    candidate_paths = [
        PROJECT_ROOT / "pkgs" / "ssot-registry" / "src",
        PROJECT_ROOT / "pkgs" / "ssot-codegen" / "src",
        PROJECT_ROOT / "pkgs" / "ssot-views" / "src",
        PROJECT_ROOT / "pkgs" / "ssot-contracts" / "src",
        PROJECT_ROOT / "pkgs" / "ssot-cli" / "src",
        PROJECT_ROOT / "pkgs" / "ssot-tui" / "src",
        PROJECT_ROOT / ".venv" / "Lib" / "site-packages",
    ]
    candidate_paths.extend((PROJECT_ROOT / ".venv" / "lib").glob("python*/site-packages"))
    for path in candidate_paths:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))


_bootstrap_paths()


def _render_help(argv: list[str]) -> str:
    from ssot_cli.main import build_parser

    parser = build_parser(prog="ssot")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        if argv:
            try:
                parser.parse_args(argv)
            except SystemExit:
                pass
        else:
            parser.print_help()
    return buffer.getvalue().rstrip()


def _write_svg(output_path: Path, title: str, text: str, *, width: int = 120) -> None:
    from rich.console import Console
    from rich.text import Text

    output_path.parent.mkdir(parents=True, exist_ok=True)
    console = Console(record=True, width=width, file=io.StringIO())
    console.print(Text(text))
    output_path.write_text(console.export_svg(title=title), encoding="utf-8")


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def capture_cli_screenshots(asset_root: Path) -> list[Path]:
    screenshots = (
        ("SSOT CLI", asset_root / "ssot-cli-help.svg", []),
        ("SSOT Boundary Help", asset_root / "ssot-cli-boundary-help.svg", ["boundary", "--help"]),
    )
    written: list[Path] = []
    for title, output_path, argv in screenshots:
        _write_svg(output_path, title, _render_help(list(argv)))
        written.append(output_path)
    return written


async def capture_tui_screenshots(repo_path: Path, asset_root: Path) -> list[Path]:
    from textual.widgets import Input

    from ssot_tui.app import SsotTuiApp

    app = SsotTuiApp()
    browser_output = asset_root / "ssot-tui-browser.svg"
    validated_output = asset_root / "ssot-tui-validated.svg"
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
    parser = argparse.ArgumentParser(description="Generate SVG screenshots for the SSOT CLI and TUI READMEs.")
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
        written.extend(asyncio.run(capture_tui_screenshots(repo_path, tui_asset_root)))

    for path in written:
        print(_display_path(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
