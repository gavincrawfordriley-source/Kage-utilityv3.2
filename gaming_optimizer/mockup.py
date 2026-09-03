"""Static preview render of the Kage Utility main window (PIL mockup)."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 980, 840
T = {  # Kage Purple theme
    "BG": "#07040d", "CARD": "#120a1f", "CARD_LOCKED": "#0b0715",
    "BORDER": "#2a1b47", "ACCENT": "#a05aff", "GOLD": "#e6b8ff",
    "DANGER": "#ff5a7c", "MUTED": "#6c5a85", "TEXT": "#efe4ff",
    "TEXT_LOCKED": "#4f4562",
}


def font(size, bold=False):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rrect(d, xy, r, **kw):
    d.rounded_rectangle(xy, radius=r, **kw)


img = Image.new("RGB", (W, H), T["BG"])
d = ImageDraw.Draw(img)

# ---- Header ----
d.text((72, 34), "\u25B2", fill=T["ACCENT"], font=font(46, True))
d.text((120, 32), "Kage Utility", fill=T["TEXT"], font=font(38, True))
d.text((120, 78), "53 Windows tweaks — fully reversible.  Move like a shadow.",
       fill=T["MUTED"], font=font(14))

# badges
def badge(x, y, w, h, text, bg, fg):
    rrect(d, [(x, y), (x + w, y + h)], 8, fill=bg)
    tw = d.textlength(text, font=font(12, True))
    d.text((x + (w - tw) // 2, y + 5), text, fill=fg, font=font(12, True))

badge(730, 44, 90, 28, "👑 OWNER", "#211a08", T["GOLD"])
badge(828, 44, 100, 28, "✓ ADMIN", "#141a1f", T["ACCENT"])
badge(730, 78, 90, 20, "★ PREMIUM", "#211a08", T["GOLD"])

# ---- Action bar ----
def button(x, y, w, h, txt, bg, fg):
    rrect(d, [(x, y), (x + w, y + h)], 10, fill=bg)
    tw = d.textlength(txt, font=font(14, True))
    d.text((x + (w - tw) // 2, y + 10), txt, fill=fg, font=font(14, True))

y = 130
button(30, y, 150, 40, "⚡  APPLY ALL", T["ACCENT"], "#0a0f0a")
button(188, y, 140, 40, "↺  RESTORE", "#242a33", T["TEXT"])
button(336, y, 160, 40, "⌫  UNDO: Game Mode", "#2a1b47", T["ACCENT"])
button(504, y, 150, 40, "🔑  MANAGE CODE", "#242a33", T["GOLD"])
button(662, y, 140, 40, "⚙  SETTINGS", "#242a33", T["TEXT"])

# ---- Category header: Gaming ----
y = 200
d.text((30, y), "🎮   GAMING   ★", fill=T["ACCENT"], font=font(16, True))
d.text((W - 100, y + 2), "6 tweaks", fill=T["MUTED"], font=font(11))

# ---- Sample cards ----
def card(x, y, w, h, icon, title, desc, on, locked=False):
    bg = T["CARD_LOCKED"] if locked else T["CARD"]
    rrect(d, [(x, y), (x + w, y + h)], 12, fill=bg, outline=T["BORDER"], width=1)
    text_col = T["TEXT_LOCKED"] if locked else T["TEXT"]
    d.text((x + 18, y + 14), icon, fill=T["ACCENT"] if not locked else T["MUTED"],
           font=font(24))
    d.text((x + 58, y + 14), title, fill=text_col, font=font(15, True))
    d.text((x + 58, y + 40), desc, fill=T["MUTED"] if not locked else "#3a3346",
           font=font(11))
    # status
    dot_c = T["ACCENT"] if on else T["MUTED"]
    if locked: dot_c = "#3a3346"
    d.ellipse([(x + w - 130, y + 20), (x + w - 118, y + 32)], fill=dot_c)
    status_txt = "ON" if on else ("LOCKED" if locked else "OFF")
    d.text((x + w - 110, y + 20), status_txt, fill=dot_c, font=font(11, True))
    # switch
    sw_bg = T["ACCENT"] if on else "#242a33"
    if locked: sw_bg = "#1a1420"
    rrect(d, [(x + w - 65, y + 42), (x + w - 20, y + 60)], 9, fill=sw_bg)
    knob_x = x + w - 30 if on else x + w - 63
    d.ellipse([(knob_x, y + 42), (knob_x + 15, y + 60)], fill=T["TEXT"])

x, cw, ch = 30, W - 60, 72

card(x, 230, cw, ch, "❌", "Disable Xbox Game Bar",
     "Turns off the Win+G overlay that costs FPS in every DirectX game.", True)
card(x, 310, cw, ch, "🎮", "Enable Windows Game Mode",
     "Tells Windows to prioritise resources for the game currently in focus.", True)
card(x, 390, cw, ch, "⚡", "Hardware-Accelerated GPU Scheduling",
     "Reduces input latency on modern GPUs (RTX / RX 5000+). Reboot required.", False)

# ---- Category: CPU & Power (locked) ----
d.text((30, 480), "⚡   CPU & POWER   ★", fill=T["GOLD"], font=font(16, True))
d.text((W - 100, 482), "5 tweaks", fill=T["MUTED"], font=font(11))

card(x, 510, cw, ch, "⚡", "✨  Ultimate Performance Power Plan",
     "Unlocks and activates the hidden Ultimate power plan.", True)
card(x, 590, cw, ch, "🧠", "✨  Disable CPU Core Parking",
     "Forces every CPU core to stay awake — eliminates micro-stutter.", True)
card(x, 670, cw, ch, "🔥", "✨  Disable CPU Throttling",
     "Sets processor minimum state to 100% so your CPU never downclocks.", False)

# ---- Status bar ----
d.text((30, H - 24), "✓ Applied: Enable Windows Game Mode          Theme: Kage Purple",
       fill=T["ACCENT"], font=font(11))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mockup.png")
img.save(out)
print(f"Saved: {out}")
