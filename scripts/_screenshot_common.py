from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-cli" / "assets"
TUI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-tui" / "assets"
DEFAULT_REPO = PROJECT_ROOT / "examples" / "minimal-repo"


def bootstrap_paths() -> None:
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


def render_help(argv: list[str]) -> str:
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


def write_svg(output_path: Path, title: str, text: str, *, width: int = 120) -> None:
    from rich.console import Console
    from rich.text import Text

    output_path.parent.mkdir(parents=True, exist_ok=True)
    console = Console(record=True, width=width, file=io.StringIO())
    console.print(Text(text))
    output_path.write_text(console.export_svg(title=title), encoding="utf-8")


def write_text_screenshot_png(output_path: Path, text: str, *, width: int = 120, height: int = 42) -> None:
    import asyncio

    from textual.app import App, ComposeResult
    from textual.widgets import Static

    output_path.parent.mkdir(parents=True, exist_ok=True)

    class ScreenshotApp(App[None]):
        CSS = """
        Screen {
            align: center middle;
        }

        #capture {
            width: 1fr;
            height: 1fr;
            padding: 1 2;
        }
        """

        def compose(self) -> ComposeResult:
            yield Static(text, id="capture")

    async def _capture() -> None:
        app = ScreenshotApp()
        async with app.run_test(size=(width, height)) as pilot:
            await pilot.pause()
            app.save_screenshot(filename=output_path.name, path=str(output_path.parent))

    asyncio.run(_capture())


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()
