"""
ui/cat_widget.py
Анимированный аватар Bongo Cat — рисуется через tkinter Canvas.
Поддерживает: idle, happy, sad, thinking, talking, sleepy, excited.
"""

import tkinter as tk
import math
import random


# Цветовая палитра кота
CAT_COLORS = {
    "body":       "#f0d8ff",
    "body_shade": "#e0c0f0",
    "inner_ear":  "#ffb3d9",
    "nose":       "#ff9eb5",
    "whisker":    "#9090a0",
    "eye_dark":   "#2a1040",
    "eye_shine":  "#ffffff",
    "blush":      "#ffb3c6",
    "tail":       "#d4a0c8",
    "tail_tip":   "#c890b8",
    "outline":    "#d0b0e8",
    "mouth":      "#ff9eb5",
    "paw":        "#eed8ff",
    "thought":    "#c8a8ff",
}


class BongoCatWidget(tk.Canvas):
    """
    Анимированный Bongo Cat.

    Использование:
        cat = BongoCatWidget(parent, size=180)
        cat.pack()
        cat.set_mood("happy")
    """

    MOODS = ("idle", "happy", "sad", "thinking", "talking", "sleepy", "excited")

    def __init__(self, parent, size: int = 180, bg: str = "#1a1a2e", **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=bg, highlightthickness=0, **kwargs)
        self.size = size
        self._bg  = bg
        self.mood = "idle"
        self._skin_colors  = None   # None = default CAT_COLORS
        self._mood_pet     = None   # dict from mood_pet.get_mood_pet_state()

        # Состояния анимации
        self._frame    = 0
        self._blink    = 0
        self._tail_a   = 0.0
        self._bounce   = 0.0
        self._mouth_o  = False   # рот открыт (talking)
        self._thought  = 0      # пульсация мыслей
        self._paw_up   = False
        self._running  = True

        self._animate()

    # ── Публичный API ──────────────────────────────────────

    def set_mood(self, mood: str):
        if mood in self.MOODS:
            self.mood = mood

    def set_mood_pet(self, state: dict):
        """Применить состояние Mood Pet (аура, блёстки, опущенные уши)."""
        self._mood_pet = state

    def set_skin(self, skin_dict: dict):
        """Применить скин (словарь цветов из ProgressSystem)."""
        self._skin_colors = skin_dict

    def stop(self):
        self._running = False

    # ── Цикл анимации ──────────────────────────────────────

    def _animate(self):
        if not self._running:
            return
        f = self._frame
        m = self.mood

        # Хвост
        speed = 0.12 if m == "excited" else 0.07 if m == "happy" else 0.05
        self._tail_a = math.sin(f * speed) * (30 if m in ("happy", "excited") else 18)

        # Прыжок/покачивание
        amp = 5 if m == "excited" else 3 if m == "happy" else 1.5
        self._bounce = math.sin(f * 0.13) * amp

        # Моргание
        self._blink = (f % 90 < 5) or (m == "sleepy" and f % 40 < 8)

        # Рот
        self._mouth_o = (m == "talking") and (f % 8 < 4)

        # Мысли (пульс)
        self._thought = (f % 30) / 30.0  # 0..1

        # Лапы вверх
        self._paw_up = m in ("happy", "excited", "talking")

        self._draw()
        self._frame += 1
        self.after(45, self._animate)

    # ── Отрисовка ──────────────────────────────────────────

    def _draw(self):
        self.delete("all")
        s  = self.size
        cx = s // 2
        cy = s // 2 + int(self._bounce)
        m  = self.mood
        c  = CAT_COLORS

        # ── Хвост ──────────────────────────────────────────
        c  = self._skin_colors if self._skin_colors else CAT_COLORS
        mp = self._mood_pet

        # ── Mood Pet: неоновый контур без заливки ────────────
        if mp and mp.get("aura_color") and mp["state"] != "neutral":
            ac    = mp["aura_color"]
            state = mp["state"]
            f_    = self._frame
            # Пульсирующий радиус — чуть больше кота
            import math as _m
            pulse = _m.sin(f_ * 0.08) * 3
            base  = 44 + int(pulse)

            if state == "glowing":
                # Золотое свечение — 3 кольца разной толщины
                for r, w, stip in [
                    (base+10, 2, "gray12"),
                    (base+5,  3, "gray25"),
                    (base,    4, "gray50"),
                ]:
                    self.create_oval(cx-r, cy-r, cx+r, cy+r,
                                     fill="", outline=ac, width=w)
            elif state == "happy":
                # Зелёный тонкий контур
                self.create_oval(cx-base-4, cy-base-4, cx+base+4, cy+base+4,
                                 fill="", outline=ac, width=3)
                self.create_oval(cx-base-8, cy-base-8, cx+base+8, cy+base+8,
                                 fill="", outline=ac, width=1, dash=(4,4))
            elif state == "sad":
                # Синеватый пунктир
                self.create_oval(cx-base-4, cy-base-4, cx+base+4, cy+base+4,
                                 fill="", outline=ac, width=2, dash=(3,5))
            elif state == "depressed":
                # Едва заметный тёмный контур
                self.create_oval(cx-base, cy-base, cx+base, cy+base,
                                 fill="", outline=ac, width=1, dash=(2,8))

        self._draw_tail(cx, cy, c)

        # ── Тело ───────────────────────────────────────────
        bx1, by1 = cx - 42, cy + 10
        bx2, by2 = cx + 42, cy + 58
        self.create_oval(bx1, by1, bx2, by2,
                         fill=c["body"], outline=c["outline"], width=1.5)

        # ── Лапы ───────────────────────────────────────────
        self._draw_paws(cx, cy, c)

        # ── Голова ─────────────────────────────────────────
        self.create_oval(cx - 40, cy - 46, cx + 40, cy + 18,
                         fill=c["body"], outline=c["outline"], width=1.5)

        # ── Уши ────────────────────────────────────────────
        self._draw_ears(cx, cy, c)

        # ── Глаза ──────────────────────────────────────────
        self._draw_eyes(cx, cy, c)

        # ── Нос ────────────────────────────────────────────
        self.create_polygon(
            cx - 5, cy - 5,
            cx + 5, cy - 5,
            cx,     cy,
            fill=c["nose"], outline=""
        )

        # ── Усы ────────────────────────────────────────────
        self._draw_whiskers(cx, cy, c)

        # ── Рот ────────────────────────────────────────────
        self._draw_mouth(cx, cy, c)

        # ── Румянец ────────────────────────────────────────
        if m not in ("sad",):
            self._draw_blush(cx, cy, c)

        # ── Декор настроения ───────────────────────────────
        if m == "thinking":
            self._draw_thought_bubble(cx, cy, c)
        elif m == "sleepy":
            self._draw_zzz(cx, cy, c)
        elif m == "excited":
            self._draw_sparkles(cx, cy, c)

        # ── Mood Pet: блёстки если glowing ─────────────────
        if mp and mp.get("sparkles"):
            f_ = self._frame
            for i, (dx, dy) in enumerate([(30,-50),(50,-38),(-34,-44),(44,-22),(-44,-28)]):
                pulse = abs(math.sin(f_ * 0.18 + i * 1.3))
                r = int(3 + pulse * 4)
                sc = self.create_oval(cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r,
                                      fill="#ffd700", outline="")
                # Лучики
                import math as _m
                for ang in range(0, 360, 90):
                    rad = _m.radians(ang + f_ * 4)
                    ex = cx+dx + _m.cos(rad)*(r+5)
                    ey = cy+dy + _m.sin(rad)*(r+5)
                    self.create_line(cx+dx, cy+dy, ex, ey,
                                     fill="#ffd700", width=1)

        # ── Шапка (из скина) ───────────────────────────────
        if self._skin_colors and self._skin_colors.get("hat"):
            hat = self._skin_colors["hat"]
            self.create_text(cx, cy - 42, text=hat,
                             font=("Segoe UI Emoji", int(self.size * 0.14)))

    def _draw_tail(self, cx, cy, c):
        tx  = cx - 36
        ty  = cy + 40
        ang = math.radians(self._tail_a - 25)
        tx2 = tx + math.cos(ang) * 48
        ty2 = ty + math.sin(ang) * 22
        # Тело хвоста
        self.create_line(tx, ty, tx2, ty2,
                         fill=c["tail"], width=9,
                         capstyle=tk.ROUND, smooth=True)
        # Кончик
        self.create_oval(tx2 - 7, ty2 - 7, tx2 + 7, ty2 + 7,
                         fill=c["tail_tip"], outline="")

    def _draw_paws(self, cx, cy, c):
        py = cy + 28
        if self._paw_up:
            # Лапы подняты
            lx1, lx2 = cx - 64, cx - 40
            rx1, rx2 = cx + 40, cx + 64
            self.create_oval(lx1, py - 22, lx2, py + 2, fill=c["paw"], outline=c["outline"], width=1)
            self.create_oval(rx1, py - 22, rx2, py + 2, fill=c["paw"], outline=c["outline"], width=1)
            # Пальчики
            for dx in (-4, 0, 4):
                self.create_oval(cx - 52 + dx - 3, py - 24,
                                 cx - 52 + dx + 3, py - 17,
                                 fill=c["body"], outline=c["outline"], width=0.5)
                self.create_oval(cx + 52 + dx - 3, py - 24,
                                 cx + 52 + dx + 3, py - 17,
                                 fill=c["body"], outline=c["outline"], width=0.5)
        else:
            # Лапы опущены
            self.create_oval(cx - 60, py,     cx - 38, py + 18,
                             fill=c["paw"], outline=c["outline"], width=1)
            self.create_oval(cx + 38, py,     cx + 60, py + 18,
                             fill=c["paw"], outline=c["outline"], width=1)

    def _draw_ears(self, cx, cy, c):
        # Левое ухо (внешнее)
        self.create_polygon(cx - 38, cy - 40,
                            cx - 56, cy - 68,
                            cx - 16, cy - 58,
                            fill=c["body"], outline=c["outline"], width=1)
        # Левое ухо (внутреннее)
        self.create_polygon(cx - 38, cy - 44,
                            cx - 52, cy - 63,
                            cx - 20, cy - 55,
                            fill=c["inner_ear"], outline="")
        # Правое ухо (внешнее)
        self.create_polygon(cx + 38, cy - 40,
                            cx + 56, cy - 68,
                            cx + 16, cy - 58,
                            fill=c["body"], outline=c["outline"], width=1)
        # Правое ухо (внутреннее)
        self.create_polygon(cx + 38, cy - 44,
                            cx + 52, cy - 63,
                            cx + 20, cy - 55,
                            fill=c["inner_ear"], outline="")

    def _draw_eyes(self, cx, cy, c):
        m  = self.mood
        ey = cy - 18
        lx = cx - 17    # центр левого глаза
        rx = cx + 17    # центр правого глаза
        r  = 9

        if self._blink:
            # Моргание
            for ex in (lx, rx):
                self.create_arc(ex - r, ey - r//2,
                                ex + r, ey + r//2,
                                start=0, extent=180,
                                style=tk.ARC, outline=c["eye_dark"], width=3)

        elif m == "sad":
            # Грустные — дуга вниз
            for ex in (lx, rx):
                self.create_arc(ex - r, ey - r//2,
                                ex + r, ey + r//2,
                                start=180, extent=180,
                                style=tk.ARC, outline=c["eye_dark"], width=3)

        elif m in ("happy", "excited"):
            # Прищур-улыбка
            for ex in (lx, rx):
                self.create_arc(ex - r, ey - 3,
                                ex + r, ey + 6,
                                start=180, extent=180,
                                style=tk.ARC, outline=c["eye_dark"], width=3)

        elif m == "sleepy":
            # Полузакрытые
            for ex in (lx, rx):
                self.create_arc(ex - r, ey - r,
                                ex + r, ey + r,
                                start=0, extent=180,
                                style=tk.ARC, outline=c["eye_dark"], width=3)
                self.create_line(ex - r, ey, ex + r, ey,
                                 fill=c["eye_dark"], width=2)

        elif m == "thinking":
            # Один прищурен, другой нормальный
            self.create_oval(lx - r, ey - r, lx + r, ey + r,
                             fill=c["eye_dark"], outline="")
            self.create_oval(lx - 5, ey - 5, lx - 1, ey - 1,
                             fill=c["eye_shine"], outline="")
            self.create_arc(rx - r, ey - 2,
                            rx + r, ey + 7,
                            start=0, extent=180,
                            style=tk.ARC, outline=c["eye_dark"], width=3)
        else:
            # Обычные круглые
            for ex in (lx, rx):
                self.create_oval(ex - r, ey - r, ex + r, ey + r,
                                 fill=c["eye_dark"], outline="")
                self.create_oval(ex - 5, ey - 5, ex - 1, ey - 1,
                                 fill=c["eye_shine"], outline="")

    def _draw_whiskers(self, cx, cy, c):
        wy = cy - 2
        w  = c["whisker"]
        # Левые
        self.create_line(cx - 32, wy - 2, cx - 9, wy - 1, fill=w, width=1)
        self.create_line(cx - 32, wy + 3, cx - 9, wy + 2, fill=w, width=1)
        # Правые
        self.create_line(cx + 9, wy - 1, cx + 32, wy - 2, fill=w, width=1)
        self.create_line(cx + 9, wy + 2, cx + 32, wy + 3, fill=w, width=1)

    def _draw_mouth(self, cx, cy, c):
        m = self.mood
        if self._mouth_o:
            # Открытый рот (talking)
            self.create_oval(cx - 8, cy + 2, cx + 8, cy + 12,
                             fill=c["inner_ear"], outline=c["mouth"], width=1)
        elif m == "sad":
            self.create_arc(cx - 9, cy + 3, cx + 9, cy + 13,
                            start=0, extent=-180,
                            style=tk.ARC, outline=c["mouth"], width=2)
        elif m in ("happy", "excited"):
            self.create_arc(cx - 11, cy + 2, cx + 11, cy + 15,
                            start=180, extent=180,
                            style=tk.ARC, outline=c["mouth"], width=2)
        else:
            self.create_arc(cx - 8, cy + 3, cx + 8, cy + 12,
                            start=180, extent=180,
                            style=tk.ARC, outline=c["mouth"], width=2)

    def _draw_blush(self, cx, cy, c):
        self.create_oval(cx - 36, cy - 2, cx - 18, cy + 9,
                         fill=c["blush"], outline="", stipple="gray25")
        self.create_oval(cx + 18, cy - 2, cx + 36, cy + 9,
                         fill=c["blush"], outline="", stipple="gray25")

    def _draw_thought_bubble(self, cx, cy, c):
        t = self._thought
        base_alpha = 0.4 + t * 0.5
        for i, (dx, dy, r) in enumerate([(28, -52, 4), (40, -63, 6), (54, -73, 9)]):
            fill = c["thought"] if i == 2 else "#b090ee"
            self.create_oval(cx + dx - r, cy + dy - r,
                             cx + dx + r, cy + dy + r,
                             fill=fill, outline="")
        # Знак вопроса в большом пузыре
        self.create_text(cx + 54, cy - 73, text="?",
                         fill="#3a1060", font=("Segoe UI", 8, "bold"))

    def _draw_zzz(self, cx, cy, c):
        f = self._frame
        for i, (dx, dy, size) in enumerate([(28, -50, 9), (38, -62, 11), (50, -72, 13)]):
            alpha = 0.3 + 0.2 * i + math.sin(f * 0.1 + i) * 0.15
            self.create_text(cx + dx, cy + dy, text="z",
                             fill="#a080cc",
                             font=("Segoe UI", size, "bold"))

    def _draw_sparkles(self, cx, cy, c):
        f   = self._frame
        pts = [(cx - 48, cy - 50), (cx + 48, cy - 55), (cx, cy - 65)]
        for i, (sx, sy) in enumerate(pts):
            pulse = abs(math.sin(f * 0.15 + i * 1.2))
            r = int(4 + pulse * 4)
            self.create_oval(sx - r, sy - r, sx + r, sy + r,
                             fill="#ffe066", outline="")
            # Лучики
            for angle in range(0, 360, 90):
                rad = math.radians(angle + f * 3)
                ex  = sx + math.cos(rad) * (r + 5)
                ey  = sy + math.sin(rad) * (r + 5)
                self.create_line(sx, sy, ex, ey, fill="#ffe066", width=1)