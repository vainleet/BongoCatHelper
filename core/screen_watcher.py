"""
core/screen_watcher.py
Vision-анализ экрана через llava (Ollama) или Claude API.
Промпт на английском — llava отвечает конкретно, без отказов.
"""

import threading, time, ctypes, ctypes.wintypes, base64, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    from PIL import ImageGrab, Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    _u32 = ctypes.windll.user32
    _k32 = ctypes.windll.kernel32
    _HAS_WIN = True
except Exception:
    _HAS_WIN = False


# ── Windows API ───────────────────────────────────────────
def get_active_window_title() -> str:
    if not _HAS_WIN: return ""
    try:
        hwnd = _u32.GetForegroundWindow()
        n = _u32.GetWindowTextLengthW(hwnd)
        if not n: return ""
        buf = ctypes.create_unicode_buffer(n + 1)
        _u32.GetWindowTextW(hwnd, buf, n + 1)
        return buf.value
    except: return ""

def get_active_process_name() -> str:
    if not _HAS_WIN: return ""
    try:
        hwnd = _u32.GetForegroundWindow()
        pid  = ctypes.wintypes.DWORD()
        _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = _k32.OpenProcess(0x1000, False, pid.value)
        if not h: return ""
        buf  = ctypes.create_unicode_buffer(260)
        size = ctypes.wintypes.DWORD(260)
        _k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size))
        _k32.CloseHandle(h)
        return os.path.basename(buf.value).lower() if buf.value else ""
    except: return ""

def is_blacklisted(title: str) -> bool:
    return any(b.lower() in title.lower() for b in config.SCREEN_BLACKLIST)

def categorize_window(title: str, proc: str = "") -> str:
    c = (title + " " + proc).lower()
    if any(w in c for w in ["vscode","visual studio","pycharm","sublime","notepad++","vim","terminal","cmd","powershell","python","code.exe","cursor"]): return "code"
    if any(w in c for w in ["chrome","firefox","edge","opera","brave","yandex","vivaldi","msedge.exe"]): return "browser"
    if any(w in c for w in ["youtube","vlc","netflix","twitch","spotify","mpv","potplayer","video","music","кино"]): return "media"
    if any(w in c for w in ["word","excel","powerpoint","notion","obsidian","документ","pdf","acrobat"]): return "docs"
    if any(w in c for w in ["steam","minecraft","roblox","valorant","cs2","dota","fortnite","pubg","игра","game"]): return "game"
    if any(w in c for w in ["telegram","discord","whatsapp","вконтакте","instagram","twitter","slack","zoom","viber"]): return "social"
    return ""


# ── Скриншот → base64 ────────────────────────────────────
def take_screenshot_b64(max_width: int = 1024) -> str:
    if not HAS_PIL: return ""
    try:
        img = ImageGrab.grab()
        w, h = img.size
        if w > max_width:
            img = img.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=72)
        return base64.b64encode(buf.getvalue()).decode()
    except: return ""


# ── Промпт (английский — llava работает точнее) ──────────
# Русский промпт заставляет llava "думать" на украинском/русском
# и часто отказываться. Английский даёт конкретные факты.
VISION_PROMPT = (
    "Describe this screenshot in ONE sentence (max 12 words). "
    "Be specific: name the exact website, game, app or file. "
    "Examples: 'Playing Minecraft', 'Watching YouTube', 'Writing Python in VSCode', "
    "'Reading Reddit thread about cats', 'Browsing Steam store'. "
    "Just the fact. Do not refuse. Do not explain."
)

# Простой словарь EN→RU для самых частых слов
_TR = {
    "playing": "играет в", "watching": "смотрит", "reading": "читает",
    "writing": "пишет", "browsing": "сидит в", "coding": "пишет код",
    "editing": "редактирует", "working on": "работает над",
    "searching for": "ищет", "chatting on": "общается в",
    "using": "использует", "opening": "открывает",
    "downloading": "скачивает", "scrolling": "листает",
    "looking at": "смотрит на",
}

# Фразы-отказы которые нужно игнорировать
_REFUSALS = [
    "i cannot", "i can't", "i'm unable", "i am unable",
    "i'm sorry", "i am sorry", "sorry, i", "as an ai",
    "я не могу", "не можу", "вибачте", "извините",
    "i don't see", "i cannot see", "no image",
]

def _clean_vision(text: str) -> str:
    """
    Убираем отказы и мусор из ответа llava.
    Оставляем только конкретное описание.
    """
    if not text: return ""
    low = text.lower()

    # Если это отказ — выбрасываем
    if any(r in low for r in _REFUSALS):
        return ""

    # Убираем лишние кавычки и переносы
    text = text.strip().strip('"').strip("'")

    # Если слишком длинно — берём первое предложение
    for sep in [".", "\n", "!"]:
        if sep in text:
            text = text.split(sep)[0].strip()
            break

    # Лёгкий перевод частых глаголов
    low2 = text.lower()
    for en, ru in _TR.items():
        if low2.startswith(en + " ") or low2.startswith(en.capitalize() + " "):
            text = ru + " " + text[len(en):].strip()
            break

    return text if len(text) > 3 else ""


