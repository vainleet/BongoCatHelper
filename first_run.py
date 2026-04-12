"""
first_run.py — Мастер первого запуска Bongo Cat AI

Показывается ОДИН РАЗ при первом запуске.
Позволяет выбрать язык, модель Ollama, включить/выключить автозапуск и OCR.
Результат сохраняется в data/user_settings.json
"""

import tkinter as tk
from tkinter import ttk
import json
import os
import sys
import subprocess
import threading

# ── Локализация ───────────────────────────────────────────────
STRINGS = {
    "ru": {
        "title":        "Добро пожаловать в Bongo Cat AI! 🐱",
        "subtitle":     "Давай быстро настроим всё под тебя",
        "lang_label":   "Язык / Language:",
        "model_label":  "AI-модель:",
        "model_hint":   "Если не знаешь — оставь Gemma3. Если модель ещё не скачана — она загрузится при первом чате.",
        "ocr_label":    "Анализ экрана (OCR):",
        "ocr_hint":     "Кот будет видеть, что на экране, и давать советы по контексту.",
        "autostart":    "Запускать с Windows",
        "finish":       "Готово! Запустить Bongo Cat 🐱",
        "models": {
            "gemma3":  "Gemma3 (~3 ГБ) — рекомендуется, хорошо на русском",
            "mistral": "Mistral (~4 ГБ) — мощнее, отличный английский",
            "phi3":    "Phi-3 Mini (~2 ГБ) — самая лёгкая и быстрая",
            "llama3":  "Llama3 (~5 ГБ) — самая умная, нужно больше RAM",
            "none":    "Без AI (умные шаблонные ответы)",
        },
        "ocr_on":  "Включить",
        "ocr_off": "Выключить",
    },
    "en": {
        "title":        "Welcome to Bongo Cat AI! 🐱",
        "subtitle":     "Let's set things up quickly",
        "lang_label":   "Language / Язык:",
        "model_label":  "AI Model:",
        "model_hint":   "Not sure? Leave Gemma3. If the model isn't downloaded yet, it'll be fetched on first chat.",
        "ocr_label":    "Screen Analysis (OCR):",
        "ocr_hint":     "The cat will see what's on your screen and give context-aware tips.",
        "autostart":    "Launch with Windows",
        "finish":       "Done! Launch Bongo Cat 🐱",
        "models": {
            "gemma3":  "Gemma3 (~3 GB) — recommended, great multilingual",
            "mistral": "Mistral (~4 GB) — powerful, excellent English",
            "phi3":    "Phi-3 Mini (~2 GB) — lightest & fastest",
            "llama3":  "Llama3 (~5 GB) — smartest, needs more RAM",
            "none":    "No AI (smart template responses)",
        },
        "ocr_on":  "Enable",
        "ocr_off": "Disable",
    }
}

