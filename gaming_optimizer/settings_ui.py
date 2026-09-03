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
        if licensing.is_owner_session():
            tabs.add("\U0001F451 Owner")

        self._build_themes(tabs.tab("\U0001F3A8 Themes"))
        self._build_profiles(tabs.tab("\U0001F4CB Profiles"))
        self._build_benchmark(tabs.tab("\U0001F4CA Benchmark"))
        if licensing.is_owner_session():
            self._build_owner(tabs.tab("\U0001F451 Owner"))

    # ---------- Themes ----------
    def _build_themes(self, parent):
        current, _ = get_theme()
        ctk.CTkLabel(
            parent, text="Pick a colour vibe",
            font=("Rajdhani", 18, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Match your setup. Change is instant.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
        ).pack(anchor="w", pady=(0, 14))

        grid = ctk.CTkFrame(parent, fg_color=self.theme["BG"])
        grid.pack(fill="both", expand=True)

        for i, (name, t) in enumerate(THEMES.items()):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(
                grid, fg_color=t["CARD"], corner_radius=12,
                border_width=2 if name == current else 1,
                border_color=t["ACCENT"] if name == current else t["BORDER"],
                height=100,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            grid.grid_columnconfigure(col, weight=1)

            ctk.CTkLabel(
                card, text=name,
                font=("Rajdhani", 15, "bold"),
                text_color=t["ACCENT"],
            ).pack(anchor="w", padx=14, pady=(12, 2))

            # swatches
            sw = ctk.CTkFrame(card, fg_color=t["CARD"])
            sw.pack(anchor="w", padx=14, pady=(4, 8))
            for c in [t["ACCENT"], t["GOLD"], t["TEXT"], t["BG"], t["MUTED"]]:
                ctk.CTkFrame(sw, fg_color=c, width=22, height=22,
                             corner_radius=6, border_width=1,
                             border_color=t["BORDER"]).pack(side="left", padx=2)

            btn = ctk.CTkButton(
                card, text="ACTIVE" if name == current else "APPLY",
                command=lambda n=name: self._apply_theme(n),
                fg_color=t["ACCENT"] if name != current else "#242a33",
                hover_color=t["ACCENT_DIM"],
                text_color="#0a0f0a" if name != current else t["MUTED"],
                font=("Rajdhani", 12, "bold"),
                height=28, width=90, corner_radius=8,
                state="disabled" if name == current else "normal",
            )
            btn.pack(anchor="e", padx=14, pady=(0, 10))

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

    # ---------- Owner Console ----------
    def _build_owner(self, parent):
        ctk.CTkLabel(
            parent, text="\U0001F451  Owner Console",
            font=("Rajdhani", 20, "bold"),
            text_color=self.theme["GOLD"],
        ).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(
            parent,
            text="Rotate the secret code without recompiling. The change persists on this PC only.",
            font=("Inter", 11), text_color=self.theme["MUTED"],
            wraplength=640, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        current = licensing.get_secret_code()
        ctk.CTkLabel(
            parent, text=f"Current secret code:  {current}",
            font=("JetBrains Mono", 13),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            parent, text="New secret code",
            font=("Rajdhani", 12, "bold"),
            text_color=self.theme["TEXT"],
        ).pack(anchor="w")

        self.new_code_entry = ctk.CTkEntry(
            parent, width=320, height=38,
            font=("JetBrains Mono", 14), justify="center",
            placeholder_text="e.g. FRAG2026",
            fg_color=self.theme["CARD"], border_color=self.theme["BORDER"],
        )
        self.new_code_entry.pack(anchor="w", pady=(4, 6))

        self.owner_msg = ctk.CTkLabel(
            parent, text="", font=("Inter", 11),
            text_color=self.theme["MUTED"],
        )
        self.owner_msg.pack(anchor="w", pady=(0, 10))

        bar = ctk.CTkFrame(parent, fg_color=self.theme["BG"])
        bar.pack(anchor="w")

        ctk.CTkButton(
            bar, text="ROTATE CODE", command=self._rotate,
            fg_color=self.theme["GOLD"], hover_color="#dbaf3e",
            text_color="#141005",
            font=("Rajdhani", 13, "bold"), width=140, height=34, corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            bar, text="RESET TO DEFAULT", command=self._reset,
            fg_color="#242a33", hover_color="#2f3742",
            text_color=self.theme["TEXT"],
            font=("Rajdhani", 12, "bold"), width=160, height=34, corner_radius=8,
        ).pack(side="left")

        # revoke controls
        ctk.CTkLabel(
            parent, text="", height=6,
        ).pack()
        revoke_bar = ctk.CTkFrame(parent, fg_color=self.theme["BG"])
        revoke_bar.pack(anchor="w", pady=(20, 0))

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
        # simulate re-entering owner code
        licensing.submit_code(licensing.OWNER_CODE)
        self.destroy()
