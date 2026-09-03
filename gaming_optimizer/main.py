"""
FragBoost — Windows 11 Gaming Optimizer
Modern dark GUI with free/premium tweaks + unlock-code system.
"""
import os
import sys
import ctypes
import threading
import platform
import customtkinter as ctk
from tkinter import messagebox

if getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimizations import TWEAKS, CATEGORIES, is_admin
from licensing import (
    submit_code, is_unlocked, is_owner_revoked, is_owner_session,
)
from settings_ui import SettingsDialog, get_theme
import history
import updater
from splash import Splash
from tray import TrayController
from discord_rp import RichPresence

APP_NAME = "Kage Utility"
APP_VER = "1.3"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

CATEGORY_ICONS = {
    "CPU & Power": "\u26A1",
    "Network": "\U0001F310",
    "GPU / DirectX": "\U0001F3AE",
    "Input": "\U0001F5B1",
    "System": "\U0001F680",
    "Gaming": "\U0001F3AE",
    "Visuals": "\u2728",
    "Startup": "\U0001F510",
    "Disk": "\U0001F4BE",
    "Privacy": "\U0001F576",
    "Audio": "\U0001F3B5",
}


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


# ============================================================
# Tweak card
# ============================================================
class TweakCard(ctk.CTkFrame):
    def __init__(self, master, tweak, on_change, unlocked, theme):
        self.tweak = tweak
        self.on_change = on_change
        self.unlocked = unlocked
        self.theme = theme
        locked_visual = tweak["locked"] and not unlocked
        self.locked_visual = locked_visual

        super().__init__(
            master,
            fg_color=theme["CARD_LOCKED"] if locked_visual else theme["CARD"],
            corner_radius=12,
            border_width=1,
            border_color=theme["BORDER"],
        )
        self._build()
        self.refresh_status()

    def _build(self):
        t = self.theme
        self.grid_columnconfigure(1, weight=1)

        title_color = t["TEXT_LOCKED"] if self.locked_visual else t["TEXT"]
        desc_color = t["MUTED_LOCKED"] if self.locked_visual else t["MUTED"]
        icon_color = t["MUTED_LOCKED"] if self.locked_visual else t["ACCENT"]

        icon = ctk.CTkLabel(self, text=self.tweak["icon"],
                            font=("Segoe UI Emoji", 22),
                            text_color=icon_color, width=36)
        icon.grid(row=0, column=0, rowspan=2, padx=(14, 8), pady=12, sticky="n")

        title_text = self.tweak["title"]
        if self.tweak["locked"]:
            title_text = ("\U0001F512  " if self.locked_visual else "\u2728  ") + title_text

        title = ctk.CTkLabel(self, text=title_text,
                             font=("Rajdhani", 15, "bold"),
                             text_color=title_color, anchor="w")
        title.grid(row=0, column=1, sticky="ew", pady=(12, 0))

        desc = ctk.CTkLabel(self, text=self.tweak["desc"],
                            font=("Inter", 11), text_color=desc_color,
                            anchor="w", justify="left", wraplength=460)
        desc.grid(row=1, column=1, sticky="ew", pady=(2, 12))

        self.status_dot = ctk.CTkLabel(self, text="\u25CF",
                                       font=("Segoe UI", 12),
                                       text_color=t["MUTED_LOCKED"] if self.locked_visual else t["MUTED"])
        self.status_dot.grid(row=0, column=2, padx=(0, 2), pady=(16, 0), sticky="e")

        self.status_text = ctk.CTkLabel(self, text="OFF",
                                        font=("Rajdhani", 11, "bold"),
                                        text_color=t["MUTED_LOCKED"] if self.locked_visual else t["MUTED"],
                                        width=32)
        self.status_text.grid(row=0, column=3, padx=(0, 10), pady=(16, 0), sticky="e")

        self.switch = ctk.CTkSwitch(
            self, text="", command=self._toggle,
            progress_color=t["GOLD"] if self.tweak["locked"] else t["ACCENT"],
            button_color=t["TEXT"], button_hover_color=t["ACCENT"],
            fg_color="#242a33", width=44,
        )
        self.switch.grid(row=1, column=2, columnspan=2,
                         padx=(0, 14), pady=(0, 10), sticky="e")

        if self.locked_visual:
            self.switch.configure(state="disabled")

    def refresh_status(self):
        t = self.theme
        if self.locked_visual:
            self.status_dot.configure(text_color=t["MUTED_LOCKED"])
            self.status_text.configure(text="LOCKED", text_color=t["MUTED_LOCKED"])
            return
        try:
            state = self.tweak["status"]()
        except Exception:
            state = "off"
        applied = state == "on"
        if applied:
            self.switch.select()
            color = t["GOLD"] if self.tweak["locked"] else t["ACCENT"]
            self.status_dot.configure(text_color=color)
            self.status_text.configure(text="ON", text_color=color)
        else:
            self.switch.deselect()
            self.status_dot.configure(text_color=t["MUTED"])
            self.status_text.configure(text="OFF", text_color=t["MUTED"])

    def _toggle(self):
        if self.locked_visual:
            return
        self.on_change(self.tweak, bool(self.switch.get()), self)


