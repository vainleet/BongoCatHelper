"""
core/ai_engine.py
AI движок: Ollama + умные fallback-ответы + авторестарт Ollama.
"""

import random
import threading
import subprocess
import time
from typing import Optional, Callable

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

# ─── Локализованные ответы ────────────────────────────────
_RESPONSES = {
    "ru": {
        "greet":  [
            "Привет! 🐱 Рада тебя видеть! Как дела сегодня?",
            "Мяу! Привет-привет! Что нового?",
            "Хей! Я здесь, рядом. Как ты?",
        ],
        "sad": [
            "Мне жаль, что тебе сейчас тяжело 💙 Хочешь рассказать подробнее?",
            "Это звучит непросто... Я здесь и слушаю тебя.",
            "Ты не одинок(а). Иногда просто выговориться уже помогает — расскажи мне.",
        ],
        "tired": [
            "Звучит как сигнал сделать паузу ☕ Когда ты последний раз нормально отдыхал(а)?",
            "Усталость — это тело говорит «стоп». Может, 10 минут просто ничего не делать?",
            "Ты много работаешь! Прогулка или чашка чего-нибудь тёплого могут помочь 🍵",
        ],
        "happy": [
            "Ура! Это здорово слышать! 🎉 Расскажи, что случилось?",
            "Вот это да! Радуйся — ты заслуживаешь хороших моментов 🌟",
            "Мяу-отлично! Я тоже рада за тебя! 😺",
        ],
        "stress": [
            "Стресс бывает изматывающим... Попробуй сделать 3 глубоких вдоха прямо сейчас 🌬️",
            "Когда всё навалилось — сделай один маленький шаг. Не всё сразу.",
            "Ты справляешься! Может, сделать небольшой перерыв — встать, потянуться?",
        ],
        "work": [
            "Работа бывает изматывающей... Ты стараешься, и это уже немало 💪",
            "Может, попробовать разбить задачи на мелкие части? Иногда это помогает.",
            "Когда работы много — особенно важно делать перерывы каждый час.",
        ],
        "screen_code": [
            "Вижу, ты пишешь код 💻 Как продвигается? Если застрял(а) — расскажи!",
            "Программирование — это труд. Не забывай делать паузы для глаз и рук 🤲",
        ],
        "screen_browser": [
            "Много времени в браузере? Иногда полезно оторваться от экрана на минуту 👀",
            "Листаешь что-то интересное? 😸",
        ],
        "default": [
            "Понимаю тебя 💙 Расскажи больше — я слушаю.",
            "Интересно! А что ты об этом думаешь?",
            "Хм, я здесь рядом. Что ещё на сердце?",
            "Спасибо, что поделился(ась). Как ты себя чувствуешь прямо сейчас?",
            "Слышу тебя. Иногда важно просто знать, что кто-то рядом — и я рядом 🐱",
        ],
    },
    "en": {
        "greet": [
            "Hey there! 🐱 So glad to see you! How are you doing today?",
            "Meow! Hi hi! What's new with you?",
            "Hey! I'm right here. How are you feeling?",
        ],
        "sad": [
            "I'm sorry you're going through something tough 💙 Want to tell me more?",
            "That sounds really hard... I'm here and I'm listening.",
            "You're not alone. Sometimes just talking about it helps — tell me what's going on.",
        ],
        "tired": [
            "Sounds like a signal to take a break ☕ When did you last get some proper rest?",
            "Tiredness is your body saying 'stop'. Maybe 10 minutes of doing nothing?",
            "You've been working hard! A short walk or something warm to drink might help 🍵",
        ],
        "happy": [
            "Yay! That's so great to hear! 🎉 Tell me what happened!",
            "Awesome! Enjoy it — you deserve good moments 🌟",
            "Meow-excellent! I'm so happy for you! 😺",
        ],
        "stress": [
            "Stress can be exhausting... Try taking 3 deep breaths right now 🌬️",
            "When everything piles up — just take one small step. Not everything at once.",
            "You've got this! Maybe a short break — stand up, stretch a little?",
        ],
        "work": [
            "Work can be draining... You're trying your best, and that already matters 💪",
            "Maybe try breaking tasks into smaller pieces? It often helps.",
            "When there's a lot to do — taking breaks every hour is especially important.",
        ],
        "screen_code": [
            "Looks like you're writing code 💻 How's it going? Stuck on something? Tell me!",
            "Coding takes effort. Don't forget to rest your eyes and hands 🤲",
        ],
        "screen_browser": [
            "Lots of browser time? It can help to step away from the screen for a minute 👀",
            "Scrolling through something interesting? 😸",
        ],
        "default": [
            "I hear you 💙 Tell me more — I'm listening.",
            "Interesting! What do you think about it?",
            "Hmm, I'm right here. What else is on your mind?",
            "Thanks for sharing. How are you feeling right now?",
            "I hear you. Sometimes just knowing someone is there helps — and I'm here 🐱",
        ],
    }
}

