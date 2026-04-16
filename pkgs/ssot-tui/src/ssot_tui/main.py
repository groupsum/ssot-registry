from __future__ import annotations

from .app import SsotTuiApp


def main() -> int:
    app = SsotTuiApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
