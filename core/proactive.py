"""
core/proactive.py
Кот пишет сам. gemma3 генерирует живую реплику
на основе заголовка активного окна — никаких шаблонов.
"""

import threading, time, random, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from core.screen_watcher import (
    get_active_window_title, get_active_process_name, categorize_window
)

try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Молчание и перерывы ───────────────────────────────────
SILENCE_PROMPTS = [
    "Эй, как ты там? 🐱 Давно не писал(а)...",
    "Всё хорошо? Я здесь если что 💙",
    "Уже {min} минут молчишь. Как дела?",
    "Хочу убедиться что у тебя всё ок 🐾",
    "Перерыв бы не помешал! ☕ Давно вставал(а) из-за стола?",
    "Тихо стало... Я рядом если нужна поддержка 💙",
]

BREAK_REMINDERS = [
    "Долго за экраном 😿 Может, встать на 5 минут?",
    "Глазам нужен отдых — посмотри вдаль на 20 секунд 👀",
    "Каждые 20 минут полезно смотреть вдаль 20 секунд 🌿",
]

# ── Промпт для gemma3 ─────────────────────────────────────
REACTION_PROMPT = """Ты — Bongo Cat, милый кот-компаньон на рабочем столе пользователя.
Сейчас у пользователя открыто: {window_title}
Процесс: {process_name}

Напиши одну короткую реплику (максимум 15 слов) — живо, тепло, как настоящий друг.
Правила:
- Упомяни конкретно что открыто (название игры, сайта, программы)
- Задай один вопрос ИЛИ скажи что-то ободряющее
- Один эмодзи в конце
- Только сама реплика — никаких объяснений, никаких кавычек, никаких мыслей вслух

Примеры:
Открыт Minecraft → Строишь что-нибудь в Minecraft? 🏗
Открыт YouTube → Нашёл что посмотреть на YouTube? 🎬
Открыт VS Code → Как идёт код в VS Code? 💻
Открыт Discord → Хорошо общаешься в Discord? 💬
"""

def _ask_gemma(window_title: str, process_name: str, text_model: str) -> str:
    """gemma3 придумывает реплику по заголовку окна."""
    if not HAS_REQUESTS or not text_model or not window_title:
        return ""
    prompt = (REACTION_PROMPT
              .replace("{window_title}", window_title[:80])
              .replace("{process_name}", process_name[:40]))
    try:
        r = _req.post("http://localhost:11434/api/generate", json={
            "model": text_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "num_predict": 35,
                "stop": ["\n", "**", "Примеры", "Правила", "Открыт"],
            },
        }, timeout=15)
        if r.status_code == 200:
            text = r.json().get("response", "").strip()
            # Берём только первую строку, убираем кавычки и лишнее
            line = text.split("\n")[0].strip().strip('"').strip("'").strip("*")
            # Если модель написала слишком много — обрезаем
            words = line.split()
            if len(words) > 20:
                line = " ".join(words[:18]) + "..."
            return line
    except Exception as e:
        print(f"  ⚠ gemma reaction: {e}")
    return ""

# ── Fallback реплики (если gemma не ответил) ─────────────
_FALLBACKS = {
    "code":    ["Как идёт код? 💻", "Пишешь что-то интересное? 😸", "Долго кодишь — сделай паузу 👀"],
    "browser": ["Нашёл что-то интересное? 😸", "Как настроение сейчас? 💙"],
    "media":   ["Смотришь что-нибудь? 🎬", "Слушаешь музыку? 🎵"],
    "docs":    ["Много работы сегодня? 📄", "Успеваешь всё? 💙"],
    "game":    ["Играешь? 🎮 Мяу-удачи!", "Расслабляешься? 🕹"],
    "social":  ["Хорошо общаешься? 💬", "Приятный разговор? 💙"],
    "files":   ["Разбираешь файлы? 📁"],
}

def _fallback(category: str, title: str) -> str:
    options = _FALLBACKS.get(category, ["Как ты? 🐱", "Всё хорошо? 💙"])
    return random.choice(options)


# ── Основной класс ────────────────────────────────────────
class ProactiveWatcher:
    def __init__(self, screen_watcher, on_message):
        self._sw       = screen_watcher
        self._callback = on_message
        self._running  = False
        self._thread   = None

        self._last_user_msg  = time.time()
        self._last_proactive = time.time()
        self._last_window    = ""
        self._session_start  = time.time()

    def notify_user_message(self):
        self._last_user_msg  = time.time()
        self._last_proactive = time.time()

    def start(self):
        if not config.PROACTIVE_ENABLED:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"  🐱  ProactiveWatcher запущен")

    def stop(self):
        self._running = False

    def _loop(self):
        time.sleep(60)
        while self._running:
            try:
                self._tick()
            except Exception as e:
                print(f"  ⚠ ProactiveWatcher: {e}")
            time.sleep(15)

    def _tick(self):
        now          = time.time()
        silence_s    = config.PROACTIVE_SILENCE_MIN  * 60
        interval_s   = config.PROACTIVE_INTERVAL_MIN * 60
        since_user   = now - self._last_user_msg
        since_pro    = now - self._last_proactive

        # ── 1. Реакция на активное окно ──────────────────
        if since_pro >= 120 and since_user >= 30:
            title    = get_active_window_title()
            proc     = get_active_process_name()
            category = categorize_window(title, proc)

            # Реагируем если окно сменилось ИЛИ давно молчим
            window_changed = (title != self._last_window and bool(title))
            long_silence   = (since_pro >= interval_s)

            if (window_changed or long_silence) and title:
                text_model = getattr(self._sw, "_text_model", "")

                # gemma3 пишет живую реплику
                msg = _ask_gemma(title, proc, text_model)

                # Fallback если gemma не ответил
                if not msg:
                    msg = _fallback(category, title)

                self._last_window   = title
                self._last_proactive = now
                mood = "happy" if category in ("game", "media") else "idle"
                self._send(msg, mood)
                return

        # ── 2. Молчание пользователя ─────────────────────
        if since_user >= silence_s and since_pro >= interval_s:
            minutes = int(since_user // 60)
            msg = random.choice(SILENCE_PROMPTS).replace("{min}", str(minutes))
            self._last_proactive = now
            self._send(msg, "idle")
            return

        # ── 3. Напоминание о перерыве ────────────────────
        session_min = (now - self._session_start) / 60
        if session_min > 90 and since_pro >= interval_s and since_user >= silence_s // 2:
            self._last_proactive = now
            self._send(random.choice(BREAK_REMINDERS), "sad")

    def _send(self, text: str, mood: str):
        self._callback(text, mood)
