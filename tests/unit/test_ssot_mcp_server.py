from __future__ import annotations

import pytest

from ssot_mcp.server import build_server, main


def test_server_requires_repo_or_explicit_repo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: None)

    with pytest.raises(SystemExit):
        main(["--transport", "stdio"])


def test_server_rejects_repo_with_explicit_mode(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: None)

    with pytest.raises(SystemExit):
        main(["--transport", "stdio", "--repo", str(tmp_path), "--repo-mode", "explicit"])


def test_server_accepts_explicit_repo_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeServer:
        def __init__(self) -> None:
            self.transport = None

        def run(self, transport: str) -> None:
            self.transport = transport

    server = FakeServer()
    monkeypatch.setattr("ssot_mcp.server.build_server", lambda: server)

    assert main(["--transport", "stdio", "--repo-mode", "explicit"]) == 0
    assert server.transport == "stdio"


def test_server_build_registers_mcp_resources() -> None:
    assert build_server() is not None
