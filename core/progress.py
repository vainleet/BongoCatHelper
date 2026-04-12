"""
core/progress.py — система прогресса с полноценными скинами кота.
"""

import json, os, sys, random
from datetime import datetime, date, timedelta
from typing import Dict, List
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

SAVE_PATH = os.path.join(config.DATA_DIR, "progress.json")

XP_REWARDS = {
    "message_sent":   5,
    "daily_checkin": 20,
    "mood_logged":   10,
    "quest_complete":50,
    "streak_bonus":  15,
    "long_talk":     25,
    "crisis_handled":30,
}

LEVELS = [
    (0,    "Котёнок 🐣"),
    (100,  "Малыш 🐱"),
    (250,  "Друг 😺"),
    (500,  "Товарищ 🌟"),
    (900,  "Приятель 💙"),
    (1500, "Мудрец 🎓"),
    (2500, "Легенда 👑"),
    (4000, "Бессмертный 🏆"),
]

# ── Полноценные скины кота ────────────────────────────────
# Каждый скин меняет: цвет тела, ушей, хвоста, румянца, контура + шапку
CAT_SKINS = {
    0: {
        "name": "Обычный",
        "hat": None,
        "body":      "#f0d8ff",
        "body_shade":"#e0c0f0",
        "inner_ear": "#ffb3d9",
        "tail":      "#d4a0c8",
        "tail_tip":  "#c890b8",
        "blush":     "#ffb3c6",
        "outline":   "#d0b0e8",
        "paw":       "#eed8ff",
        "eye_dark":  "#2a1040",
        "nose":      "#ff9eb5",
        "mouth":     "#ff9eb5",
        "whisker":   "#9090a0",
        "thought":   "#c8a8ff",
        "eye_shine": "#ffffff",
    },
    2: {
        "name": "Джентльмен 🎩",
        "hat": "🎩",
        "body":      "#f5f0ff",
        "body_shade":"#e8e0f5",
        "inner_ear": "#ffccdd",
        "tail":      "#c8b8e8",
        "tail_tip":  "#b0a0d8",
        "blush":     "#ffaacc",
        "outline":   "#c0a8e0",
        "paw":       "#ede0ff",
        "eye_dark":  "#1a0830",
        "nose":      "#ff88aa",
        "mouth":     "#ff88aa",
        "whisker":   "#808090",
        "thought":   "#b898ff",
        "eye_shine": "#ffffff",
    },
    3: {
        "name": "Королева 👑",
        "hat": "👑",
        "body":      "#fff4cc",
        "body_shade":"#ffe8a0",
        "inner_ear": "#ffccaa",
        "tail":      "#e8c870",
        "tail_tip":  "#d4aa50",
        "blush":     "#ffaa88",
        "outline":   "#d4a840",
        "paw":       "#fff0aa",
        "eye_dark":  "#301800",
        "nose":      "#ff8844",
        "mouth":     "#ff8844",
        "whisker":   "#a09060",
        "thought":   "#ffd060",
        "eye_shine": "#ffffff",
    },
    4: {
        "name": "Академик 🎓",
        "hat": "🎓",
        "body":      "#d8f0ff",
        "body_shade":"#b8d8f0",
        "inner_ear": "#aaccff",
        "tail":      "#80b8e8",
        "tail_tip":  "#60a0d0",
        "blush":     "#88ccff",
        "outline":   "#60a0d0",
        "paw":       "#c8e8ff",
        "eye_dark":  "#001830",
        "nose":      "#4488ff",
        "mouth":     "#4488ff",
        "whisker":   "#6080a0",
        "thought":   "#80c0ff",
        "eye_shine": "#ffffff",
    },
    5: {
        "name": "Ниндзя 🥷",
        "hat": "🥷",
        "body":      "#2a2a3a",
        "body_shade":"#1a1a2a",
        "inner_ear": "#884466",
        "tail":      "#444455",
        "tail_tip":  "#333344",
        "blush":     "#664455",
        "outline":   "#555566",
        "paw":       "#3a3a4a",
        "eye_dark":  "#cc2244",
        "nose":      "#cc4466",
        "mouth":     "#cc4466",
        "whisker":   "#888899",
        "thought":   "#aa3355",
        "eye_shine": "#ffaacc",
    },
    6: {
        "name": "Призрак 👻",
        "hat": "👻",
        "body":      "#eef8ff",
        "body_shade":"#d0e8f8",
        "inner_ear": "#c8e0ff",
        "tail":      "#b0cce8",
        "tail_tip":  "#98b8d8",
        "blush":     "#b8d0ff",
        "outline":   "#a0b8d8",
        "paw":       "#e0f0ff",
        "eye_dark":  "#000830",
        "nose":      "#8899bb",
        "mouth":     "#8899bb",
        "whisker":   "#a0b0c8",
        "thought":   "#c0d8ff",
        "eye_shine": "#ffffff",
    },
    7: {
        "name": "Дракон 🐉",
        "hat": "🐉",
        "body":      "#d0ffd8",
        "body_shade":"#a8e8b0",
        "inner_ear": "#88ffaa",
        "tail":      "#70cc88",
        "tail_tip":  "#50aa66",
        "blush":     "#88ffcc",
        "outline":   "#60bb77",
        "paw":       "#c0ffc8",
        "eye_dark":  "#002800",
        "nose":      "#22aa44",
        "mouth":     "#22aa44",
        "whisker":   "#60a070",
        "thought":   "#88ffaa",
        "eye_shine": "#ffffff",
    },
    8: {
        "name": "Космос 🚀",
        "hat": "🚀",
        "body":      "#1a0a2e",
        "body_shade":"#0e0518",
        "inner_ear": "#6600cc",
        "tail":      "#330066",
        "tail_tip":  "#220044",
        "blush":     "#4400aa",
        "outline":   "#5500bb",
        "paw":       "#280a40",
        "eye_dark":  "#ff00ff",
        "nose":      "#aa00ff",
        "mouth":     "#aa00ff",
        "whisker":   "#8800cc",
        "thought":   "#cc00ff",
        "eye_shine": "#ff88ff",
    },
}