_CRISIS = {
    "ru": (
        "💙 Мне очень жаль, что тебе так тяжело прямо сейчас.\n\n"
        "Я не могу заменить специалиста, но знаю, что тебе можно помочь.\n\n"
        "📞 Пожалуйста, позвони на бесплатную горячую линию:\n"
        "    🇷🇺  8-800-2000-122  (круглосуточно, бесплатно)\n\n"
        "Ты не один(а). ❤️"
    ),
    "en": (
        "💙 I'm so sorry you're feeling this way right now.\n\n"
        "I can't replace a professional, but I know help is available for you.\n\n"
        "📞 Please reach out to a free crisis line:\n"
        "    🇺🇸  988 Suicide & Crisis Lifeline (call or text 988)\n"
        "    🌍  findahelpline.com for other countries\n\n"
        "You're not alone. ❤️"
    ),
}

CRISIS_RESPONSE = _CRISIS.get(config.LANGUAGE, _CRISIS["en"])

_KEYWORDS = {
    "ru": {
        "greet":  ["привет", "хей", "здравствуй", "мяу"],
        "sad":    ["грустно", "плохо", "депресс", "тяжело", "трудно", "боль", "страшно"],
        "tired":  ["устал", "устала", "нет сил", "вымотал", "сонн"],
        "stress": ["стресс", "нервничаю", "тревог", "паник", "беспокой"],
        "happy":  ["радост", "счастлив", "хорошо", "отлично", "супер", "класс"],
        "work":   ["работ", "задач", "дедлайн", "офис", "проект", "начальник"],
    },
    "en": {
        "greet":  ["hello", "hi", "hey", "meow", "good morning", "good evening"],
        "sad":    ["sad", "depressed", "feeling down", "unhappy", "miserable", "hurt", "scared"],
        "tired":  ["tired", "exhausted", "no energy", "sleepy", "worn out", "drained"],
        "stress": ["stressed", "anxious", "nervous", "panic", "worried", "overwhelmed"],
        "happy":  ["happy", "great", "awesome", "excellent", "amazing", "good mood"],
        "work":   ["work", "task", "deadline", "office", "project", "boss", "meeting"],
    },
}


def detect_crisis(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in config.CRISIS_KEYWORDS)


def smart_reply(text: str, screen_context: str = "") -> str:
    lang = config.LANGUAGE
    responses = _RESPONSES.get(lang, _RESPONSES["en"])
    keywords  = _KEYWORDS.get(lang, _KEYWORDS["en"])
    t = text.lower()

    for category, words in keywords.items():
        if any(w in t for w in words):
            return random.choice(responses[category])

    # Screen context
    if screen_context:
        sc = screen_context.lower()
        if any(w in sc for w in ["def ", "function", "class ", "import", "const ", "var "]):
            return random.choice(responses["screen_code"])
        if any(w in sc for w in ["http", "google", "chrome", "firefox", "browser"]):
            return random.choice(responses["screen_browser"])

    return random.choice(responses["default"])


def detect_mood_from_reply(reply: str) -> str:
    t = reply.lower()
    if any(w in t for w in ["рада", "отлично", "ура", "yay", "great", "awesome", "🎉", "🌟", "😺"]):
        return "happy"
    if any(w in t for w in ["жаль", "тяжело", "sorry", "tough", "hard", "💙", "❤️"]):
        return "sad"
    if any(w in t for w in ["думаю", "интересно", "think", "interesting", "hmm"]):
        return "thinking"
    return "talking"


