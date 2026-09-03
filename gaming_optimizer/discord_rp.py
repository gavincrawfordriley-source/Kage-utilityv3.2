"""
Discord Rich Presence — optional. Silently no-ops if pypresence isn't
installed or Discord isn't running. Uses a public Discord application ID
placeholder — swap DISCORD_CLIENT_ID for your own once you create one at
https://discord.com/developers/applications
"""
import time
import threading

# Replace with your own after creating an app at discord.com/developers
DISCORD_CLIENT_ID = "1234567890123456789"

try:
    from pypresence import Presence
    _HAS_RP = True
except Exception:
    _HAS_RP = False


class RichPresence:
    def __init__(self):
        self.rpc = None
        self.start_time = int(time.time())
        self._connected = False

    @property
    def available(self):
        return _HAS_RP

    def connect_async(self):
        if not _HAS_RP:
            return
        threading.Thread(target=self._connect, daemon=True).start()

    def _connect(self):
        try:
            self.rpc = Presence(DISCORD_CLIENT_ID)
            self.rpc.connect()
            self._connected = True
            self.update("Optimizing with Kage", "\u5F71 Move like a shadow")
        except Exception:
            self._connected = False
            self.rpc = None

    def update(self, state, details):
        if not self._connected or not self.rpc:
            return
        try:
            self.rpc.update(
                state=state,
                details=details,
                start=self.start_time,
                large_image="kage_logo",
                large_text="Kage Utility",
            )
        except Exception:
            pass

    def close(self):
        try:
            if self.rpc:
                self.rpc.close()
        except Exception:
            pass
        self._connected = False
