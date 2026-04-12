"""
core/weekly_report.py
Еженедельный отчёт от кота — генерируется каждое воскресенье.
Виральная фича: скриншот отчёта = идеальный пост в TikTok/Twitter.
"""

import json, os, sys, threading
from datetime import date, timedelta, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

REPORT_SAVE = os.path.join(config.DATA_DIR, "weekly_report.json")

# Шаблон промпта для генерации отчёта
REPORT_PROMPT = """Ты — Bongo Cat, милый кот-компаньон. Напиши тёплый еженедельный отчёт пользователю.

Данные за неделю:
- Сообщений написано: {messages}
- Дней streak подряд: {streak}
- Среднее настроение: {mood_avg} из 5 {mood_emoji}
- Лучший день: {best_day}
- Уровень кота: {level} ({level_title})
- XP за неделю: {xp_gained}
- Приложений открыто больше всего: {top_app}

Напиши отчёт в 4-5 предложениях. Стиль: тёплый, личный, как дневник питомца.
Начни с обращения "Дорогой хозяин," или похожего.
Упомяни 2-3 конкретных факта из данных.
В конце — одна мотивирующая фраза на следующую неделю.
Добавь 2-3 эмодзи. Только отчёт, без лишних слов."""


def _ask_ollama(prompt: str, model: str) -> str:
    if not HAS_REQUESTS: return ""
    try:
        r = _req.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.9, "num_predict": 150},
        }, timeout=30)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
    except Exception:
        pass
    return ""


def _fallback_report(data: dict) -> str:
    """Шаблонный отчёт если Ollama недоступна."""
    msgs    = data.get("messages", 0)
    streak  = data.get("streak", 0)
    mood    = data.get("mood_avg", 0)
    level   = data.get("level", 0)
    xp      = data.get("xp_gained", 0)

    mood_e = "😢" if mood < 2 else "😔" if mood < 3 else "😐" if mood < 4 else "😊" if mood < 4.5 else "😄"

    lines = [
        f"Дорогой хозяин, эта неделя была особенной! 🐾",
        f"Ты написал мне {msgs} сообщений — я очень рада что ты рядом.",
    ]
    if streak >= 3:
        lines.append(f"Наш streak уже {streak} дней подряд — это здорово! 🔥")
    if mood > 0:
        lines.append(f"Твоё среднее настроение за неделю: {mood:.1f}/5 {mood_e}")
    lines.append(f"За неделю ты заработал {xp} XP и вырос до уровня {level}.")
    lines.append(f"На следующей неделе я буду рядом — что бы ни случилось 💙")
    return "\n".join(lines)


class WeeklyReportSystem:
    def __init__(self, progress_system, screen_watcher=None, ollama_model=""):
        self._p       = progress_system
        self._sw      = screen_watcher
        self._model   = ollama_model
        self._data    = self._load()
        self._app_hits: dict = {}  # счётчик приложений за неделю

    def _load(self) -> dict:
        if os.path.exists(REPORT_SAVE):
            try:
                with open(REPORT_SAVE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_report_week": None, "last_report_text": "",
                "week_start_xp": 0, "week_start_messages": 0}

    def _save(self):
        try:
            os.makedirs(config.DATA_DIR, exist_ok=True)
            with open(REPORT_SAVE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def track_app(self, app_name: str):
        """Вызывать при каждом захвате экрана."""
        if app_name:
            key = app_name.split(".")[0].lower()[:20]
            self._app_hits[key] = self._app_hits.get(key, 0) + 1

    def _get_week_key(self) -> str:
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat()

    def _build_report_data(self) -> dict:
        p  = self._p
        li = p.level_info

        # Настроение за 7 дней
        stats    = p.get_mood_stats()
        moods    = [d["mood"] for d in stats if d["mood"] is not None]
        mood_avg = round(sum(moods) / len(moods), 1) if moods else 0
        mood_e   = "😢" if mood_avg < 2 else "😔" if mood_avg < 3 else "😐" if mood_avg < 4 else "😊" if mood_avg < 4.5 else "😄"

        # Лучший день
        best = max(stats, key=lambda d: d["mood"] or 0)
        best_day_raw = best.get("label", "")
        day_names = {"Mon":"Пн","Tue":"Вт","Wed":"Ср","Thu":"Чт",
                     "Fri":"Пт","Sat":"Сб","Sun":"Вс"}
        best_day = day_names.get(best_day_raw, best_day_raw)

        # XP за неделю
        week_start_xp = self._data.get("week_start_xp", 0)
        xp_gained = max(0, p.xp - week_start_xp)

        # Топ приложение
        top_app = max(self._app_hits, key=self._app_hits.get) if self._app_hits else "неизвестно"

        # Сообщений за неделю
        week_start_msgs = self._data.get("week_start_messages", 0)
        messages = max(0, p.total_messages - week_start_msgs)

        return {
            "messages":   messages,
            "streak":     p.streak,
            "mood_avg":   mood_avg,
            "mood_emoji": mood_e,
            "best_day":   best_day if moods else "—",
            "level":      li["level"],
            "level_title":li["title"],
            "xp_gained":  xp_gained,
            "top_app":    top_app,
        }

    def generate_report_async(self, callback):
        """Генерирует отчёт асинхронно. callback(report_text)."""
        def _worker():
            data   = self._build_report_data()
            prompt = REPORT_PROMPT.format(**data)
            text   = _ask_ollama(prompt, self._model) if self._model else ""
            if not text:
                text = _fallback_report(data)

            # Сохраняем
            self._data["last_report_week"] = self._get_week_key()
            self._data["last_report_text"] = text
            self._data["week_start_xp"]    = self._p.xp
            self._data["week_start_messages"] = self._p.total_messages
            self._save()
            callback(text, data)

        threading.Thread(target=_worker, daemon=True).start()

    def should_generate(self) -> bool:
        """Нужно ли генерировать отчёт сейчас?"""
        today = date.today()
        # Каждое воскресенье
        if today.weekday() != 6:
            return False
        week_key = self._get_week_key()
        return self._data.get("last_report_week") != week_key

    @property
    def last_report(self) -> str:
        return self._data.get("last_report_text", "")

    def force_generate(self, callback):
        """Принудительная генерация (для тестов / кнопки)."""
        self.generate_report_async(callback)
