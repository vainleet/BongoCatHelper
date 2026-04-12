"""
core/history.py
Хранение истории чата локально (JSON).
Данные хранятся только на устройстве пользователя.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


class ChatHistory:
    """Простое локальное хранилище истории диалога."""

    def __init__(self):
        self._messages: List[Dict] = []
        self._data_dir = config.DATA_DIR
        self._filepath = os.path.join(self._data_dir, "history.json")
        os.makedirs(self._data_dir, exist_ok=True)
        if config.SAVE_HISTORY:
            self._load()

    def add(self, role: str, content: str):
        """Добавить сообщение. role = 'user' | 'assistant'"""
        self._messages.append({
            "role": role,
            "content": content,
            "ts": datetime.now().isoformat()
        })
        if config.SAVE_HISTORY:
            self._save()

    def get_for_llm(self) -> List[Dict]:
        """Возвращает историю в формате для LLM (без timestamp)."""
        return [{"role": m["role"], "content": m["content"]}
                for m in self._messages[-config.AI_HISTORY_LEN:]]

    def clear(self):
        self._messages.clear()
        if config.SAVE_HISTORY and os.path.exists(self._filepath):
            os.remove(self._filepath)

    def _save(self):
        try:
            # Оставляем только последние 200 сообщений
            recent = self._messages[-200:]
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(recent, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  ⚠  Ошибка сохранения истории: {e}")

    def _load(self):
        if not os.path.exists(self._filepath):
            return
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                all_msgs = json.load(f)
            # Фильтруем по дате
            cutoff = datetime.now() - timedelta(days=config.HISTORY_MAX_DAYS)
            self._messages = [
                m for m in all_msgs
                if datetime.fromisoformat(m.get("ts", "2000-01-01")) > cutoff
            ]
            print(f"  📂 Загружено {len(self._messages)} сообщений из истории")
        except Exception as e:
            print(f"  ⚠  Ошибка загрузки истории: {e}")
            self._messages = []

    def __len__(self):
        return len(self._messages)
