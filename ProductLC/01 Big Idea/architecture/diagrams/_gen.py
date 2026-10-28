# -*- coding: utf-8 -*-
from pathlib import Path

OUT = Path(__file__).resolve().parent

EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    "endArrow=blockThin;endFill=1;strokeColor=#4A4A4A;fontColor=#222222;"
    "fontFamily=Arial;fontSize=11;labelBackgroundColor=#FFFFFF;endSize=8;"
)
PERSON = (
    "shape=mxgraph.c4.person2;html=1;whiteSpace=wrap;fillColor=#08427B;"
    "strokeColor=#072F57;fontColor=#ffffff;align=center;verticalAlign=bottom;"
    "fontFamily=Arial;fontSize=13;spacingBottom=2;resizable=1;"
)
SYSTEM = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#1168BD;strokeColor=#0E5091;"
    "fontColor=#ffffff;arcSize=8;fontFamily=Arial;fontSize=14;verticalAlign=middle;"
    "align=center;spacing=8;"
)
EXTERNAL = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#999999;strokeColor=#6B6B6B;"
    "fontColor=#ffffff;arcSize=8;fontFamily=Arial;fontSize=13;verticalAlign=middle;"
    "align=center;spacing=6;"
)
MODULE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F4F8FC;strokeColor=#0E5091;"
    "fontColor=#1A1A1A;arcSize=8;fontFamily=Arial;fontSize=12;verticalAlign=middle;"
    "align=center;spacing=6;"
)
STORE = (
    "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=14;"
    "fillColor=#438DD5;strokeColor=#2E6295;fontColor=#ffffff;fontFamily=Arial;"
    "fontSize=13;spacing=4;"
)
TRUST = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#B00020;dashed=1;"
    "dashPattern=8 4;strokeWidth=2;verticalAlign=top;align=left;spacingLeft=10;"
    "spacingTop=6;fontColor=#B00020;fontFamily=Arial;fontSize=13;fontStyle=1;"
)
BOUNDARY = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;dashed=1;"
    "dashPattern=2 3;strokeWidth=1;verticalAlign=top;align=left;spacingLeft=10;"
    "spacingTop=6;fontColor=#333333;fontFamily=Arial;fontSize=13;fontStyle=1;"
)
TITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=20;fontColor=#0E5091;fontStyle=1;"
)
SUB = (
    "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
    "fontFamily=Arial;fontSize=13;fontColor=#333333;"
)
NOTE = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#D0D0D0;"
    "fontColor=#333333;fontFamily=Arial;fontSize=12;align=left;verticalAlign=top;"
    "spacingLeft=10;spacingTop=6;"
)
APP = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#1168BD;strokeColor=#0E5091;"
    "fontColor=#ffffff;arcSize=3;verticalAlign=top;align=left;spacingLeft=12;"
    "spacingTop=8;fontFamily=Arial;fontSize=14;fontStyle=1;"
)


def xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def block(name: str, kind: str, line: str) -> str:
    html = (
        f"<b>{name}</b><br>"
        f"<font style=\"font-size: 11px\">{kind}</font><br>{line}"
    )
    return xml(html)


def cell(cid, value, style, x, y, w, h):
    return (
        f'<mxCell id="{cid}" value="{value}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        f"</mxCell>"
    )


def edge(cid, label, src, tgt, extra=""):
    return (
        f'<mxCell id="{cid}" value="{xml(label)}" style="{EDGE}{extra}" edge="1" parent="1" '
        f'source="{src}" target="{tgt}">'
        f'<mxGeometry relative="1" as="geometry"/></mxCell>'
    )


def legend():
    html = """<b>Легенда</b><br>
<span style="background:#08427B;color:#ffffff;">&nbsp;человек&nbsp;</span>&nbsp;
<span style="background:#1168BD;color:#ffffff;">&nbsp;наша система / контейнер&nbsp;</span>&nbsp;
<span style="background:#F4F8FC;color:#1A1A1A;border:1px solid #0E5091;">&nbsp;модуль&nbsp;</span>&nbsp;
<span style="background:#438DD5;color:#ffffff;">&nbsp;хранилище&nbsp;</span>&nbsp;
<span style="background:#999999;color:#ffffff;">&nbsp;внешняя система&nbsp;</span><br>
<span style="color:#B00020;">— — рамка доверия</span>&nbsp;&nbsp;
<span style="color:#666666;">- - граница системы</span>&nbsp;&nbsp;
сплошная стрелка — синхронный вызов&nbsp;&nbsp;
пунктирная стрелка — асинхронно, на этих листах таких связей нет<br>
Пометка «позже» — шов архитектуры, в текущий MVP не входит."""
    return cell("legend", xml(html), NOTE, 24, 1008, 1606, 140)


