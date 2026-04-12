"""
core/notifications.py
Windows-уведомления от кота — без интернета, локально.
Использует plyer (если есть) или win10toast как fallback.
"""

import threading
import time
import random
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

# ── Тексты уведомлений ────────────────────────────────────

MISS_YOU = [
    ("Кот скучает 😿", "Ты не заходил(а) уже давно. Всё хорошо?"),
    ("Привет! 🐱", "Давно не виделись! Зайди пообщаться."),
    ("Мяу? 🐾", "Твой кот ждёт тебя. Загляни на минутку!"),
]

QUEST_REMIND = [
    ("Квест ждёт! 🎯", "У тебя есть незавершённые задания на сегодня."),
    ("Ежедневный квест 📋", "Не забудь выполнить задания дня!"),
    ("XP сами себя не заработают 🌟", "Квесты дня ещё не выполнены!"),
]

STREAK_WARN = [
    ("Стрик под угрозой! 🔥", "Зайди сегодня, чтобы не потерять серию дней."),
    ("Не сломай серию! 💙", "Ещё не отметился сегодня — стрик может прерваться."),
]

GOOD_MORNING = [
    ("Доброе утро! ☀️", "Кот уже ждёт тебя. Начни день с check-in!"),
    ("Вставай, соня! 🐱", "Новый день — новые квесты. Доброе утро!"),
]

EVENING = [
    ("Как прошёл день? 🌙", "Запиши настроение перед сном — кот хочет знать."),
    ("Вечерний check-in 🌛", "Не забудь отметить настроение дня!"),
]


# ── Утилита отправки ──────────────────────────────────────

def _send_notification(title: str, message: str, app_name: str = "Bongo Cat AI"):
    """Отправляет уведомление. Пробует plyer, затем win10toast, затем просто print."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            app_icon=None,
            timeout=6,
        )
        return True
    except Exception:
        pass

    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
        return True
    except Exception:
        pass

    # Fallback — вывод в консоль
    print(f"\n  🔔 [{app_name}] {title}\n     {message}\n")
    return False


# ── Основной класс ────────────────────────────────────────

class NotificationSystem:
    """
    Планировщик уведомлений. Запускается в фоне.
    Не требует интернета.
    """

    def __init__(self, progress_system):
        self._p = progress_system
        self._running = False
        self._thread = None
        self._last_notif: dict = {}   # {type: timestamp}
        self._app_visible = True      # флаг — приложение видно пользователю

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("  🔔 NotificationSystem запущен")

    def stop(self):
        self._running = False

    def set_app_visible(self, visible: bool):
        """Вызывай когда окно показывается/скрывается."""
        self._app_visible = visible

    def notify_user_active(self):
        """Вызывай при каждом сообщении пользователя."""
        self._last_notif["last_active"] = time.time()

    # ── Принудительные уведомления (вызывай снаружи) ─────

    def send_level_up(self, level: int, title: str):
        _send_notification(
            f"Новый уровень {level}! 🎉",
            f"Ты стал '{title}'. Поздравляю! 🐱"
        )

    def send_achievement(self, ach_title: str, ach_desc: str):
        _send_notification(
            f"Достижение разблокировано! 🏆",
            f"{ach_title} — {ach_desc}"
        )

    def send_streak_milestone(self, days: int):
        _send_notification(
            f"Стрик {days} дней! 🔥",
            f"Ты заходишь {days} дней подряд. Невероятно!"
        )

    def send_quest_complete(self, quest_title: str):
        _send_notification(
            "Квест выполнен! ✅",
            f"«{quest_title}» завершён. Забирай XP!"
        )

    # ── Фоновый цикл ──────────────────────────────────────

    def _loop(self):
        # Немного ждём после старта
        time.sleep(30)
        while self._running:
            try:
                self._tick()
            except Exception as e:
                print(f"  ⚠ NotificationSystem: {e}")
            time.sleep(60)  # проверяем раз в минуту

    def _cooldown(self, key: str, seconds: int) -> bool:
        """True если с последнего уведомления этого типа прошло достаточно времени."""
        last = self._last_notif.get(key, 0)
        return (time.time() - last) >= seconds

    def _tick(self):
        now = datetime.now()
        hour = now.hour
        last_active = self._last_notif.get("last_active", time.time())
        since_active = time.time() - last_active

        # Не шлём уведомления пока приложение открыто
        if self._app_visible:
            return

        # ── Доброе утро (7–9 утра) ────────────────────────
        if 7 <= hour <= 9 and self._cooldown("morning", 20 * 3600):
            self._last_notif["morning"] = time.time()
            t, m = random.choice(GOOD_MORNING)
            _send_notification(t, m)
            return

        # ── Вечернее настроение (20–22) ───────────────────
        if 20 <= hour <= 22 and self._cooldown("evening", 20 * 3600):
            # Проверяем — не записывал ли уже настроение сегодня
            stats = self._p.get_mood_stats()
            today_str = date.today().isoformat()
            today_logged = any(
                d["date"] == today_str and d["mood"] is not None
                for d in stats
            )
            if not today_logged:
                self._last_notif["evening"] = time.time()
                t, m = random.choice(EVENING)
                _send_notification(t, m)
                return

        # ── Стрик под угрозой (после 18 часов) ───────────
        if hour >= 18 and self._cooldown("streak_warn", 20 * 3600):
            checkin_today = self._p._data.get("checkin_date") == date.today().isoformat()
            if not checkin_today and self._p.streak >= 2:
                self._last_notif["streak_warn"] = time.time()
                t, m = random.choice(STREAK_WARN)
                _send_notification(t, m)
                return

        # ── Скучает (не заходили > 24 часов) ─────────────
        if since_active > 24 * 3600 and self._cooldown("miss_you", 24 * 3600):
            self._last_notif["miss_you"] = time.time()
            t, m = random.choice(MISS_YOU)
            _send_notification(t, m)
            return

        # ── Напоминание о квестах (днём) ─────────────────
        if 10 <= hour <= 17 and self._cooldown("quest", 12 * 3600):
            quests = self._p.daily_quests
            has_unfinished = any(not q.get("done") for q in quests)
            if has_unfinished:
                self._last_notif["quest"] = time.time()
                t, m = random.choice(QUEST_REMIND)
                _send_notification(t, m)
