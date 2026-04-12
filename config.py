"""
Конфигурация Bongo Cat AI
"""

import json, os

# ─── Язык — читается из user_settings.json ─────────────────
def _load_language():
    settings_path = os.path.join(os.path.dirname(__file__), "data", "user_settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f).get("language", "ru")
    except Exception:
        return "ru"

LANGUAGE = _load_language()   # "ru" или "en"

# ─── AI / Ollama ───────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

SYSTEM_PROMPT_RU = """Ты — Bongo Cat, дружелюбный и заботливый AI-компаньон на рабочем столе.
Говори тепло, просто, по-дружески. Поддерживай, не осуждай.
Отвечай кратко (2–4 предложения). Не ставь диагнозов, не советуй лекарства.
Предлагай простые стратегии: прогулки, дыхание, перерывы, хобби.
Если видишь кризис — сразу направь на горячую линию 8-800-2000-122.
ВАЖНО: Отвечай ТОЛЬКО на русском языке."""

SYSTEM_PROMPT_EN = """You are Bongo Cat, a friendly and caring AI companion on the desktop.
Speak warmly, simply, and in a friendly manner. Be supportive, not judgmental.
Keep replies short (2–4 sentences). Do not diagnose or recommend medications.
Suggest simple strategies: walks, breathing, breaks, hobbies.
If you detect a crisis, immediately provide the crisis hotline: 988 (US) or your local line.
IMPORTANT: Always reply in English only."""

SYSTEM_PROMPT = SYSTEM_PROMPT_EN if LANGUAGE == "en" else SYSTEM_PROMPT_RU

AI_TEMPERATURE  = 0.8
AI_MAX_TOKENS   = 200
AI_HISTORY_LEN  = 10

# ─── Анализ экрана ─────────────────────────────────────────
SCREEN_CAPTURE_INTERVAL = 30
SCREEN_CAPTURE_ENABLED  = True
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

SCREEN_BLACKLIST = [
    "KeePass", "1Password", "Bitwarden",
    "Task Manager", "Диспетчер задач",
    "LastPass", "Credential"
]

# ─── Окно / Интерфейс ──────────────────────────────────────
WINDOW_WIDTH  = 440
WINDOW_HEIGHT = 680
WINDOW_TITLE  = "Bongo Cat AI"
ALWAYS_ON_TOP = True
HOTKEY_TOGGLE = "ctrl+alt+b"

# ─── Приватность ───────────────────────────────────────────
SAVE_HISTORY     = True
HISTORY_MAX_DAYS = 7
DATA_DIR         = "data"

# ─── Активный режим ────────────────────────────────────────
PROACTIVE_ENABLED           = True
PROACTIVE_SILENCE_MIN       = 3
PROACTIVE_INTERVAL_MIN      = 7
PROACTIVE_ON_WINDOW_CHANGE  = True

# ─── Кризисная поддержка ───────────────────────────────────
CRISIS_HOTLINE  = "988" if LANGUAGE == "en" else "8-800-2000-122"
CRISIS_KEYWORDS = [
    "суицид", "покончу", "убью себя", "причиню себе вред",
    "не хочу жить", "повешусь", "порежу себя",
    "suicide", "kill myself", "self-harm", "hurt myself",
    "end my life", "want to die",
]

CLAUDE_API_KEY = ""