def page(name, diagram_id, body):
    cells = "\n        ".join(body)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" type="device">
  <diagram id="{diagram_id}" name="{xml(name)}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1654" pageHeight="1169" math="0" shadow="0" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def context():
    body = [
        cell("title", xml("Business Mindset — контекст системы"), TITLE, 24, 16, 1400, 32),
        cell(
            "sub",
            xml("C4, уровень 1. Одно ядро, два входа в MVP: Telegram и мобильное приложение. Веб, Макс и оплата — позже."),
            SUB,
            24,
            48,
            1550,
            22,
        ),
        cell("trust", xml("Наш контур"), TRUST, 430, 110, 480, 840),
        cell(
            "sys",
            block(
                "Business Mindset",
                "[Software System]",
                "Ведёт разбор новости и хранит аккаунт",
            ),
            SYSTEM,
            500,
            380,
            340,
            250,
        ),
        cell("p_user", block("Предприниматель", "[Person]", "Проходит разбор и входит в аккаунт"), PERSON, 40, 170, 200, 190),
        cell("p_author", block("Автор скиллов", "[Person]", "Публикует скилл и правила оценки"), PERSON, 40, 430, 200, 190),
        cell("p_coach", block("Наставник группы", "[Person]", "Позже. Читает сводку группы"), PERSON, 40, 700, 200, 190),
        cell(
            "tg",
            block("Telegram", "[Software System]", "Первый канал. Вход и разбор"),
            EXTERNAL,
            1060,
            140,
            540,
            90,
        ),
        cell(
            "models",
            block("Провайдеры моделей", "[Software System]", "Отвечают выбранной бесплатной моделью"),
            EXTERNAL,
            1060,
            270,
            540,
            100,
        ),
        cell(
            "news",
            block("Новостные сайты", "[Software System]", "Позже. Страница по ссылке и рубрики скилла"),
            EXTERNAL,
            1060,
            410,
            540,
            100,
        ),
        cell(
            "max",
            block("Макс", "[Software System]", "Позже. Тот же ход и тот же аккаунт"),
            EXTERNAL,
            1060,
            550,
            540,
            90,
        ),
        cell(
            "pay",
            block("Оплата", "[Software System]", "Позже. Открывает платные модели"),
            EXTERNAL,
            1060,
            680,
            540,
            90,
        ),
        edge(
            "e1",
            "входит и проходит разбор",
            "p_user",
            "sys",
            "exitX=1;exitY=0.35;entryX=0;entryY=0.35;",
        ),
        edge(
            "e2",
            "ведёт диалог и отдаёт сводку разбора",
            "sys",
            "p_user",
            "exitX=0;exitY=0.7;entryX=1;entryY=0.7;",
        ),
        edge("e3", "публикует скилл и правила оценки", "p_author", "sys"),
        edge("e4", "читает сводку группы", "p_coach", "sys"),
        edge("e5", "ведёт тренировку ботом", "sys", "tg"),
        edge("e6", "вызывает выбранную модель", "sys", "models"),
        edge("e7", "позже забирает страницу", "sys", "news"),
        edge("e8", "позже ведёт тот же ход", "sys", "max"),
        edge("e9", "позже проверяет право на платную модель", "sys", "pay"),
        cell(
            "stamp",
            xml("<b>Штамп.</b> Business Mindset · контекст системы, C4 L1 · черновик · 2026-10-28 · горизонт: MVP и швы роста"),
            SUB,
            24,
            972,
            1550,
            22,
        ),
        legend(),
    ]
    return page("01 Контекст", "c4-context", body)


