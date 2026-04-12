# 🐱 Bongo Cat AI — Desktop Companion

An animated AI companion that lives on your Windows desktop. Talks to you, reacts to what you're doing, tracks your mood and productivity — all fully offline.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Local AI via Ollama** — runs Gemma3, Mistral, Phi-3, or Llama3 entirely on your machine. No data leaves your PC.
- **Smart fallback replies** — works without Ollama too, using keyword-based responses.
- **Ollama auto-restart** — if Ollama crashes, the app detects it and restarts the server automatically.
- **Screen analysis (OCR)** — optionally reads your screen with Tesseract and gives context-aware tips.
- **Proactive messages** — the cat writes to you on its own if you've been quiet for a few minutes.
- **App reactions** — reacts when you switch between apps (detects coding, browsing, etc.).
- **Mood & progress tracking** — XP system, level-ups, weekly reports, prestige.
- **Mini-games** — daily mini-game built into the chat window.
- **Diary & productivity tracker** — built-in windows for journaling and task tracking.
- **Co-op mode** — see other Bongo Cat instances on your local network.
- **Seasonal skins** — the cat's appearance changes with the time of year.
- **Crisis support** — automatically provides a crisis hotline number if certain keywords are detected.
- **Bilingual UI** — full English and Russian interface, including the cat's responses.
- **First-run setup wizard** — language, AI model, OCR, and autostart configured on first launch.

---

## Requirements

- Windows 10 / 11
- Python 3.10+
- [Ollama](https://ollama.com) *(optional, for full AI)*
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) *(optional, for screen analysis)*

---

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/yourname/bongocat-ai.git
cd bongocat-ai
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
python main.py
```

A setup wizard will open on the first launch to configure language, AI model, and other preferences.

---

## Setting up Ollama (recommended)

Ollama runs the language model locally — free, private, no internet needed after setup.

```bash
# 1. Download Ollama from https://ollama.com and install it
# 2. Pull a model
ollama pull gemma3      # ~3 GB, recommended
ollama pull mistral     # ~4 GB, strong English
ollama pull phi3        # ~2 GB, lightest
ollama pull llama3      # ~5 GB, most capable
# 3. Restart main.py — the status indicator turns green
```

---

## Setting up Screen Analysis (optional)

1. Download **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
2. During install, enable the Russian language pack if needed
3. Default path expected: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   If yours differs, update `TESSERACT_PATH` in `config.py`
4. Toggle screen analysis with the 👁 button in the app header

---

## Project Structure

```
bongocat_v9/
├── main.py                  # Entry point
├── config.py                # All settings
├── first_run.py             # First-launch setup wizard
├── requirements.txt
│
├── core/
│   ├── ai_engine.py         # Ollama + smart fallback + auto-restart
│   ├── screen_watcher.py    # OCR and screen capture
│   ├── history.py           # Chat history (local JSON)
│   ├── proactive.py         # Proactive message scheduler
│   ├── progress.py          # XP, levels, skins
│   ├── productivity.py      # Productivity tracker
│   ├── notifications.py     # Windows notifications
│   ├── app_reactions.py     # Reactions to active app changes
│   ├── mood_pet.py          # Mood state machine
│   ├── coop.py              # Local network co-op
│   ├── minigame.py          # Daily mini-game
│   ├── seasonal.py          # Seasonal skins and greetings
│   ├── share_card.py        # Share card image export
│   └── weekly_report.py     # Weekly summary generator
│
├── ui/
│   ├── app_window.py        # Main floating window
│   ├── cat_widget.py        # Animated Bongo Cat widget
│   ├── profile_window.py    # Profile, XP, quests
│   ├── report_window.py     # Weekly report window
│   ├── productivity_window.py
│   ├── diary_window.py
│   └── prestige_window.py
│
└── data/                    # Local user data (not committed)
    ├── history.json
    ├── progress.json
    ├── productivity.json
    ├── weekly_report.json
    └── user_settings.json   # Created by first-run wizard
```

---

## Configuration

All settings live in `config.py`. Key options:

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `gemma3` | Model to use: gemma3, mistral, phi3, llama3 |
| `LANGUAGE` | auto | Loaded from `data/user_settings.json` |
| `SCREEN_CAPTURE_ENABLED` | `True` | Enable/disable OCR |
| `SCREEN_CAPTURE_INTERVAL` | `30` | Seconds between screen captures |
| `ALWAYS_ON_TOP` | `True` | Keep window above others |
| `HOTKEY_TOGGLE` | `ctrl+alt+b` | Hotkey to show/hide chat |
| `SAVE_HISTORY` | `True` | Persist chat history locally |
| `HISTORY_MAX_DAYS` | `7` | Days to keep chat history |
| `PROACTIVE_ENABLED` | `True` | Cat messages you when you go quiet |
| `PROACTIVE_SILENCE_MIN` | `3` | Minutes of silence before first proactive message |
| `SCREEN_BLACKLIST` | `[...]` | Apps that are never captured (password managers, etc.) |

---

## Language Support

The interface and the cat's responses are fully localized in **Russian** and **English**. The language is chosen during the first-run wizard and saved to `data/user_settings.json`. To switch language later, edit that file or delete `data/.setup_done` to re-run the wizard.

---

## Privacy

- All processing happens **locally** on your machine
- Screenshots are analyzed in memory and never saved to disk
- Chat history is stored only in `data/history.json` on your PC
- Passwords, emails, and card numbers are filtered from screen captures
- Screen capture can be disabled at any time via the 🔒 button
- The 🗑 button deletes all chat history

---

## Building an EXE

Uses PyInstaller. Run from the project folder:

```bash
pip install pyinstaller
python -m PyInstaller --onedir --noconsole --name BongoCatAI main.py
```

The output will be in `dist/BongoCatAI/`. Distribute the entire folder.

---

## Crisis Support

If certain keywords are detected in the conversation, Bongo Cat immediately provides crisis hotline information:

- 🇷🇺 **8-800-2000-122** (Russia, free, 24/7)
- 🇺🇸 **988** (US Suicide & Crisis Lifeline, call or text)
- 🌍 [findahelpline.com](https://findahelpline.com) for other countries

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

MIT
