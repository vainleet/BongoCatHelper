"""
ui/productivity_window.py
Окно дашборда продуктивности — показывает время по приложениям за неделю.
Открывается из главного окна, никакого интернета.
"""

import tkinter as tk
from tkinter import ttk
import math
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BG      = "#0e0e14"
BG2     = "#161622"
BG3     = "#1e1e2e"
PURPLE  = "#9b7fff"
PURPLE2 = "#7b5fff"
GREEN   = "#34d399"
AMBER   = "#fbbf24"
RED     = "#f87171"
BLUE    = "#60a5fa"
PINK    = "#f472b6"
GRAY    = "#6b7280"
TEXT    = "#e2e0f0"
TEXT2   = "#9090b8"
TEXT3   = "#4a4a6a"

CATEGORY_COLORS = {
    "code":    PURPLE,
    "browser": BLUE,
    "media":   PINK,
    "docs":    GREEN,
    "game":    AMBER,
    "social":  RED,
    "other":   GRAY,
}
CATEGORY_LABELS = {
    "code":    "Код",
    "browser": "Браузер",
    "media":   "Медиа",
    "docs":    "Документы",
    "game":    "Игры",
    "social":  "Соцсети",
    "other":   "Остальное",
}


class ProductivityWindow(tk.Toplevel):
    def __init__(self, parent, productivity_tracker):
        super().__init__(parent)
        self._pt = productivity_tracker
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._visible = False
        self._drag_x = self._drag_y = 0

    def show(self, cat_x: int, cat_y: int):
        W, H = 460, 480
        sw   = self.winfo_screenwidth()
        sh   = self.winfo_screenheight()
        x    = max(4, min(cat_x - W - 10, sw - W - 4))
        y    = max(4, min(cat_y - H // 2, sh - H - 40))
        self.geometry(f"{W}x{H}+{x}+{y}")
        self._build(W, H)
        self.deiconify()
        self._visible = True

    def _build(self, W, H):
        for w in self.winfo_children():
            w.destroy()

        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)
        wrap = tk.Frame(outer, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True)

        # ── Header ────────────────────────────────────────
        hdr = tk.Frame(wrap, bg=BG2, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📊  Продуктивность",
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

        body = tk.Frame(wrap, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # ── Сегодня ───────────────────────────────────────
        tk.Label(body, text="Сегодня", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        today = self._pt.get_today()
        total_today = sum(today.values())
        total_str = self._pt.format_duration(total_today) if total_today else "—"

        tk.Label(body, text=total_str, bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(body, text="за компьютером", bg=BG, fg=TEXT3,
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=8)

        # ── Полоски категорий (сегодня) ───────────────────
        if today and total_today > 0:
            sorted_cats = sorted(today.items(), key=lambda x: x[1], reverse=True)
            for cat, secs in sorted_cats[:5]:
                color = CATEGORY_COLORS.get(cat, GRAY)
                label = CATEGORY_LABELS.get(cat, cat)
                pct   = secs / total_today
                row   = tk.Frame(body, bg=BG)
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text=label, bg=BG, fg=TEXT2,
                         font=("Segoe UI", 9), width=11,
                         anchor="w").pack(side=tk.LEFT)
                bar_frame = tk.Frame(row, bg=BG3, height=12)
                bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4,6))
                bar_frame.pack_propagate(False)
                bar_frame.update_idletasks()
                bar_w = bar_frame.winfo_width()
                fill_w = max(4, int(bar_w * pct))
                tk.Frame(bar_frame, bg=color, width=fill_w,
                         height=12).place(x=0, y=0)
                tk.Label(row, text=self._pt.format_duration(secs),
                         bg=BG, fg=TEXT3,
                         font=("Segoe UI", 9), width=8,
                         anchor="e").pack(side=tk.RIGHT)
        else:
            tk.Label(body, text="Ещё нет данных сегодня 🐱",
                     bg=BG, fg=TEXT3, font=("Segoe UI", 10)).pack(pady=8)

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=8)

        # ── График за 7 дней ─────────────────────────────
        tk.Label(body, text="7 дней", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))

        cv = tk.Canvas(body, bg=BG3, height=110,
                       highlightthickness=0)
        cv.pack(fill=tk.X)
        cv.update_idletasks()
        cv_w = cv.winfo_width() or 420
        cv_h = 110

        daily = self._pt.get_daily_totals(7)
        max_total = max((d["total"] for d in daily), default=1) or 1
        bar_area_w = cv_w - 20
        bar_w_each = bar_area_w // 7
        bar_max_h  = cv_h - 28

        for i, d in enumerate(daily):
            bx   = 10 + i * bar_w_each + 4
            bw   = bar_w_each - 8
            tot  = d["total"]
            by_cat = d["by_cat"]

            if tot > 0:
                # Стек категорий
                y_bottom = cv_h - 18
                sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
                for cat, secs in sorted_cats:
                    seg_h = max(2, int(bar_max_h * secs / max_total))
                    color = CATEGORY_COLORS.get(cat, GRAY)
                    cv.create_rectangle(bx, y_bottom - seg_h, bx + bw, y_bottom,
                                        fill=color, outline="")
                    y_bottom -= seg_h
            else:
                cv.create_rectangle(bx, cv_h - 20, bx + bw, cv_h - 18,
                                    fill=TEXT3, outline="")

            cv.create_text(bx + bw // 2, cv_h - 8,
                           text=d["label"][:2],
                           fill=TEXT3,
                           font=("Segoe UI", 8))

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=8)

        # ── Легенда ───────────────────────────────────────
        legend_frame = tk.Frame(body, bg=BG)
        legend_frame.pack(fill=tk.X)
        items = list(CATEGORY_COLORS.items())
        cols  = 3
        for idx, (cat, color) in enumerate(items):
            row_f = legend_frame
            if idx % cols == 0:
                row_f = tk.Frame(legend_frame, bg=BG)
                row_f.pack(fill=tk.X, pady=1)
            cell = tk.Frame(row_f, bg=BG)
            cell.pack(side=tk.LEFT, padx=(0, 12))
            dot = tk.Canvas(cell, width=8, height=8, bg=BG,
                            highlightthickness=0)
            dot.pack(side=tk.LEFT)
            dot.create_oval(0, 0, 8, 8, fill=color, outline="")
            tk.Label(cell, text=CATEGORY_LABELS.get(cat, cat),
                     bg=BG, fg=TEXT3,
                     font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)

        # ── Кнопка обновить ───────────────────────────────
        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=(8, 4))
        btn = tk.Label(body, text=" ↻ Обновить ",
                       bg=BG3, fg=TEXT2,
                       font=("Segoe UI", 9),
                       pady=4)
        btn.pack()
        btn.bind("<Button-1>", lambda e: self.show(
            self.winfo_x() + self.winfo_width(),
            self.winfo_y() + self.winfo_height() // 2
        ))
        btn.bind("<Enter>", lambda e: btn.config(bg="#2d2d45"))
        btn.bind("<Leave>", lambda e: btn.config(bg=BG3))

    def _ds(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _dm(self, e):
        self.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def close(self):
        self.withdraw()
        self._visible = False

    @property
    def visible(self):
        return self._visible