# ============================================================
# Unlock dialog
# ============================================================
class UnlockDialog(ctk.CTkToplevel):
    def __init__(self, master, theme, on_result):
        super().__init__(master)
        self.theme = theme
        self.on_result = on_result
        self.title("Enter Code")
        self.geometry("440x290")
        self.resizable(False, False)
        self.configure(fg_color=theme["BG"])
        self.transient(master)
        self.grab_set()

        ctk.CTkLabel(self, text="\U0001F512  ENTER UNLOCK CODE",
                     font=("Rajdhani", 20, "bold"),
                     text_color=theme["GOLD"]).pack(pady=(28, 4))

        ctk.CTkLabel(self,
                     text="Premium code unlocks all 53 tweaks on this PC.",
                     font=("Inter", 11), text_color=theme["MUTED"]).pack(pady=(0, 20))

        self.entry = ctk.CTkEntry(self, width=280, height=44,
                                  font=("JetBrains Mono", 16),
                                  justify="center", show="",
                                  placeholder_text="XXXXXX",
                                  fg_color=theme["CARD"], border_color=theme["BORDER"])
        self.entry.pack(pady=(0, 6))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self._submit())

        self.msg = ctk.CTkLabel(self, text="", font=("Inter", 11),
                                text_color=theme["MUTED"], wraplength=380)
        self.msg.pack(pady=(6, 10))

        btns = ctk.CTkFrame(self, fg_color=theme["BG"])
        btns.pack(pady=(4, 20))
        ctk.CTkButton(btns, text="Cancel", command=self.destroy,
                      fg_color="#242a33", hover_color="#2f3742",
                      text_color=theme["TEXT"], width=110, height=36,
                      font=("Rajdhani", 13, "bold")).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="SUBMIT", command=self._submit,
                      fg_color=theme["GOLD"], hover_color="#dbaf3e",
                      text_color="#141005", width=110, height=36,
                      font=("Rajdhani", 13, "bold")).pack(side="left", padx=6)

    def _submit(self):
        level, message = submit_code(self.entry.get())
        t = self.theme
        color = t["ACCENT"] if level in ("unlock", "owner_unlock", "already") else (
            t["GOLD"] if level == "owner_revoke" else t["DANGER"]
        )
        self.msg.configure(text=message, text_color=color)
        if level in ("unlock", "owner_unlock", "owner_revoke"):
            self.after(1100, lambda: (self.on_result(), self.destroy()))


