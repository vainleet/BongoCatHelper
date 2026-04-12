import tkinter as tk
from tkinter import scrolledtext
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config

_UI = {
    "ru": {
        "placeholder":  "Напиши мне...",
        "mood_btns":    [("😊","Хорошо!"),("😔","Грустно"),("😴","Устал(а)"),("💼","Стресс")],
        "menu_chat":    "💬  Чат",
        "menu_profile": "📊  Профиль / Квесты",
        "menu_report":  "📋  Отчёт недели",
        "menu_game":    "🎮  Мини-игра дня",
        "menu_ocr":     "👁  Анализ экрана",
        "menu_prod":    "📈  Продуктивность",
        "menu_diary":   "📓  Дневник",
        "menu_share":   "🖼  Поделиться",
        "menu_quit":    "✕   Выйти",
        "ocr_off":      "🔒 Анализ экрана выключен",
        "ocr_on":       "👁 Анализ экрана включён",
        "crisis_line":  "💙 Позвони: 8-800-2000-122",
        "greeting_chat":"Мяу! 🐱 Привет! Двойной клик — чат, правый клик — меню и профиль!",
        "greeting_bub": "Привет! 🐱 Двойной клик чтобы поговорить!",
        "report_bub":   "Составляю отчёт... 📋",
        "deadline_bub": "ЭТО СЕГОДНЯ?! 😱 Ты справишься, я верю!!!",
        "coop_online":  "онлайн",
        "coop_sys":     "в сети",
        "game_invite":  "🎮 Хочешь сыграть в мини-игру? (правый клик → Мини-игра)",
        "smart_mode":   "умные ответы",
    },
    "en": {
        "placeholder":  "Write to me...",
        "mood_btns":    [("😊","Good!"),("😔","Sad"),("😴","Tired"),("💼","Stressed")],
        "menu_chat":    "💬  Chat",
        "menu_profile": "📊  Profile / Quests",
        "menu_report":  "📋  Weekly Report",
        "menu_game":    "🎮  Daily Mini-game",
        "menu_ocr":     "👁  Screen Analysis",
        "menu_prod":    "📈  Productivity",
        "menu_diary":   "📓  Diary",
        "menu_share":   "🖼  Share",
        "menu_quit":    "✕   Quit",
        "ocr_off":      "🔒 Screen analysis disabled",
        "ocr_on":       "👁 Screen analysis enabled",
        "crisis_line":  "💙 Call or text: 988",
        "greeting_chat":"Meow! 🐱 Hello! Double-click to chat, right-click for menu!",
        "greeting_bub": "Hi! 🐱 Double-click to start chatting!",
        "report_bub":   "Generating report... 📋",
        "deadline_bub": "IS THIS DUE TODAY?! 😱 You got this, I believe in you!!!",
        "coop_online":  "online",
        "coop_sys":     "online",
        "game_invite":  "🎮 Want to play a mini-game? (right-click → Mini-game)",
        "smart_mode":   "smart replies",
    },
}

def _t(key):
    """Возвращает строку на текущем языке."""
    return _UI.get(config.LANGUAGE, _UI["en"]).get(key, _UI["en"][key])

from core.ai_engine      import AIEngine, detect_crisis, CRISIS_RESPONSE
from core.screen_watcher import ScreenWatcher
from core.history        import ChatHistory
from core.proactive      import ProactiveWatcher
from core.progress       import ProgressSystem
from ui.cat_widget       import BongoCatWidget
from ui.profile_window   import ProfileWindow
from ui.report_window    import ReportWindow
from core.weekly_report  import WeeklyReportSystem
from core.app_reactions  import get_app_reaction
from core.mood_pet       import get_mood_pet_state, get_mood_pet_message
from core.coop           import CoopSystem
from core.minigame       import MiniGameWindow

# ── Новые фичи v9 ─────────────────────────────────────────
from core.notifications  import NotificationSystem
from core.share_card     import open_share_dialog
from core.seasonal       import get_seasonal_skin, get_seasonal_banner, get_seasonal_greeting
from core.productivity   import ProductivityTracker
from ui.productivity_window import ProductivityWindow
from ui.diary_window        import DiaryWindow
from ui.prestige_window     import PrestigeWindow

