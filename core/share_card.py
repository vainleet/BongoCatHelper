"""
core/share_card.py
Экспорт красивой PNG-карточки с котом, уровнем и стриком.
Использует только Pillow — никакого интернета.

Генерирует карточку 600×340 px в стиле «Spotify card».
"""

import os
import sys
import math
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# ── Цветовая схема карточки ───────────────────────────────
CARD_BG        = (14, 14, 20)        # очень тёмный фон
CARD_BG2       = (22, 22, 34)        # немного светлее
PURPLE         = (155, 127, 255)
PURPLE_DARK    = (80, 60, 160)
GREEN          = (52, 211, 153)
AMBER          = (251, 191, 36)
TEXT_WHITE     = (226, 224, 240)
TEXT_MUTED     = (120, 120, 180)
TEXT_DIM       = (60, 60, 100)

W, H = 600, 340


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Пробуем красивые шрифты системы, fallback — default."""
    candidates = []
    if bold:
        candidates = [
            "C:/Windows/Fonts/seguisb.ttf",     # Segoe UI Semibold
            "C:/Windows/Fonts/segoeuib.ttf",    # Segoe UI Bold
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()


def _get_emoji_font(size: int) -> ImageFont.FreeTypeFont:
    """Шрифт с эмодзи."""
    candidates = [
        "C:/Windows/Fonts/seguiemj.ttf",   # Segoe UI Emoji
        "C:/Windows/Fonts/seguisym.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return _get_font(size)


def _draw_rounded_rect(draw: ImageDraw.Draw, xy, radius: int, fill, outline=None, width=1):
    """Рисует прямоугольник с закруглёнными углами."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                            outline=outline, width=width)