def containers():
    body = [
        cell("title", xml("Business Mindset — контейнеры"), TITLE, 24, 12, 1200, 30),
        cell(
            "sub",
            xml("C4, уровень 2. Один процесс. Аккаунт и разбор новости — модули, не отдельные сервисы."),
            SUB,
            24,
            42,
            1550,
            20,
        ),
        cell("boundary", xml("Business Mindset"), BOUNDARY, 250, 68, 900, 888),
        cell("trust", xml("Серверный контур"), TRUST, 450, 84, 680, 852),
        cell("app", xml("Приложение  [Container: сервис]"), APP, 470, 112, 640, 470),
        cell(
            "channels",
            block("Каналы", "[Модуль]", "Telegram сейчас. Сюда же приложение. Макс позже"),
            MODULE,
            486,
            150,
            608,
            56,
        ),
        cell(
            "account",
            block("Аккаунт", "[Модуль]", "Внутренний id, телефон, Telegram user id, слияние кодом"),
            MODULE,
            486,
            214,
            608,
            56,
        ),
        cell(
            "workout",
            block("Ход упражнения", "[Модуль]", "Одна формулировка человека. Шаг, диалог, сводка"),
            MODULE,
            486,
            278,
            608,
            56,
        ),
        cell(
            "skills",
            block("Скилл новости", "[Модуль]", "Вопросы и правила оценки. Версия хранится на ходе"),
            MODULE,
            486,
            342,
            608,
            56,
        ),
        cell(
            "gateway",
            block("Шлюз моделей", "[Модуль]", "Только модели, которые открыл аккаунт. В MVP бесплатные"),
            MODULE,
            486,
            406,
            608,
            56,
        ),
        cell(
            "profile",
            block("Профиль навыка", "[Модуль]", "Скрытый след. Человек видит только личные данные"),
            MODULE,
            486,
            470,
            608,
            56,
        ),
        cell(
            "db",
            block("База", "[Container: хранилище]", "Аккаунты, ходы, диалоги, сводки, скрытый след"),
            STORE,
            486,
            620,
            290,
            130,
        ),
        cell(
            "secrets",
            block("Секреты", "[Container: хранилище]", "Ключи сервиса к бесплатным моделям"),
            STORE,
            800,
            620,
            280,
            130,
        ),
        cell(
            "note",
            xml("Ссылка на страницу и подборка сайтов — позже, отдельным модулем загрузки. Свой ключ человека к платной модели — тоже позже."),
            NOTE,
            486,
            770,
            594,
            56,
        ),
        cell(
            "mobile",
            block("Мобильное приложение", "[Container: клиент]", "Вход по телефону. Ходит только в каналы"),
            SYSTEM,
            266,
            180,
            170,
            130,
        ),
        cell(
            "web",
            block("Веб", "[Container: клиент]", "Позже. Тот же аккаунт и те же ходы"),
            SYSTEM,
            266,
            340,
            170,
            110,
        ),
        cell(
            "tg",
            block("Telegram", "[Software System]", "Первый канал"),
            EXTERNAL,
            16,
            180,
            220,
            100,
        ),
        cell(
            "max",
            block("Макс", "[Software System]", "Позже. Тот же ход"),
            EXTERNAL,
            16,
            310,
            220,
            90,
        ),
        cell(
            "pay",
            block("Оплата", "[Software System]", "Позже. Открывает платные модели"),
            EXTERNAL,
            16,
            640,
            220,
            110,
        ),
        cell(
            "models",
            block("Провайдеры моделей", "[Software System]", "Вызов с сервера, не с телефона"),
            EXTERNAL,
            1180,
            390,
            440,
            90,
        ),
        cell(
            "sites",
            block("Новостные сайты", "[Software System]", "Позже. Страница по ссылке"),
            EXTERNAL,
            1180,
            520,
            440,
            90,
        ),
        edge("e_m", "реплика человека", "mobile", "channels"),
        edge("e_w", "реплика человека", "web", "channels"),
        edge("e_tg", "реплика и ответ бота", "tg", "channels"),
        edge("e_max", "реплика и ответ бота", "max", "channels"),
        edge("e_ca", "кто вошёл", "channels", "account"),
        edge("e_aw", "чей это ход", "account", "workout"),
        edge("e_ws", "читает версию скилла", "workout", "skills"),
        edge("e_wg", "ход и оценка той же моделью", "workout", "gateway"),
        edge("e_wp", "пишет скрытый след", "workout", "profile"),
        edge("e_gm", "вызывает разрешённую модель", "gateway", "models"),
        edge("e_gs", "берёт ключ сервиса", "gateway", "secrets"),
        edge("e_gp", "позже проверяет платное право", "account", "pay"),
        edge("e_db", "хранит аккаунты, ходы и след", "app", "db"),
        cell(
            "stamp",
            xml("<b>Штамп.</b> Business Mindset · контейнеры, C4 L2 · черновик · 2026-10-28 · горизонт: MVP и швы роста"),
            SUB,
            24,
            972,
            1550,
            22,
        ),
        legend(),
    ]
    return page("02 Контейнеры", "c4-containers", body)


