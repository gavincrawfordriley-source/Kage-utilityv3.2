"""
Splash screen shown for ~2 seconds on launch.
Uses the user-provided logo (splash_source.png) with a fade-in effect.
"""
import os
import sys
import tkinter as tk
import customtkinter as ctk
from PIL import Image


def _asset_path(name):
    """Resolve asset both in dev and PyInstaller-frozen mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


class Splash(ctk.CTkToplevel):
    """
    Frameless, centered splash. Fades in the logo then closes.
    Call Splash.show(root, on_done_callback) — on_done fires when it closes.
    """
    def __init__(self, master, on_done):
        super().__init__(master)
        self.on_done = on_done
        self.overrideredirect(True)          # no titlebar
        self.configure(fg_color="#07040d")
        self.attributes("-topmost", True)

        W, H = 460, 460
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw - W)//2}+{(sh - H)//2}")

        # Try to load logo
        logo_path = _asset_path("splash_source.png")
        if not os.path.exists(logo_path):
            logo_path = _asset_path("icon.png")

        try:
            pil = Image.open(logo_path).convert("RGBA")
            pil.thumbnail((W - 20, H - 60), Image.LANCZOS)
            self._img = ctk.CTkImage(light_image=pil, dark_image=pil,
                                     size=pil.size)
            self._label = ctk.CTkLabel(self, text="", image=self._img,
                                       fg_color="#07040d")
        except Exception:
            self._label = ctk.CTkLabel(
                self, text="KAGE UTILITY",
                font=("Rajdhani", 42, "bold"),
                text_color="#a05aff", fg_color="#07040d",
            )
        self._label.pack(expand=True, fill="both", padx=10, pady=(10, 4))

        self._tag = ctk.CTkLabel(
            self, text="Move like a shadow  \u5F71",
            font=("Rajdhani", 14, "bold"),
            text_color="#6c5a85", fg_color="#07040d",
        )
        self._tag.pack(pady=(0, 20))

        # Start fade
        self.attributes("-alpha", 0.0)
        self._alpha = 0.0
        self._fade_in()

    def _fade_in(self):
        self._alpha += 0.08
        if self._alpha >= 1.0:
            self._alpha = 1.0
            self.attributes("-alpha", 1.0)
            self.after(1400, self._close)          # visible time
        else:
            self.attributes("-alpha", self._alpha)
            self.after(30, self._fade_in)

    def _close(self):
        try:
            self.destroy()
        finally:
            if self.on_done:
                self.on_done()

    @classmethod
    def show(cls, master, on_done):
        try:
            cls(master, on_done)
        except Exception:
            # if splash fails for any reason, jump straight to the app
            if on_done:
                on_done()
