from __future__ import annotations

import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .events import format_sse_event
from .sqlite_store import ControlStore


class WorkerEventStreamHandler(BaseHTTPRequestHandler):
    store: ControlStore
    poll_interval_seconds = 1.0

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/events/stream":
            self.send_response(404)
            self.end_headers()
            return
        query = parse_qs(parsed.query)
        worker_id = query.get("worker_id", [None])[0]
        campaign_id = query.get("campaign_id", [None])[0]
        last_seen = int(query.get("last_seen_event_id", ["0"])[0] or 0)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        cursor = last_seen
        try:
            while True:
                events = self.store.get_events(worker_id=worker_id, campaign_id=campaign_id, after_event_id=cursor, limit=100)
                for event in events:
                    cursor = max(cursor, int(event["event_id"]))
                    self.wfile.write(format_sse_event(event).encode("utf-8"))
                    self.wfile.flush()
                time.sleep(self.poll_interval_seconds)
        except (BrokenPipeError, ConnectionResetError):
            return


def build_sse_server(repo_root: str | Path, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    store = ControlStore(repo_root)
    store.initialize()

    class Handler(WorkerEventStreamHandler):
        pass

    Handler.store = store
    return ThreadingHTTPServer((host, port), Handler)
