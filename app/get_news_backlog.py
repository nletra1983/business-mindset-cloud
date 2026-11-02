"""Refresh get-news backlog when older than 4 hours (skill period)."""

from __future__ import annotations

import logging
import re
import threading
import time
from datetime import datetime
from pathlib import Path

log = logging.getLogger("bot")

BACKLOG = (
    Path(__file__).resolve().parent.parent
    / "features"
    / "business-idea-from-news"
    / "FeatureArtifacts"
    / "get-news-backlog.md"
)
PERIOD_HOURS = 4
_CREATED_RE = re.compile(r"^Создан:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})")


def backlog_is_stale(now: datetime | None = None) -> bool:
    now = now or datetime.now()
    if not BACKLOG.is_file():
        return True
    first = BACKLOG.read_text(encoding="utf-8").splitlines()[:1]
    if not first:
        return True
    m = _CREATED_RE.match(first[0].strip())
    if not m:
        return True
    created = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
    return (now - created).total_seconds() > PERIOD_HOURS * 3600


def mark_refresh_needed() -> bool:
    """Return True if backlog should be rebuilt (fetch is later / operator / story 2)."""
    stale = backlog_is_stale()
    if stale:
        log.info("get-news backlog stale or missing; refresh needed (period %sh)", PERIOD_HOURS)
    return stale


def start_backlog_ticker(interval_sec: int = 600) -> None:
    def loop() -> None:
        while True:
            try:
                mark_refresh_needed()
            except Exception:
                log.exception("get-news backlog tick failed")
            time.sleep(interval_sec)

    thread = threading.Thread(target=loop, name="get-news-backlog", daemon=True)
    thread.start()
