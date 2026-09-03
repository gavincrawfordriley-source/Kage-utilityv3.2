"""Static gaming-style preview of the Kage Utility main window."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os, random

W, H = 980, 840
T = {
    "BG": (7, 4, 13), "CARD_A": (18, 10, 31), "CARD_B": (28, 15, 55),
    "CARD_L": (11, 7, 21), "BORDER": (42, 27, 71), "ACCENT": (160, 90, 255),
    "GOLD": (230, 184, 255), "DANGER": (255, 90, 124),
    "MUTED": (108, 90, 133), "TEXT": (239, 228, 255), "TEXT_L": (79, 69, 98),
}


def font(size, bold=False):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def rrect(d, xy, r, **kw):
    d.rounded_rectangle(xy, radius=r, **kw)


# ---------- background layer ----------
img = Image.new("RGB", (W, H), T["BG"])
d = ImageDraw.Draw(img)

# radial glows
for cx, cy, radius, col in [
    (-80, H + 80, 900, (90, 40, 180)),
    (W + 80, -80, 700, (55, 25, 120)),
    (W // 2, H // 2, 500, (60, 25, 130)),
]:
    for i in range(50, 0, -1):
        r = int(radius * (i / 50))
        alpha = int(3 + 55 * (1 - i / 50))
        over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        od.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=col + (alpha,))
        img.paste(over, (0, 0), over)

# diagonal slashes
over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(over)
for x in range(-H, W, 42):
    od.line([(x, H), (x + H, 0)], fill=(160, 90, 255, 10), width=1)
img.paste(over, (0, 0), over)

# grid
over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(over)
for x in range(0, W, 36):
    od.line([(x, 0), (x, H)], fill=(160, 90, 255, 8), width=1)
for y in range(0, H, 36):
    od.line([(0, y), (W, y)], fill=(160, 90, 255, 8), width=1)
img.paste(over, (0, 0), over)

# stars
random.seed(3)
over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(over)
for _ in range(180):
    od.point((random.randrange(W), random.randrange(H)),
             fill=(230, 200, 255, random.randint(40, 140)))
img.paste(over, (0, 0), over)

d = ImageDraw.Draw(img)


# ---------- helpers ----------
def glow_rect(xy, r, colour, blur=8, alpha=120, width=2):
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.rounded_rectangle(xy, radius=r, outline=colour + (alpha,), width=width)
    over = over.filter(ImageFilter.GaussianBlur(radius=blur))
    img.paste(over, (0, 0), over)


def gradient_card(x, y, w, h, r, ca, cb, border=None, glow=False):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(h):
        t = i / h
        c = tuple(int(ca[k] + (cb[k] - ca[k]) * t) for k in range(3)) + (245,)
        ld.line([(0, i), (w, i)], fill=c)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (w, h)], radius=r, fill=255)
    img.paste(layer, (x, y), mask)
    if glow:
        glow_rect([(x - 1, y - 1), (x + w + 1, y + h + 1)], r + 1,
                  T["ACCENT"], blur=10, alpha=90, width=2)
    if border:
        d.rounded_rectangle([(x, y), (x + w, y + h)], radius=r,
                            outline=border, width=1)


# ---------- header ----------
d.text((72, 34), "\u25B2", fill=T["ACCENT"], font=font(46, True))
d.text((120, 32), "KAGE UTILITY", fill=T["TEXT"], font=font(36, True))
d.text((120, 78),
       "53 Windows tweaks — fully reversible.   移  Move like a shadow.",
       fill=T["MUTED"], font=font(13))


def badge(x, y, w, h, text, bg, fg, glow_col=None):
    rrect(d, [(x, y), (x + w, y + h)], 8, fill=bg)
    if glow_col:
        glow_rect([(x, y), (x + w, y + h)], 8, glow_col, blur=6, alpha=110)
    tw = d.textlength(text, font=font(11, True))
    d.text((x + (w - tw) // 2, y + 4), text, fill=fg, font=font(11, True))


badge(720, 44, 90, 26, "OWNER", (33, 26, 8), T["GOLD"], T["GOLD"])
badge(818, 44, 100, 26, "ADMIN", (20, 26, 31), T["ACCENT"])
badge(720, 76, 90, 22, "PREMIUM", (33, 26, 8), T["GOLD"])


# ---------- action bar ----------
def button(x, y, w, h, txt, bg, fg, glow_col=None):
    rrect(d, [(x, y), (x + w, y + h)], 10, fill=bg)
    if glow_col:
        glow_rect([(x, y), (x + w, y + h)], 10, glow_col, blur=10, alpha=90)
    tw = d.textlength(txt, font=font(13, True))
    d.text((x + (w - tw) // 2, y + 12), txt, fill=fg, font=font(13, True))


y = 130
button(30, y, 150, 40, "⚡  APPLY ALL", T["ACCENT"], (10, 15, 10), T["ACCENT"])
button(188, y, 130, 40, "↺  RESTORE", (36, 42, 51), T["TEXT"])
button(326, y, 180, 40, "⌫  UNDO: Game Mode", (42, 27, 71), T["ACCENT"], T["ACCENT"])
button(514, y, 150, 40, "🔑  MANAGE CODE", (36, 42, 51), T["GOLD"])
button(672, y, 140, 40, "⚙  SETTINGS", (36, 42, 51), T["TEXT"])


# ---------- category header helper ----------
def cat_hdr(y, title, colour, count, locked=False):
    # bracket accents
    d.line([(24, y + 22), (30, y + 22)], fill=colour, width=3)
    d.line([(30, y + 8), (30, y + 22)], fill=colour, width=3)
    d.text((44, y), title, fill=colour, font=font(15, True))
    d.text((W - 90, y + 4), f"[ {count} ]", fill=T["MUTED"], font=font(11, True))


# ---------- card renderer ----------
def sample_card(x, y, w, h, icon, title, desc, on, locked=False):
    if locked:
        gradient_card(x, y, w, h, 12, T["CARD_L"], T["CARD_L"],
                      border=T["BORDER"])
    elif on:
        gradient_card(x, y, w, h, 12, T["CARD_A"], T["CARD_B"],
                      border=T["ACCENT"], glow=True)
    else:
        gradient_card(x, y, w, h, 12, T["CARD_A"], T["CARD_A"],
                      border=T["BORDER"])
    # diagonal accent stripe (when on)
    if on and not locked:
        over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        od.polygon([(0, 0), (16, 0), (0, 16)], fill=T["ACCENT"] + (200,))
        img.paste(over, (x, y), over)

    text_col = T["TEXT_L"] if locked else T["TEXT"]
    icon_col = T["MUTED"] if locked else T["ACCENT"]
    d.text((x + 18, y + 14), icon, fill=icon_col, font=font(22, True))
    d.text((x + 58, y + 14), title, fill=text_col, font=font(14, True))
    d.text((x + 58, y + 40), desc, fill=T["MUTED"] if not locked else (58, 51, 70),
           font=font(11))

    dot_c = T["ACCENT"] if on else T["MUTED"]
    if locked: dot_c = (58, 51, 70)
    d.ellipse([(x + w - 130, y + 20), (x + w - 118, y + 32)], fill=dot_c)
    status_txt = "ON" if on else ("LOCKED" if locked else "OFF")
    d.text((x + w - 110, y + 20), status_txt, fill=dot_c, font=font(11, True))
    sw_bg = T["ACCENT"] if on else (36, 42, 51)
    if locked: sw_bg = (26, 20, 32)
    rrect(d, [(x + w - 65, y + 42), (x + w - 20, y + 60)], 9, fill=sw_bg)
    knob_x = x + w - 30 if on else x + w - 63
    d.ellipse([(knob_x, y + 42), (knob_x + 15, y + 60)], fill=T["TEXT"])


x, cw, ch = 30, W - 60, 72

cat_hdr(200, "GAMING  ★", T["ACCENT"], 6)
sample_card(x, 228, cw, ch, "❌", "Disable Xbox Game Bar",
            "Turns off the Win+G overlay that costs FPS in every DirectX game.", True)
sample_card(x, 308, cw, ch, "🎮", "Enable Windows Game Mode",
            "Tells Windows to prioritise resources for the game currently in focus.", True)
sample_card(x, 388, cw, ch, "⚡", "Hardware-Accelerated GPU Scheduling",
            "Reduces input latency on modern GPUs (RTX / RX 5000+). Reboot required.", False)

cat_hdr(478, "CPU & POWER  ✦ PREMIUM", T["GOLD"], 5)
sample_card(x, 506, cw, ch, "⚡", "Ultimate Performance Power Plan",
            "Unlocks the hidden Ultimate power plan for max CPU responsiveness.", True)
sample_card(x, 586, cw, ch, "🧠", "Disable CPU Core Parking",
            "Forces every CPU core to stay awake — eliminates micro-stutter.", False)
sample_card(x, 666, cw, ch, "🔥", "Disable CPU Throttling  [LOCKED]",
            "Sets processor minimum state to 100% so your CPU never downclocks.",
            False, locked=True)

# status bar
d.text((30, H - 24),
       "✓ Applied: Game Mode          Theme: Kage Purple          🟣 Discord: Optimizing with Kage",
       fill=T["ACCENT"], font=font(11))

img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mockup.png"))
print("Saved mockup.png")