DATA_DIR     = os.path.join(os.path.dirname(__file__), "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "user_settings.json")
FLAG_PATH    = os.path.join(DATA_DIR, ".setup_done")


def already_configured() -> bool:
    return os.path.exists(FLAG_PATH)


def save_settings(lang: str, model: str, ocr: bool, autostart: bool):
    os.makedirs(DATA_DIR, exist_ok=True)
    settings = {
        "language":  lang,
        "model":     model,
        "ocr":       ocr,
        "autostart": autostart,
    }
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

    # Обновляем config.py на лету
    _patch_config(model, ocr)

    # Автозапуск Windows
    if autostart:
        _set_autostart(True)

    # Флаг «уже настраивали»
    with open(FLAG_PATH, "w") as f:
        f.write("1")


def _patch_config(model: str, ocr: bool):
    """Переписывает нужные строки в config.py без импорта."""
    cfg_path = os.path.join(os.path.dirname(__file__), "config.py")
    if not os.path.exists(cfg_path):
        return
    with open(cfg_path, "r", encoding="utf-8") as f:
        text = f.read()

    import re
    if model and model != "none":
        text = re.sub(r'OLLAMA_MODEL\s*=\s*"[^"]*"',
                      f'OLLAMA_MODEL = "{model}"', text)

    text = re.sub(r'SCREEN_CAPTURE_ENABLED\s*=\s*(True|False)',
                  f'SCREEN_CAPTURE_ENABLED = {str(ocr)}', text)

    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(text)


def _set_autostart(enable: bool):
    import winreg
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    exe = sys.executable if getattr(sys, "frozen", False) else __file__
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0,
                             winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(reg, "BongoCatAI", 0, winreg.REG_SZ, f'"{exe}"')
        else:
            try:
                winreg.DeleteValue(reg, "BongoCatAI")
            except FileNotFoundError:
                pass
        winreg.CloseKey(reg)
    except Exception:
        pass  # Не критично


# ── GUI ───────────────────────────────────────────────────────

class FirstRunWizard:
    BG      = "#0e0e14"
    BG2     = "#161622"
    BG3     = "#1e1e2e"
    BORDER  = "#2d2d45"
    PURPLE  = "#9b7fff"
    TEAL    = "#2dd4bf"
    TEXT    = "#e2e0f0"
    TEXT2   = "#9090b8"

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self._lang   = tk.StringVar(value="ru")
        self._model  = tk.StringVar(value="gemma3")
        self._ocr    = tk.BooleanVar(value=True)
        self._auto   = tk.BooleanVar(value=False)

        self._build()
        self._lang.trace_add("write", lambda *_: self._refresh_lang())

    def _s(self, key):
        return STRINGS[self._lang.get()][key]

    def _build(self):
        r = self.root
        r.title("Bongo Cat AI — Setup")
        r.geometry("540x560")
        r.resizable(False, False)
        r.configure(bg=self.BG)
        r.eval('tk::PlaceWindow . center')

        # Header
        hdr = tk.Frame(r, bg=self.PURPLE, height=6)
        hdr.pack(fill="x")

        body = tk.Frame(r, bg=self.BG, padx=32, pady=24)
        body.pack(fill="both", expand=True)

        self._title_lbl = tk.Label(body, text=self._s("title"),
            font=("Segoe UI", 16, "bold"), bg=self.BG, fg=self.TEXT)
        self._title_lbl.pack(anchor="w")

        self._sub_lbl = tk.Label(body, text=self._s("subtitle"),
            font=("Segoe UI", 10), bg=self.BG, fg=self.TEXT2)
        self._sub_lbl.pack(anchor="w", pady=(2, 20))

        # ── Язык ────────────────────────────────────────────
        row = tk.Frame(body, bg=self.BG)
        row.pack(fill="x", pady=6)
        self._lang_lbl = tk.Label(row, text=self._s("lang_label"),
            font=("Segoe UI", 10, "bold"), bg=self.BG, fg=self.TEXT, width=22, anchor="w")
        self._lang_lbl.pack(side="left")

        lang_frame = tk.Frame(row, bg=self.BG)
        lang_frame.pack(side="left")
        for val, txt in [("ru", "🇷🇺 Русский"), ("en", "🇬🇧 English")]:
            tk.Radiobutton(lang_frame, text=txt, variable=self._lang, value=val,
                bg=self.BG, fg=self.TEXT, selectcolor=self.BG3,
                activebackground=self.BG, activeforeground=self.PURPLE,
                font=("Segoe UI", 10)).pack(side="left", padx=8)

        # ── Модель ──────────────────────────────────────────
        sep = tk.Frame(body, bg=self.BORDER, height=1)
        sep.pack(fill="x", pady=12)

        row2 = tk.Frame(body, bg=self.BG)
        row2.pack(fill="x", pady=4)
        self._model_lbl = tk.Label(row2, text=self._s("model_label"),
            font=("Segoe UI", 10, "bold"), bg=self.BG, fg=self.TEXT, width=22, anchor="w")
        self._model_lbl.pack(side="left")

        self._model_combo = ttk.Combobox(row2, textvariable=self._model,
            values=["gemma3", "mistral", "phi3", "llama3", "none"],
            state="readonly", width=26, font=("Segoe UI", 10))
        self._model_combo.pack(side="left")

        self._model_hint = tk.Label(body, text=self._s("model_hint"),
            font=("Segoe UI", 8), bg=self.BG, fg=self.TEXT2, wraplength=460, justify="left")
        self._model_hint.pack(anchor="w", pady=(2, 0))

        # ── OCR ─────────────────────────────────────────────
        sep2 = tk.Frame(body, bg=self.BORDER, height=1)
        sep2.pack(fill="x", pady=12)

        row3 = tk.Frame(body, bg=self.BG)
        row3.pack(fill="x", pady=4)
        self._ocr_lbl = tk.Label(row3, text=self._s("ocr_label"),
            font=("Segoe UI", 10, "bold"), bg=self.BG, fg=self.TEXT, width=22, anchor="w")
        self._ocr_lbl.pack(side="left")

        ocr_frame = tk.Frame(row3, bg=self.BG)
        ocr_frame.pack(side="left")
        self._ocr_on  = tk.Radiobutton(ocr_frame, text=self._s("ocr_on"),
            variable=self._ocr, value=True,
            bg=self.BG, fg=self.TEXT, selectcolor=self.BG3,
            activebackground=self.BG, activeforeground=self.PURPLE,
            font=("Segoe UI", 10))
        self._ocr_on.pack(side="left", padx=8)
        self._ocr_off = tk.Radiobutton(ocr_frame, text=self._s("ocr_off"),
            variable=self._ocr, value=False,
            bg=self.BG, fg=self.TEXT, selectcolor=self.BG3,
            activebackground=self.BG, activeforeground=self.PURPLE,
            font=("Segoe UI", 10))
        self._ocr_off.pack(side="left", padx=8)

        self._ocr_hint = tk.Label(body, text=self._s("ocr_hint"),
            font=("Segoe UI", 8), bg=self.BG, fg=self.TEXT2, wraplength=460, justify="left")
        self._ocr_hint.pack(anchor="w", pady=(2, 0))

        # ── Автозапуск ──────────────────────────────────────
        sep3 = tk.Frame(body, bg=self.BORDER, height=1)
        sep3.pack(fill="x", pady=12)

        self._auto_chk = tk.Checkbutton(body, text=self._s("autostart"),
            variable=self._auto,
            bg=self.BG, fg=self.TEXT, selectcolor=self.BG3,
            activebackground=self.BG, activeforeground=self.PURPLE,
            font=("Segoe UI", 10))
        self._auto_chk.pack(anchor="w")

        # ── Кнопка ──────────────────────────────────────────
        sep4 = tk.Frame(body, bg=self.BORDER, height=1)
        sep4.pack(fill="x", pady=16)

        self._finish_btn = tk.Button(body,
            text=self._s("finish"),
            command=self._on_finish,
            bg=self.PURPLE, fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat", bd=0, padx=20, pady=10, cursor="hand2",
            activebackground="#7b5fff", activeforeground="white")
        self._finish_btn.pack(fill="x")

    def _refresh_lang(self):
        lang = self._lang.get()
        s = STRINGS[lang]
        self._title_lbl.config(text=s["title"])
        self._sub_lbl.config(text=s["subtitle"])
        self._lang_lbl.config(text=s["lang_label"])
        self._model_lbl.config(text=s["model_label"])
        self._model_hint.config(text=s["model_hint"])
        self._ocr_lbl.config(text=s["ocr_label"])
        self._ocr_hint.config(text=s["ocr_hint"])
        self._ocr_on.config(text=s["ocr_on"])
        self._ocr_off.config(text=s["ocr_off"])
        self._auto_chk.config(text=s["autostart"])
        self._finish_btn.config(text=s["finish"])

    def _on_finish(self):
        save_settings(
            lang=self._lang.get(),
            model=self._model.get(),
            ocr=self._ocr.get(),
            autostart=self._auto.get(),
        )
        self.root.destroy()

    def run(self):
        self.root.deiconify()
        self.root.mainloop()


def run_if_needed():
    """Вызывается из main.py ПЕРЕД запуском основного приложения."""
    if not already_configured():
        wizard = FirstRunWizard()
        wizard.run()