# ============================================================
# Main App
# ============================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_name, self.theme = get_theme()
        self.title(f"{APP_NAME} \u2014 Windows Gaming Optimizer")
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if getattr(sys, "frozen", False):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico") if hasattr(sys, "_MEIPASS") else icon_path
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        self.geometry("980x840")
        self.minsize(880, 700)
        self.configure(fg_color=self.theme["BG"])
        self.cards = []
        self.tray = TrayController(self)
        self.rp = RichPresence()
        self._build_ui()
        self._check_platform()
        # Async update check
        updater.check_async(self._on_update_available)
        # Start tray + Discord in background
        self.tray.start()
        self.rp.connect_async()
        # Hide close = minimize to tray (if tray available)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _unlocked(self):
        return is_unlocked()

    def _build_ui(self):
        t = self.theme
        # ---------- Header ----------
        header = ctk.CTkFrame(self, fg_color=t["BG"], height=90)
        header.pack(fill="x", padx=28, pady=(22, 6))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="\u25B2",
                     font=("Segoe UI", 40, "bold"),
                     text_color=t["ACCENT"]).grid(row=0, column=0, rowspan=2,
                                                  padx=(0, 12), sticky="w")

        ctk.CTkLabel(header, text=APP_NAME,
                     font=("Rajdhani", 32, "bold"),
                     text_color=t["TEXT"], anchor="w").grid(row=0, column=1, sticky="sw")

        ctk.CTkLabel(header,
                     text="53 Windows tweaks \u2014 fully reversible. \u5F71  Move like a shadow.",
                     font=("Inter", 11), text_color=t["MUTED"],
                     anchor="w").grid(row=1, column=1, sticky="nw")

        # Badges (right)
        badges = ctk.CTkFrame(header, fg_color=t["BG"])
        badges.grid(row=0, column=2, rowspan=2, sticky="e")

        if self._unlocked():
            self.premium_badge = ctk.CTkLabel(
                badges, text="\u2605 PREMIUM",
                font=("Rajdhani", 12, "bold"),
                text_color=t["GOLD"], fg_color="#211a08", corner_radius=8,
                width=100, height=26,
            )
        else:
            self.premium_badge = ctk.CTkLabel(
                badges, text="FREE",
                font=("Rajdhani", 12, "bold"),
                text_color=t["MUTED"], fg_color="#161a1f", corner_radius=8,
                width=100, height=26,
            )
        self.premium_badge.pack(side="right", padx=(4, 0))

        admin_txt = "\u2713 ADMIN" if is_admin() else "\u26A0 NO ADMIN"
        admin_color = t["ACCENT"] if is_admin() else t["DANGER"]
        self.admin_badge = ctk.CTkLabel(
            badges, text=admin_txt, font=("Rajdhani", 12, "bold"),
            text_color=admin_color, fg_color="#141a1f", corner_radius=8,
            width=100, height=26,
        )
        self.admin_badge.pack(side="right", padx=(4, 4))

        if is_owner_session():
            self.owner_badge = ctk.CTkLabel(
                badges, text="\U0001F451 OWNER",
                font=("Rajdhani", 12, "bold"),
                text_color=t["GOLD"], fg_color="#211a08", corner_radius=8,
                width=90, height=26,
            )
            self.owner_badge.pack(side="right", padx=(4, 4))

        # ---------- Action bar ----------
        actions = ctk.CTkFrame(self, fg_color=t["BG"])
        actions.pack(fill="x", padx=28, pady=(6, 10))

        ctk.CTkButton(
            actions, text="\u26A1  APPLY ALL",
            command=self.apply_all,
            fg_color=t["ACCENT"], hover_color=t["ACCENT_DIM"], text_color="#0a0f0a",
            font=("Rajdhani", 14, "bold"), height=40, corner_radius=10, width=150,
        ).pack(side="left")

        ctk.CTkButton(
            actions, text="\u21BA  RESTORE ALL",
            command=self.restore_all,
            fg_color="#242a33", hover_color="#2f3742", text_color=t["TEXT"],
            font=("Rajdhani", 14, "bold"), height=40, corner_radius=10, width=140,
        ).pack(side="left", padx=(8, 0))

        # Undo last
        self.btn_undo = ctk.CTkButton(
            actions, text="\u238C  UNDO LAST",
            command=self.undo_last,
            fg_color="#2a1b47", hover_color="#3d2865", text_color=t["ACCENT"],
            font=("Rajdhani", 14, "bold"), height=40, corner_radius=10, width=140,
        )
        self.btn_undo.pack(side="left", padx=(8, 0))
        self._refresh_undo_state()

        if not self._unlocked():
            self.btn_unlock = ctk.CTkButton(
                actions, text="\U0001F512  ENTER CODE",
                command=self._open_unlock,
                fg_color=t["GOLD"], hover_color="#dbaf3e", text_color="#141005",
                font=("Rajdhani", 14, "bold"), height=40, corner_radius=10, width=150,
            )
            self.btn_unlock.pack(side="left", padx=(8, 0))
        else:
            self.btn_unlock = ctk.CTkButton(
                actions, text="\U0001F511  MANAGE CODE",
                command=self._open_unlock,
                fg_color="#242a33", hover_color="#2f3742", text_color=t["GOLD"],
                font=("Rajdhani", 13, "bold"), height=40, corner_radius=10, width=150,
            )
            self.btn_unlock.pack(side="left", padx=(8, 0))

        # Settings gear
        ctk.CTkButton(
            actions, text="\u2699  SETTINGS",
            command=self._open_settings,
            fg_color="#242a33", hover_color="#2f3742", text_color=t["TEXT"],
            font=("Rajdhani", 13, "bold"), height=40, corner_radius=10, width=140,
        ).pack(side="left", padx=(8, 0))

        if not is_admin():
            ctk.CTkButton(
                actions, text="\U0001F510  RUN AS ADMIN",
                command=relaunch_as_admin,
                fg_color=t["DANGER"], hover_color="#c44660", text_color="#150507",
                font=("Rajdhani", 13, "bold"), height=40, corner_radius=10, width=160,
            ).pack(side="right")

        # ---------- Scroll body ----------
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=t["BG"], corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=22, pady=(2, 4))

        self._render_cards()

        # ---------- Status bar ----------
        self.status_bar = ctk.CTkLabel(self, text=f"Ready.  Theme: {self.theme_name}",
                                       font=("Inter", 11),
                                       text_color=t["MUTED"], anchor="w")
        self.status_bar.pack(fill="x", padx=32, pady=(0, 12))

    def _render_cards(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.cards = []
        unlocked = self._unlocked()
        t = self.theme

        by_cat = {}
        for tw in TWEAKS:
            by_cat.setdefault(tw["category"], []).append(tw)

        for cat in CATEGORIES:
            items = by_cat.get(cat, [])
            if not items:
                continue

            header = ctk.CTkFrame(self.scroll, fg_color=t["BG"], height=36)
            header.pack(fill="x", pady=(14, 4), padx=6)
            cat_locked = items[0]["locked"] and not unlocked
            cat_color = t["GOLD"] if items[0]["locked"] else t["ACCENT"]
            icon = CATEGORY_ICONS.get(cat, "\u25CF")
            lock_marker = "  \U0001F512" if cat_locked else ("  \u2605" if items[0]["locked"] else "")
            ctk.CTkLabel(
                header,
                text=f"{icon}   {cat.upper()}{lock_marker}",
                font=("Rajdhani", 15, "bold"),
                text_color=cat_color if not cat_locked else t["MUTED_LOCKED"],
                anchor="w",
            ).pack(side="left")

            ctk.CTkLabel(
                header, text=f"{len(items)} tweaks",
                font=("Inter", 10),
                text_color=t["MUTED"], anchor="e",
            ).pack(side="right", padx=(0, 4))

            for tw in items:
                card = TweakCard(self.scroll, tw, self.on_toggle, unlocked, t)
                card.pack(fill="x", padx=6, pady=4)
                self.cards.append(card)

    def _on_close(self):
        """Hide to tray if available, otherwise quit."""
        if self.tray.available:
            try:
                self.withdraw()
                self.tray.notify("Kage Utility", "Still running \u2014 tray icon in the system tray.")
            except Exception:
                self.destroy()
        else:
            try:
                self.rp.close()
            except Exception:
                pass
            self.destroy()

    def _refresh_undo_state(self):
        if hasattr(self, "btn_undo"):
            if history.has_undo():
                last = history.peek()
                self.btn_undo.configure(
                    state="normal",
                    text=f"\u238C  UNDO: {last['title'][:18]}\u2026" if len(last["title"]) > 18 else f"\u238C  UNDO",
                )
            else:
                self.btn_undo.configure(state="disabled", text="\u238C  UNDO LAST")

    def undo_last(self):
        tw = history.pop()
        if not tw:
            return

        def worker():
            self.set_status(f"Undoing: {tw['title']}\u2026", self.theme["ACCENT"])
            try:
                tw["restore"]()
                self.set_status(f"\u21BA Undid: {tw['title']}", self.theme["MUTED"])
            except Exception as e:
                self.set_status(f"\u2717 Undo failed on '{tw['title']}': {e}",
                                self.theme["DANGER"])
            for card in self.cards:
                if card.tweak["id"] == tw["id"]:
                    card.refresh_status()
                    break
            self._refresh_undo_state()

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_available(self, info):
        # Called from a background thread — marshal to Tk main thread
        def show():
            msg = (
                f"Kage Utility {info['version']} is available "
                f"(you're on {updater.APP_VERSION}).\n\n"
                f"{info.get('notes', '')[:300] or 'Open the release page for details.'}\n\n"
                "Open the download page now?"
            )
            if messagebox.askyesno("Update available", msg):
                try:
                    import webbrowser
                    webbrowser.open(info["url"])
                except Exception:
                    pass

        self.after(600, show)

    def _check_platform(self):
        if platform.system() != "Windows":
            messagebox.showwarning(
                "Not Windows",
                "FragBoost is designed for Windows 11. On other platforms "
                "the tweaks will silently fail \u2014 nothing will be harmed."
            )
        if is_owner_revoked():
            self.set_status(
                "\U0001F451  Owner has revoked premium on this PC. Enter owner code to restore.",
                self.theme["DANGER"],
            )

    def set_status(self, msg, color=None):
        if color is None:
            color = self.theme["MUTED"]
        self.status_bar.configure(text=msg, text_color=color)

    def _open_unlock(self):
        UnlockDialog(self, self.theme, on_result=self._rebuild)

    def _open_settings(self):
        SettingsDialog(
            self, self.theme,
            on_theme_change=self._on_theme_change,
            on_profile_apply=self._apply_profile_ids,
        )

    def _on_theme_change(self, name):
        self.theme_name = name
        from settings_ui import get_theme as gt
        _, self.theme = gt()
        self.configure(fg_color=self.theme["BG"])
        self._rebuild()

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self.cards = []
        self._build_ui()

    def _apply_profile_ids(self, tweak_ids):
        unlocked = self._unlocked()

        def worker():
            applied = skipped = failed = 0
            for tid in tweak_ids:
                tw = next((x for x in TWEAKS if x["id"] == tid), None)
                if not tw:
                    continue
                if tw["locked"] and not unlocked:
                    skipped += 1
                    continue
                if tw.get("requires_admin") and not is_admin():
                    skipped += 1
                    continue
                self.set_status(f"Applying: {tw['title']}\u2026", self.theme["ACCENT"])
                try:
                    tw["apply"]()
                    applied += 1
                except Exception:
                    failed += 1
            for card in self.cards:
                card.refresh_status()
            self.set_status(
                f"\u2713 Profile applied: {applied} on, {skipped} skipped, {failed} failed.",
                self.theme["ACCENT"],
            )

        threading.Thread(target=worker, daemon=True).start()

    def on_toggle(self, tweak, wants_on, card):
        if tweak.get("requires_admin") and not is_admin():
            messagebox.showwarning(
                "Admin required",
                f"'{tweak['title']}' needs administrator rights.\n\n"
                "Click 'RUN AS ADMIN' to relaunch elevated."
            )
            card.refresh_status()
            return

        def worker():
            self.set_status(f"Working: {tweak['title']}\u2026", self.theme["ACCENT"])
            try:
                if wants_on:
                    result = tweak["apply"]()
                    history.record(tweak)
                    self.rp.update(f"Applied: {tweak['title'][:40]}",
                                   "Optimizing with Kage")
                    if tweak["id"] == "clean_temp" and isinstance(result, int):
                        mb = result / (1024 * 1024)
                        self.set_status(f"\u2713 Cleaned {mb:.1f} MB of temp files.",
                                        self.theme["ACCENT"])
                    else:
                        self.set_status(f"\u2713 Applied: {tweak['title']}",
                                        self.theme["ACCENT"])
                else:
                    tweak["restore"]()
                    history.drop(tweak["id"])
                    self.set_status(f"\u21BA Restored: {tweak['title']}",
                                    self.theme["MUTED"])
            except Exception as e:
                self.set_status(f"\u2717 Error on '{tweak['title']}': {e}",
                                self.theme["DANGER"])
            finally:
                card.refresh_status()
                self._refresh_undo_state()

        threading.Thread(target=worker, daemon=True).start()

    def apply_all(self):
        unlocked = self._unlocked()
        eligible = [c for c in self.cards if not (c.tweak["locked"] and not unlocked)]
        locked_count = len(self.cards) - len(eligible)

        confirm_text = (
            f"Apply {len(eligible)} tweaks?\n\n"
            "Every change is backed up and reversible via 'Restore All'."
        )
        if locked_count:
            confirm_text += f"\n\n\U0001F512 {locked_count} premium tweaks will be skipped."

        if not messagebox.askyesno("Apply all", confirm_text):
            return

        def worker():
            for card in eligible:
                tw = card.tweak
                if tw.get("requires_admin") and not is_admin():
                    self.set_status(f"Skipping (needs admin): {tw['title']}",
                                    self.theme["DANGER"])
                    continue
                self.set_status(f"Applying: {tw['title']}\u2026", self.theme["ACCENT"])
                try:
                    tw["apply"]()
                    history.record(tw)
                except Exception as e:
                    self.set_status(f"\u2717 {tw['title']}: {e}", self.theme["DANGER"])
                card.refresh_status()
            self._refresh_undo_state()
            self.set_status(
                "\u2713 Done. Reboot recommended for full effect.", self.theme["ACCENT"]
            )

        threading.Thread(target=worker, daemon=True).start()

    def restore_all(self):
        if not messagebox.askyesno(
            "Restore defaults",
            "Restore every setting FragBoost changed back to its original value?"
        ):
            return

        def worker():
            for card in self.cards:
                if card.locked_visual:
                    continue
                tw = card.tweak
                self.set_status(f"Restoring: {tw['title']}\u2026", self.theme["MUTED"])
                try:
                    tw["restore"]()
                except Exception as e:
                    self.set_status(f"\u2717 {tw['title']}: {e}", self.theme["DANGER"])
                card.refresh_status()
            history.clear()
            self._refresh_undo_state()
            self.set_status("\u21BA All settings restored.", self.theme["MUTED"])

        threading.Thread(target=worker, daemon=True).start()


def main():
    # Bootstrap: create a hidden root, show splash, then reveal the app.
    root = ctk.CTk()
    root.withdraw()  # hide the root while splash is up

    app_holder = {"app": None}

    def build_app():
        try:
            root.destroy()
        except Exception:
            pass
        app_holder["app"] = App()
        app_holder["app"].mainloop()

    Splash.show(root, on_done=build_app)
    root.mainloop()


if __name__ == "__main__":
    main()
