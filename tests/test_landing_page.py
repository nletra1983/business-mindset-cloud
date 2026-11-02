from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "web" / "index.html"
CSS = ROOT / "web" / "styles.css"

REQUIRED_IDS = (
    "hero",
    "demo",
    "how",
    "not-chatgpt",
    "outcomes",
    "levels",
    "example",
    "audience",
    "author",
    "faq",
    "final-cta",
)


def test_index_and_css_exist():
    assert INDEX.is_file()
    assert CSS.is_file()


def test_all_required_section_ids_present():
    html = INDEX.read_text(encoding="utf-8")
    for section_id in REQUIRED_IDS:
        assert f'id="{section_id}"' in html, section_id


def test_hero_has_single_primary_cta_to_demo():
    html = INDEX.read_text(encoding="utf-8")
    hero = html.split('id="hero"', 1)[1].split('id="demo"', 1)[0]
    assert 'href="#demo"' in hero
    assert hero.count('class="cta"') == 1
    assert "без регистрации" in hero.lower()


def test_no_fake_testimonials_or_partner_logos():
    html = INDEX.read_text(encoding="utf-8").lower()
    banned = ("отзыв клиента", "★★★★★", "5 из 5", "партнёр:", "logo-partner", "testimonial")
    for token in banned:
        assert token not in html, token
    example = html.split('id="example"', 1)[1].split('id="audience"', 1)[0]
    assert "без чужих отзывов" in example or "без фейковых" in example or "честный" in example


def test_levels_mention_default_amount():
    html = INDEX.read_text(encoding="utf-8")
    levels = html.split('id="levels"', 1)[1].split('id="example"', 1)[0]
    assert "100" in levels
    assert "₽" in levels or "руб" in levels.lower()


def test_faq_has_educational_disclaimer():
    html = INDEX.read_text(encoding="utf-8").lower()
    faq = html.split('id="faq"', 1)[1].split('id="final-cta"', 1)[0]
    assert "образовательн" in faq


def test_mobile_first_css_present():
    css = CSS.read_text(encoding="utf-8")
    assert "max-width" in css
    assert "@media" in css
    assert "375" in css or "400px" in css or "phone" in css.lower()


def test_lang_is_russian():
    html = INDEX.read_text(encoding="utf-8")
    assert 'lang="ru"' in html
