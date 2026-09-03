"""Settings modal with tabs: Themes / Profiles / Benchmark / Owner Console."""
import json
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from pathlib import Path

from themes import THEMES, DEFAULT_THEME
from optimizations import APPDIR, TWEAKS
import profiles as prof
import benchmark
import licensing

SETTINGS_FILE = APPDIR / "settings.json"


def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_settings(d):
    SETTINGS_FILE.write_text(json.dumps(d, indent=2))


def get_theme():
    name = load_settings().get("theme", DEFAULT_THEME)
    return name, THEMES.get(name, THEMES[DEFAULT_THEME])


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, theme, on_theme_change, on_profile_apply):
        super().__init__(master)
        self.theme = theme
        self.on_theme_change = on_theme_change
        self.on_profile_apply = on_profile_apply
        self.title("FragBoost Settings")
        self.geometry("720x580")
        self.minsize(680, 540)
        self.configure(fg_color=theme["BG"])
        self.transient(master)
        self.grab_set()

        # Tab view
        tabs = ctk.CTkTabview(
            self,
            fg_color=theme["BG"],
            segmented_button_fg_color=theme["CARD"],
            segmented_button_selected_color=theme["ACCENT"],
            segmented_button_selected_hover_color=theme["ACCENT_DIM"],
            segmented_button_unselected_color=theme["CARD"],
            segmented_button_unselected_hover_color=theme["BORDER"],
            text_color=theme["TEXT"],
        )
        tabs.pack(fill="both", expand=True, padx=16, pady=16)

        tabs.add("\U0001F3A8 Themes")
        tabs.add("\U0001F4CB Profiles")
        tabs.add("\U0001F4CA Benchmark")
        tabs.add("\u2699 System")
        # Customize tab: owner + partner only
        if licensing.is_owner_session() or licensing.is_partner():
            tabs.add("\U0001F3A8 Customize")
        if licensing.is_owner_session():
            tabs.add("\U0001F91D Partnership")
            tabs.add("\U0001F451 Owner")

        self._build_themes(tabs.tab("\U0001F3A8 Themes"))
        self._build_profiles(tabs.tab("\U0001F4CB Profiles"))
        self._build_benchmark(tabs.tab("\U0001F4CA Benchmark"))
        self._build_system(tabs.tab("\u2699 System"))
        if licensing.is_owner_session() or licensing.is_partner():
            self._build_customize(tabs.tab("\U0001F3A8 Customize"))
        if licensing.is_owner_session():
            self._build_partnership(tabs.tab("\U0001F91D Partnership"))
            self._build_owner(tabs.tab("\U0001F451 Owner"))

    # ---------- Themes ----------
    def _build_themes(self, parent):
        current, _ = get_theme()
        premium_unlocked = licensing.is_unlocked()
        ctk.CTkLabel(
            parent, text="Kage Skin Store",
            font=("Rajdhani", 18, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Free skins for everyone \u2014 premium skins unlock with FRAG42.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
        ).pack(anchor="w", pady=(0, 14))

        grid = ctk.CTkFrame(parent, fg_color=self.theme["BG"])
        grid.pack(fill="both", expand=True)

        for i, (name, t) in enumerate(THEMES.items()):
            row, col = divmod(i, 2)
            is_premium = t.get("premium", False)
            locked = is_premium and not premium_unlocked
            card = ctk.CTkFrame(
                grid, fg_color=t["CARD"], corner_radius=12,
                border_width=2 if name == current else 1,
                border_color=t["ACCENT"] if name == current else t["BORDER"],
                height=100,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1)

            title = ("\U0001F512  " if locked else ("\u2605  " if is_premium else "")) + name
            ctk.CTkLabel(
                card, text=title,
                font=("Rajdhani", 15, "bold"),
                text_color=t["MUTED"] if locked else t["ACCENT"],
            ).pack(anchor="w", padx=14, pady=(12, 2))

            sw = ctk.CTkFrame(card, fg_color=t["CARD"])
            sw.pack(anchor="w", padx=14, pady=(4, 8))
            for c in [t["ACCENT"], t["GOLD"], t["TEXT"], t["BG"], t["MUTED"]]:
                ctk.CTkFrame(sw, fg_color=c, width=22, height=22,
                             corner_radius=6, border_width=1,
                             border_color=t["BORDER"]).pack(side="left", padx=2)

            btn_text = "ACTIVE" if name == current else ("PREMIUM" if locked else "APPLY")
            btn = ctk.CTkButton(
                card, text=btn_text,
                command=(lambda n=name: self._apply_theme(n)) if not locked else self._premium_pop,
                fg_color=t["ACCENT"] if name != current and not locked else "#242a33",
                hover_color=t["ACCENT_DIM"],
                text_color="#0a0f0a" if name != current and not locked else t["MUTED"],
                font=("Rajdhani", 12, "bold"),
                height=28, width=90, corner_radius=8,
                state="disabled" if name == current else "normal",
            )
            btn.pack(anchor="e", padx=14, pady=(0, 10))

    def _premium_pop(self):
        messagebox.showinfo(
            "Premium skin",
            "This skin is part of the Kage Premium pack.\n\n"
            "Enter the FRAG42 code (main window \u2192 ENTER CODE) to unlock all premium skins."
        )

    def _apply_theme(self, name):
        s = load_settings()
        s["theme"] = name
        save_settings(s)
        self.on_theme_change(name)
        self.destroy()

    # ---------- Profiles ----------
    def _build_profiles(self, parent):
        ctk.CTkLabel(
            parent, text="Tweak Profiles",
            font=("Rajdhani", 18, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Apply presets or save your current setup as a named profile.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
        ).pack(anchor="w", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(
            parent, fg_color=self.theme["BG"], height=340,
        )
        scroll.pack(fill="both", expand=True)

        all_ids = {t["id"] for t in TWEAKS}
        for name, info in prof.list_profiles().items():
            valid = [tid for tid in info["tweaks"] if tid in all_ids]
            self._profile_row(scroll, name, info["builtin"], valid)

        # save current
        save_bar = ctk.CTkFrame(parent, fg_color=self.theme["BG"])
        save_bar.pack(fill="x", pady=(10, 4))
        ctk.CTkButton(
            save_bar, text="\U0001F4BE  SAVE CURRENT AS PROFILE",
            command=self._save_current,
            fg_color=self.theme["ACCENT"], hover_color=self.theme["ACCENT_DIM"],
            text_color="#0a0f0a",
            font=("Rajdhani", 13, "bold"), height=34, corner_radius=8,
        ).pack(side="left")

    def _profile_row(self, parent, name, builtin, tweak_ids):
        row = ctk.CTkFrame(
            parent, fg_color=self.theme["CARD"], corner_radius=10,
            border_width=1, border_color=self.theme["BORDER"],
        )
        row.pack(fill="x", padx=4, pady=4)

        info = ctk.CTkFrame(row, fg_color=self.theme["CARD"])
        info.pack(side="left", fill="x", expand=True, padx=14, pady=10)

        label = f"{name}  \u2022  {len(tweak_ids)} tweaks"
        if builtin:
            label += "  \u2022  built-in"
        ctk.CTkLabel(
            info, text=label,
            font=("Rajdhani", 13, "bold"),
            text_color=self.theme["ACCENT"] if builtin else self.theme["GOLD"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=", ".join(tweak_ids[:6]) + (" \u2026" if len(tweak_ids) > 6 else ""),
            font=("Inter", 10), text_color=self.theme["MUTED"],
            anchor="w", justify="left",
        ).pack(anchor="w")

        btns = ctk.CTkFrame(row, fg_color=self.theme["CARD"])
        btns.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btns, text="APPLY",
            command=lambda: self._apply_profile(name, tweak_ids),
            fg_color=self.theme["ACCENT"], hover_color=self.theme["ACCENT_DIM"],
            text_color="#0a0f0a",
            font=("Rajdhani", 11, "bold"), width=70, height=28, corner_radius=6,
        ).pack(side="left", padx=2)

        if not builtin:
            ctk.CTkButton(
                btns, text="\U0001F5D1",
                command=lambda: self._delete_profile(name),
                fg_color=self.theme["DANGER"], hover_color="#c44660",
                text_color="#150507",
                width=36, height=28, corner_radius=6,
                font=("Segoe UI", 12),
            ).pack(side="left", padx=2)

    def _apply_profile(self, name, tweak_ids):
        if not messagebox.askyesno(
            "Apply profile",
            f"Apply '{name}'?\n\n"
            f"This will enable {len(tweak_ids)} tweaks.\n"
            "Locked tweaks will be skipped without premium."
        ):
            return
        self.on_profile_apply(tweak_ids)
        self.destroy()

    def _delete_profile(self, name):
        if messagebox.askyesno("Delete profile", f"Delete '{name}'?"):
            prof.delete_profile(name)
            self.destroy()

    def _save_current(self):
        name = simpledialog.askstring(
            "Save profile", "Profile name:", parent=self,
        )
        if not name:
            return
        ids = prof.current_enabled_ids()
        if not ids:
            messagebox.showinfo("Nothing enabled",
                                "No tweaks are currently applied.")
            return
        if prof.save_profile(name, ids):
            messagebox.showinfo("Saved",
                                f"Saved '{name}' with {len(ids)} tweaks.")
            self.destroy()
        else:
            messagebox.showerror("Failed",
                                 "Name conflicts with a built-in or is empty.")

    # ---------- Benchmark ----------
    def _build_benchmark(self, parent):
        ctk.CTkLabel(
            parent, text="System Snapshot",
            font=("Rajdhani", 18, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Live check of every setting that matters for FPS.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
        ).pack(anchor="w", pady=(0, 12))

        self.bench_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=self.theme["BG"], height=380,
        )
        self.bench_scroll.pack(fill="both", expand=True)

        self._render_bench()

        ctk.CTkButton(
            parent, text="\u21BB  REFRESH SNAPSHOT",
            command=self._render_bench,
            fg_color=self.theme["ACCENT"], hover_color=self.theme["ACCENT_DIM"],
            text_color="#0a0f0a",
            font=("Rajdhani", 13, "bold"), height=34, corner_radius=8,
        ).pack(anchor="w", pady=(10, 4))

    def _render_bench(self):
        for w in self.bench_scroll.winfo_children():
            w.destroy()
        for label, value, good in benchmark.collect():
            row = ctk.CTkFrame(
                self.bench_scroll, fg_color=self.theme["CARD"],
                corner_radius=8, border_width=1, border_color=self.theme["BORDER"],
            )
            row.pack(fill="x", padx=4, pady=3)

            dot = "\u25CF"
            if good is True:
                dot_color = self.theme["ACCENT"]
            elif good is False:
                dot_color = self.theme["DANGER"]
            else:
                dot_color = self.theme["MUTED"]

            ctk.CTkLabel(row, text=dot, font=("Segoe UI", 14),
                         text_color=dot_color, width=24).pack(side="left", padx=(10, 4), pady=8)
            ctk.CTkLabel(row, text=label, font=("Rajdhani", 12, "bold"),
                         text_color=self.theme["TEXT"], anchor="w",
                         width=210).pack(side="left", pady=8)
            ctk.CTkLabel(row, text=str(value), font=("Inter", 11),
                         text_color=self.theme["MUTED"], anchor="w",
                         justify="left", wraplength=380).pack(side="left", fill="x",
                                                              expand=True, padx=(0, 12), pady=8)

    # ---------- System ----------
    def _build_system(self, parent):
        import startup as autostart

        ctk.CTkLabel(
            parent, text="System integration",
            font=("Rajdhani", 18, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Make Kage part of your Windows setup.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
        ).pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(
            parent, fg_color=self.theme["CARD"], corner_radius=12,
            border_width=1, border_color=self.theme["BORDER"],
        )
        card.pack(fill="x", padx=4, pady=6)

        ctk.CTkLabel(
            card, text="\U0001F680  Start with Windows",
            font=("Rajdhani", 14, "bold"),
            text_color=self.theme["TEXT"], anchor="w",
        ).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(
            card,
            text="Kage will boot silently to the system tray on login.",
            font=("Inter", 11), text_color=self.theme["MUTED"], anchor="w",
        ).pack(anchor="w", padx=16, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color=self.theme["CARD"])
        row.pack(anchor="w", padx=16, pady=(0, 14))

        enabled = autostart.is_enabled()
        self.startup_switch = ctk.CTkSwitch(
            row, text="Enabled" if enabled else "Disabled",
            command=self._toggle_autostart,
            progress_color=self.theme["ACCENT"],
            button_color=self.theme["TEXT"],
            button_hover_color=self.theme["ACCENT"],
            fg_color="#242a33",
            text_color=self.theme["TEXT"],
            font=("Rajdhani", 12, "bold"),
        )
        if enabled:
            self.startup_switch.select()
        self.startup_switch.pack(side="left")

        self.startup_msg = ctk.CTkLabel(
            card, text="", font=("Inter", 10),
            text_color=self.theme["MUTED"],
        )
        self.startup_msg.pack(anchor="w", padx=16, pady=(0, 10))

    def _toggle_autostart(self):
        import startup as autostart
        want = bool(self.startup_switch.get())
        ok = autostart.enable() if want else autostart.disable()
        if ok:
            self.startup_switch.configure(text="Enabled" if want else "Disabled")
            self.startup_msg.configure(
                text=("\u2713 Kage will now start with Windows (minimized to tray)."
                      if want else "\u21BA Auto-start disabled."),
                text_color=self.theme["ACCENT"] if want else self.theme["MUTED"],
            )
        else:
            self.startup_msg.configure(
                text="\u2717 Couldn't update Run key. Try Run as Admin.",
                text_color=self.theme["DANGER"],
            )

    # ---------- Owner Console ----------
    def _build_owner(self, parent):
        # Use a scrollable frame — content is now bigger with owner-code rotation
        scroll = ctk.CTkScrollableFrame(parent, fg_color=self.theme["BG"], corner_radius=0)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            scroll, text="\U0001F451  Owner Console",
            font=("Rajdhani", 20, "bold"),
            text_color=self.theme["GOLD"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            scroll,
            text="Rotate premium AND owner codes at runtime. Rotated codes persist on this PC only.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
            wraplength=640, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        # ===== Premium code section =====
        ctk.CTkLabel(
            scroll, text="\u2605  PREMIUM CODE",
            font=("Rajdhani", 14, "bold"),
            text_color=self.theme["GOLD"],
        ).pack(anchor="w", pady=(8, 4))

        current = licensing.get_secret_code()
        ctk.CTkLabel(
            scroll, text=f"Current premium code:  {current}",
            font=("JetBrains Mono", 12),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(0, 8))

        self.new_code_entry = ctk.CTkEntry(
            scroll, width=320, height=36,
            font=("JetBrains Mono", 13), justify="center",
            placeholder_text="e.g. FRAG2026",
            fg_color=self.theme["CARD"], border_color=self.theme["BORDER"],
        )
        self.new_code_entry.pack(anchor="w", pady=(2, 6))

        self.owner_msg = ctk.CTkLabel(
            scroll, text="", font=("Inter", 11),
            text_color=self.theme["MUTED"],
        )
        self.owner_msg.pack(anchor="w", pady=(0, 8))

        bar = ctk.CTkFrame(scroll, fg_color=self.theme["BG"])
        bar.pack(anchor="w")
        ctk.CTkButton(
            bar, text="ROTATE PREMIUM CODE", command=self._rotate,
            fg_color=self.theme["GOLD"], hover_color="#dbaf3e",
            text_color="#141005",
            font=("Rajdhani", 12, "bold"), width=200, height=32, corner_radius=8,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            bar, text="RESET DEFAULT", command=self._reset,
            fg_color="#242a33", hover_color="#2f3742",
            text_color=self.theme["TEXT"],
            font=("Rajdhani", 11, "bold"), width=140, height=32, corner_radius=8,
        ).pack(side="left")

        # ===== Owner code section =====
        ctk.CTkLabel(
            scroll, text="\U0001F451  OWNER CODE (Master Key)",
            font=("Rajdhani", 14, "bold"),
            text_color=self.theme["GOLD"],
        ).pack(anchor="w", pady=(24, 4))
        ctk.CTkLabel(
            scroll,
            text="Rotate your master key to hand out owner rights to a trusted mate. "
                 "Give them the current code, then rotate to something new so only you keep it.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
            wraplength=640, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        current_owner = licensing.get_owner_code()
        ctk.CTkLabel(
            scroll, text=f"Current owner code:  {current_owner}",
            font=("JetBrains Mono", 12),
            text_color=self.theme["GOLD"],
        ).pack(anchor="w", pady=(0, 8))

        self.new_owner_entry = ctk.CTkEntry(
            scroll, width=320, height=36,
            font=("JetBrains Mono", 13), justify="center",
            placeholder_text="e.g. shadow-lord-2026",
            fg_color=self.theme["CARD"], border_color=self.theme["BORDER"],
        )
        self.new_owner_entry.pack(anchor="w", pady=(2, 6))

        self.owner_code_msg = ctk.CTkLabel(
            scroll, text="", font=("Inter", 11),
            text_color=self.theme["MUTED"],
        )
        self.owner_code_msg.pack(anchor="w", pady=(0, 8))

        bar2 = ctk.CTkFrame(scroll, fg_color=self.theme["BG"])
        bar2.pack(anchor="w")
        ctk.CTkButton(
            bar2, text="ROTATE OWNER CODE", command=self._rotate_owner,
            fg_color=self.theme["GOLD"], hover_color="#dbaf3e",
            text_color="#141005",
            font=("Rajdhani", 12, "bold"), width=200, height=32, corner_radius=8,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            bar2, text="RESET DEFAULT", command=self._reset_owner,
            fg_color="#242a33", hover_color="#2f3742",
            text_color=self.theme["TEXT"],
            font=("Rajdhani", 11, "bold"), width=140, height=32, corner_radius=8,
        ).pack(side="left")

        # ===== Revoke section =====
        revoke_bar = ctk.CTkFrame(scroll, fg_color=self.theme["BG"])
        revoke_bar.pack(anchor="w", pady=(24, 0))

        ctk.CTkLabel(
            revoke_bar, text="Revocation state:",
            font=("Rajdhani", 12, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(side="left")

        state = "REVOKED" if licensing.is_owner_revoked() else "ACTIVE"
        color = self.theme["DANGER"] if licensing.is_owner_revoked() else self.theme["ACCENT"]
        ctk.CTkLabel(
            revoke_bar, text=f"  {state}",
            font=("Rajdhani", 12, "bold"), text_color=color,
        ).pack(side="left", padx=(4, 12))

        ctk.CTkButton(
            revoke_bar,
            text=("RE-ENABLE ON THIS PC" if licensing.is_owner_revoked() else "REVOKE THIS PC"),
            command=self._toggle_revoke,
            fg_color=self.theme["DANGER"] if not licensing.is_owner_revoked() else self.theme["ACCENT"],
            hover_color="#c44660",
            text_color="#150507",
            font=("Rajdhani", 12, "bold"), width=200, height=32, corner_radius=8,
        ).pack(side="left")

    def _rotate_owner(self):
        new = self.new_owner_entry.get().strip()
        if licensing.rotate_owner_code(new):
            self.owner_code_msg.configure(
                text=f"\u2713 Owner code rotated to '{new}'. Old owner code no longer works.",
                text_color=self.theme["ACCENT"],
            )
        else:
            self.owner_code_msg.configure(
                text="\u2717 Invalid code (3\u201340 chars, must not match premium or partner code).",
                text_color=self.theme["DANGER"],
            )

    def _reset_owner(self):
        licensing.reset_owner_code()
        self.owner_code_msg.configure(
            text="\u21BA Owner code reset to default (2006james).",
            text_color=self.theme["MUTED"],
        )

    def _rotate(self):
        new = self.new_code_entry.get().strip()
        if licensing.rotate_secret_code(new):
            self.owner_msg.configure(
                text=f"\u2713 Secret code rotated to '{new}'. Old code no longer works.",
                text_color=self.theme["ACCENT"],
            )
        else:
            self.owner_msg.configure(
                text="\u2717 Invalid code (3\u201340 chars, cannot match owner code).",
                text_color=self.theme["DANGER"],
            )

    def _reset(self):
        licensing.reset_secret_code()
        self.owner_msg.configure(
            text="\u21BA Secret code reset to default (FRAG42).",
            text_color=self.theme["MUTED"],
        )

    def _toggle_revoke(self):
        if licensing.is_owner_revoked():
            licensing.owner_reenable_pc()
        else:
            licensing.owner_revoke_pc()
        self.destroy()

    # ---------- Partnership Panel ----------
    def _build_partnership(self, parent):
        t = self.theme
        # Distinct cyan/teal accent for partner branding
        PARTNER_COLOR = "#2dd4bf"

        ctk.CTkLabel(
            parent, text="\U0001F91D  Partnership Panel",
            font=("Rajdhani", 20, "bold"),
            text_color=PARTNER_COLOR,
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Generate a rotatable code to grant partners access to the Partner tab "
                 "and exclusive tweaks. Old codes stop working after a rotation.",
            font=("Inter", 11), text_color=t["MUTED"],
            wraplength=640, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        current = licensing.get_partner_code()
        ctk.CTkLabel(
            parent, text=f"Current partner code:  {current}",
            font=("JetBrains Mono", 13),
            text_color=PARTNER_COLOR,
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            parent, text="New partner code",
            font=("Rajdhani", 12, "bold"),
            text_color=t["TEXT"],
        ).pack(anchor="w")

        self.new_partner_entry = ctk.CTkEntry(
            parent, width=320, height=38,
            font=("JetBrains Mono", 14), justify="center",
            placeholder_text="e.g. KAGE-ALPHA-2026",
            fg_color=t["CARD"], border_color=t["BORDER"],
        )
        self.new_partner_entry.pack(anchor="w", pady=(4, 6))

        self.partner_msg = ctk.CTkLabel(
            parent, text="", font=("Inter", 11),
            text_color=t["MUTED"],
        )
        self.partner_msg.pack(anchor="w", pady=(0, 10))

        bar = ctk.CTkFrame(parent, fg_color=t["BG"])
        bar.pack(anchor="w")

        ctk.CTkButton(
            bar, text="ROTATE PARTNER CODE", command=self._rotate_partner,
            fg_color=PARTNER_COLOR, hover_color="#14b8a6", text_color="#053b32",
            font=("Rajdhani", 13, "bold"), width=200, height=34, corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            bar, text="RESET TO DEFAULT", command=self._reset_partner,
            fg_color="#242a33", hover_color="#2f3742", text_color=t["TEXT"],
            font=("Rajdhani", 12, "bold"), width=160, height=34, corner_radius=8,
        ).pack(side="left")

    def _rotate_partner(self):
        new = self.new_partner_entry.get().strip()
        if licensing.rotate_partner_code(new):
            self.partner_msg.configure(
                text=f"\u2713 Partner code rotated to '{new}'. Give it to your partners.",
                text_color=self.theme["ACCENT"],
            )
        else:
            self.partner_msg.configure(
                text="\u2717 Invalid code (3\u201340 chars, must not match owner or premium code).",
                text_color=self.theme["DANGER"],
            )

    def _reset_partner(self):
        licensing.reset_partner_code()
        self.partner_msg.configure(
            text="\u21BA Partner code reset to default (KAGE-PARTNER).",
            text_color=self.theme["MUTED"],
        )

    # ---------- Customize (background) ----------
    def _build_customize(self, parent):
        t = self.theme
        ctk.CTkLabel(
            parent, text="\U0001F3A8  Custom Background",
            font=("Rajdhani", 20, "bold"),
            text_color=t["ACCENT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Exclusive to Owner + Partners. Pick any PNG/JPG on your PC — it becomes "
                 "the app background on next launch.",
            font=("Inter", 11), text_color=t["MUTED"],
            wraplength=640, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        current = licensing.get_custom_bg_path() or "(default Kage background)"
        self.bg_current_label = ctk.CTkLabel(
            parent, text=f"Current:  {current}",
            font=("JetBrains Mono", 11),
            text_color=t["MUTED"], wraplength=640, justify="left",
        )
        self.bg_current_label.pack(anchor="w", pady=(0, 16))

        bar = ctk.CTkFrame(parent, fg_color=t["BG"])
        bar.pack(anchor="w")

        ctk.CTkButton(
            bar, text="\U0001F5BC   BROWSE IMAGE...", command=self._pick_bg,
            fg_color=t["ACCENT"], hover_color=t["ACCENT_DIM"], text_color="#0a0f0a",
            font=("Rajdhani", 13, "bold"), width=200, height=36, corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            bar, text="RESET TO DEFAULT", command=self._reset_bg,
            fg_color="#242a33", hover_color="#2f3742", text_color=t["TEXT"],
            font=("Rajdhani", 12, "bold"), width=160, height=36, corner_radius=8,
        ).pack(side="left")

        ctk.CTkLabel(
            parent,
            text="\u2139  Restart the app after changing to see the new background.",
            font=("Inter", 10), text_color=t["MUTED"],
        ).pack(anchor="w", pady=(16, 0))

    def _pick_bg(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            parent=self,
            title="Choose your background image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        if licensing.set_custom_bg_path(path):
            self.bg_current_label.configure(
                text=f"Current:  {path}",
                text_color=self.theme["ACCENT"],
            )
            messagebox.showinfo(
                "Background updated",
                "New background saved. Restart Kage Utility to see it.",
            )

    def _reset_bg(self):
        licensing.reset_custom_bg()
        self.bg_current_label.configure(
            text="Current:  (default Kage background)",
            text_color=self.theme["MUTED"],
        )
