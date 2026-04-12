"""
ui/prestige_window.py
Окно Prestige и еженедельных челленджей.
"""

import tkinter as tk
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BG     = "#0e0e14"
BG2    = "#161622"
BG3    = "#1e1e2e"
PURPLE = "#9b7fff"
PURPLE2= "#7b5fff"
GREEN  = "#34d399"
AMBER  = "#fbbf24"
RED    = "#f87171"
TEXT   = "#e2e0f0"
TEXT2  = "#9090b8"
TEXT3  = "#4a4a6a"


class PrestigeWindow(tk.Toplevel):
    def __init__(self, parent, progress_system, on_prestige_done=None):
        super().__init__(parent)
        self._p    = progress_system
        self._cb   = on_prestige_done
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()
        self._visible  = False
        self._drag_x = self._drag_y = 0

    def show(self, cat_x: int, cat_y: int):
        W, H = 380, 460
        sw   = self.winfo_screenwidth()
        sh   = self.winfo_screenheight()
        x    = max(4, min(cat_x - W - 10, sw - W - 4))
        y    = max(4, min(cat_y - H // 2, sh - H - 40))
        self.geometry(f"{W}x{H}+{x}+{y}")
        self._build()
        self.deiconify()
        self._visible = True

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
        tk.Label(hdr, text="⭐  Prestige & Челлендж",
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
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        # ── Prestige секция ───────────────────────────────
        prestige = self._p.prestige
        badge    = self._p.prestige_badge
        can      = self._p.can_prestige()
        level    = self._p.level_info["level"]
        max_lvl  = 7   # индекс последнего LEVELS

        tk.Label(body, text="Pertige — Перерождение",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        pframe = tk.Frame(body, bg=BG3)
        pframe.pack(fill=tk.X, pady=(4, 0))

        # Значок prestige
        star_text = badge if badge else "✦"
        tk.Label(pframe, text=star_text,
                 bg=BG3, fg=AMBER,
                 font=("Segoe UI", 26)).pack(side=tk.LEFT, padx=16, pady=10)

        pinfo = tk.Frame(pframe, bg=BG3)
        pinfo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        if prestige > 0:
            tk.Label(pinfo, text=f"Перерождений: {prestige}",
                     bg=BG3, fg=TEXT,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
        else:
            tk.Label(pinfo, text="Ещё не перерождался",
                     bg=BG3, fg=TEXT2,
                     font=("Segoe UI", 10)).pack(anchor="w")

        total_xp = self._p._data.get("prestige_total_xp", 0) + self._p.xp
        tk.Label(pinfo, text=f"Суммарный XP: {total_xp:,}",
                 bg=BG3, fg=TEXT3,
                 font=("Segoe UI", 9)).pack(anchor="w")

        if can:
            desc = "Достиг максимального уровня!\nXP сбросится, но ты получишь значок ★"
        else:
            desc = f"Достигни уровня {max_lvl} для перерождения\n(сейчас: уровень {level})"
        tk.Label(pinfo, text=desc,
                 bg=BG3, fg=TEXT3,
                 font=("Segoe UI", 8),
                 wraplength=200,
                 justify="left").pack(anchor="w", pady=(4,0))

        # Кнопка Prestige
        p_btn = tk.Label(body,
                          text="  ★ Переродиться  " if can else "  Уровень ещё не максимальный  ",
                          bg=PURPLE2 if can else BG3,
                          fg="#fff" if can else TEXT3,
                          font=("Segoe UI", 10, "bold"),
                          pady=7)
        p_btn.pack(fill=tk.X, pady=(8, 0))
        if can:
            p_btn.bind("<Button-1>", self._do_prestige)
            p_btn.bind("<Enter>",    lambda e: p_btn.config(bg=PURPLE))
            p_btn.bind("<Leave>",    lambda e: p_btn.config(bg=PURPLE2))

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=12)

        # ── Еженедельный челлендж ─────────────────────────
        tk.Label(body, text="Недельный челлендж",
                 bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        ch = self._p.weekly_challenge
        if ch:
            wframe = tk.Frame(body, bg=BG3)
            wframe.pack(fill=tk.X, pady=(4, 0))

            # Прогресс
            prog    = ch.get("progress", 0)
            target  = ch.get("target", 1)
            done    = ch.get("done", False)
            pct     = min(1.0, prog / target)
            xp_rew  = ch.get("xp", 100)

            title_color = GREEN if done else TEXT
            title_text  = f"✅ {ch['title']}" if done else ch["title"]

            header = tk.Frame(wframe, bg=BG3)
            header.pack(fill=tk.X, padx=12, pady=(10, 4))
            tk.Label(header, text=title_text,
                     bg=BG3, fg=title_color,
                     font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
            tk.Label(header, text=f"+{xp_rew} XP",
                     bg=BG3, fg=AMBER,
                     font=("Segoe UI", 10, "bold")).pack(side=tk.RIGHT)

            tk.Label(wframe, text=ch["desc"],
                     bg=BG3, fg=TEXT2,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=12)

            # Прогресс бар
            bar_outer = tk.Frame(wframe, bg="#2a2a40", height=8)
            bar_outer.pack(fill=tk.X, padx=12, pady=(6, 4))
            bar_outer.pack_propagate(False)
            bar_outer.update_idletasks()
            bar_w = bar_outer.winfo_width() or 320
            fill_w = max(4, int(bar_w * pct))
            tk.Frame(bar_outer,
                     bg=GREEN if done else PURPLE,
                     width=fill_w, height=8).place(x=0, y=0)

            prog_text = f"{prog} / {target}" if not done else "Выполнено!"
            tk.Label(wframe, text=prog_text,
                     bg=BG3, fg=TEXT3,
                     font=("Segoe UI", 8)).pack(anchor="e", padx=12, pady=(0, 8))

        tk.Frame(body, bg="#2d2d45", height=1).pack(fill=tk.X, pady=8)

        # ── Счётчик достижений ────────────────────────────
        ach      = self._p.achievements
        unlocked = sum(1 for a in ach if a["unlocked"])
        total    = len(ach)
        tk.Label(body,
                 text=f"🏆  Достижений разблокировано: {unlocked} / {total}",
                 bg=BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(anchor="w")

    def _do_prestige(self, event=None):
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Перерождение ★",
            "Твой XP будет сброшен до 0.\n"
            "Ты получишь значок Ветерана ★ и начнёшь путь снова.\n\n"
            "Подтвердить перерождение?",
            parent=self
        )
        if confirm:
            msg = self._p.do_prestige()
            if self._cb:
                self._cb(msg)
            self._build()

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