# ─── Авторестарт Ollama ───────────────────────────────────
def _try_restart_ollama():
    """Пытается запустить ollama serve в фоне."""
    try:
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            r"C:\Program Files\Ollama\ollama.exe",
        ]
        for p in paths:
            if os.path.exists(p):
                subprocess.Popen(
                    [p, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                print("  🔄 Ollama restarted")
                return True
    except Exception as e:
        print(f"  ⚠  Could not restart Ollama: {e}")
    return False


class AIEngine:
    def __init__(self):
        self.ollama_available = False
        self.model_name = config.OLLAMA_MODEL
        self._fail_count = 0
        self._MAX_FAILS = 3        # после 3 сбоев — авторестарт
        self._restarting = False
        self._check_ollama()

    def _check_ollama(self):
        if not HAS_REQUESTS:
            return
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                for candidate in ["gemma3", "gemma", "mistral", "phi3", "phi", "llama3", "llama"]:
                    for m in models:
                        if candidate in m.lower():
                            self.model_name = m
                            self.ollama_available = True
                            self._fail_count = 0
                            print(f"  ✅ Ollama: {m}")
                            return
                if models:
                    self.model_name = models[0]
                    self.ollama_available = True
                    self._fail_count = 0
                    print(f"  ✅ Ollama: {models[0]}")
        except Exception:
            print("  ⚠  Ollama not found — using smart replies")

    def _ask_ollama(self, history: list, screen_context: str = "") -> Optional[str]:
        if not HAS_REQUESTS or not self.ollama_available:
            return None
        try:
            parts = [f"[SYSTEM]\n{config.SYSTEM_PROMPT}\n"]
            if screen_context:
                label = "SCREEN CONTEXT" if config.LANGUAGE == "en" else "КОНТЕКСТ ЭКРАНА"
                parts.append(f"[{label}]\n{screen_context[:500]}\n")
            for m in history[-config.AI_HISTORY_LEN:]:
                role = "User" if m["role"] == "user" else "Bongo Cat"
                parts.append(f"{role}: {m['content']}")
            parts.append("Bongo Cat:")

            resp = requests.post(config.OLLAMA_URL, json={
                "model": self.model_name,
                "prompt": "\n".join(parts),
                "stream": False,
                "options": {
                    "temperature": config.AI_TEMPERATURE,
                    "num_predict": config.AI_MAX_TOKENS,
                }
            }, timeout=30)

            if resp.status_code == 200:
                self._fail_count = 0
                return resp.json().get("response", "").strip()

        except Exception as e:
            self._fail_count += 1
            print(f"  ⚠  Ollama error ({self._fail_count}/{self._MAX_FAILS}): {e}")
            self.ollama_available = False

            # Авторестарт после N сбоев
            if self._fail_count >= self._MAX_FAILS and not self._restarting:
                self._restarting = True
                def _restart_and_reconnect():
                    if _try_restart_ollama():
                        time.sleep(5)   # ждём пока сервер поднимется
                        self._check_ollama()
                    self._restarting = False
                threading.Thread(target=_restart_and_reconnect, daemon=True).start()

        return None

    def get_reply_async(
        self,
        user_text: str,
        history: list,
        screen_context: str,
        callback: Callable[[str, str], None]
    ):
        def _worker():
            time.sleep(0.3 + random.uniform(0, 0.5))
            reply = self._ask_ollama(history, screen_context)
            if not reply:
                reply = smart_reply(user_text, screen_context)
            mood = detect_mood_from_reply(reply)
            callback(reply, mood)

        threading.Thread(target=_worker, daemon=True).start()

    @property
    def status(self) -> str:
        if self._restarting:
            return "⟳ Restarting Ollama..." if config.LANGUAGE == "en" else "⟳ Перезапуск Ollama..."
        if self.ollama_available:
            return f"● AI: {self.model_name}"
        return "● Smart replies" if config.LANGUAGE == "en" else "● умные ответы"

    @property
    def status_color(self) -> str:
        if self._restarting:
            return "#f59e0b"
        return "#22c55e" if self.ollama_available else "#f59e0b"
