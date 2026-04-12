"""
ui/diary_window.py
Окно личного дневника. Записи хранятся локально в progress.json.
"""

import tkinter as tk
from datetime import datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BG     = "#0e0e14"
BG2    = "#161622"
BG3    = "#1e1e2e"
PURPLE = "#9b7fff"
PURPLE2= "#7b5fff"
GREEN  = "#34d399"
RED    = "#f87171"
TEXT   = "#e2e0f0"
TEXT2  = "#9090b8"
TEXT3  = "#4a4a6a"


class DiaryWindow(tk.Toplevel):
    def __init__(self, parent, progress_system, ai_callback=None):
        super().__init__(parent)
        self._p  = progress_system
        self._ai = ai_callback   # опционально: функция(text) → строка-ответ кота
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._visible = False
        self._drag_x = self._drag_y = 0

    def show(self, cat_x: int, cat_y: int):
        W, H = 400, 500
        sw   = self.winfo_screenwidth()
        sh   = self.winfo_screenheight()
        x    = max(4, min(cat_x - W - 10, sw - W - 4))
        y    = max(4, min(cat_y - H // 2, sh - H - 40))
        self.geometry(f"{W}x{H}+{x}+{y}")
        self._build()
        self.deiconify()
        self._visible = True
        self._input.focus_set()

    def _build(self):
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
        tk.Label(hdr, text="📓  Дневник",
                 bg=BG2, fg=PURPLE,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=12)
        count_lbl = tk.Label(hdr, text=f"{self._p.diary_count} записей",
                             bg=BG2, fg=TEXT3,
                             font=("Segoe UI", 9))
        count_lbl.pack(side=tk.LEFT, padx=4)
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
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # ── Поле ввода ────────────────────────────────────
        tk.Label(body, text="Как прошёл день?",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(anchor="w")

        self._input = tk.Text(body, height=5,
                               bg=BG3, fg=TEXT,
                               font=("Segoe UI", 10),
                               relief="flat",
                               padx=8, pady=6,
                               wrap=tk.WORD,
                               insertbackground=PURPLE)
        self._input.pack(fill=tk.X, pady=(4, 0))
        self._input.bind("<Control-Return>", lambda e: self._save())

        # Кнопка сохранить
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill=tk.X, pady=(6, 0))
        self._status_lbl = tk.Label(btn_row, text="Ctrl+Enter — сохранить",
                                     bg=BG, fg=TEXT3,
                                     font=("Segoe UI", 8))
        self._status_lbl.pack(side=tk.LEFT)
        save_btn = tk.Label(btn_row, text=" Сохранить 📓 ",
                             bg=PURPLE2, fg="#fff",
                             font=("Segoe UI", 9, "bold"),
                             pady=5, padx=8)
        save_btn.pack(side=tk.RIGHT)
        save_btn.bind("<Button-1>", lambda e: self._save())
        save_btn.bind("<Enter>",    lambda e: save_btn.config(bg=PURPLE))
        save_btn.bind("<Leave>",    lambda e: save_btn.config(bg=PURPLE2))

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=8)

        # ── Прошлые записи ───────────────────────────────
        tk.Label(body, text="Последние записи",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        scroll_frame = tk.Frame(body, bg=BG)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(scroll_frame, bg=BG2, troughcolor=BG3,
                                  activebackground=PURPLE2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._entries_box = tk.Text(scroll_frame,
                                     bg=BG3, fg=TEXT,
                                     font=("Segoe UI", 9),
                                     relief="flat",
                                     padx=8, pady=6,
                                     wrap=tk.WORD,
                                     state=tk.DISABLED,
                                     yscrollcommand=scrollbar.set)
        self._entries_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._entries_box.yview)

        self._refresh_entries()

    def _save(self):
        text = self._input.get("1.0", tk.END).strip()
        if not text:
            return
        result = self._p.add_diary_entry(text)
        self._input.delete("1.0", tk.END)
        self._status_lbl.config(text=f"✅ {result}", fg=GREEN)
        self.after(3000, lambda: self._status_lbl.config(
            text="Ctrl+Enter — сохранить", fg=TEXT3))
        self._refresh_entries()

        # Реакция кота (если есть AI)
        if self._ai:
            short = text[:100]
            self._ai(f"[Запись в дневнике] {short}")

    def _refresh_entries(self):
        entries = self._p.get_diary(last_n=20)
        box = self._entries_box
        box.config(state=tk.NORMAL)
        box.delete("1.0", tk.END)
        if not entries:
            box.insert(tk.END, "Пока нет записей. Начни сегодня! 🐱")
        else:
            for e in entries:
                dt  = e.get("ts", e.get("date", ""))[:16].replace("T", " ")
                txt = e.get("text", "")
                box.insert(tk.END, f"  {dt}\n", "date")
                box.insert(tk.END, f"  {txt}\n\n", "text")
        box.tag_config("date", foreground=TEXT3, font=("Segoe UI", 8))
        box.tag_config("text", foreground=TEXT,  font=("Segoe UI", 9))
        box.config(state=tk.DISABLED)
        box.see("1.0")

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
