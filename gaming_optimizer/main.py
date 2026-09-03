"""
FragBoost — Windows 11 Gaming Optimizer
Modern CustomTkinter GUI, single-window, individual toggles + one-click apply/restore.
"""
import os
import sys
import ctypes
import threading
import platform
import customtkinter as ctk
from tkinter import messagebox

# Ensure we import from same folder when frozen
if getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimizations import TWEAKS, is_admin, clean_temp_files  # noqa

APP_NAME = "FragBoost"
APP_VER = "1.0"

# ---------- theme ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#0b0d10"
CARD = "#14181d"
CARD_HOVER = "#1a1f26"
ACCENT = "#7cff5a"      # neon green
ACCENT_DIM = "#4a9c37"
DANGER = "#ff5a7c"
MUTED = "#7d848d"
TEXT = "#e8ecef"


def relaunch_as_admin():
    if is_admin():
        return
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Admin required", f"Failed to elevate: {e}")


class TweakCard(ctk.CTkFrame):
    def __init__(self, master, tweak, on_change):
        super().__init__(master, fg_color=CARD, corner_radius=14, border_width=1,
                         border_color="#1f252c")
        self.tweak = tweak
        self.on_change = on_change
        self.applied = False
        self._build()
        self.refresh_status()

    def _build(self):
        self.grid_columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(self, text=self.tweak["icon"], font=("Segoe UI Emoji", 26),
                            text_color=ACCENT, width=44)
        icon.grid(row=0, column=0, rowspan=2, padx=(18, 10), pady=16, sticky="n")

        title = ctk.CTkLabel(self, text=self.tweak["title"],
                             font=("Rajdhani", 18, "bold"), text_color=TEXT, anchor="w")
        title.grid(row=0, column=1, sticky="ew", pady=(16, 0))

        desc = ctk.CTkLabel(self, text=self.tweak["desc"], font=("Inter", 12),
                            text_color=MUTED, anchor="w", justify="left", wraplength=460)
        desc.grid(row=1, column=1, sticky="ew", pady=(2, 16))

        self.status_dot = ctk.CTkLabel(self, text="\u25CF", font=("Segoe UI", 14),
                                       text_color=MUTED)
        self.status_dot.grid(row=0, column=2, padx=(0, 4), pady=(20, 0), sticky="e")

        self.status_text = ctk.CTkLabel(self, text="OFF", font=("Rajdhani", 12, "bold"),
                                        text_color=MUTED, width=38)
        self.status_text.grid(row=0, column=3, padx=(0, 12), pady=(20, 0), sticky="e")

        self.switch = ctk.CTkSwitch(
            self, text="", command=self._toggle,
            progress_color=ACCENT, button_color=TEXT,
            button_hover_color=ACCENT, fg_color="#242a33",
            width=52,
        )
        self.switch.grid(row=1, column=2, columnspan=2, padx=(0, 18), pady=(0, 14), sticky="e")

    def refresh_status(self):
        try:
            state = self.tweak["status"]()
        except Exception:
            state = "off"
        self.applied = (state == "on")
        if self.applied:
            self.switch.select()
            self.status_dot.configure(text_color=ACCENT)
            self.status_text.configure(text="ON", text_color=ACCENT)
        else:
            self.switch.deselect()
            self.status_dot.configure(text_color=MUTED)
            self.status_text.configure(text="OFF", text_color=MUTED)

    def _toggle(self):
        wants_on = bool(self.switch.get())
        self.on_change(self.tweak, wants_on, self)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} \u2014 Gaming Optimizer")
        self.geometry("880x760")
        self.minsize(820, 680)
        self.configure(fg_color=BG)
        self.cards = []
        self._build_ui()
        self._check_platform()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=BG, height=90)
        header.pack(fill="x", padx=28, pady=(24, 8))
        header.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkLabel(header, text="\u25B2", font=("Segoe UI", 42, "bold"),
                            text_color=ACCENT)
        logo.grid(row=0, column=0, rowspan=2, padx=(0, 14), sticky="w")

        title = ctk.CTkLabel(header, text=APP_NAME,
                             font=("Rajdhani", 34, "bold"), text_color=TEXT, anchor="w")
        title.grid(row=0, column=1, sticky="sw")

        sub = ctk.CTkLabel(header, text="Windows 11 gaming tweaks \u2014 one click, fully reversible.",
                           font=("Inter", 12), text_color=MUTED, anchor="w")
        sub.grid(row=1, column=1, sticky="nw")

        # Admin badge
        admin_txt = "\u2713 ADMIN" if is_admin() else "\u26A0 NO ADMIN"
        admin_color = ACCENT if is_admin() else DANGER
        self.admin_badge = ctk.CTkLabel(header, text=admin_txt,
                                        font=("Rajdhani", 12, "bold"),
                                        text_color=admin_color,
                                        fg_color="#141a1f", corner_radius=8,
                                        width=90, height=28)
        self.admin_badge.grid(row=0, column=2, rowspan=2, sticky="e", padx=(0, 4))

        # Action bar
        actions = ctk.CTkFrame(self, fg_color=BG)
        actions.pack(fill="x", padx=28, pady=(4, 12))

        self.btn_apply_all = ctk.CTkButton(
            actions, text="\u26A1  APPLY ALL", command=self.apply_all,
            fg_color=ACCENT, hover_color=ACCENT_DIM, text_color="#0a0f0a",
            font=("Rajdhani", 15, "bold"), height=42, corner_radius=10, width=170,
        )
        self.btn_apply_all.pack(side="left")

        self.btn_restore_all = ctk.CTkButton(
            actions, text="\u21BA  RESTORE ALL", command=self.restore_all,
            fg_color="#242a33", hover_color="#2f3742", text_color=TEXT,
            font=("Rajdhani", 15, "bold"), height=42, corner_radius=10, width=170,
        )
        self.btn_restore_all.pack(side="left", padx=(10, 0))

        if not is_admin():
            self.btn_admin = ctk.CTkButton(
                actions, text="\U0001F512  RUN AS ADMIN", command=relaunch_as_admin,
                fg_color=DANGER, hover_color="#c44660", text_color="#150507",
                font=("Rajdhani", 13, "bold"), height=42, corner_radius=10, width=170,
            )
            self.btn_admin.pack(side="right")

        # Scrollable list of tweak cards
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=22, pady=(4, 6))
        scroll._scrollbar.configure(button_color="#242a33", button_hover_color="#2f3742")

        for tweak in TWEAKS:
            card = TweakCard(scroll, tweak, self.on_toggle)
            card.pack(fill="x", padx=6, pady=6)
            self.cards.append(card)

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready.",
                                       font=("Inter", 11), text_color=MUTED, anchor="w")
        self.status_bar.pack(fill="x", padx=32, pady=(0, 14))

    def _check_platform(self):
        if platform.system() != "Windows":
            messagebox.showwarning(
                "Not Windows",
                "FragBoost is designed for Windows 11. It won't harm your system, "
                "but tweaks will silently fail on this platform."
            )

    def set_status(self, msg, color=MUTED):
        self.status_bar.configure(text=msg, text_color=color)

    def on_toggle(self, tweak, wants_on, card):
        if tweak.get("requires_admin") and not is_admin():
            messagebox.showwarning(
                "Admin required",
                f"'{tweak['title']}' needs administrator rights.\n\n"
                "Click 'RUN AS ADMIN' at the top-right to relaunch."
            )
            card.refresh_status()
            return

        def worker():
            self.set_status(f"Working on: {tweak['title']}...", ACCENT)
            try:
                if wants_on:
                    result = tweak["apply"]()
                    if tweak["id"] == "temp" and isinstance(result, int):
                        mb = result / (1024 * 1024)
                        self.set_status(f"\u2713 Cleaned {mb:.1f} MB of temp files.", ACCENT)
                    else:
                        self.set_status(f"\u2713 Applied: {tweak['title']}", ACCENT)
                else:
                    tweak["restore"]()
                    self.set_status(f"\u21BA Restored: {tweak['title']}", MUTED)
            except Exception as e:
                self.set_status(f"\u2717 Error: {e}", DANGER)
            finally:
                card.refresh_status()

        threading.Thread(target=worker, daemon=True).start()

    def apply_all(self):
        if not messagebox.askyesno(
            "Apply all tweaks",
            "This will apply every gaming optimization. "
            "Everything is reversible via 'Restore All'.\n\nContinue?"
        ):
            return

        def worker():
            for card in self.cards:
                tweak = card.tweak
                if tweak.get("requires_admin") and not is_admin():
                    self.set_status(f"Skipping (needs admin): {tweak['title']}", DANGER)
                    continue
                self.set_status(f"Applying: {tweak['title']}...", ACCENT)
                try:
                    tweak["apply"]()
                except Exception as e:
                    self.set_status(f"\u2717 {tweak['title']}: {e}", DANGER)
                card.refresh_status()
            self.set_status("\u2713 All tweaks applied. Reboot recommended for full effect.", ACCENT)

        threading.Thread(target=worker, daemon=True).start()

    def restore_all(self):
        if not messagebox.askyesno(
            "Restore defaults",
            "Restore every setting FragBoost changed back to its original value?"
        ):
            return

        def worker():
            for card in self.cards:
                tweak = card.tweak
                self.set_status(f"Restoring: {tweak['title']}...", MUTED)
                try:
                    tweak["restore"]()
                except Exception as e:
                    self.set_status(f"\u2717 {tweak['title']}: {e}", DANGER)
                card.refresh_status()
            self.set_status("\u21BA All settings restored. Reboot for full effect.", MUTED)

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
