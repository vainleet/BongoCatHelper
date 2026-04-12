"""
core/minigame.py
Мини-игры — раз в день кот предлагает быструю игру за XP.
"""
import tkinter as tk
import random
import time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BG      = "#0e0e14"
BG2     = "#161622"
BG3     = "#1e1e2e"
PURPLE  = "#9b7fff"
PURPLE2 = "#7b5fff"
GREEN   = "#34d399"
RED     = "#f87171"
AMBER   = "#fbbf24"
TEAL    = "#2dd4bf"
TEXT    = "#e2e0f0"
TEXT2   = "#9090b8"
TEXT3   = "#4a4a6a"


class MiniGameWindow(tk.Toplevel):
    """Окно мини-игры — появляется раз в день."""

    GAMES = ["catch_mouse", "mood_guess", "reaction", "word_cat"]

    def __init__(self, parent, on_reward):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._on_reward = on_reward  # callback(xp: int, msg: str)
        self._visible   = False
        self._game      = None

    def show(self, cat_x: int, cat_y: int):
        for w in self.winfo_children():
            w.destroy()
        self._game = random.choice(self.GAMES)
        W, H = 320, 340
        sw = self.winfo_screenwidth()
        x  = max(4, cat_x - W - 10)
        if x + W > sw: x = cat_x + 175
        y  = max(4, cat_y - H + 160)
        self.geometry(f"{W}x{H}+{x}+{y}")

        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)
        wrap = tk.Frame(outer, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(wrap, bg=BG2, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🎮  Мини-игра дня!",
                 bg=BG2, fg=PURPLE,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=12)
        cl = tk.Label(hdr, text=" ✕ ", bg=BG2, fg=TEXT3,
                      font=("Segoe UI", 11))
        cl.pack(side=tk.RIGHT, padx=6)
        cl.bind("<Button-1>", lambda e: self.close())
        cl.bind("<Enter>",    lambda e: cl.config(fg=RED, bg=BG3))
        cl.bind("<Leave>",    lambda e: cl.config(fg=TEXT3, bg=BG2))

        hdr.bind("<ButtonPress-1>", self._ds)
        hdr.bind("<B1-Motion>",     self._dm)

        tk.Frame(wrap, bg="#2d2d45", height=1).pack(fill=tk.X)

        self._body = tk.Frame(wrap, bg=BG)
        self._body.pack(fill=tk.BOTH, expand=True)

        {"catch_mouse":  self._game_catch_mouse,
         "mood_guess":   self._game_mood_guess,
         "reaction":     self._game_reaction,
         "word_cat":      self._game_word_cat}[self._game]()

        self.deiconify()
        self._visible = True

    # ── Игра 1: Поймай мышку ─────────────────────────────

    def _game_catch_mouse(self):
        f = self._body
        tk.Label(f, text="🐭  Поймай мышку!",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16,4))
        tk.Label(f, text="Кликни на мышку 5 раз за 10 секунд",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack()

        self._catch_count = 0
        self._catch_start = time.time()

        cv = tk.Canvas(f, width=280, height=160,
                        bg=BG3, highlightthickness=0)
        cv.pack(padx=20, pady=12)

        self._catch_cv    = cv
        self._catch_mouse = None
        self._catch_timer = None
        self._time_lbl    = tk.Label(f, text="⏱ 10с", bg=BG, fg=AMBER,
                                      font=("Segoe UI", 11, "bold"))
        self._time_lbl.pack()
        self._score_lbl   = tk.Label(f, text="🐭 0 / 5", bg=BG, fg=TEXT,
                                      font=("Segoe UI", 11))
        self._score_lbl.pack()

        self._spawn_mouse()
        self._catch_tick()

    def _spawn_mouse(self):
        cv = self._catch_cv
        if self._catch_mouse:
            cv.delete(self._catch_mouse)
        x = random.randint(20, 260)
        y = random.randint(10, 150)
        self._catch_mouse = cv.create_text(x, y, text="🐭",
                                            font=("Segoe UI Emoji", 20))
        cv.tag_bind(self._catch_mouse, "<Button-1>", self._on_catch)

    def _on_catch(self, e):
        self._catch_count += 1
        self._score_lbl.config(text=f"🐭 {self._catch_count} / 5")
        if self._catch_count >= 5:
            self._end_catch(True)
        else:
            self._spawn_mouse()

    def _catch_tick(self):
        elapsed = time.time() - self._catch_start
        remaining = max(0, 10 - int(elapsed))
        self._time_lbl.config(text=f"⏱ {remaining}с")
        if remaining <= 0:
            self._end_catch(False)
        else:
            self._catch_timer = self.after(200, self._catch_tick)

    def _end_catch(self, won: bool):
        if self._catch_timer:
            self.after_cancel(self._catch_timer)
        xp  = 30 if won else 10
        msg = "🎉 Поймал(а)! +30 XP" if won else f"😅 Поймал {self._catch_count}/5. +10 XP"
        self._show_result(msg, xp)

    # ── Игра 2: Угадай настроение ─────────────────────────

    def _game_mood_guess(self):
        f = self._body
        tk.Label(f, text="💜  Угадай настроение!",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16,4))

        situations = [
            ("Получил пятёрку на экзамене 🎓",        "😄"),
            ("Опоздал на автобус под дождём ☔",       "😔"),
            ("Нашёл деньги в старой куртке 💸",        "😊"),
            ("Пролил кофе на клавиатуру ☕",            "😢"),
            ("Неожиданный выходной! 🎉",               "😄"),
            ("Дедлайн через час, а ничего не готово 😱", "😢"),
            ("Обычный вторник, ничего особенного",     "😐"),
            ("Любимая песня в наушниках 🎵",           "😊"),
        ]
        sit_text, correct = random.choice(situations)

        tk.Label(f, text=sit_text,
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 10),
                 wraplength=260).pack(padx=20, pady=(8,12))
        tk.Label(f, text="Какое это настроение?",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack()

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(pady=12)
        for em in ["😢","😔","😐","😊","😄"]:
            b = tk.Label(btn_row, text=em, bg=BG3,
                          font=("Segoe UI Emoji", 22),
                          padx=8, pady=6)
            b.pack(side=tk.LEFT, padx=4)
            b.bind("<Enter>",    lambda e, lb=b: lb.config(bg="#2d2d45"))
            b.bind("<Leave>",    lambda e, lb=b: lb.config(bg=BG3))
            b.bind("<Button-1>", lambda e, ans=em, c=correct: self._check_mood(ans, c))

    def _check_mood(self, answer: str, correct: str):
        if answer == correct:
            self._show_result("✅ Правильно! +25 XP", 25)
        else:
            self._show_result(f"❌ Нет, это было {correct}. +5 XP", 5)

    # ── Игра 3: Реакция ───────────────────────────────────

    def _game_reaction(self):
        f = self._body
        tk.Label(f, text="⚡  Тест реакции!",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16,4))
        tk.Label(f, text="Нажми как только увидишь кота!",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack()

        self._react_state = "waiting"
        self._react_start = 0

        self._react_cv = tk.Canvas(f, width=280, height=120,
                                    bg=BG3, highlightthickness=0)
        self._react_cv.pack(padx=20, pady=16)

        self._react_lbl = tk.Label(f, text="Жди...",
                                    bg=BG, fg=TEXT2,
                                    font=("Segoe UI", 11))
        self._react_lbl.pack()

        self._react_cv.bind("<Button-1>", self._on_react_click)

        # Показываем "жди" и через случайное время — кота
        delay = random.randint(1500, 4000)
        self.after(delay, self._show_react_cat)

    def _show_react_cat(self):
        cv = self._react_cv
        cv.delete("all")
        cv.create_text(140, 60, text="🐱",
                        font=("Segoe UI Emoji", 44))
        self._react_state = "ready"
        self._react_start = time.time()
        self._react_lbl.config(text="ЖМИИ! ⚡", fg=GREEN)

    def _on_react_click(self, e):
        if self._react_state == "waiting":
            self._show_result("😅 Слишком рано! +5 XP", 5)
        elif self._react_state == "ready":
            ms = int((time.time() - self._react_start) * 1000)
            if ms < 300:
                self._show_result(f"🚀 {ms}мс — молния! +40 XP", 40)
            elif ms < 600:
                self._show_result(f"⚡ {ms}мс — отлично! +30 XP", 30)
            elif ms < 1000:
                self._show_result(f"👍 {ms}мс — неплохо! +20 XP", 20)
            else:
                self._show_result(f"🐢 {ms}мс — медленновато. +10 XP", 10)

    # ── Результат ─────────────────────────────────────────

    def _show_result(self, msg: str, xp: int):
        for w in self._body.winfo_children():
            w.destroy()

        col = GREEN if "+" in msg and int(''.join(filter(str.isdigit, msg.split('+')[1][:3]))) >= 20 else AMBER
        tk.Label(self._body, text=msg,
                 bg=BG, fg=col,
                 font=("Segoe UI", 13, "bold"),
                 wraplength=260).pack(pady=(40,12))

        tk.Label(self._body, text="🐱 Хорошая работа!",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 10)).pack()

        close = tk.Label(self._body,
                          text="  Забрать награду  ",
                          bg=PURPLE2, fg="#fff",
                          font=("Segoe UI", 11, "bold"),
                          pady=8)
        close.pack(pady=20)
        close.bind("<Button-1>", lambda e: self._claim(xp, msg))
        close.bind("<Enter>",    lambda e: close.config(bg=PURPLE))
        close.bind("<Leave>",    lambda e: close.config(bg=PURPLE2))

    def _claim(self, xp: int, msg: str):
        self._on_reward(xp, msg)
        self.close()

    # ── Drag / close ──────────────────────────────────────

    def _ds(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()
    def _dm(self, e):
        self.geometry(f"+{e.x_root-self._dx}+{e.y_root-self._dy}")

    def close(self):
        self.withdraw()
        self._visible = False

    @property
    def visible(self): return self._visible

    # ── Игра 4: Слова кота (новая) ────────────────────────

    def _game_word_cat(self):
        """Угадай слово по подсказкам кота — как Wordle, но проще."""
        f = self._body
        WORDS = [
            ("кот",   "мяу, усы, лапы"),
            ("сон",   "ночь, подушка, тихо"),
            ("рыба",  "море, плавник, вода"),
            ("игра",  "веселье, очки, победа"),
            ("музыка","ноты, ритм, звук"),
            ("кофе",  "утро, чашка, тепло"),
            ("книга", "страницы, слова, чтение"),
            ("луна",  "ночь, свет, небо"),
        ]
        import random as _r
        word, hint = _r.choice(WORDS)
        self._wcat_word = word
        self._wcat_tries = 0

        tk.Label(f, text="🔤  Угадай слово кота!",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16, 4))
        tk.Label(f, text=f"Подсказка: {hint}",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 10),
                 wraplength=260).pack()
        tk.Label(f, text=f"({len(word)} букв)",
                 bg=BG, fg=TEXT3,
                 font=("Segoe UI", 9)).pack(pady=(0, 8))

        self._wcat_var = tk.StringVar()
        entry = tk.Entry(f, textvariable=self._wcat_var,
                         bg=BG3, fg=TEXT,
                         font=("Segoe UI", 13),
                         relief="flat",
                         insertbackground=PURPLE,
                         justify="center")
        entry.pack(padx=30, fill=tk.X, pady=4)
        entry.bind("<Return>", lambda e: self._check_word())
        entry.focus_set()

        self._wcat_lbl = tk.Label(f, text="Введи слово и нажми Enter",
                                   bg=BG, fg=TEXT3,
                                   font=("Segoe UI", 9))
        self._wcat_lbl.pack(pady=4)

        btn = tk.Label(f, text=" Проверить ",
                        bg=PURPLE2, fg="#fff",
                        font=("Segoe UI", 10),
                        pady=6)
        btn.pack(pady=8)
        btn.bind("<Button-1>", lambda e: self._check_word())
        btn.bind("<Enter>",    lambda e: btn.config(bg=PURPLE))
        btn.bind("<Leave>",    lambda e: btn.config(bg=PURPLE2))

    def _check_word(self):
        guess = self._wcat_var.get().strip().lower()
        self._wcat_tries += 1
        if guess == self._wcat_word:
            xp = max(10, 40 - (self._wcat_tries - 1) * 10)
            self._show_result(f"🎉 Правильно! «{self._wcat_word}» +{xp} XP", xp)
        elif self._wcat_tries >= 3:
            self._show_result(f"😔 Загадано: «{self._wcat_word}». +5 XP", 5)
        else:
            left = 3 - self._wcat_tries
            self._wcat_lbl.config(
                text=f"Не угадал. Осталось попыток: {left}",
                fg=RED
            )
            self._wcat_var.set("")
