from __future__ import annotations

from .app import SsotTuiApp


def main() -> int:
    app = SsotTuiApp()
    try:
        app.run()
    except KeyboardInterrupt:
        return 130
    return app.return_code or 0


if __name__ == "__main__":
    raise SystemExit(main())
