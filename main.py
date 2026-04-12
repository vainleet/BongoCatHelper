
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# ── Мастер первого запуска (язык, модель, OCR, автозапуск) ──
from first_run import run_if_needed
run_if_needed()

# ── Основное приложение ─────────────────────────────────────
from ui.app_window import BongoCatApp

if __name__ == "__main__":
    app = BongoCatApp()
    app.run()