DAILY_QUESTS_POOL = [
    {"id":"talk_5",       "title":"Поговори с котом",   "desc":"Напиши 5 сообщений",        "target":5,  "type":"messages",  "xp":40},
    {"id":"checkin",      "title":"Дневной check-in",   "desc":"Отметься сегодня",           "target":1,  "type":"checkin",   "xp":30},
    {"id":"mood_log",     "title":"Запись настроения",  "desc":"Запиши настроение 1 раз",    "target":1,  "type":"mood",      "xp":25},
    {"id":"long_convo",   "title":"Глубокий разговор",  "desc":"Напиши 10 сообщений подряд", "target":10, "type":"messages",  "xp":60},
    {"id":"morning",      "title":"Доброе утро!",       "desc":"Открой до 10 утра",          "target":1,  "type":"morning",   "xp":25},
    {"id":"share_problem","title":"Выговорись",         "desc":"Расскажи о проблеме",         "target":1,  "type":"deep_talk", "xp":50},
    {"id":"mood_3",       "title":"Следи за собой",     "desc":"Записывай настроение 3 раза", "target":3,  "type":"mood",      "xp":45},
]

ALL_ACHIEVEMENTS = [
    {"id":"first_message", "title":"Первое слово 🐾",     "desc":"Написал первое сообщение",    "secret":False},
    {"id":"streak_3",      "title":"3 дня подряд 🔥",     "desc":"Streak 3 дня",                "secret":False},
    {"id":"streak_7",      "title":"Неделя! 🌟",          "desc":"Streak 7 дней",               "secret":False},
    {"id":"streak_30",     "title":"Месяц 💙",            "desc":"Streak 30 дней",              "secret":False},
    {"id":"level_3",       "title":"Растёшь ⭐",           "desc":"Достиг 3-го уровня",          "secret":False},
    {"id":"level_5",       "title":"Верный друг 💫",       "desc":"Достиг 5-го уровня",          "secret":False},
    {"id":"100_messages",  "title":"Болтун 💬",           "desc":"100 сообщений",               "secret":False},
    {"id":"mood_week",     "title":"Самоанализ 📊",       "desc":"Настроение 7 дней подряд",    "secret":False},
    {"id":"night_owl",     "title":"Сова 🦉",             "desc":"Написал после полуночи",      "secret":True},
    {"id":"early_bird",    "title":"Жаворонок 🌅",        "desc":"Открыл до 7 утра",            "secret":True},
    {"id":"deep_talk",     "title":"Открытое сердце 💜",  "desc":"Поделился чем-то важным",     "secret":True},
    {"id":"all_quests",    "title":"Перфекционист ✨",     "desc":"Все квесты за день",          "secret":False},
    {"id":"level_max",     "title":"Космос 🚀",           "desc":"Максимальный уровень",        "secret":False},
    # Prestige
    {"id":"prestige_1",    "title":"Ветеран ★",           "desc":"Первое перерождение",         "secret":False},
    {"id":"prestige_3",    "title":"Легенда ★★★",         "desc":"Три перерождения",            "secret":False},
    # Weekly challenges
    {"id":"weekly_done",   "title":"Недельный чемпион 🏅", "desc":"Выполнил еженедельный челлендж","secret":False},
    # Diary
    {"id":"diary_7",       "title":"Дневник 📓",          "desc":"7 записей в дневнике",        "secret":False},
]

