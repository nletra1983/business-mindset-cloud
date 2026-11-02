from pathlib import Path

from app import web_landing

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "web" / "index.html"
METRIKA_JS = ROOT / "web" / "metrika.js"
DEMO_JS = ROOT / "web" / "demo.js"

EVENTS = (
    "cta_hero",
    "step_1",
    "step_2",
    "step_3",
    "gate_shown",
    "email_submitted",
    "step_4",
    "step_5",
    "step_6",
    "paywall_shown",
    "pay_click",
    "day2_return",
)


def test_metrika_js_lists_contract_events():
    text = METRIKA_JS.read_text(encoding="utf-8")
    for name in EVENTS:
        assert name in text


def test_demo_wires_core_tracks():
    text = DEMO_JS.read_text(encoding="utf-8")
    for name in (
        "cta_hero",
        "step_1",
        "gate_shown",
        "email_submitted",
        "paywall_shown",
        "pay_click",
    ):
        assert name in text


def test_index_includes_metrika_helper():
    html = INDEX.read_text(encoding="utf-8")
    assert "/web/metrika.js" in html


def test_inject_without_counter_no_tag_js(monkeypatch):
    monkeypatch.delenv("YANDEX_METRIKA_COUNTER_ID", raising=False)
    html = "<html><head></head><body></body></html>"
    out = web_landing.inject_metrika(html)
    assert "mc.yandex.ru/metrika/tag.js" not in out
    assert "YANDEX_METRIKA_COUNTER_ID" in out


def test_inject_with_counter_embeds_snippet(monkeypatch):
    monkeypatch.setenv("YANDEX_METRIKA_COUNTER_ID", "12345678")
    html = "<html><head></head><body></body></html>"
    out = web_landing.inject_metrika(html)
    assert "mc.yandex.ru/metrika/tag.js" in out
    assert "12345678" in out


def test_window_limit_module_independent_of_metrika():
    from app.web_landing import WINDOWS_LIMIT

    assert WINDOWS_LIMIT == 3
