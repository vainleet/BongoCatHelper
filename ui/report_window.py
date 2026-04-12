"""
ui/report_window.py
Красивое окно еженедельного отчёта — идеально для скриншота/TikTok.
"""
import tkinter as tk
from datetime import date
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BG      = "#0e0e14"
BG2     = "#161622"
BG3     = "#1e1e2e"
PURPLE  = "#9b7fff"
PURPLE2 = "#7b5fff"
TEAL    = "#2dd4bf"
AMBER   = "#fbbf24"
GREEN   = "#34d399"
RED     = "#f87171"
TEXT    = "#e2e0f0"
TEXT2   = "#9090b8"
TEXT3   = "#4a4a6a"

MOOD_E = ["", "😢","😔","😐","😊","😄"]
MOOD_C = ["", "#f87171","#fb923c","#fbbf24","#86efac","#34d399"]


class ReportWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._visible = False

    def show_report(self, report_text: str, data: dict, cat_x: int, cat_y: int):
        """Показать красивый отчёт."""
        for w in self.winfo_children():
            w.destroy()

        W, H = 380, 520

        # Рамка
        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(outer, bg=BG)
        inner.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        hdr = tk.Frame(inner, bg=BG2, padx=16, pady=12)
        hdr.pack(fill=tk.X)

        left = tk.Frame(hdr, bg=BG2)
        left.pack(side=tk.LEFT)
        tk.Label(left, text="📋  Отчёт недели",
                 bg=BG2, fg=PURPLE,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        week = date.today().strftime("%d.%m.%Y")
        tk.Label(left, text=f"Составлен {week}",
                 bg=BG2, fg=TEXT3,
                 font=("Segoe UI", 8)).pack(anchor="w")

        cl = tk.Label(hdr, text=" ✕ ", bg=BG2, fg=TEXT3,
                      font=("Segoe UI", 12), cursor="hand2")
        cl.pack(side=tk.RIGHT)
        cl.bind("<Enter>",    lambda e: cl.config(fg=RED, bg=BG3))
        cl.bind("<Leave>",    lambda e: cl.config(fg=TEXT3, bg=BG2))
        cl.bind("<Button-1>", lambda e: self.close())

        hdr.bind("<ButtonPress-1>", self._ds)
        hdr.bind("<B1-Motion>",     self._dm)

        # Кот
        cat_frame = tk.Frame(inner, bg=BG3, pady=10)
        cat_frame.pack(fill=tk.X, padx=12, pady=(8,0))
        tk.Label(cat_frame, text="🐱", bg=BG3,
                 font=("Segoe UI Emoji", 36)).pack()
        tk.Label(cat_frame, text=f"Ур. {data.get('level',0)} · {data.get('level_title','')}",
                 bg=BG3, fg=PURPLE,
                 font=("Segoe UI", 9, "bold")).pack()

        # Статы в ряд
        stats = tk.Frame(inner, bg=BG)
        stats.pack(fill=tk.X, padx=12, pady=8)
        stats.columnconfigure((0,1,2,3), weight=1)

        mood_avg = data.get("mood_avg", 0)
        mood_e   = MOOD_E[round(mood_avg)] if mood_avg else "—"
        mood_c   = MOOD_C[round(mood_avg)] if mood_avg else TEXT3

        for col, (val, lbl, col_) in enumerate([
            (str(data.get("messages",0)),  "сообщений",  TEAL),
            (f"{data.get('streak',0)}🔥",  "streak",     AMBER),
            (f"{mood_e}",                  "настроение", mood_c),
            (f"+{data.get('xp_gained',0)}","XP",         PURPLE),
        ]):
            card = tk.Frame(stats, bg=BG3, padx=4, pady=8)
            card.grid(row=0, column=col, padx=2, sticky="ew")
            tk.Label(card, text=val, bg=BG3, fg=col_,
                     font=("Segoe UI", 14, "bold")).pack()
            tk.Label(card, text=lbl, bg=BG3, fg=TEXT3,
                     font=("Segoe UI", 7)).pack()

        # Текст отчёта
        tk.Frame(inner, bg=PURPLE2, height=1).pack(fill=tk.X, padx=12, pady=(4,8))

        text_frame = tk.Frame(inner, bg=BG2, padx=14, pady=12)
        text_frame.pack(fill=tk.X, padx=12)

        # Рендерим текст с эмодзи
        txt = tk.Text(text_frame, bg=BG2, fg=TEXT,
                      font=("Segoe UI", 10),
                      relief=tk.FLAT, bd=0,
                      wrap=tk.WORD, height=8,
                      cursor="arrow",
                      state=tk.NORMAL)
        txt.pack(fill=tk.BOTH)
        txt.insert("1.0", report_text)
        txt.config(state=tk.DISABLED)

        # График настроения
        tk.Label(inner, text="  Настроение за неделю:",
                 bg=BG, fg=TEXT3,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(8,2))
        self._draw_chart(inner, data.get("mood_stats", []))

        # Кнопки
        btn_row = tk.Frame(inner, bg=BG)
        btn_row.pack(fill=tk.X, padx=12, pady=8)

        share_btn = tk.Label(btn_row,
                             text="  📸  Скопировать для поста  ",
                             bg=PURPLE2, fg="#fff",
                             font=("Segoe UI", 10, "bold"),
                             pady=8, cursor="hand2")
        share_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,4))
        share_btn.bind("<Button-1>", lambda e: self._copy_report(report_text, data))
        share_btn.bind("<Enter>", lambda e: share_btn.config(bg=PURPLE))
        share_btn.bind("<Leave>", lambda e: share_btn.config(bg=PURPLE2))

        close_btn = tk.Label(btn_row, text="  Закрыть  ",
                             bg=BG3, fg=TEXT2,
                             font=("Segoe UI", 10),
                             pady=8, cursor="hand2")
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.close())

        # Позиция
        sw = self.winfo_screenwidth()
        x = max(4, cat_x - W - 10)
        if x + W > sw: x = cat_x + 175
        y = max(4, cat_y - H + 160)
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.deiconify()
        self._visible = True

    def _draw_chart(self, parent, mood_stats):
        if not mood_stats:
            return
        cv = tk.Canvas(parent, bg=BG, height=60, highlightthickness=0)
        cv.pack(fill=tk.X, padx=12, pady=(0,4))
        cv.update_idletasks()
        W  = cv.winfo_reqwidth() or 340
        cw = W // 7
        day_names = {"Mon":"Пн","Tue":"Вт","Wed":"Ср","Thu":"Чт",
                     "Fri":"Пт","Sat":"Сб","Sun":"Вс"}
        for i, day in enumerate(mood_stats):
            x   = i*cw + cw//2
            lbl = day_names.get(day.get("label",""), day.get("label",""))
            cv.create_text(x, 55, text=lbl, fill=TEXT3, font=("Segoe UI",7))
            m = day.get("mood")
            if m is not None:
                h   = max(3, int((m/5)*38))
                col = MOOD_C[round(m)] if 1<=round(m)<=5 else TEXT3
                cv.create_rectangle(x-9,48-h, x+9,48, fill=col, outline="")
                cv.create_text(x, 43-h, text=MOOD_E[round(m)],
                               font=("Segoe UI Emoji",8))
            else:
                cv.create_rectangle(x-9,44, x+9,48, fill=BG3, outline="")

    def _copy_report(self, report_text: str, data: dict):
        """Копирует красивый текст для поста."""
        mood_avg = data.get("mood_avg", 0)
        mood_e   = MOOD_E[round(mood_avg)] if mood_avg else ""

        post = (
            f"🐱 Мой Bongo Cat составил отчёт за неделю:\n\n"
            f"{report_text}\n\n"
            f"📊 Статистика:\n"
            f"💬 Сообщений: {data.get('messages',0)}\n"
            f"🔥 Streak: {data.get('streak',0)} дней\n"
            f"✨ XP: +{data.get('xp_gained',0)}\n"
            f"{mood_e} Настроение: {mood_avg}/5\n\n"
            f"#BongoCatAI #МойПитомец #ПсихологическаяПоддержка"
        )
        try:
            self.clipboard_clear()
            self.clipboard_append(post)
            self._flash("✅ Скопировано! Вставь в TikTok/Twitter")
        except Exception:
            pass

    def _flash(self, msg: str):
        pop = tk.Toplevel(self)
        pop.overrideredirect(True)
        pop.wm_attributes("-topmost", True)
        pop.configure(bg=GREEN)
        tk.Label(pop, text=msg, bg=GREEN, fg="#000",
                 font=("Segoe UI", 10, "bold"), padx=14, pady=8).pack()
        pop.geometry(f"+{self.winfo_x()+20}+{self.winfo_y()+20}")
        self.after(2500, pop.destroy)

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
