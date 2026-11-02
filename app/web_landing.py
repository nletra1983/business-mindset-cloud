"""Guest landing channel: static shell, guest cookie session, /web/v1 stubs."""

from __future__ import annotations

import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

WEB_ROOT = Path(__file__).resolve().parent.parent / "web"
GUEST_COOKIE = "gbi_guest"
WINDOWS_LIMIT = 3
TTL_HOURS = 24
MSK = ZoneInfo("Europe/Moscow")


def moscow_today() -> date:
    return datetime.now(MSK).date()


def parse_cookie_guest_id(header: str | None) -> str | None:
    if not header:
        return None
    jar = SimpleCookie()
    try:
        jar.load(header)
    except Exception:
        return None
    morsel = jar.get(GUEST_COOKIE)
    if not morsel:
        return None
    raw = morsel.value.strip()
    try:
        uuid.UUID(raw)
    except ValueError:
        return None
    return raw


def purge_expired_transcripts(conn) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=TTL_HOURS)
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE guest_window
            SET transcript = '[]'::jsonb
            WHERE first_reply_at IS NOT NULL
              AND first_reply_at < %s
              AND transcript <> '[]'::jsonb
            """,
            (cutoff,),
        )


def ensure_guest_session(conn, guest_id: str | None) -> dict[str, Any]:
    purge_expired_transcripts(conn)
    today = moscow_today()
    with conn.cursor() as cur:
        if guest_id:
            cur.execute(
                "SELECT id, windows_day, windows_used_today, current_window_id, person_id "
                "FROM guest_session WHERE id = %s",
                (guest_id,),
            )
            row = cur.fetchone()
            if row:
                sid, wday, used, cur_win, person_id = row
                if wday != today:
                    cur.execute(
                        "UPDATE guest_session SET windows_day = %s, windows_used_today = 0, "
                        "updated_at = now() WHERE id = %s",
                        (today, sid),
                    )
                    used = 0
                    wday = today
                return {
                    "id": str(sid),
                    "windows_day": wday,
                    "windows_used_today": used,
                    "windows_limit": WINDOWS_LIMIT,
                    "current_window_id": str(cur_win) if cur_win else None,
                    "person_id": str(person_id) if person_id else None,
                    "new_cookie": False,
                }
        new_id = uuid.uuid4()
        cur.execute(
            """
            INSERT INTO guest_session (id, windows_day, windows_used_today)
            VALUES (%s, %s, 0)
            """,
            (str(new_id), today),
        )
        return {
            "id": str(new_id),
            "windows_day": today,
            "windows_used_today": 0,
            "windows_limit": WINDOWS_LIMIT,
            "current_window_id": None,
            "person_id": None,
            "new_cookie": True,
        }


def set_guest_cookie_header(guest_id: str, secure: bool = False) -> str:
    parts = [
        f"{GUEST_COOKIE}={guest_id}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        "Max-Age=2592000",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def static_path(url_path: str) -> Path | None:
    parsed = urlparse(url_path)
    path = parsed.path or "/"
    if path in ("/", "/index.html"):
        return WEB_ROOT / "index.html"
    if path.startswith("/web/"):
        rel = path[len("/web/") :]
        if ".." in rel or rel.startswith("/"):
            return None
        candidate = (WEB_ROOT / rel).resolve()
        if not str(candidate).startswith(str(WEB_ROOT.resolve())):
            return None
        if candidate.is_file():
            return candidate
    return None


def content_type_for(path: Path) -> str:
    if path.suffix == ".css":
        return "text/css; charset=utf-8"
    if path.suffix == ".js":
        return "application/javascript; charset=utf-8"
    if path.suffix == ".html":
        return "text/html; charset=utf-8"
    return "application/octet-stream"


def inject_metrika(html: str) -> str:
    counter = os.environ.get("YANDEX_METRIKA_COUNTER_ID", "").strip()
    captcha = os.environ.get("SMARTCAPTCHA_CLIENT_KEY", "").strip()
    parts = [
        f'<script>window.YANDEX_METRIKA_COUNTER_ID={json.dumps(counter)};</script>',
        f'<script>window.SMARTCAPTCHA_CLIENT_KEY={json.dumps(captcha)};</script>',
    ]
    if counter:
        # Official tag shape; id from non-secret env. Product works if ym never loads.
        parts.append(
            f'<script type="text/javascript">'
            f'(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};'
            f'm[i].l=1*new Date();'
            f'for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}'
            f"k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)"
            f'}})(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");'
            f'ym({json.dumps(counter)}, "init", {{ clickmap:true, trackLinks:true, accurateTrackBounce:true }});'
            f"</script>"
        )
    snippet = "\n".join(parts) + "\n"
    if "</head>" in html:
        return html.replace("</head>", snippet + "</head>", 1)
    return snippet + html


def guest_session_json(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "guest_id": session["id"],
        "windows_used_today": session["windows_used_today"],
        "windows_limit": session["windows_limit"],
        "current_window_id": session.get("current_window_id"),
    }