# ── Еженедельные челленджи ────────────────────────────────
WEEKLY_CHALLENGES_POOL = [
    {"id":"w_msgs_50",   "title":"Разговорчивый 💬",  "desc":"Напиши 50 сообщений за неделю",    "target":50,  "type":"messages",  "xp":150},
    {"id":"w_streak_7",  "title":"Железный стрик 🔥", "desc":"Streak 7 дней подряд",             "target":7,   "type":"streak",    "xp":200},
    {"id":"w_mood_5",    "title":"Самонаблюдение 🧘", "desc":"Запиши настроение 5 дней",          "target":5,   "type":"mood",      "xp":120},
    {"id":"w_checkin_5", "title":"Постоянство ✅",     "desc":"Check-in 5 дней из 7",             "target":5,   "type":"checkin",   "xp":130},
    {"id":"w_deep_3",    "title":"Душевный разговор 💜","desc":"3 глубоких разговора за неделю",  "target":3,   "type":"deep_talk", "xp":180},
    {"id":"w_quests_7",  "title":"Квестоман 🎯",       "desc":"Заверши хотя бы 7 квестов",       "target":7,   "type":"quest",     "xp":160},
]

# ── Prestige скины (значки ★ добавляются к любому скину) ─
PRESTIGE_BADGES = {
    1: "★",
    2: "★★",
    3: "★★★",
    4: "★★★★",
    5: "★★★★★",
}


def _today(): return date.today().isoformat()


def get_level_info(xp: int) -> dict:
    level, title = 0, LEVELS[0][1]
    for i, (req, name) in enumerate(LEVELS):
        if xp >= req: level, title = i, name
    nxt = LEVELS[level+1][0] if level+1 < len(LEVELS) else None
    prv = LEVELS[level][0]
    return {"level":level,"title":title,"xp":xp,"prev_xp":prv,
            "next_xp":nxt,"progress":(xp-prv)/(nxt-prv) if nxt else 1.0}


def get_skin(level: int) -> dict:
    """Возвращает словарь цветов скина для текущего уровня."""
    best_lvl = 0
    for lvl in sorted(CAT_SKINS.keys()):
        if level >= lvl:
            best_lvl = lvl
    return CAT_SKINS[best_lvl]