# ── Цвета ─────────────────────────────────────────────────
BG      = "#0e0e14"
BG2     = "#161622"
BG3     = "#1e1e2e"
BG4     = "#252538"
CARD    = "#1a1a2a"
BORDER  = "#2d2d45"
PURPLE  = "#9b7fff"
PURPLE2 = "#7b5fff"
TEAL    = "#2dd4bf"
AMBER   = "#fbbf24"
GREEN   = "#34d399"
RED     = "#f87171"
TEXT    = "#e2e0f0"
TEXT2   = "#9090b8"
TEXT3   = "#4a4a6a"
USER_BG = "#1c2845"
USER_C  = "#60a5fa"
BOT_C   = "#9b7fff"

CAT_W = 160
CAT_H = 160


# ── Речевой пузырь ────────────────────────────────────────

class BubbleWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "#010203")
        self.configure(bg="#010203")
        self.withdraw()
        self._hide_job = None
        self._visible  = False

        # Внешняя тонкая рамка
        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack()

        inner = tk.Frame(outer, bg=BG2, padx=14, pady=10)
        inner.pack()

        self._var = tk.StringVar()
        self._lbl = tk.Label(inner, textvariable=self._var,
                              bg=BG2, fg=TEXT,
                              font=("Segoe UI", 10),
                              wraplength=230, justify=tk.LEFT)
        self._lbl.pack()

        # Хвостик
        tail = tk.Canvas(self, width=20, height=12,
                          bg="#010203", highlightthickness=0)
        tail.pack()
        tail.create_polygon(2,0, 18,0, 10,12,
                             fill=PURPLE2, outline="")

    def show(self, text: str, cat_x: int, cat_y: int, duration: int = 5000):
        self._var.set(text)
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = max(8, cat_x + CAT_W//2 - w//2)
        y = cat_y - h - 4
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self._visible = True
        if self._hide_job:
            self.after_cancel(self._hide_job)
        self._hide_job = self.after(duration, self.hide)

    def hide(self):
        self.withdraw()
        self._visible = False


# ── Окно чата ─────────────────────────────────────────────

class ChatWindow(tk.Toplevel):
    def __init__(self, parent, on_send, on_close):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._on_send  = on_send
        self._on_close = on_close
        self._ph       = False
        self._visible  = False
        self._build()

    def _build(self):
        # Тонкая рамка
        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)
        wrap = tk.Frame(outer, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        hdr = tk.Frame(wrap, bg=BG2, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🐱  Bongo Cat",
                 bg=BG2, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=12)

        close = tk.Label(hdr, text=" ✕ ", bg=BG2, fg=TEXT3,
                          font=("Segoe UI", 11), cursor="hand2")
        close.pack(side=tk.RIGHT, padx=8)
        close.bind("<Enter>",    lambda e: close.config(fg=RED, bg=BG3))
        close.bind("<Leave>",    lambda e: close.config(fg=TEXT3, bg=BG2))
        close.bind("<Button-1>", lambda e: self.close())

        hdr.bind("<ButtonPress-1>", self._ds)
        hdr.bind("<B1-Motion>",     self._dm)

        tk.Frame(wrap, bg=BORDER, height=1).pack(fill=tk.X)

        # Чат
        self.chat = scrolledtext.ScrolledText(
            wrap, bg=BG, fg=TEXT,
            font=("Segoe UI", 9),
            relief=tk.FLAT, bd=0,
            padx=6, pady=4,
            wrap=tk.WORD,
            cursor="arrow",
            state=tk.DISABLED,
            height=13)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=1)

        self.chat.tag_config("user_lbl",   foreground=USER_C,  font=("Segoe UI", 7,"bold"), lmargin1=44)
        self.chat.tag_config("user_msg",   foreground=TEXT,    background=USER_BG, lmargin1=44, lmargin2=44, rmargin=4, spacing1=1, spacing3=3)
        self.chat.tag_config("bot_lbl",    foreground=BOT_C,   font=("Segoe UI", 7,"bold"), lmargin1=4)
        self.chat.tag_config("bot_msg",    foreground=TEXT,    background=BG, lmargin1=4, lmargin2=4, rmargin=44, spacing1=1, spacing3=3)
        self.chat.tag_config("sys_msg",    foreground=TEXT3,   font=("Segoe UI", 7,"italic"), justify=tk.CENTER)
        self.chat.tag_config("crisis_msg", foreground="#ffaaaa", background="#2d0808", lmargin1=4, lmargin2=4, rmargin=4, spacing1=3, spacing3=4)

        # Ввод
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill=tk.X)
        inp = tk.Frame(wrap, bg=BG3)
        inp.pack(fill=tk.X, padx=1, pady=1)

        self.entry = tk.Text(inp, bg=BG3, fg=TEXT,
                              insertbackground=TEXT,
                              font=("Segoe UI", 9),
                              relief=tk.FLAT, bd=6,
                              height=2, wrap=tk.WORD)
        self.entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.entry.bind("<Return>",       self._enter)
        self.entry.bind("<Shift-Return>", lambda e: None)
        self.entry.bind("<FocusIn>",      self._cp)
        self.entry.bind("<FocusOut>",     self._sp)
        self._sp()

        send = tk.Label(inp, text=" ➤ ", bg=PURPLE2, fg="#fff",
                         font=("Segoe UI", 12), cursor="hand2", padx=4)
        send.pack(side=tk.RIGHT, fill=tk.Y)
        send.bind("<Button-1>", lambda e: self._send())
        send.bind("<Enter>",    lambda e: send.config(bg=PURPLE))
        send.bind("<Leave>",    lambda e: send.config(bg=PURPLE2))

        # Быстрые кнопки
        qf = tk.Frame(wrap, bg=BG2)
        qf.pack(fill=tk.X, padx=8, pady=6)
        for em, txt in _t("mood_btns"):
            b = tk.Label(qf, text=em, bg=BG3, fg=TEXT2,
                          font=("Segoe UI Emoji", 14),
                          padx=6, pady=3, cursor="hand2")
            b.pack(side=tk.LEFT, padx=2)
            b.bind("<Button-1>", lambda e, t=txt: self._quick(t))
            b.bind("<Enter>",    lambda e, lb=b: lb.config(bg=PURPLE2))
            b.bind("<Leave>",    lambda e, lb=b: lb.config(bg=BG3))

    def _sp(self, e=None):
        if not self.entry.get("1.0","end-1c").strip():
            self.entry.config(fg=TEXT3); self.entry.delete("1.0",tk.END)
            self.entry.insert("1.0", _t("placeholder")); self._ph=True
    def _cp(self, e=None):
        if self._ph:
            self.entry.delete("1.0",tk.END); self.entry.config(fg=TEXT); self._ph=False

    def _enter(self, e):
        if not (e.state&1): self._send(); return "break"
    def _quick(self, t):
        self._cp(); self.entry.delete("1.0",tk.END); self.entry.insert("1.0",t); self._send()
    def _send(self):
        if self._ph: return
        t = self.entry.get("1.0","end-1c").strip()
        if not t: return
        self.entry.delete("1.0",tk.END); self._on_send(t)

    def add_user(self, t):   self._app(("\nТы\n","user_lbl"),(f"{t}\n","user_msg"))
    def add_bot(self, t, c=False):
        self._app(("\nBongo Cat\n","bot_lbl"),(f"{t}\n","crisis_msg" if c else "bot_msg"))
    def add_sys(self, t):    self._app((f"\n{t}\n","sys_msg"),)

    def _app(self, *args):
        self.chat.config(state=tk.NORMAL)
        for t,tag in args: self.chat.insert(tk.END,t,tag)
        self.chat.config(state=tk.DISABLED); self.chat.see(tk.END)

    def _ds(self,e): self._dx=e.x_root-self.winfo_x(); self._dy=e.y_root-self.winfo_y()
    def _dm(self,e): self.geometry(f"+{e.x_root-self._dx}+{e.y_root-self._dy}")

    def open_near(self, cx, cy):
        sw=self.winfo_screenwidth(); w,h=300,380
        x=cx+CAT_W+8
        if x+w>sw: x=cx-w-8
        self.geometry(f"{w}x{h}+{x}+{cy}")
        self.deiconify(); self.entry.focus(); self._visible=True

    def close(self):
        self.withdraw(); self._visible=False; self._on_close()

    @property
    def visible(self): return self._visible


