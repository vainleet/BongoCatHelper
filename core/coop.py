"""
core/coop.py
Совместные коты — два пользователя в одной сети видят котов друг друга.
Работает через UDP broadcast, полностью локально.
"""
import socket, threading, json, time, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

COOP_PORT    = 47842
BCAST_ADDR   = "255.255.255.255"
PING_INTERVAL = 5    # секунд между пингами
PEER_TIMEOUT  = 15   # секунд до считать пира оффлайн


class CoopSystem:
    """
    Рассылает UDP broadcast со своим статусом и слушает других котов в сети.
    Когда находит пира — вызывает on_peer_message(name, message, mood).
    """

    def __init__(self, cat_name: str, on_peer_message):
        self.cat_name        = cat_name
        self._on_peer        = on_peer_message
        self._peers: dict    = {}   # {addr: {name, message, mood, last_seen}}
        self._running        = False
        self._sock           = None
        self._my_message     = "Привет! 🐱"
        self._my_mood        = "idle"
        self._my_level       = 1

    def start(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(("", COOP_PORT))
            self._sock.settimeout(1.0)
            self._running = True
            threading.Thread(target=self._recv_loop, daemon=True).start()
            threading.Thread(target=self._send_loop, daemon=True).start()
            print(f"  🐱🐱 Coop запущен — ищем котов в сети...")
        except Exception as e:
            print(f"  ⚠ Coop не запустился: {e}")

    def stop(self):
        self._running = False
        if self._sock:
            try: self._sock.close()
            except: pass

    def set_status(self, message: str, mood: str, level: int = 1):
        self._my_message = message[:80]
        self._my_mood    = mood
        self._my_level   = level

    def get_peers(self) -> list:
        """Список активных пиров."""
        now    = time.time()
        active = {a: p for a, p in self._peers.items()
                  if now - p["last_seen"] < PEER_TIMEOUT}
        self._peers = active
        return list(active.values())

    def _make_packet(self) -> bytes:
        return json.dumps({
            "name":    self.cat_name,
            "message": self._my_message,
            "mood":    self._my_mood,
            "level":   self._my_level,
            "ts":      time.time(),
        }, ensure_ascii=False).encode("utf-8")

    def _send_loop(self):
        while self._running:
            try:
                pkt = self._make_packet()
                self._sock.sendto(pkt, (BCAST_ADDR, COOP_PORT))
            except Exception:
                pass
            time.sleep(PING_INTERVAL)

    def _recv_loop(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(1024)
                ip = addr[0]
                # Игнорируем свои пакеты
                if self._is_self(ip):
                    continue
                pkt = json.loads(data.decode("utf-8"))
                is_new = ip not in self._peers
                self._peers[ip] = {
                    "addr":      ip,
                    "name":      pkt.get("name", "Кот"),
                    "message":   pkt.get("message", ""),
                    "mood":      pkt.get("mood", "idle"),
                    "level":     pkt.get("level", 1),
                    "last_seen": time.time(),
                }
                if is_new:
                    # Новый кот в сети!
                    peer = self._peers[ip]
                    self._on_peer(peer["name"], peer["message"], peer["mood"])
            except socket.timeout:
                pass
            except Exception:
                pass

    def _is_self(self, ip: str) -> bool:
        try:
            local = socket.gethostbyname(socket.gethostname())
            return ip == local or ip == "127.0.0.1"
        except Exception:
            return False
