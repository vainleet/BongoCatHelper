"""
core/seasonal.py
Сезонные скины и ивенты — меняются автоматически по дате.
Никакого интернета — только datetime.
"""

from datetime import date, datetime


# ── Описание сезонов ──────────────────────────────────────
# Каждый сезон: (month, day_from, day_to, name, skin_override, banner)
# skin_override — полная замена цветов скина (как в progress.py CAT_SKINS)
# banner — текст баннера в интерфейсе

SEASONAL_EVENTS = [
    # Новый год (25 дек — 10 янв)
    {
        "name":    "Новый год 🎆",
        "months":  [(12, 25, 31), (1, 1, 10)],
        "banner":  "🎆 С Новым годом! Праздничный кот активирован!",
        "skin": {
            "name":       "Дед Мороз 🎅",
            "hat":        "🎅",
            "body":       "#f5f0ff",
            "body_shade": "#e8e0f8",
            "inner_ear":  "#ff9999",
            "tail":       "#c8b8e0",
            "tail_tip":   "#b0a0d0",
            "blush":      "#ff8888",
            "outline":    "#c0a0e0",
            "paw":        "#ede8ff",
            "eye_dark":   "#1a0030",
            "nose":       "#ff4444",
            "mouth":      "#ff4444",
            "whisker":    "#8080a0",
            "thought":    "#ffaaaa",
            "eye_shine":  "#ffffff",
        },
        "quests_bonus": [
            {"id": "ny_wish",  "title": "Загадай желание 🎆",  "desc": "Напиши котику новогоднее желание", "target": 1, "type": "messages", "xp": 80},
            {"id": "ny_cheer", "title": "Поздравь кота 🎉",    "desc": "Скажи коту «С Новым годом»",       "target": 1, "type": "messages", "xp": 50},
        ],
    },

    # Рождество (24–26 дек)
    {
        "name":   "Рождество 🎄",
        "months": [(12, 24, 26)],
        "banner": "🎄 Рождественский кот! Хо-хо-хо!",
        "skin": {
            "name":       "Санта 🎄",
            "hat":        "🎄",
            "body":       "#fff0f0",
            "body_shade": "#ffd8d8",
            "inner_ear":  "#ff6666",
            "tail":       "#dd8888",
            "tail_tip":   "#cc6666",
            "blush":      "#ff5555",
            "outline":    "#cc4444",
            "paw":        "#ffeeee",
            "eye_dark":   "#330000",
            "nose":       "#ff2222",
            "mouth":      "#ff2222",
            "whisker":    "#aa8888",
            "thought":    "#ff8888",
            "eye_shine":  "#ffffff",
        },
        "quests_bonus": [],
    },

    # Хэллоуин (25 окт — 1 ноя)
    {
        "name":   "Хэллоуин 🎃",
        "months": [(10, 25, 31), (11, 1, 1)],
        "banner": "🎃 Страшный кот активирован! Угощение или проделка?",
        "skin": {
            "name":       "Вампир 🧛",
            "hat":        "🧛",
            "body":       "#1a0a2e",
            "body_shade": "#0e0518",
            "inner_ear":  "#880022",
            "tail":       "#330022",
            "tail_tip":   "#220011",
            "blush":      "#660022",
            "outline":    "#550033",
            "paw":        "#280a40",
            "eye_dark":   "#ff0033",
            "nose":       "#880022",
            "mouth":      "#880022",
            "whisker":    "#6600aa",
            "thought":    "#cc0044",
            "eye_shine":  "#ff88cc",
        },
        "quests_bonus": [
            {"id": "spooky_talk", "title": "Страшная история 👻", "desc": "Расскажи коту страшилку", "target": 1, "type": "messages", "xp": 60},
        ],
    },

    # День Святого Валентина (12–14 фев)
    {
        "name":   "День влюблённых 💝",
        "months": [(2, 12, 14)],
        "banner": "💝 Кот влюблён! С Днём всех влюблённых!",
        "skin": {
            "name":       "Амур 💘",
            "hat":        "💘",
            "body":       "#fff0f5",
            "body_shade": "#ffd8e8",
            "inner_ear":  "#ff88bb",
            "tail":       "#ff99cc",
            "tail_tip":   "#ff77aa",
            "blush":      "#ff5599",
            "outline":    "#ff3388",
            "paw":        "#ffeeee",
            "eye_dark":   "#330011",
            "nose":       "#ff3377",
            "mouth":      "#ff3377",
            "whisker":    "#cc8899",
            "thought":    "#ff88bb",
            "eye_shine":  "#ffffff",
        },
        "quests_bonus": [
            {"id": "love_note", "title": "Признание 💌", "desc": "Напиши коту что-то доброе", "target": 1, "type": "messages", "xp": 70},
        ],
    },

    # 8 марта (7–8 марта)
    {
        "name":   "8 марта 🌷",
        "months": [(3, 7, 8)],
        "banner": "🌷 Весенний кот! С праздником весны!",
        "skin": {
            "name":       "Весна 🌷",
            "hat":        "🌷",
            "body":       "#fff5ee",
            "body_shade": "#ffe8d8",
            "inner_ear":  "#ffbbaa",
            "tail":       "#ffcc88",
            "tail_tip":   "#ffbb66",
            "blush":      "#ffaa77",
            "outline":    "#ee9955",
            "paw":        "#fff0e8",
            "eye_dark":   "#331100",
            "nose":       "#ff7744",
            "mouth":      "#ff7744",
            "whisker":    "#aa8866",
            "thought":    "#ffcc88",
            "eye_shine":  "#ffffff",
        },
        "quests_bonus": [],
    },

    # День победы (8–9 мая)
    {
        "name":   "9 мая 🎖",
        "months": [(5, 8, 9)],
        "banner": "🎖 День победы. Помним и гордимся.",
        "skin":   None,   # оставляем текущий скин
        "quests_bonus": [],
    },

    # Лето (июнь–август)
    {
        "name":   "Лето ☀️",
        "months": [(6, 1, 30), (7, 1, 31), (8, 1, 31)],
        "banner": "☀️ Летний кот! Отдыхай и наслаждайся!",
        "skin": {
            "name":       "Пляжник ☀️",
            "hat":        "☀️",
            "body":       "#fff8e0",
            "body_shade": "#ffe8a0",
            "inner_ear":  "#ffcc66",
            "tail":       "#ffbb44",
            "tail_tip":   "#ff9922",
            "blush":      "#ffaa33",
            "outline":    "#dd8811",
            "paw":        "#fff5cc",
            "eye_dark":   "#331100",
            "nose":       "#ff8800",
            "mouth":      "#ff8800",
            "whisker":    "#aa8844",
            "thought":    "#ffdd88",
            "eye_shine":  "#ffffff",
        },
        "quests_bonus": [],
    },
]