class ProgressSystem:
    def __init__(self):
        os.makedirs(config.DATA_DIR, exist_ok=True)
        self._data = self._load()
        self._ensure_daily_quests()

    def _load(self):
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH,"r",encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return self._default()

    def _default(self):
        return {"xp":0,"total_messages":0,"streak":0,
                "last_active_date":None,"achievements":[],
                "daily_quests":[],"quests_date":None,
                "mood_log":[],"mood_days":0,
                "checkin_date":None,"session_messages":0,
                "selected_skin":0,
                "prestige":0,"prestige_total_xp":0,
                "weekly_challenge":None,"weekly_date":None,"weekly_progress":0,
                "weekly_checkins":0,"weekly_quests_done":0,"weekly_deep_talks":0,
                "diary":[]}

    def save(self):
        try:
            with open(SAVE_PATH,"w",encoding="utf-8") as f:
                json.dump(self._data,f,ensure_ascii=False,indent=2)
        except Exception as e:
            print(f"  ⚠ Progress save: {e}")

    def _update_streak(self):
        today = _today()
        last  = self._data.get("last_active_date")
        if last == today: return
        if last:
            diff = (date.today() - date.fromisoformat(last)).days
            self._data["streak"] = self._data["streak"]+1 if diff==1 else 1
        else:
            self._data["streak"] = 1
        self._data["last_active_date"] = today
        s = self._data["streak"]
        if s>=3:  self._unlock("streak_3")
        if s>=7:  self._unlock("streak_7")
        if s>=30: self._unlock("streak_30")
        self._progress_weekly("streak", s)

    def add_xp(self, reason: str) -> int:
        amt = XP_REWARDS.get(reason, 0)
        if not amt: return 0
        old = get_level_info(self._data["xp"])["level"]
        self._data["xp"] += amt
        new = get_level_info(self._data["xp"])["level"]
        self.save()
        if new > old:
            if new>=3: self._unlock("level_3")
            if new>=5: self._unlock("level_5")
            if new>=len(LEVELS)-1: self._unlock("level_max")
        return amt

    def on_message(self) -> List[str]:
        events = []
        self._update_streak()
        self._data["total_messages"] = self._data.get("total_messages",0)+1
        self._data["session_messages"] = self._data.get("session_messages",0)+1
        xp = self.add_xp("message_sent")
        if xp: events.append(f"+{xp} XP")
        if self._data["streak"]>1: self.add_xp("streak_bonus")
        n = self._data["total_messages"]
        if n==1:   self._unlock("first_message"); events.append("🏆 Первое слово!")
        if n>=100: self._unlock("100_messages");  events.append("💬 100 сообщений!")
        if self._data["session_messages"]>=10: self.add_xp("long_talk")
        h = datetime.now().hour
        if 0<=h<5: self._unlock("night_owl")
        if h<7:    self._unlock("early_bird")
        if h<10:   self._progress_quest("morning",1)
        self._progress_quest("messages",1)
        self._progress_weekly("messages", 1)
        self.save()
        return events

    def log_mood(self, mood: int, note: str="") -> str:
        today = _today()
        log = self._data.setdefault("mood_log",[])
        already = any(e.get("date")==today for e in log)
        log.append({"date":today,"mood":mood,"note":note,"ts":datetime.now().isoformat()})
        self._data["mood_log"] = log[-90:]
        if not already:
            self._data["mood_days"] = self._data.get("mood_days",0)+1
            self.add_xp("mood_logged")
            self._progress_quest("mood",1)
            if self._data["mood_days"]>=7: self._unlock("mood_week")
        self.save()
        emojis={1:"😢",2:"😔",3:"😐",4:"😊",5:"😄"}
        texts={1:"Слышу тебя 💙",2:"Непросто... Поговорим?",
               3:"Обычный день 🐾",4:"Хороший день! 😊",5:"Отлично! 🌟"}
        return f"{emojis.get(mood,'😐')} {texts.get(mood,'')}"

    def get_mood_stats(self):
        log = self._data.get("mood_log",[])
        week = []
        for i in range(6,-1,-1):
            d = (date.today()-timedelta(days=i)).isoformat()
            entries = [e["mood"] for e in log if e.get("date")==d]
            avg = round(sum(entries)/len(entries),1) if entries else None
            week.append({"date":d,"mood":avg,
                         "label":(date.today()-timedelta(days=i)).strftime("%a")})
        return week

    def do_checkin(self) -> str:
        today = _today()
        if self._data.get("checkin_date")==today:
            return "Уже отмечен сегодня 🐱"
        self._data["checkin_date"] = today
        self.add_xp("daily_checkin")
        self._progress_quest("checkin",1)
        self._progress_weekly("checkin", 1)
        self.save()
        return f"✅ Check-in! +{XP_REWARDS['daily_checkin']} XP · Streak: {self._data['streak']} 🔥"

    def _ensure_daily_quests(self):
        today = _today()
        if self._data.get("quests_date")==today: return
        pool = DAILY_QUESTS_POOL.copy()
        random.shuffle(pool)
        self._data["daily_quests"] = [{**q,"progress":0,"done":False} for q in pool[:3]]
        self._data["quests_date"] = today
        self._data["session_messages"] = 0
        self.save()

    def _progress_quest(self, qtype: str, amount: int):
        changed = False
        for q in self._data.get("daily_quests",[]):
            if q.get("done"): continue
            if q.get("type")==qtype:
                q["progress"] = min(q.get("progress",0)+amount, q["target"])
                if q["progress"]>=q["target"]:
                    q["done"]=True; self.add_xp("quest_complete"); changed=True
        if changed:
            if all(q.get("done") for q in self._data.get("daily_quests",[])):
                self._unlock("all_quests")
            self.save()

    def mark_deep_talk(self):
        self._unlock("deep_talk"); self.add_xp("crisis_handled")
        self._progress_quest("deep_talk",1)
        self._progress_weekly("deep_talk", 1)
        self.save()

    def _unlock(self, aid: str) -> bool:
        if aid not in self._data.get("achievements",[]):
            self._data.setdefault("achievements",[]).append(aid)
            self.save(); return True
        return False

    def is_unlocked(self, aid: str) -> bool:
        return aid in self._data.get("achievements",[])

    @property
    def xp(self): return self._data.get("xp",0)
    @property
    def level_info(self): return get_level_info(self.xp)
    @property
    def streak(self): return self._data.get("streak",0)
    @property
    def total_messages(self): return self._data.get("total_messages",0)
    def select_skin(self, skin_level: int):
        """Выбрать скин если он разблокирован."""
        if self.level_info["level"] >= skin_level:
            self._data["selected_skin"] = skin_level
            self.save()
            return True
        return False

    @property
    def selected_skin_level(self) -> int:
        return self._data.get("selected_skin", 0)

    @property
    def skin(self):
        sel = self._data.get("selected_skin", 0)
        lvl = self.level_info["level"]
        # Если выбранный скин разблокирован — используем его, иначе лучший доступный
        if lvl >= sel:
            return CAT_SKINS.get(sel, get_skin(lvl))
        return get_skin(lvl)
    @property
    def accessory(self): return self.skin
    @property
    def daily_quests(self):
        self._ensure_daily_quests()
        return self._data.get("daily_quests",[])
    @property
    def achievements(self):
        unlocked = set(self._data.get("achievements",[]))
        return [{**a,"unlocked":a["id"] in unlocked} for a in ALL_ACHIEVEMENTS]

    # ── Prestige ──────────────────────────────────────────
    @property
    def prestige(self) -> int:
        return self._data.get("prestige", 0)

    @property
    def prestige_badge(self) -> str:
        p = self.prestige
        return PRESTIGE_BADGES.get(min(p, max(PRESTIGE_BADGES.keys())), "") if p > 0 else ""

    def can_prestige(self) -> bool:
        """True если достигнут максимальный уровень."""
        return self.level_info["level"] >= len(LEVELS) - 1

    def do_prestige(self) -> str:
        """Перерождение: сбрасывает XP, увеличивает prestige, выдаёт эксклюзивный скин."""
        if not self.can_prestige():
            return "Сначала достигни максимального уровня! 🚀"
        p = self._data.get("prestige", 0) + 1
        total = self._data.get("prestige_total_xp", 0) + self._data.get("xp", 0)
        self._data["prestige"] = p
        self._data["prestige_total_xp"] = total
        self._data["xp"] = 0
        self._data["selected_skin"] = 0   # сброс на базовый скин
        if p == 1: self._unlock("prestige_1")
        if p >= 3: self._unlock("prestige_3")
        self.save()
        badge = PRESTIGE_BADGES.get(min(p, max(PRESTIGE_BADGES.keys())), "★")
        return f"🌟 Перерождение {p}! Ты теперь «{badge} Ветеран». XP сброшен, путь начинается снова!"

    # ── Еженедельные челленджи ────────────────────────────
    def _get_week_start(self) -> str:
        """Понедельник текущей недели ISO."""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return monday.isoformat()

    def _ensure_weekly_challenge(self):
        week_start = self._get_week_start()
        if self._data.get("weekly_date") == week_start:
            return
        # Новая неделя — выбираем челлендж и сбрасываем прогресс
        challenge = random.choice(WEEKLY_CHALLENGES_POOL)
        self._data["weekly_challenge"] = {**challenge, "progress": 0, "done": False}
        self._data["weekly_date"] = week_start
        self._data["weekly_checkins"] = 0
        self._data["weekly_quests_done"] = 0
        self._data["weekly_deep_talks"] = 0
        self.save()

    @property
    def weekly_challenge(self) -> dict | None:
        self._ensure_weekly_challenge()
        return self._data.get("weekly_challenge")

    def _progress_weekly(self, qtype: str, amount: int = 1):
        self._ensure_weekly_challenge()
        ch = self._data.get("weekly_challenge")
        if not ch or ch.get("done"):
            return
        if ch.get("type") == qtype:
            ch["progress"] = min(ch.get("progress", 0) + amount, ch["target"])
            if ch["progress"] >= ch["target"]:
                ch["done"] = True
                xp = ch.get("xp", 100)
                self.add_xp("quest_complete")
                self._data["xp"] += xp - XP_REWARDS["quest_complete"]  # доплата разницы
                self._unlock("weekly_done")
                self.save()

    # ── Дневник ───────────────────────────────────────────
    def add_diary_entry(self, text: str) -> str:
        """Добавляет запись в дневник. Возвращает подтверждение."""
        if not text.strip():
            return "Напиши хоть пару слов 🐱"
        entry = {
            "date": date.today().isoformat(),
            "ts":   datetime.now().isoformat(),
            "text": text.strip()[:500],
        }
        diary = self._data.setdefault("diary", [])
        diary.append(entry)
        self._data["diary"] = diary[-365:]   # храним год
        count = len(diary)
        if count >= 7:
            self._unlock("diary_7")
        self.save()
        return f"📓 Запись сохранена (всего: {count})"

    def get_diary(self, last_n: int = 10) -> list:
        """Последние N записей дневника (новые первые)."""
        diary = self._data.get("diary", [])
        return list(reversed(diary[-last_n:]))

    @property
    def diary_count(self) -> int:
        return len(self._data.get("diary", []))
