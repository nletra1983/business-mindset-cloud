import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app.channel_api import APP_PREFIX, dispatch
from app.db import connect
from app.entrances import SqlBook
from app.sessions import SqlSessionStore
from app import web_email_gate, web_fake_pay, web_guest_smoke, web_landing

log = logging.getLogger("bot")

WEB_API_PREFIX = "/web/v1"


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
    log.info("channel entrance on /app/v1 and landing on / + /web/v1 port %s", channel_port())
    return server


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.info("channel %s", format % args)

    def do_GET(self):
        if self._try_landing_get():
            return
        self._handle_app("GET")

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith(WEB_API_PREFIX):
            self._handle_web_api("POST")
            return
        self._handle_app("POST")

    def _try_landing_get(self) -> bool:
        path = urlparse(self.path).path
        if path.startswith(WEB_API_PREFIX):
            self._handle_web_api("GET")
            return True
        static = web_landing.static_path(self.path)
        if static is None:
            if path.startswith(APP_PREFIX):
                return False
            self._write_json(404, {"error": "not_found", "message": "путь не найден"})
            return True
        raw = static.read_bytes()
        if static.suffix == ".html":
            text = web_landing.inject_metrika(raw.decode("utf-8"))
            raw = text.encode("utf-8")
        guest_header = None
        if static.name == "index.html":
            conn = connect()
            try:
                cookie_id = web_landing.parse_cookie_guest_id(self.headers.get("Cookie"))
                session = web_landing.ensure_guest_session(conn, cookie_id)
                conn.commit()
                if session["new_cookie"] or cookie_id != session["id"]:
                    secure = self.headers.get("X-Forwarded-Proto", "").lower() == "https"
                    guest_header = web_landing.set_guest_cookie_header(session["id"], secure=secure)
            finally:
                conn.close()
        self.send_response(200)
        self.send_header("Content-Type", web_landing.content_type_for(static))
        self.send_header("Content-Length", str(len(raw)))
        if guest_header:
            self.send_header("Set-Cookie", guest_header)
        self.end_headers()
        self.wfile.write(raw)
        return True

    def _handle_web_api(self, method: str) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if raw:
            try:
                json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._write_json(400, {"error": "bad_json", "message": "тело не разобрано"})
                return
        conn = connect()
        try:
            cookie_id = web_landing.parse_cookie_guest_id(self.headers.get("Cookie"))
            session = web_landing.ensure_guest_session(conn, cookie_id)
            set_cookie = session["new_cookie"] or cookie_id != session["id"]
            payload = {}
            if raw:
                payload = json.loads(raw.decode("utf-8"))
            route = path.rstrip("/")
            if method == "GET" and route == f"{WEB_API_PREFIX}/guest/session":
                body = web_landing.guest_session_json(session)
                status = 200
            elif method == "POST" and route == f"{WEB_API_PREFIX}/guest/ping":
                body = {"ok": True, **web_landing.guest_session_json(session)}
                status = 200
            elif method == "POST" and route == f"{WEB_API_PREFIX}/guest/window/start":
                status, body = web_guest_smoke.start_window(
                    conn,
                    session,
                    fact=payload.get("fact"),
                    use_news=bool(payload.get("use_news", True)),
                )
            elif method == "POST" and route == f"{WEB_API_PREFIX}/guest/window/message":
                status, body = web_guest_smoke.post_message(
                    conn,
                    session,
                    text=str(payload.get("text") or ""),
                    captcha_token=payload.get("captcha_token") or payload.get("smart-token"),
                    ip=self.client_address[0] if self.client_address else None,
                )
            elif method == "POST" and route == f"{WEB_API_PREFIX}/guest/window/clear":
                status, body = web_guest_smoke.clear_window(conn, session)
            elif method == "POST" and route == f"{WEB_API_PREFIX}/gate/email":
                status, body = web_email_gate.submit_email(
                    conn, session, str(payload.get("email") or "")
                )
            elif method == "POST" and route == f"{WEB_API_PREFIX}/gate/resume":
                status, body = web_email_gate.resume_email(
                    conn, session, str(payload.get("email") or "")
                )
            elif method == "POST" and route == f"{WEB_API_PREFIX}/gate/message":
                status, body = web_email_gate.post_continue_message(
                    conn, session, text=str(payload.get("text") or "")
                )
            elif method == "GET" and route == f"{WEB_API_PREFIX}/paywall":
                status, body = web_fake_pay.paywall_state(conn, session)
            elif method == "POST" and route == f"{WEB_API_PREFIX}/paywall/click":
                status, body = web_fake_pay.record_click(
                    conn, session, payload.get("amount")
                )
            else:
                body = {"error": "not_found", "message": "путь не найден"}
                status = 404
                set_cookie = False
            if status < 400:
                conn.commit()
            else:
                conn.rollback()
        finally:
            conn.close()
        extra = {}
        if set_cookie:
            secure = self.headers.get("X-Forwarded-Proto", "").lower() == "https"
            extra["Set-Cookie"] = web_landing.set_guest_cookie_header(session["id"], secure=secure)
        self._write_json(status, body, extra_headers=extra)

    def _handle_app(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        body = {}
        if raw:
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._write_json(400, {"error": "bad_json", "message": "тело не разобрано"})
                return
        if not self.path.startswith(APP_PREFIX):
            self._write_json(404, {"error": "not_found", "message": "путь не найден"})
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
            if result["status"] < 400:
                conn.commit()
            else:
                conn.rollback()
        finally:
            conn.close()
        self._write_json(result["status"], result["body"])

    def _write_json(self, status: int, body: dict, extra_headers: dict | None = None) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)
