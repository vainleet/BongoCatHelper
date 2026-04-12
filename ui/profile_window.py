"""
ui/profile_window.py  —  Discord-style profile UI
"""
import tkinter as tk
from datetime import date, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.progress import ProgressSystem, ALL_ACHIEVEMENTS, LEVELS, CAT_SKINS, get_skin

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

MOOD_C = ["", "#f87171","#fb923c","#fbbf24","#86efac","#34d399"]
MOOD_E = ["", "😢","😔","😐","😊","😄"]


class ProfileWindow(tk.Toplevel):
    def __init__(self, parent, progress: ProgressSystem, on_mood_log=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.configure(bg=BG)
        self.withdraw()

        self._p        = progress
        self._on_mood  = on_mood_log
        self._visible  = False
        self._tab      = "profile"
        self._mood_sel      = 0
        self._on_skin_change = None
        self._W        = 360
        self._H        = 520

        self._build()

    # ── Build ─────────────────────────────────────────────

    def _build(self):
        outer = tk.Frame(self, bg=PURPLE2, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(outer, bg=BG)
        inner.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(inner, bg=BG2, height=42)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="✦  Bongo Cat  ✦", bg=BG2, fg=PURPLE,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=12)
        cl = tk.Label(hdr, text=" ✕ ", bg=BG2, fg=TEXT3,
                      font=("Segoe UI", 12), cursor="hand2")
        cl.pack(side=tk.RIGHT, padx=6)
        cl.bind("<Enter>",    lambda e: cl.config(fg=RED, bg=BG3))
        cl.bind("<Leave>",    lambda e: cl.config(fg=TEXT3, bg=BG2))
        cl.bind("<Button-1>", lambda e: self.close())
        hdr.bind("<ButtonPress-1>", self._ds)
        hdr.bind("<B1-Motion>",     self._dm)

        # Tabs
        bar = tk.Frame(inner, bg=BG2, height=36)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        self._tlbls = {}
        for tid, lbl in [("profile","👤 Профиль"),("quests","🎯 Квесты"),
                          ("mood","💜 Настроение"),("achievements","🏆 Трофеи")]:
            lb = tk.Label(bar, text=lbl, bg=BG2, fg=TEXT3,
                          font=("Segoe UI", 8), padx=8, pady=8, cursor="hand2")
            lb.pack(side=tk.LEFT)
            lb.bind("<Button-1>", lambda e, t=tid: self._switch(t))
            lb.bind("<Enter>",  lambda e, l=lb: l.config(fg=TEXT))
            lb.bind("<Leave>",  lambda e, l=lb, t=tid: l.config(
                fg=PURPLE if self._tab==t else TEXT3))
            self._tlbls[tid] = lb
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X)

        self._body = tk.Frame(inner, bg=BG)
        self._body.pack(fill=tk.BOTH, expand=True)
        self._switch("profile")

    def _switch(self, tab):
        self._tab = tab
        for tid, lb in self._tlbls.items():
            lb.config(fg=PURPLE if tid==tab else TEXT3,
                      bg=BG3 if tid==tab else BG2)
        for w in self._body.winfo_children():
            w.destroy()
        getattr(self, f"_tab_{tab}")()

    # ── Tab: Profile ──────────────────────────────────────

    def _tab_profile(self):
        f  = self._body
        p  = self._p
        li = p.level_info
        skin = get_skin(li["level"])

        # Avatar canvas
        av = tk.Canvas(f, width=360, height=120, bg=BG, highlightthickness=0)
        av.pack()
        self._draw_avatar(av, li, skin)

        # Level + XP bar
        xf = tk.Frame(f, bg=BG2, padx=14, pady=12)
        xf.pack(fill=tk.X, padx=14, pady=(0,6))
        top = tk.Frame(xf, bg=BG2)
        top.pack(fill=tk.X)
        tk.Label(top, text=f"Ур. {li['level']}  {li['title']}",
                 bg=BG2, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        nxt = li.get("next_xp")
        tk.Label(top, text=f"{li['xp']}/{nxt} XP" if nxt else f"{li['xp']} XP",
                 bg=BG2, fg=TEXT2, font=("Segoe UI", 8)).pack(side=tk.RIGHT)
        bc = tk.Canvas(xf, bg=BG4, height=8, highlightthickness=0)
        bc.pack(fill=tk.X, pady=(8,0))
        bc.update_idletasks()
        W = bc.winfo_width() or 300
        fw = max(4, int(W * li["progress"]))
        bc.create_rectangle(0,0,W,8, fill=BG4, outline="")
        bc.create_rectangle(0,0,fw,8, fill=PURPLE, outline="")
        bc.create_oval(fw-4,1,fw+4,7, fill=PURPLE2, outline="")

        # Stats row
        sg = tk.Frame(f, bg=BG)
        sg.pack(fill=tk.X, padx=14, pady=4)
        for col,(val,lbl,col_) in enumerate([
            (f"{p.streak}🔥","Streak",AMBER),
            (str(p.total_messages),"Сообщений",TEAL),
            (str(sum(1 for a in p.achievements if a["unlocked"])),"Трофеев",PURPLE),
        ]):
            card = tk.Frame(sg, bg=BG3, padx=4, pady=8)
            card.grid(row=0, column=col, padx=3, sticky="ew")
            sg.columnconfigure(col, weight=1)
            tk.Label(card, text=val, bg=BG3, fg=col_,
                     font=("Segoe UI", 15, "bold")).pack()
            tk.Label(card, text=lbl, bg=BG3, fg=TEXT3,
                     font=("Segoe UI", 8)).pack()

        # Skin gallery
        sel_row = tk.Frame(f, bg=BG)
        sel_row.pack(fill=tk.X, padx=14, pady=(0,2))
        tk.Label(sel_row, text="  Скины:", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self._skin_label = tk.Label(sel_row,
                 text=f"  {p.skin.get('name','')}  ",
                 bg=PURPLE2, fg="#fff",
                 font=("Segoe UI", 8, "bold"))
        self._skin_label.pack(side=tk.RIGHT)

        row = tk.Frame(f, bg=BG)
        row.pack(fill=tk.X, padx=14)

        selected_lvl = p.selected_skin_level

        for skin_lvl, sdata in sorted(CAT_SKINS.items()):
            unlocked   = li["level"] >= skin_lvl
            is_selected = skin_lvl == selected_lvl
            border_col = GREEN if is_selected else (PURPLE if unlocked else BORDER)
            bg_col     = BG2 if unlocked else BG3

            sc = tk.Canvas(row, width=52, height=72,
                           bg=bg_col,
                           highlightthickness=2 if is_selected else 1,
                           highlightbackground=border_col,
                           cursor="hand2" if unlocked else "arrow")
            sc.pack(side=tk.LEFT, padx=2)

            if unlocked:
                body = sdata.get("body","#f0d8ff")
                ear  = sdata.get("inner_ear","#ffb3d9")
                out  = sdata.get("outline","#d0b0e8")
                eye  = sdata.get("eye_dark","#2a1040")
                hat  = sdata.get("hat") or ""
                sc.create_oval(14,20,38,44, fill=body, outline=out, width=1)
                sc.create_polygon(14,26, 6,10, 20,16, fill=body, outline=out)
                sc.create_polygon(15,27, 8,13, 19,18, fill=ear,  outline="")
                sc.create_polygon(38,26, 46,10, 32,16, fill=body, outline=out)
                sc.create_polygon(37,27, 44,13, 33,18, fill=ear,  outline="")
                sc.create_oval(19,28,24,33, fill=eye, outline="")
                sc.create_oval(28,28,33,33, fill=eye, outline="")
                if hat:
                    sc.create_text(26, 13, text=hat, font=("Segoe UI Emoji", 11))
                # "Выбран" badge
                if is_selected:
                    sc.create_rectangle(4,54,48,66, fill=GREEN, outline="")
                    sc.create_text(26,60, text="✓ выбран",
                                   fill="#000", font=("Segoe UI",7,"bold"))
                else:
                    sc.create_text(26,58, text=f"Lv{skin_lvl}",
                                   fill=PURPLE, font=("Segoe UI",7,"bold"))
                name_short = sdata["name"].split()[0]
                sc.create_text(26,68, text=name_short,
                               fill=TEXT2, font=("Segoe UI",6))

                def on_click(sl=skin_lvl):
                    if p.select_skin(sl):
                        if hasattr(self, "_on_skin_change") and self._on_skin_change:
                            self._on_skin_change()
                        self._switch("profile")  # обновить вид

                sc.bind("<Button-1>", lambda e, fn=on_click: fn())
                sc.bind("<Enter>",  lambda e, c=sc: c.config(highlightbackground=TEAL))
                sc.bind("<Leave>",  lambda e, c=sc, sl=skin_lvl:
                    c.config(highlightbackground=GREEN if sl==p.selected_skin_level else PURPLE))
            else:
                sc.create_text(26,28, text="🔒", font=("Segoe UI Emoji",16))
                need = LEVELS[skin_lvl][0] if skin_lvl < len(LEVELS) else 9999
                sc.create_text(26,50, text=f"-{max(0,need-li['xp'])}xp",
                               fill=TEXT3, font=("Segoe UI",7))
                sc.create_text(26,64, text=sdata["name"].split()[0],
                               fill=TEXT3, font=("Segoe UI",6))

    def _draw_avatar(self, cv, li, skin):
        cv.delete("all")
        cx, cy = 180, 60
        lvl  = li["level"]
        body = skin.get("body","#f0d8ff")
        ear  = skin.get("inner_ear","#ffb3d9")
        out  = skin.get("outline","#d0b0e8")
        eye  = skin.get("eye_dark","#2a1040")
        nose = skin.get("nose","#ff9eb5")
        shin = skin.get("eye_shine","#ffffff")
        hat  = skin.get("hat") or ""

        # Glow
        for r,c in [(50,"#1a0a3a"),(42,"#220d4a"),(34,"#2d1060")]:
            cv.create_oval(cx-r, cy-r, cx+r, cy+r, fill=c, outline="")

        # Body
        cv.create_oval(cx-30,cy-30, cx+30,cy+30, fill=body, outline=out, width=2)

        # Ears
        cv.create_polygon(cx-30,cy-24, cx-44,cy-48, cx-14,cy-40,
                          fill=body, outline=out)
        cv.create_polygon(cx-30,cy-26, cx-42,cy-45, cx-16,cy-38,
                          fill=ear, outline="")
        cv.create_polygon(cx+30,cy-24, cx+44,cy-48, cx+14,cy-40,
                          fill=body, outline=out)
        cv.create_polygon(cx+30,cy-26, cx+42,cy-45, cx+16,cy-38,
                          fill=ear, outline="")

        # Eyes
        cv.create_oval(cx-20,cy-12, cx-8,cy,  fill=eye, outline="")
        cv.create_oval(cx+8, cy-12, cx+20,cy, fill=eye, outline="")
        cv.create_oval(cx-18,cy-11, cx-15,cy-8, fill=shin, outline="")
        cv.create_oval(cx+10,cy-11, cx+13,cy-8, fill=shin, outline="")

        # Nose
        cv.create_polygon(cx-3,cy+4, cx+3,cy+4, cx,cy+9, fill=nose, outline="")

        # Hat
        if hat:
            cv.create_text(cx, cy-34, text=hat, font=("Segoe UI Emoji", 24))

        # Level badge
        cv.create_rectangle(cx+22,cy+16, cx+52,cy+30, fill=PURPLE2, outline="")
        cv.create_text(cx+37,cy+23, text=f"Lv{lvl}",
                       fill="#fff", font=("Segoe UI", 8, "bold"))

        # Skin name
        skin_name = skin.get("name","")
        cv.create_text(cx, cy+48, text=skin_name,
                       fill=PURPLE, font=("Segoe UI", 9, "bold"))

    # ── Tab: Quests ───────────────────────────────────────

    def _tab_quests(self):
        f = self._body
        p = self._p

        top = tk.Frame(f, bg=BG3, padx=14, pady=10)
        top.pack(fill=tk.X, padx=14, pady=(10,4))
        tk.Label(top, text=f"🔥  {p.streak} день подряд",
                 bg=BG3, fg=AMBER, font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        ci_done = p._data.get("checkin_date") == date.today().isoformat()
        ci = tk.Label(top,
                      text="  ✅ Отмечен  " if ci_done else "  ☀️ Check-in  ",
                      bg=BG4 if ci_done else GREEN,
                      fg=GREEN if ci_done else "#000",
                      font=("Segoe UI", 9, "bold"), padx=2, pady=3, cursor="hand2")
        ci.pack(side=tk.RIGHT)
        if not ci_done:
            ci.bind("<Button-1>", lambda e: self._do_checkin())

        tk.Label(f, text="  Квесты на сегодня",
                 bg=BG, fg=TEXT2, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4,2))

        for q in p.daily_quests:
            done = q.get("done", False)
            prog = min(q.get("progress",0), q.get("target",1))
            total = q.get("target",1)

            outer = tk.Frame(f, bg=GREEN if done else PURPLE2, padx=1, pady=1)
            outer.pack(fill=tk.X, padx=14, pady=2)
            card = tk.Frame(outer, bg=CARD, padx=12, pady=8)
            card.pack(fill=tk.X)

            row = tk.Frame(card, bg=CARD)
            row.pack(fill=tk.X)
            tk.Label(row, text=("✅  " if done else "○  ") + q["title"],
                     bg=CARD, fg=TEXT3 if done else TEXT,
                     font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(row, text=f"+{q['xp']} XP",
                     bg=CARD, fg=AMBER if not done else TEXT3,
                     font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
            tk.Label(card, text=q["desc"], bg=CARD, fg=TEXT3,
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(2,4))

            bar = tk.Canvas(card, bg=BG4, height=5, highlightthickness=0)
            bar.pack(fill=tk.X)
            bar.update_idletasks()
            W = bar.winfo_reqwidth() or 280
            fw = max(0, int(W * prog/total))
            bar.create_rectangle(0,0,W,5, fill=BG4, outline="")
            if fw > 0:
                bar.create_rectangle(0,0,fw,5,
                                     fill=GREEN if done else PURPLE, outline="")
            tk.Label(card, text=f"{prog}/{total}", bg=CARD, fg=TEXT3,
                     font=("Segoe UI", 7)).pack(anchor="e")

        total_xp = sum(q.get("xp",0) for q in p.daily_quests if q.get("done"))
        max_xp   = sum(q.get("xp",0) for q in p.daily_quests)
        tk.Label(f, text=f"  XP сегодня: {total_xp}/{max_xp}",
                 bg=BG, fg=TEXT3, font=("Segoe UI", 8)).pack(anchor="w", pady=(6,0))

    def _do_checkin(self):
        self._flash(self._p.do_checkin())
        self._switch("quests")

    # ── Tab: Mood ─────────────────────────────────────────

    def _tab_mood(self):
        f = self._body
        tk.Label(f, text="Как ты себя чувствуешь?",
                 bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(pady=(16,8))

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack()
        self._mbtn_refs = []

        for i, (em, lbl) in enumerate([("😢","Плохо"),("😔","Грустно"),
                                        ("😐","Нейтрально"),("😊","Хорошо"),("😄","Отлично")], 1):
            col = MOOD_C[i]
            fr = tk.Frame(btn_row, bg=BG, padx=3)
            fr.pack(side=tk.LEFT)
            cv = tk.Canvas(fr, width=52, height=60, bg=BG, highlightthickness=0, cursor="hand2")
            cv.pack()
            rect = cv.create_rectangle(2,2,50,58, fill=BG3, outline=BORDER)
            cv.create_text(26,22, text=em, font=("Segoe UI Emoji",18))
            num  = cv.create_text(26,44, text=str(i), fill=TEXT3, font=("Segoe UI",8))

            def click(v=i, c=col, cv_=cv, r=rect, n=num):
                self._mood_sel = v
                for cv2,r2,n2,c2 in self._mbtn_refs:
                    cv2.itemconfig(r2, fill=BG3, outline=BORDER)
                    cv2.itemconfig(n2, fill=TEXT3)
                cv_.itemconfig(r, fill=BG4, outline=c)
                cv_.itemconfig(n, fill=c)

            cv.bind("<Button-1>", lambda e, fn=click: fn())
            self._mbtn_refs.append((cv, rect, num, col))

        tk.Label(f, text="Заметка:", bg=BG, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(12,3))
        nf = tk.Frame(f, bg=BORDER, padx=1, pady=1)
        nf.pack(fill=tk.X, padx=18)
        self._note = tk.Text(nf, bg=BG3, fg=TEXT, insertbackground=TEXT,
                              font=("Segoe UI", 9), relief=tk.FLAT,
                              bd=6, height=3, wrap=tk.WORD)
        self._note.pack(fill=tk.X)

        sv = tk.Label(f, text="  Сохранить настроение  ",
                      bg=PURPLE2, fg="#fff",
                      font=("Segoe UI", 10, "bold"), pady=7, cursor="hand2")
        sv.pack(pady=10)
        sv.bind("<Button-1>", lambda e: self._save_mood())
        sv.bind("<Enter>",    lambda e: sv.config(bg=PURPLE))
        sv.bind("<Leave>",    lambda e: sv.config(bg=PURPLE2))

        tk.Label(f, text="За 7 дней:", bg=BG, fg=TEXT3,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=18)
        self._draw_chart(f)

    def _save_mood(self):
        if not self._mood_sel:
            self._flash("Выбери настроение! 🐱"); return
        note = self._note.get("1.0","end-1c").strip()
        result = self._p.log_mood(self._mood_sel, note)
        if self._on_mood: self._on_mood(result)
        self._mood_sel = 0
        self._switch("mood")

    def _draw_chart(self, parent):
        stats = self._p.get_mood_stats()
        cv = tk.Canvas(parent, bg=BG, height=72, highlightthickness=0)
        cv.pack(fill=tk.X, padx=18, pady=4)
        cv.update_idletasks()
        W = cv.winfo_reqwidth() or 300
        cw = W // 7
        for i, day in enumerate(stats):
            x = i*cw + cw//2
            cv.create_text(x, 65, text=day["label"], fill=TEXT3, font=("Segoe UI",7))
            m = day["mood"]
            if m is not None:
                h   = max(4, int((m/5)*46))
                col = MOOD_C[round(m)]
                cv.create_rectangle(x-10,58-h, x+10,58, fill=col, outline="")
                cv.create_text(x, 53-h, text=MOOD_E[round(m)],
                               font=("Segoe UI Emoji",9))
            else:
                cv.create_rectangle(x-10,54, x+10,58, fill=BG3, outline="")

    # ── Tab: Achievements ─────────────────────────────────

    def _tab_achievements(self):
        f = self._body
        p = self._p
        unlocked = sum(1 for a in p.achievements if a["unlocked"])
        total    = len(p.achievements)

        hdr = tk.Frame(f, bg=BG3, padx=14, pady=8)
        hdr.pack(fill=tk.X, padx=14, pady=(10,4))
        tk.Label(hdr, text=f"🏆  {unlocked} / {total}",
                 bg=BG3, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        bc = tk.Canvas(f, bg=BG4, height=4, highlightthickness=0)
        bc.pack(fill=tk.X, padx=14, pady=(0,6))
        bc.update_idletasks()
        W = bc.winfo_reqwidth() or 300
        fw = max(0, int(W * (unlocked/total if total else 0)))
        bc.create_rectangle(0,0,W,4, fill=BG4, outline="")
        bc.create_rectangle(0,0,fw,4, fill=AMBER, outline="")

        wrap = tk.Frame(f, bg=BG)
        wrap.pack(fill=tk.BOTH, expand=True, padx=14)
        cv = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(wrap, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=BG)
        inner.bind("<Configure>",
                   lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.bind("<MouseWheel>",
                lambda e: cv.yview_scroll(int(-1*(e.delta/120)),"units"))

        for a in p.achievements:
            unlck  = a["unlocked"]
            secret = a.get("secret",False) and not unlck
            row = tk.Frame(inner, bg=BG3 if unlck else BG2, padx=10, pady=7)
            row.pack(fill=tk.X, pady=1)
            icon = "🔒" if secret else ("✅" if unlck else "○")
            tk.Label(row, text=icon, bg=row["bg"],
                     font=("Segoe UI Emoji",14), width=2).pack(side=tk.LEFT)
            txt = tk.Frame(row, bg=row["bg"])
            txt.pack(side=tk.LEFT, padx=8)
            title = a["title"] if not secret else "???"
            tk.Label(txt, text=title, bg=row["bg"],
                     fg=AMBER if unlck else TEXT3,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            desc = a["desc"] if not secret else "Секретное достижение"
            tk.Label(txt, text=desc, bg=row["bg"],
                     fg=TEXT2 if unlck else TEXT3,
                     font=("Segoe UI", 8)).pack(anchor="w")

    # ── Flash ─────────────────────────────────────────────

    def _flash(self, msg: str):
        pop = tk.Toplevel(self)
        pop.overrideredirect(True)
        pop.wm_attributes("-topmost", True)
        pop.configure(bg=PURPLE2)
        tk.Label(pop, text=msg, bg=PURPLE2, fg="#fff",
                 font=("Segoe UI", 10), padx=16, pady=10).pack()
        pop.geometry(f"+{self.winfo_x()+20}+{self.winfo_y()+self._H//2}")
        self.after(2500, pop.destroy)

    # ── Drag ─────────────────────────────────────────────

    def _ds(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()
    def _dm(self, e):
        self.geometry(f"+{e.x_root-self._dx}+{e.y_root-self._dy}")

    # ── Open / Close ──────────────────────────────────────

    def open_near(self, cat_x: int, cat_y: int):
        W, H = self._W, self._H
        x = cat_x - W - 10
        if x < 4: x = cat_x + 175
        y = max(4, cat_y - H + 170)
        self.geometry(f"{W}x{H}+{x}+{y}")
        self._switch("profile")
        self.deiconify()
        self._visible = True

    def refresh(self):
        if self._visible:
            self._switch(self._tab)

    def close(self):
        self.withdraw()
        self._visible = False

    @property
    def visible(self): return self._visible