def _draw_progress_bar(draw: ImageDraw.Draw, x: int, y: int, w: int, h: int,
                        progress: float, color_fill, color_bg=(30, 30, 50)):
    """Рисует прогресс-бар (0.0–1.0)."""
    _draw_rounded_rect(draw, (x, y, x + w, y + h), radius=h // 2, fill=color_bg)
    if progress > 0:
        fill_w = max(h, int(w * min(progress, 1.0)))
        _draw_rounded_rect(draw, (x, y, x + fill_w, y + h), radius=h // 2, fill=color_fill)


def _mood_to_color(avg: float):
    """Цвет настроения по среднему значению 1–5."""
    if avg is None or avg == 0:
        return TEXT_MUTED
    if avg >= 4.5:
        return (255, 215, 0)
    if avg >= 3.5:
        return GREEN
    if avg >= 2.5:
        return (150, 200, 255)
    if avg >= 1.5:
        return (255, 160, 80)
    return (248, 113, 113)


def _mood_emoji(avg: float) -> str:
    if avg is None or avg == 0:
        return "😐"
    if avg >= 4.5:
        return "😄"
    if avg >= 3.5:
        return "😊"
    if avg >= 2.5:
        return "😐"
    if avg >= 1.5:
        return "😔"
    return "😢"


def generate_share_card(progress_system, save_path: str = None) -> str:
    """
    Генерирует PNG-карточку и сохраняет по пути save_path.
    Возвращает путь к файлу.
    """
    if not HAS_PILLOW:
        raise RuntimeError(
            "Pillow не установлен. Запусти: pip install Pillow"
        )

    # ── Данные ────────────────────────────────────────────
    level_info  = progress_system.level_info
    level       = level_info["level"]
    level_title = level_info["title"]
    xp          = level_info["xp"]
    xp_prev     = level_info["prev_xp"]
    xp_next     = level_info["next_xp"]
    xp_progress = level_info["progress"]
    streak      = progress_system.streak
    total_msgs  = progress_system.total_messages
    skin        = progress_system.skin
    skin_name   = skin.get("name", "Обычный")

    mood_stats  = progress_system.get_mood_stats()
    mood_vals   = [d["mood"] for d in mood_stats if d["mood"] is not None]
    mood_avg    = round(sum(mood_vals) / len(mood_vals), 1) if mood_vals else None

    achievements_unlocked = sum(1 for a in progress_system.achievements if a["unlocked"])
    achievements_total    = len(progress_system.achievements)

    today_str = date.today().strftime("%-d %b %Y") if sys.platform != "win32" else date.today().strftime("%d.%m.%Y")

    # ── Холст ─────────────────────────────────────────────
    img  = Image.new("RGB", (W, H), CARD_BG)
    draw = ImageDraw.Draw(img)

    # Декоративный градиент-фон (простые полосы)
    for i in range(H):
        alpha = i / H
        r = int(CARD_BG[0] + (CARD_BG2[0] - CARD_BG[0]) * alpha * 0.5)
        g = int(CARD_BG[1] + (CARD_BG2[1] - CARD_BG[1]) * alpha * 0.5)
        b = int(CARD_BG[2] + (CARD_BG2[2] - CARD_BG[2]) * alpha * 0.5)
        draw.line([(0, i), (W, i)], fill=(r, g, b))

    # Акцентная полоса слева
    draw.rounded_rectangle([0, 0, 4, H], radius=2, fill=PURPLE)

    # ── Шрифты ────────────────────────────────────────────
    fnt_big   = _get_font(32, bold=True)
    fnt_med   = _get_font(20, bold=True)
    fnt_norm  = _get_font(15)
    fnt_small = _get_font(12)
    fnt_emoji = _get_emoji_font(22)

    # ── Заголовок ─────────────────────────────────────────
    draw.text((24, 20), "Bongo Cat AI", font=fnt_med, fill=PURPLE)
    draw.text((24, 46), today_str, font=fnt_small, fill=TEXT_MUTED)

    # ── Большой кот ASCII / текстовый аватар ─────────────
    # Рисуем круглый аватар с уровнем
    cx, cy = 470, 100
    r_outer = 68
    r_inner = 62

    # Кольцо прогресса XP
    bbox = [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer]
    draw.ellipse(bbox, fill=(25, 25, 40), outline=(40, 35, 80), width=1)

    # Дуга прогресса
    if xp_progress > 0:
        start_angle = -90
        end_angle   = start_angle + int(360 * xp_progress)
        for i in range(3):   # толстая дуга
            draw.arc(
                [cx - r_outer + i, cy - r_outer + i,
                 cx + r_outer - i, cy + r_outer - i],
                start=start_angle, end=end_angle,
                fill=PURPLE, width=4
            )

    # Внутренний круг
    draw.ellipse(
        [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
        fill=(18, 18, 30)
    )

    # Текст уровня в круге
    lvl_text = str(level)
    draw.text((cx, cy - 14), lvl_text, font=fnt_big, fill=PURPLE,
              anchor="mm")
    draw.text((cx, cy + 18), "уровень", font=fnt_small, fill=TEXT_MUTED,
              anchor="mm")

    # Название скина под кругом
    draw.text((cx, cy + r_outer + 14), skin_name,
              font=fnt_small, fill=TEXT_DIM, anchor="mm")

    # ── Левая колонка: основные статы ────────────────────
    left_x = 24
    y = 90

    # Уровень + название
    draw.text((left_x, y), level_title, font=fnt_big, fill=TEXT_WHITE)
    y += 42

    # Прогресс XP
    if xp_next:
        xp_text = f"XP: {xp}  /  {xp_next}"
    else:
        xp_text = f"XP: {xp}  (макс.)"
    draw.text((left_x, y), xp_text, font=fnt_small, fill=TEXT_MUTED)
    y += 18
    _draw_progress_bar(draw, left_x, y, 260, 6, xp_progress, PURPLE)
    y += 24

    # Стрик
    streak_color = AMBER if streak >= 7 else GREEN if streak >= 3 else TEXT_MUTED
    draw.text((left_x, y), f"🔥  {streak} дней подряд",
              font=fnt_norm, fill=streak_color)
    y += 32

    # Сообщений
    draw.text((left_x, y), f"💬  {total_msgs} сообщений",
              font=fnt_norm, fill=TEXT_WHITE)
    y += 32

    # Настроение
    if mood_avg:
        m_color = _mood_to_color(mood_avg)
        m_emoji = _mood_emoji(mood_avg)
        draw.text((left_x, y), f"{m_emoji}  настроение {mood_avg}/5",
                  font=fnt_norm, fill=m_color)
    else:
        draw.text((left_x, y), "😐  настроение не записано",
                  font=fnt_norm, fill=TEXT_MUTED)
    y += 32

    # Достижения
    draw.text((left_x, y), f"🏆  {achievements_unlocked}/{achievements_total} достижений",
              font=fnt_norm, fill=TEXT_WHITE)

    # ── Мини-график настроения (7 дней) ──────────────────
    bar_y_base = 285
    bar_w      = 24
    bar_gap    = 8
    bar_max_h  = 40
    total_bars = 7
    bars_total_w = total_bars * (bar_w + bar_gap) - bar_gap
    bar_start_x  = (W - bars_total_w) // 2

    draw.text((W // 2, bar_y_base - bar_max_h - 16), "Настроение за 7 дней",
              font=fnt_small, fill=TEXT_DIM, anchor="mm")

    for i, d in enumerate(mood_stats):
        bx = bar_start_x + i * (bar_w + bar_gap)
        mood_val = d["mood"]
        label    = d["label"]

        if mood_val:
            bar_h = int(bar_max_h * (mood_val / 5))
            color = _mood_to_color(mood_val)
        else:
            bar_h = 3
            color = TEXT_DIM

        # Столбик
        _draw_rounded_rect(
            draw,
            (bx, bar_y_base - bar_h, bx + bar_w, bar_y_base),
            radius=4, fill=color
        )
        # Подпись дня
        draw.text((bx + bar_w // 2, bar_y_base + 8), label[:2],
                  font=fnt_small, fill=TEXT_DIM, anchor="mm")

    # ── Нижняя строка ─────────────────────────────────────
    draw.text((left_x, H - 22), "bongo-cat-ai",
              font=fnt_small, fill=TEXT_DIM)
    draw.text((W - 24, H - 22), "#BongoCat",
              font=fnt_small, fill=PURPLE_DARK, anchor="ra")

    # ── Сохранение ────────────────────────────────────────
    if save_path is None:
        save_path = os.path.join(
            os.path.expanduser("~"),
            "Desktop",
            f"bongo_cat_{date.today().isoformat()}.png"
        )

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    img.save(save_path, "PNG", optimize=True)
    return save_path


def open_share_dialog(progress_system, parent_window=None):
    """
    Генерирует карточку и открывает диалог сохранения / проводник.
    Вызывай из UI-потока.
    """
    import tkinter as tk
    from tkinter import filedialog, messagebox

    default_name = f"bongo_cat_{date.today().isoformat()}.png"
    default_dir  = os.path.expanduser("~/Desktop")

    save_path = filedialog.asksaveasfilename(
        title="Сохранить карточку",
        initialfile=default_name,
        initialdir=default_dir,
        defaultextension=".png",
        filetypes=[("PNG изображение", "*.png"), ("Все файлы", "*.*")],
        parent=parent_window,
    )

    if not save_path:
        return None   # пользователь отменил

    try:
        path = generate_share_card(progress_system, save_path)
        messagebox.showinfo(
            "Карточка сохранена! 🎉",
            f"Файл сохранён:\n{path}\n\nПоделись им в соцсетях с тегом #BongoCat!",
            parent=parent_window,
        )
        # Открываем в проводнике
        os.startfile(os.path.dirname(path))
        return path
    except RuntimeError as e:
        messagebox.showerror("Ошибка", str(e), parent=parent_window)
        return None
