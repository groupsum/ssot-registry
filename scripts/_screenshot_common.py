from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from binascii import crc32
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-cli" / "assets"
TUI_ASSET_ROOT = PROJECT_ROOT / "pkgs" / "ssot-tui" / "assets"
DEFAULT_REPO = PROJECT_ROOT
SCREENSHOT_TEXTUAL_THEME = "textual-dark"
SCREENSHOT_BACKGROUND_HEX = "#07111f"
SCREENSHOT_SURFACE_HEX = "#0f1b2e"
SCREENSHOT_FOREGROUND_HEX = "#edf6ff"
SCREENSHOT_ACCENT_HEX = "#38d5ff"
SCREENSHOT_CANVAS_WIDTH = 3600
SCREENSHOT_CANVAS_HEIGHT = 2240


def bootstrap_paths() -> None:
    candidate_paths = [
        PROJECT_ROOT / "pkgs" / "ssot-core" / "src",
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
    from rich.terminal_theme import TerminalTheme
    from rich.text import Text

    output_path.parent.mkdir(parents=True, exist_ok=True)
    console = Console(record=True, width=width, file=io.StringIO())
    console.print(Text(text))
    screenshot_theme = TerminalTheme(
        (11, 18, 32),
        (217, 226, 242),
        [
            (11, 18, 32),
            (239, 83, 80),
            (111, 200, 155),
            (255, 214, 102),
            (89, 169, 255),
            (190, 153, 255),
            (106, 226, 210),
            (217, 226, 242),
        ],
        [
            (95, 112, 138),
            (255, 138, 128),
            (170, 235, 202),
            (255, 229, 148),
            (149, 203, 255),
            (216, 189, 255),
            (159, 241, 231),
            (241, 245, 255),
        ],
    )
    output_path.write_text(console.export_svg(title=title, theme=screenshot_theme), encoding="utf-8")


def write_text_screenshot_png(output_path: Path, text: str, *, width: int = 120, height: int = 42) -> None:
    import asyncio

    from textual.app import App, ComposeResult
    from textual.widgets import Static

    output_path.parent.mkdir(parents=True, exist_ok=True)
    capture_css = f"""
    Screen {{
        align: center middle;
        background: {SCREENSHOT_BACKGROUND_HEX};
        color: {SCREENSHOT_FOREGROUND_HEX};
    }}

    #capture {{
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        background: {SCREENSHOT_SURFACE_HEX};
        color: {SCREENSHOT_FOREGROUND_HEX};
        border: round {SCREENSHOT_ACCENT_HEX};
    }}
    """

    class ScreenshotApp(App[None]):
        CSS = capture_css

        def compose(self) -> ComposeResult:
            yield Static(text, id="capture")

    async def _capture() -> None:
        app = ScreenshotApp()
        async with app.run_test(size=(width, height)) as pilot:
            await pilot.pause()
            save_textual_screenshot_png(app, output_path)

    asyncio.run(_capture())


def save_textual_screenshot_png(app: object, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output_path.parent) as temp_dir:
        svg_path = Path(temp_dir) / f"{output_path.stem}.svg"
        app.save_screenshot(filename=svg_path.name, path=str(svg_path.parent))
        render_svg_to_png(svg_path, output_path)


def render_svg_to_png(svg_path: Path, output_path: Path) -> None:
    browser = _find_headless_browser()
    if browser is not None:
        try:
            _render_svg_to_png_with_browser(svg_path, output_path, browser)
            return
        except RuntimeError:
            pass
    if os.name == "nt":
        _render_svg_to_png_with_powershell(svg_path, output_path)
        return
    _write_placeholder_png_from_svg(svg_path, output_path)


def _render_svg_to_png_with_browser(svg_path: Path, output_path: Path, browser: Path) -> None:
    svg_text = svg_path.read_text(encoding="utf-8", errors="replace")
    title = _display_title_from_path(output_path)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: {SCREENSHOT_BACKGROUND_HEX};
      --surface: {SCREENSHOT_SURFACE_HEX};
      --fg: {SCREENSHOT_FOREGROUND_HEX};
      --accent: {SCREENSHOT_ACCENT_HEX};
      --hot: #ff5c9a;
      --green: #75f0b4;
      --amber: #ffcf5a;
    }}

    * {{
      box-sizing: border-box;
    }}

    html,
    body {{
      width: {SCREENSHOT_CANVAS_WIDTH}px;
      height: {SCREENSHOT_CANVAS_HEIGHT}px;
      margin: 0;
      overflow: hidden;
    }}

    body {{
      background:
        radial-gradient(circle at 13% 18%, rgba(56, 213, 255, 0.42), transparent 26%),
        radial-gradient(circle at 82% 16%, rgba(255, 92, 154, 0.32), transparent 24%),
        radial-gradient(circle at 74% 83%, rgba(117, 240, 180, 0.24), transparent 27%),
        linear-gradient(135deg, #06101d 0%, #0c1e32 44%, #10162a 100%);
      color: var(--fg);
      font-family: "Aptos", "Segoe UI", sans-serif;
    }}

    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      opacity: 0.28;
      background-image:
        linear-gradient(rgba(237, 246, 255, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(237, 246, 255, 0.08) 1px, transparent 1px);
      background-size: 96px 96px;
      mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), transparent 88%);
    }}

    .frame {{
      position: absolute;
      inset: 152px;
      display: grid;
      grid-template-rows: auto 1fr;
      border: 1px solid rgba(237, 246, 255, 0.18);
      border-radius: 68px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.11), rgba(255, 255, 255, 0.035)),
        rgba(7, 17, 31, 0.74);
      box-shadow:
        0 84px 240px rgba(0, 0, 0, 0.48),
        inset 0 1px 0 rgba(255, 255, 255, 0.22);
      backdrop-filter: blur(18px);
      overflow: hidden;
    }}

    .topbar {{
      height: 156px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 68px;
      border-bottom: 1px solid rgba(237, 246, 255, 0.12);
      background: linear-gradient(90deg, rgba(15, 27, 46, 0.92), rgba(21, 38, 63, 0.72));
      letter-spacing: 0.01em;
    }}

    .window-controls {{
      display: flex;
      gap: 24px;
    }}

    .window-controls span {{
      width: 32px;
      height: 32px;
      border-radius: 999px;
      box-shadow: 0 0 48px currentColor;
    }}

    .window-controls span:nth-child(1) {{ color: var(--hot); background: var(--hot); }}
    .window-controls span:nth-child(2) {{ color: var(--amber); background: var(--amber); }}
    .window-controls span:nth-child(3) {{ color: var(--green); background: var(--green); }}

    .title {{
      font-size: 46px;
      font-weight: 720;
      color: rgba(237, 246, 255, 0.94);
    }}

    .pill {{
      padding: 16px 30px;
      border: 1px solid rgba(56, 213, 255, 0.44);
      border-radius: 999px;
      color: #b9f2ff;
      background: rgba(56, 213, 255, 0.1);
      font-size: 30px;
      font-weight: 650;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .shot {{
      min-height: 0;
      padding: 64px;
      background:
        radial-gradient(circle at 8% 12%, rgba(56, 213, 255, 0.18), transparent 23%),
        linear-gradient(135deg, rgba(7, 17, 31, 0.92), rgba(15, 27, 46, 0.96));
    }}

    .shot svg {{
      width: 100%;
      height: 100%;
      display: block;
      border-radius: 40px;
      filter: drop-shadow(0 44px 84px rgba(0, 0, 0, 0.42));
    }}
  </style>
</head>
<body>
  <main class="frame">
    <header class="topbar">
      <div class="window-controls" aria-hidden="true"><span></span><span></span><span></span></div>
      <div class="title">{title}</div>
      <div class="pill">SSOT</div>
    </header>
    <section class="shot">
      {svg_text}
    </section>
  </main>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output_path.parent) as temp_dir:
        html_path = Path(temp_dir) / f"{output_path.stem}.html"
        profile_path = Path(temp_dir) / "browser-profile"
        html_path.write_text(html, encoding="utf-8")
        result = subprocess.run(
            [
                str(browser),
                "--headless",
                "--disable-gpu",
                "--disable-crash-reporter",
                "--disable-features=Crashpad",
                "--hide-scrollbars",
                f"--user-data-dir={profile_path}",
                f"--window-size={SCREENSHOT_CANVAS_WIDTH},{SCREENSHOT_CANVAS_HEIGHT}",
                f"--screenshot={output_path}",
                html_path.resolve().as_uri(),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"SVG-to-PNG render failed: {result.returncode}")


def _display_title_from_path(path: Path) -> str:
    words = [word.upper() if word in {"cli", "tui", "ssot"} else word.title() for word in path.stem.split("-")]
    return " ".join(words)


def _write_placeholder_png_from_svg(svg_path: Path, output_path: Path) -> None:
    width, height = _svg_viewbox_dimensions(svg_path)
    background = _svg_background_rgba(svg_path)
    row = bytes([0]) + bytes(background) * width
    compressed = zlib.compress(row * height, level=9)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return len(payload).to_bytes(4, "big") + kind + payload + crc32(kind + payload).to_bytes(4, "big")

    ihdr = width.to_bytes(4, "big") + height.to_bytes(4, "big") + bytes((8, 6, 0, 0, 0))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    output_path.write_bytes(png)


def _svg_background_rgba(svg_path: Path) -> tuple[int, int, int, int]:
    text = svg_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"<rect[^>]*fill=\"(#[0-9A-Fa-f]{6})\"[^>]*/?>", text)
    if match is None:
        return (0, 0, 0, 255)
    value = match.group(1)
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5)) + (255,)