def deployment():
    body = [
        cell("title", xml("Business Mindset — размещение"), TITLE, 24, 16, 1200, 32),
        cell(
            "sub",
            xml("Данные в российском регионе. Телефон не вызывает провайдера модели. Исходящий шлюз — только для модели, до которой регион не достучится."),
            SUB,
            24,
            48,
            1580,
            22,
        ),
        cell(
            "rf",
            xml("Российский регион · одна зона · здесь лежат данные"),
            TRUST,
            300,
            120,
            700,
            640,
        ),
        cell(
            "egress",
            xml("Исходящий контур · позже · диалоги не хранятся"),
            TRUST,
            1080,
            120,
            530,
            250,
        ),
        cell(
            "user",
            block("Предприниматель", "[Person]", "Телефон с VPN и без него"),
            PERSON,
            40,
            280,
            200,
            200,
        ),
        cell(
            "app",
            block("Приложение", "[Container: сервис]", "Единственный вход для телефона"),
            SYSTEM,
            360,
            200,
            300,
            150,
        ),
        cell(
            "db",
            block("База", "[Container: хранилище]", "Аккаунты, ходы, след"),
            STORE,
            360,
            420,
            250,
            140,
        ),
        cell(
            "secrets",
            block("Секреты", "[Container: хранилище]", "Ключи сервиса"),
            STORE,
            660,
            420,
            250,
            140,
        ),
        cell(
            "relay",
            block("Исходящий шлюз", "[Container: шлюз]", "Позже. Передаёт запрос и не пишет диалог"),
            SYSTEM,
            1160,
            180,
            360,
            130,
        ),
        cell(
            "rfm",
            block("Провайдеры моделей из РФ", "[Software System]", "Бесплатные модели MVP. Вызов из региона"),
            EXTERNAL,
            340,
            800,
            620,
            110,
        ),
        cell(
            "foreign",
            block("Зарубежные провайдеры моделей", "[Software System]", "Позже. Только через исходящий шлюз"),
            EXTERNAL,
            1160,
            430,
            400,
            110,
        ),
        cell(
            "tg",
            block("Telegram", "[Software System]", "Бот. Телефон к API Telegram не ходит за моделью"),
            EXTERNAL,
            1160,
            600,
            400,
            110,
        ),
        cell(
            "note",
            xml("Непроизводственная среда повторяет этот контур и меньше его. Если API Telegram из региона не откроется, тонкий исходящий путь получает только модуль каналов."),
            NOTE,
            360,
            640,
            560,
            70,
        ),
        edge("e_in", "HTTPS, с VPN и без него", "user", "app"),
        edge("e_db", "аккаунт, ход и след", "app", "db"),
        edge("e_sec", "ключ в момент вызова", "app", "secrets"),
        edge("e_rf", "модель, досягаемая из региона", "app", "rfm"),
        edge("e_rel", "позже: модель вне досягаемости региона", "app", "relay"),
        edge("e_for", "запрос без записи диалога", "relay", "foreign"),
        edge("e_tg", "бот", "app", "tg"),
        cell(
            "stamp",
            xml("<b>Штамп.</b> Business Mindset · размещение · черновик · 2026-10-28 · горизонт: MVP и швы роста"),
            SUB,
            24,
            972,
            1550,
            22,
        ),
        legend(),
    ]
    return page("03 Размещение", "deployment", body)


def main():
    (OUT / "01-system-context.drawio").write_text(context(), encoding="utf-8")
    (OUT / "02-containers.drawio").write_text(containers(), encoding="utf-8")
    (OUT / "03-deployment.drawio").write_text(deployment(), encoding="utf-8")


if __name__ == "__main__":
    main()
