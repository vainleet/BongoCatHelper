"""
core/mood_pet.py
Mood Pet — кот визуально меняется в зависимости от настроения за неделю.
Чем лучше настроение — тем ярче и счастливее кот.
Чем хуже — тем серее, уши опускаются, сидит в углу.
"""

from core.progress import ProgressSystem


def get_mood_pet_state(progress: ProgressSystem) -> dict:
    """
    Возвращает состояние Mood Pet на основе настроения за 7 дней.
    
    Returns dict:
        mood_level: float 0.0-5.0 (среднее настроение)
        state: 'glowing'|'happy'|'neutral'|'sad'|'depressed'
        color_tint: hex цвет для тинта кота
        sparkles: bool — блестит ли кот
        droopy_ears: bool — опущены ли уши
        extra_mood: str — дополнительное настроение для cat_widget
        aura_color: hex — цвет ауры вокруг кота
        status_text: str — текст состояния
    """
    stats = progress.get_mood_stats()
    moods = [d["mood"] for d in stats if d["mood"] is not None]
    
    if not moods:
        return _neutral_state()
    
    avg = sum(moods) / len(moods)
    days = len(moods)
    
    # Учитываем streak
    streak = progress.streak
    streak_bonus = min(0.5, streak * 0.05)
    effective = min(5.0, avg + streak_bonus)
    
    if effective >= 4.5:
        return {
            "mood_level": effective,
            "state": "glowing",
            "color_tint": "#fff4aa",   # золотистый
            "sparkles": True,
            "droopy_ears": False,
            "extra_mood": "excited",
            "aura_color": "#ffd700",
            "aura_radius": 55,
            "status_text": f"Сияет от счастья ✨ ({avg:.1f}/5)",
            "days": days,
        }
    elif effective >= 3.5:
        return {
            "mood_level": effective,
            "state": "happy",
            "color_tint": "#c8f0d0",   # зелёноватый
            "sparkles": False,
            "droopy_ears": False,
            "extra_mood": "happy",
            "aura_color": "#34d399",
            "aura_radius": 45,
            "status_text": f"Доволен жизнью 😊 ({avg:.1f}/5)",
            "days": days,
        }
    elif effective >= 2.5:
        return _neutral_state(avg, days)
    elif effective >= 1.5:
        return {
            "mood_level": effective,
            "state": "sad",
            "color_tint": "#b0b0c8",   # серо-синий
            "sparkles": False,
            "droopy_ears": True,
            "extra_mood": "sad",
            "aura_color": "#6060a0",
            "aura_radius": 38,
            "status_text": f"Грустит вместе с тобой 💙 ({avg:.1f}/5)",
            "days": days,
        }
    else:
        return {
            "mood_level": effective,
            "state": "depressed",
            "color_tint": "#888898",   # почти серый
            "sparkles": False,
            "droopy_ears": True,
            "extra_mood": "sleepy",
            "aura_color": "#404050",
            "aura_radius": 30,
            "status_text": f"Переживает за тебя... 😢 ({avg:.1f}/5)",
            "days": days,
        }


def _neutral_state(avg=3.0, days=0):
    return {
        "mood_level": avg,
        "state": "neutral",
        "color_tint": None,
        "sparkles": False,
        "droopy_ears": False,
        "extra_mood": "idle",
        "aura_color": "#555570",
        "aura_radius": 40,
        "status_text": f"Обычный день 😐 ({avg:.1f}/5)" if days else "Запиши настроение!",
        "days": days,
    }


def get_mood_pet_message(state: str) -> str:
    """Сообщение кота в зависимости от состояния Mood Pet."""
    import random
    messages = {
        "glowing": [
            "Ты просто светишься на этой неделе! ✨ Я так рада!",
            "Целая неделя хорошего настроения! Ты молодец 🌟",
            "Смотри как я блещу — это потому что ты счастлив(а)! 🎉",
        ],
        "happy": [
            "Хорошая неделя! Продолжай в том же духе 😊",
            "Ты в хорошей форме — я чувствую! 🐱",
        ],
        "neutral": [
            "Обычная неделя. Расскажи как дела? 🐾",
            "Я здесь. Как ты на самом деле? 💙",
        ],
        "sad": [
            "Вижу что неделя была непростой... Хочешь поговорить? 💙",
            "Я немного посерел — потому что переживаю за тебя 🩶",
        ],
        "depressed": [
            "Мне грустно видеть тебя в таком состоянии. Ты не один(а) 💙",
            "Пожалуйста, расскажи мне что происходит... 🐱",
        ],
    }
    opts = messages.get(state, messages["neutral"])
    return random.choice(opts)