def _render_svg_to_png_with_powershell(svg_path: Path, output_path: Path) -> None:
    script = """
param(
    [string]$SvgPath,
    [string]$PngPath
)

Add-Type -AssemblyName System.Drawing

[xml]$svg = Get-Content -LiteralPath $SvgPath -Raw -Encoding UTF8
$viewBoxParts = ($svg.svg.viewBox -split ' ')
$width = [int][Math]::Ceiling([double]$viewBoxParts[2])
$height = [int][Math]::Ceiling([double]$viewBoxParts[3])

$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear([System.Drawing.ColorTranslator]::FromHtml("__SCREENSHOT_BACKGROUND__"))

$backgroundRect = $svg.svg.rect | Where-Object { $_.fill -and $_.stroke } | Select-Object -First 1
if ($backgroundRect -and $backgroundRect.fill) {
    $graphics.Clear([System.Drawing.ColorTranslator]::FromHtml($backgroundRect.fill))
}

$styleText = [string]$svg.svg.style.'#text'
$styleMatches = [regex]::Matches($styleText, '\\.(?<class>[^\\s{]+)\\s*\\{\\s*fill:\\s*(?<fill>#[0-9A-Fa-f]{6})(?<rest>[^}]*)\\}')
$fills = @{}
$weights = @{}
foreach ($match in $styleMatches) {
    $className = $match.Groups['class'].Value
    $fills[$className] = $match.Groups['fill'].Value
    $weights[$className] = $match.Groups['rest'].Value -match 'font-weight:\\s*bold'
}

$ns = New-Object System.Xml.XmlNamespaceManager($svg.NameTable)
$ns.AddNamespace('svg', 'http://www.w3.org/2000/svg')
$textNodes = $svg.SelectNodes('//svg:text', $ns)

foreach ($node in $textNodes) {
    $content = [System.Net.WebUtility]::HtmlDecode($node.InnerText).Replace([char]0xA0, ' ')
    if ([string]::IsNullOrWhiteSpace($content)) {
        continue
    }

    $className = [string]$node.class
    $fill = [string]$node.fill
    if (-not $fill -and $className -and $fills.ContainsKey($className)) {
        $fill = $fills[$className]
    }
    if (-not $fill) {
        $fill = '__SCREENSHOT_FOREGROUND__'
    }

    $isTitle = $className -like '*-title'
    $isBold = $isTitle -or ($className -and $weights.ContainsKey($className) -and $weights[$className])
    $fontFamily = if ($isTitle) { 'Arial' } else { 'Consolas' }
    $fontSize = if ($isTitle) { 18.0 } else { 20.0 }
    $fontStyle = if ($isBold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }

    $font = New-Object System.Drawing.Font($fontFamily, $fontSize, $fontStyle, [System.Drawing.GraphicsUnit]::Pixel)
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($fill))
    $x = [float]$node.x
    $y = [float]$node.y
    $drawY = $y - $font.Size

    if ([string]$node.'text-anchor' -eq 'middle') {
        $format = New-Object System.Drawing.StringFormat
        $format.Alignment = [System.Drawing.StringAlignment]::Center
        $graphics.DrawString($content, $font, $brush, $x, $drawY, $format)
        $format.Dispose()
    } else {
        $graphics.DrawString($content, $font, $brush, $x, $drawY)
    }

    $brush.Dispose()
    $font.Dispose()
}

$bitmap.Save($PngPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
    script = script.replace("__SCREENSHOT_BACKGROUND__", SCREENSHOT_BACKGROUND_HEX)
    script = script.replace("__SCREENSHOT_FOREGROUND__", SCREENSHOT_FOREGROUND_HEX)
    with tempfile.TemporaryDirectory(dir=output_path.parent) as temp_dir:
        script_path = Path(temp_dir) / "render_svg_to_png.ps1"
        script_path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                str(svg_path),
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"SVG-to-PNG render failed: {result.returncode}")


def _find_headless_browser() -> Path | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("msedge"),
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    return None


def _svg_viewbox_dimensions(svg_path: Path) -> tuple[int, int]:
    text = svg_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', text)
    if match is None:
        return 1726, 1026
    width = max(1, round(float(match.group(1))))
    height = max(1, round(float(match.group(2))))
    return width, height


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()