def _in_date_range(today: date, months_ranges: list) -> bool:
    """Проверяет, попадает ли дата в один из диапазонов (month, day_from, day_to)."""
    m, d = today.month, today.day
    for month, day_from, day_to in months_ranges:
        if m == month and day_from <= d <= day_to:
            return True
    return False


def get_active_event(today: date = None) -> dict | None:
    """
    Возвращает активный сезонный ивент для текущей даты или None.
    Если несколько совпадают — возвращает первый (более специфичный).
    """
    if today is None:
        today = date.today()

    for event in SEASONAL_EVENTS:
        if _in_date_range(today, event["months"]):
            return event

    return None


def get_seasonal_skin(base_skin: dict, today: date = None) -> dict:
    """
    Возвращает скин с учётом сезонного ивента.
    Если ивент активен и у него есть скин — возвращает сезонный.
    Иначе — base_skin.
    """
    event = get_active_event(today)
    if event and event.get("skin"):
        return event["skin"]
    return base_skin


def get_seasonal_banner(today: date = None) -> str | None:
    """Текст праздничного баннера или None."""
    event = get_active_event(today)
    if event:
        return event.get("banner")
    return None


def get_seasonal_quests(today: date = None) -> list:
    """Дополнительные сезонные квесты (добавляются к обычным)."""
    event = get_active_event(today)
    if event:
        return event.get("quests_bonus", [])
    return []


def get_seasonal_greeting(today: date = None) -> str | None:
    """Приветствие кота по поводу праздника."""
    event = get_active_event(today)
    if not event:
        return None
    name = event["name"]
    greetings = {
        "Новый год 🎆":       "С Наступающим! 🎆 Я уже в праздничном костюме!",
        "Рождество 🎄":       "Хо-хо-хо! 🎄 Рождественский кот желает тебе добра!",
        "Хэллоуин 🎃":        "Буу! 🎃 Не бойся, это всего лишь я — Bongo Cat!",
        "День влюблённых 💝": "С Днём Святого Валентина! 💝 Ты для меня самый лучший хозяин!",
        "8 марта 🌷":         "С праздником весны! 🌷 Ты прекрасна!",
        "9 мая 🎖":           "Помним и гордимся! 🎖 Мирного неба!",
        "Лето ☀️":             "Лето пришло! ☀️ Главное — не забывай отдыхать!",
    }
    return greetings.get(name)
