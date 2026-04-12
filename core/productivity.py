"""
core/productivity.py
Локальный дашборд продуктивности — считает время в приложениях.
Данные хранятся в data/productivity.json, никакого интернета.
"""

import json, os, sys, time, threading
from datetime import date, datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    from core.screen_watcher import get_active_window_title, get_active_process_name, categorize_window
    HAS_SCREEN = True
except ImportError:
    HAS_SCREEN = False

SAVE_PATH = os.path.join(config.DATA_DIR, "productivity.json")

CATEGORY_META = {
    "code":    {"label": "Код 💻",        "color": "#9b7fff"},
    "browser": {"label": "Браузер 🌐",    "color": "#60a5fa"},
    "media":   {"label": "Медиа 🎵",      "color": "#f472b6"},
    "docs":    {"label": "Документы 📄",  "color": "#34d399"},
    "game":    {"label": "Игры 🎮",       "color": "#fbbf24"},
    "social":  {"label": "Соцсети 💬",   "color": "#f87171"},
    "other":   {"label": "Остальное 🖥",  "color": "#6b7280"},
}

POLL_INTERVAL = 10


class ProductivityTracker:
    def __init__(self):
        self._running  = False
        self._thread   = None
        self._data     = self._load()
        self._cur_cat  = "other"
        self._cur_start = time.time()

    def _load(self):
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save(self):
        try:
            os.makedirs(config.DATA_DIR, exist_ok=True)
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠ Productivity save: {e}")

    def _record(self, category, seconds):
        today = date.today().isoformat()
        day   = self._data.setdefault(today, {})
        day[category] = day.get(category, 0) + seconds
        cutoff = (date.today() - timedelta(days=30)).isoformat()
        for k in [k for k in self._data if k < cutoff]:
            del self._data[k]

    def start(self):
        if not HAS_SCREEN:
            print("  ⚠ ProductivityTracker: screen_watcher недоступен")
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("  📊 ProductivityTracker запущен")

    def stop(self):
        self._running = False
        self._flush()

    def _flush(self):
        elapsed = int(time.time() - self._cur_start)
        if elapsed > 0:
            self._record(self._cur_cat, elapsed)
        self._cur_start = time.time()

    def _loop(self):
        while self._running:
            try:
                title = get_active_window_title()
                proc  = get_active_process_name()
                cat   = categorize_window(title, proc) or "other"
                if cat != self._cur_cat:
                    self._flush()
                    self._cur_cat = cat
                else:
                    elapsed = int(time.time() - self._cur_start)
                    if elapsed >= 60:
                        self._flush()
                        self.save()
            except Exception as e:
                print(f"  ⚠ Productivity tick: {e}")
            time.sleep(POLL_INTERVAL)

    def get_today(self):
        today = date.today().isoformat()
        base  = dict(self._data.get(today, {}))
        elapsed = int(time.time() - self._cur_start)
        base[self._cur_cat] = base.get(self._cur_cat, 0) + elapsed
        return base

    def get_daily_totals(self, days=7):
        result = []
        for i in range(days - 1, -1, -1):
            d      = date.today() - timedelta(days=i)
            d_iso  = d.isoformat()
            by_cat = dict(self._data.get(d_iso, {}))
            if i == 0:
                by_cat[self._cur_cat] = by_cat.get(self._cur_cat, 0) + int(time.time() - self._cur_start)
            total = sum(by_cat.values())
            result.append({"date": d_iso, "label": d.strftime("%a"), "total": total, "by_cat": by_cat})
        return result

    def get_top_category_today(self):
        today = self.get_today()
        if not today:
            return ("other", 0)
        cat = max(today, key=today.get)
        return (cat, today[cat])

    @staticmethod
    def format_duration(seconds):
        if seconds < 60:   return f"{seconds} сек"
        m = seconds // 60
        if m < 60:         return f"{m} мин"
        h, m = divmod(m, 60)
        return f"{h} ч {m} мин" if m else f"{h} ч"

    def get_summary_text(self):
        today   = self.get_today()
        if not today:
            return "Сегодня активность не зафиксирована."
        total_s = sum(today.values())
        top_cat, top_s = self.get_top_category_today()
        label   = CATEGORY_META.get(top_cat, CATEGORY_META["other"])["label"]
        lines   = [
            f"За компьютером сегодня: {ProductivityTracker.format_duration(total_s)}",
            f"Больше всего: {label} ({ProductivityTracker.format_duration(top_s)})",
        ]
        productive = sum(today.get(c, 0) for c in ("code", "docs"))
        if total_s > 0 and productive > 0:
            lines.append(f"Продуктивность: {int(productive * 100 / total_s)}%")
        return "\n".join(lines)