# ── Главное приложение ────────────────────────────────────

class BongoCatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Прозрачный оверлей
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-transparentcolor", "#010203")
        self.win.configure(bg="#010203")
        self.win.protocol("WM_DELETE_WINDOW", self._quit)

        # Позиция — правый нижний угол
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        self._x = sw - CAT_W - 20
        self._y = sh - CAT_H - 60
        self.win.geometry(f"{CAT_W}x{CAT_H}+{self._x}+{self._y}")

        # Кот
        self.cat = BongoCatWidget(self.win, size=CAT_W, bg="#010203")
        self.cat.pack()

        # Контекстное меню
        self._menu = tk.Menu(self.root, tearoff=0,
                              bg=BG3, fg=TEXT,
                              activebackground=PURPLE2, activeforeground="#fff",
                              font=("Segoe UI", 9), bd=0, relief=tk.FLAT)
        self._menu.add_command(label=_t("menu_chat"),              command=self._toggle_chat)
        self._menu.add_command(label=_t("menu_profile"), command=self._toggle_profile)
        self._menu.add_command(label=_t("menu_report"),     command=self._show_weekly_report)
        self._menu.add_command(label=_t("menu_game"),    command=self._open_minigame)
        self._menu.add_command(label=_t("menu_ocr"),    command=self._toggle_ocr)
        self._menu.add_separator()
        self._menu.add_command(label=_t("menu_prod"),   command=self._toggle_productivity)
        self._menu.add_command(label=_t("menu_diary"),          command=self._toggle_diary)
        self._menu.add_command(label="⭐  Prestige",          command=self._toggle_prestige)
        self._menu.add_command(label=_t("menu_share"),        command=self._share_card)
        self._menu.add_separator()
        self._menu.add_command(label=_t("menu_quit"),            command=self._quit)

        # Биндинги
        self.cat.bind("<ButtonPress-1>",   self._drag_start)
        self.cat.bind("<B1-Motion>",       self._drag_move)
        self.cat.bind("<ButtonRelease-1>", self._drag_end)
        self.cat.bind("<Button-3>",        self._show_menu)
        self.cat.bind("<Double-Button-1>", lambda e: self._toggle_chat())
        self._drag_moved = False

        # ── Модули (всё ДО дочерних окон) ─────────────────
        self.ai        = AIEngine()
        self.watcher   = ScreenWatcher()
        self.history   = ChatHistory()
        self.progress  = ProgressSystem()
        self.proactive = ProactiveWatcher(
            screen_watcher=self.watcher,
            on_message=self._on_proactive)

        # ── Новые системы v9 ──────────────────────────────
        self.notif        = NotificationSystem(self.progress)
        self.productivity = ProductivityTracker()

        self._typing            = False
        self._pending_events    = []
        self._session_start     = __import__('time').time()
        self._last_reaction_app = ''

        self.report_sys = WeeklyReportSystem(
            self.progress,
            screen_watcher=self.watcher,
            ollama_model=self.ai.model_name if self.ai.ollama_available else ''
        )

        # Кооп — имя кота = имя скина + уровень
        skin_name = self.progress.skin.get("name","Кот").split()[0]
        self.coop = CoopSystem(
            cat_name=f"{skin_name} (Ур.{self.progress.level_info['level']})",
            on_peer_message=self._on_peer_cat
        )

        # Дата последней мини-игры
        import datetime as _dt
        self._last_game_date = None

        # ── Дочерние окна ─────────────────────────────────
        self.bubble      = BubbleWindow(self.win)
        self.chat_win    = ChatWindow(self.win,
                                       on_send=self._on_user_send,
                                       on_close=lambda: None)
        self.report_win  = ReportWindow(self.win)
        self.game_win    = MiniGameWindow(self.win, on_reward=self._on_game_reward)
        self.profile_win = ProfileWindow(self.win,
                                          progress=self.progress,
                                          on_mood_log=self._on_mood_log)
        self.profile_win._on_skin_change = self._apply_skin

        # ── Новые окна v9 ─────────────────────────────────
        self.productivity_win = ProductivityWindow(self.win, self.productivity)
        self.diary_win        = DiaryWindow(self.win, self.progress,
                                             ai_callback=self._on_user_send)
        self.prestige_win     = PrestigeWindow(self.win, self.progress,
                                                on_prestige_done=self._on_prestige_msg)

        self._start_services()
        self._apply_skin()
        self._welcome()

    # ── Drag ──────────────────────────────────────────────

    def _drag_start(self, e):
        self._ox = e.x_root - self._x
        self._oy = e.y_root - self._y
        self._drag_moved = False

    def _drag_move(self, e):
        self._x = e.x_root - self._ox
        self._y = e.y_root - self._oy
        self.win.geometry(f"+{self._x}+{self._y}")
        self._drag_moved = True

    def _drag_end(self, e):
        pass

    def _show_menu(self, e):
        self._menu.tk_popup(e.x_root, e.y_root)

    # ── Переключатели ─────────────────────────────────────

    def _toggle_chat(self):
        if self.chat_win.visible: self.chat_win.close()
        else:                     self.chat_win.open_near(self._x, self._y)

    def _toggle_profile(self):
        if self.profile_win.visible: self.profile_win.close()
        else:                        self.profile_win.open_near(self._x, self._y)

    def _toggle_ocr(self):
        if self.watcher.enabled:
            self.watcher.pause()
            self._show_bubble(_t("ocr_off"), 3000)
        else:
            self.watcher.resume()
            self._show_bubble(_t("ocr_on"), 3000)

    # ── Отправка сообщения ────────────────────────────────

    def _on_user_send(self, text: str):
        self.chat_win.add_user(text)
        self.history.add("user", text)
        self.proactive.notify_user_message()
        self.notif.notify_user_active()
        self.notif.set_app_visible(True)

        # Прогресс
        events = self.progress.on_message()
        if events:
            self._pending_events = events

        # Паника при дедлайне
        self._check_deadline_panic(text)

        # Глубокий разговор
        deep = ["переживаю","тяжело","грустно","плохо","проблем","беспокоит","страшно","тревог"]
        if any(w in text.lower() for w in deep):
            self.progress.mark_deep_talk()

        # Кризис
        if detect_crisis(text):
            self.cat.set_mood("sad")
            self._show_bubble(_t("crisis_line"), 8000)
            self.chat_win.add_bot(CRISIS_RESPONSE, c=True)
            self.history.add("assistant", CRISIS_RESPONSE)
            return

        self._typing = True
        self.cat.set_mood("thinking")
        self._show_bubble("...", 30000)

        self.ai.get_reply_async(
            user_text=text,
            history=self.history.get_for_llm(),
            screen_context=self.watcher.last_context,
            callback=self._on_reply)

    def _on_reply(self, reply: str, mood: str):
        self.root.after(0, lambda: self._show_reply(reply, mood))

    def _show_reply(self, reply: str, mood: str):
        self._typing = False
        self.history.add("assistant", reply)
        short = reply if len(reply) <= 90 else reply[:87]+"..."
        self._show_bubble(short, 6000)
        self.chat_win.add_bot(reply)
        self.cat.set_mood(mood)

        # XP уведомление + level-up notification
        if self._pending_events:
            ev = " · ".join(self._pending_events)
            self._pending_events = []
            # Проверяем повышение уровня
            level_info = self.progress.level_info
            for e in (self._pending_events or []):
                pass
            self.root.after(7000, lambda: self._show_bubble(f"✨ {ev}", 2500))

        self.root.after(6500, lambda: self.cat.set_mood("idle"))
        self._apply_skin()
        self.profile_win.refresh()
        self.coop.set_status(reply[:80], mood, self.progress.level_info['level'])

    # ── Проактивные сообщения ─────────────────────────────

    def _on_proactive(self, text: str, mood: str):
        self.root.after(0, lambda: self._show_proactive(text, mood))

    def _show_proactive(self, text: str, mood: str):
        if self._typing: return
        short = text if len(text) <= 90 else text[:87]+"..."
        self._show_bubble(short, 6000)
        self.chat_win.add_bot(text)
        self.history.add("assistant", text)
        self.cat.set_mood(mood)
        self.root.after(6500, lambda: self.cat.set_mood("idle"))

    # ── Настроение ────────────────────────────────────────

    def _on_mood_log(self, result: str):
        self._show_bubble(result, 4000)
        self.progress.save()

    # ── Пузырь ────────────────────────────────────────────

    def _show_bubble(self, text: str, duration: int = 5000):
        self.bubble.show(text, self._x, self._y, duration)

    # ── Старт ─────────────────────────────────────────────

    def _apply_skin(self):
        """Применяем текущий скин кота — с учётом сезона."""
        base_skin = self.progress.skin
        active_skin = get_seasonal_skin(base_skin)
        self.cat.set_skin(active_skin)

    def _start_services(self):
        self.watcher.start()
        self.proactive.start()
        self.notif.start()
        self.productivity.start()
        # Проверяем отчёт через 30 сек после запуска
        self.root.after(30000, self._check_weekly_report)
        # Запускаем проверку реакций каждые 5 минут
        self._schedule_reaction_check()
        # Mood Pet — обновляем каждые 10 минут
        self._update_mood_pet()
        # Coop
        self.coop.start()
        # Предлагаем мини-игру раз в день через 2 мин после запуска
        self.root.after(120000, self._maybe_offer_game)
        # Сезонное приветствие через 3 сек
        greeting = get_seasonal_greeting()
        if greeting:
            self.root.after(3000, lambda: self._show_proactive(greeting, "excited"))
        banner = get_seasonal_banner()
        if banner:
            print(f"  🎉 {banner}")

    def _schedule_reaction_check(self):
        self._check_app_reaction()
        self.root.after(5 * 60 * 1000, self._schedule_reaction_check)

    def _welcome(self):
        self.cat.set_mood("happy")
        mode = f"AI: {self.ai.model_name}" if self.ai.ollama_available else _t("smart_mode")
        self.chat_win.add_sys(mode)
        self.chat_win.add_bot(_t("greeting_chat"))
        self.root.after(800, lambda: self._show_bubble(
            _t("greeting_bub"), 5000))
        self.root.after(5500, lambda: self.cat.set_mood("idle"))

    # ── Еженедельный отчёт ───────────────────────────────
    def _show_weekly_report(self):
        def on_done(text, data):
            # Добавляем mood_stats в data
            data["mood_stats"] = self.progress.get_mood_stats()
            self.root.after(0, lambda: self.report_win.show_report(
                text, data, self._x, self._y))
        self._show_bubble(_t("report_bub"), 4000)
        self.report_sys.force_generate(on_done)

    def _check_app_reaction(self):
        """Проверяем нужна ли реакция на текущее приложение."""
        import time
        title = self.watcher.last_window
        proc  = getattr(self.watcher, '_last_proc', '')

        # Не реагируем если только что говорили об этом же приложении
        if title == self._last_reaction_app:
            return

        session_min = int((time.time() - self._session_start) / 60)
        hour = __import__('datetime').datetime.now().hour

        reaction = get_app_reaction(title, proc, hour, session_min)
        if reaction:
            text, mood = reaction
            self._last_reaction_app = title
            # Показываем через случайную задержку 10-30 сек
            delay = __import__('random').randint(10000, 30000)
            self.root.after(delay, lambda: self._show_proactive(text, mood))

    def _check_weekly_report(self):
        """Проверяем нужно ли показать отчёт (каждое воскресенье)."""
        if self.report_sys.should_generate():
            self._show_weekly_report()
        # Проверяем снова через 6 часов
        self.root.after(6 * 3600 * 1000, self._check_weekly_report)

    # ── Mood Pet ──────────────────────────────────────────
    def _update_mood_pet(self):
        state = get_mood_pet_state(self.progress)
        self.cat.set_mood_pet(state)
        # Если состояние поменялось заметно — кот говорит об этом
        if hasattr(self, '_last_pet_state'):
            old = self._last_pet_state.get("state","")
            new = state["state"]
            if old != new and new in ("glowing","depressed"):
                msg = get_mood_pet_message(new)
                self.root.after(3000, lambda: self._show_proactive(msg,
                    "excited" if new=="glowing" else "sad"))
        self._last_pet_state = state
        self.root.after(10 * 60 * 1000, self._update_mood_pet)

    # ── Panic reaction (дедлайн) ──────────────────────────
    def _check_deadline_panic(self, text: str):
        """Кот паникует если видит слово дедлайн на экране."""
        panic_words = ["дедлайн","deadline","сдать до","сдать сегодня",
                       "due today","due tomorrow","срочно","asap"]
        screen = (self.watcher.last_context or "").lower()
        if any(w in screen for w in panic_words) or any(w in text.lower() for w in panic_words):
            self.cat.set_mood("excited")
            self._show_bubble(_t("deadline_bub"), 5000)

    # ── Coop ──────────────────────────────────────────────
    def _on_peer_cat(self, name: str, message: str, mood: str):
        """Другой кот появился в сети."""
        self.root.after(0, lambda: self._show_bubble(
            f"🐱🐱 {name} {_t('coop_online')}! {message[:50]}", 6000))
        self.chat_win.add_sys(f"🐱 {name} {_t('coop_sys')}!")

    # ── Мини-игра ─────────────────────────────────────────
    def _open_minigame(self):
        if not self.game_win.visible:
            self.game_win.show(self._x, self._y)

    def _maybe_offer_game(self):
        """Раз в день предлагаем мини-игру."""
        import datetime as _dt
        today = _dt.date.today()
        if self._last_game_date != today:
            self._show_bubble(_t("game_invite"), 6000)
            self.cat.set_mood("excited")
            self.root.after(3000, lambda: self.cat.set_mood("idle"))

    def _on_game_reward(self, xp: int, msg: str):
        """Награда за мини-игру."""
        for _ in range(xp // 5):
            self.progress.add_xp("message_sent")
        self._show_bubble(f"🎮 {msg}", 4000)
        self._last_game_date = __import__('datetime').date.today()
        self.profile_win.refresh()

    # ── Новые переключатели v9 ────────────────────────────

    def _toggle_productivity(self):
        if self.productivity_win.visible:
            self.productivity_win.close()
        else:
            self.productivity_win.show(self._x, self._y)

    def _toggle_diary(self):
        if self.diary_win.visible:
            self.diary_win.close()
        else:
            self.diary_win.show(self._x, self._y)

    def _toggle_prestige(self):
        if self.prestige_win.visible:
            self.prestige_win.close()
        else:
            self.prestige_win.show(self._x, self._y)

    def _share_card(self):
        open_share_dialog(self.progress, parent_window=self.win)

    def _on_prestige_msg(self, msg: str):
        self._show_bubble(msg, 7000)
        self.chat_win.add_bot(msg)
        self.cat.set_mood("excited")
        self.root.after(7500, lambda: self.cat.set_mood("idle"))

    # ── Выход ─────────────────────────────────────────────

    def _quit(self):
        self.cat.stop()
        self.watcher.stop()
        self.proactive.stop()
        self.notif.stop()
        self.productivity.stop()
        self.progress.save()
        self.coop.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