# ── Ollama vision ─────────────────────────────────────────
VISION_MODELS_PRIORITY = [
    "llava", "minicpm-v", "llava-phi3", "moondream",
    "llava:7b", "llava:13b", "gemma3:12b",
]

def _find_vision_model() -> str:
    if not HAS_REQUESTS: return ""
    try:
        r = _req.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code != 200: return ""
        installed = [m["name"] for m in r.json().get("models", [])]
        for candidate in VISION_MODELS_PRIORITY:
            base = candidate.split(":")[0]
            for m in installed:
                if base in m.lower():
                    return m
    except: pass
    return ""

def _analyze_ollama(b64: str, model: str) -> str:
    if not (HAS_REQUESTS and b64 and model): return ""
    try:
        r = _req.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": VISION_PROMPT,
            "images": [b64],
            "stream": False,
            "options": {
                "temperature": 0.1,   # ниже = конкретнее
                "num_predict": 40,    # короче = без лишних слов
                "top_p": 0.9,
            },
        }, timeout=30)
        if r.status_code == 200:
            raw = r.json().get("response", "").strip()
            return _clean_vision(raw)
    except: pass
    return ""


# ── Claude API vision (fallback) ─────────────────────────
def _analyze_claude(b64: str, api_key: str) -> str:
    if not (HAS_REQUESTS and b64 and api_key): return ""
    try:
        r = _req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 60,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": b64,
                        }},
                        {"type": "text", "text": VISION_PROMPT},
                    ]
                }]
            },
            timeout=15,
        )
        if r.status_code == 200:
            raw = "".join(
                b.get("text","") for b in r.json().get("content",[])
                if b.get("type") == "text"
            ).strip()
            return _clean_vision(raw)
    except: pass
    return ""


# ── Главный класс ─────────────────────────────────────────
class ScreenWatcher:
    def __init__(self):
        self.last_context   = ""
        self.last_window    = ""
        self.last_category  = ""
        self.last_vision    = ""
        self._vision_model  = ""
        self._use_claude    = False
        self._enabled = config.SCREEN_CAPTURE_ENABLED
        self._running = False
        self._thread  = None
        self._lock    = threading.Lock()

    @property
    def enabled(self): return self._enabled

    @property
    def has_vision(self): return bool(self._vision_model) or self._use_claude

    def start(self):
        self._running      = True
        self._vision_model = _find_vision_model()
        api_key = getattr(config, "CLAUDE_API_KEY", "")
        if not self._vision_model and api_key:
            self._use_claude = True

        if self._vision_model:
            print(f"  🎨  Vision: [{self._vision_model}] — английский промпт")
        elif self._use_claude:
            print("  🎨  Vision: Claude API")
        else:
            print("  👁  Vision не найден. Запусти: ollama pull llava")

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self): self._running = False

    def pause(self):
        self._enabled = False
        with self._lock:
            self.last_context = self.last_window = self.last_category = self.last_vision = ""

    def resume(self): self._enabled = True

    def _loop(self):
        time.sleep(5)
        self._capture()
        while self._running:
            time.sleep(config.SCREEN_CAPTURE_INTERVAL)
            if self._enabled:
                self._capture()

    def _capture(self):
        if not self._enabled: return
        try:
            title = get_active_window_title()
            proc  = get_active_process_name()
            cat   = categorize_window(title, proc)
            vision = ""

            if not is_blacklisted(title) and HAS_PIL:
                b64 = take_screenshot_b64()
                if b64:
                    if self._vision_model:
                        vision = _analyze_ollama(b64, self._vision_model)
                    elif self._use_claude:
                        vision = _analyze_claude(b64, getattr(config, "CLAUDE_API_KEY", ""))

            with self._lock:
                self.last_window   = title
                self.last_category = cat
                if vision:
                    self.last_vision  = vision
                    self.last_context = vision
                    print(f"  🎨  [{vision}]")
                else:
                    self.last_vision = ""
                    parts = []
                    if title: parts.append(f"Активное окно: {title}")
                    if proc:  parts.append(f"Приложение: {proc}")
                    self.last_context = "\n".join(parts)
                    if not vision and (self._vision_model or self._use_claude):
                        print(f"  ⚠  Vision вернул пустой ответ (заголовок: {title[:40]})")
        except Exception as e:
            print(f"  ⚠ capture: {e}")

    @property
    def status(self) -> str:
        if not self._enabled: return "⏸ приостановлен"
        if self._vision_model: mode = f"🎨 {self._vision_model.split(':')[0]}"
        elif self._use_claude:  mode = "🎨 Claude API"
        else:                   mode = "👁 заголовки"
        w = self.last_window
        s = (w[:22]+"...") if len(w)>22 else w
        return f"{mode} · {s or '...'}"
