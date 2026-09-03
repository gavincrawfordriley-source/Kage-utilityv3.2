"""
System tray integration using pystray. Falls back to a normal close if pystray
isn't available (e.g. non-Windows dev). No hard dep.
"""
import os
import sys
import threading

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    from PIL import Image
    _HAS_TRAY = True
except Exception:
    _HAS_TRAY = False


class TrayController:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self._thread = None

    @property
    def available(self):
        return _HAS_TRAY

    def _asset(self, name):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, name)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

    def start(self):
        if not _HAS_TRAY:
            return
        try:
            img = Image.open(self._asset("icon.png"))
        except Exception:
            return

        menu = Menu(
            Item("Show Kage", self._show, default=True),
            Item("Apply All", lambda: self._invoke("apply_all")),
            Item("Restore All", lambda: self._invoke("restore_all")),
            Item("Undo Last", lambda: self._invoke("undo_last")),
            Menu.SEPARATOR,
            Item("Quit", self._quit),
        )
        self.icon = pystray.Icon("KageUtility", img, "Kage Utility", menu)
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def _show(self, icon=None, item=None):
        try:
            self.app.after(0, self.app.deiconify)
            self.app.after(0, lambda: self.app.attributes("-topmost", True))
            self.app.after(200, lambda: self.app.attributes("-topmost", False))
        except Exception:
            pass

    def _invoke(self, name):
        fn = getattr(self.app, name, None)
        if fn:
            try:
                self.app.after(0, fn)
            except Exception:
                pass

    def _quit(self, icon=None, item=None):
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
        try:
            self.app.after(0, self.app.destroy)
        except Exception:
            pass

    def notify(self, title, msg):
        if self.icon:
            try:
                self.icon.notify(msg, title)
            except Exception:
                pass
