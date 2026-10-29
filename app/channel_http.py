import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.channel_api import APP_PREFIX, dispatch
from app.db import connect
from app.entrances import SqlBook
from app.sessions import SqlSessionStore

log = logging.getLogger("bot")


def channel_port() -> int:
    raw = os.environ.get("CHANNEL_HTTP_PORT", "8080").strip()
    try:
        return int(raw)
    except ValueError:
        return 8080


def start_channel_server() -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("0.0.0.0", channel_port()), _Handler)
    thread = threading.Thread(target=server.serve_forever, name="channel-http", daemon=True)
    thread.start()
    log.info("channel entrance on /app/v1 port %s", channel_port())
    return server


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.info("channel %s", format % args)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def _handle(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        body = {}
        if raw:
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._write(400, {"error": "bad_json", "message": "тело не разобрано"})
                return
        if not self.path.startswith(APP_PREFIX):
            self._write(404, {"error": "not_found", "message": "путь не найден"})
            return
        conn = connect()
        try:
            result = dispatch(
                method,
                self.path,
                {key: value for key, value in self.headers.items()},
                body,
                book=SqlBook(conn),
                sessions=SqlSessionStore(conn),
                conn=conn,
            )
        finally:
            conn.close()
        self._write(result["status"], result["body"])

    def _write(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
