"""Generates the background image for the main window — gradient + grid + noise."""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg.png")


def make(w=1600, h=1200):
    img = Image.new("RGB", (w, h), (7, 4, 13))
    d = ImageDraw.Draw(img)

    # Radial glow bottom-left (deep purple) and top-right (violet)
    def glow(cx, cy, r_max, colour, layers=60):
        for i in range(layers, 0, -1):
            r = int(r_max * (i / layers))
            alpha = int(2 + 60 * (1 - i / layers))
            over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            od = ImageDraw.Draw(over)
            od.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                       fill=colour + (alpha,))
            img.paste(over, (0, 0), over)

    glow(-120, h + 120, int(h * 1.1), (90, 40, 180))
    glow(w + 120, -120, int(h * 0.9), (55, 25, 120))

    # Diagonal accent slash lines (very faint)
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for x in range(-h, w, 46):
        od.line([(x, h), (x + h, 0)], fill=(160, 90, 255, 8), width=1)
    img.paste(over, (0, 0), over)

    # Grid
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for x in range(0, w, 40):
        od.line([(x, 0), (x, h)], fill=(160, 90, 255, 6), width=1)
    for y in range(0, h, 40):
        od.line([(0, y), (w, y)], fill=(160, 90, 255, 6), width=1)
    img.paste(over, (0, 0), over)

    # Grain / stars
    random.seed(4)
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for _ in range(300):
        x, y = random.randrange(w), random.randrange(h)
        a = random.randint(30, 120)
        od.point((x, y), fill=(230, 200, 255, a))
    img.paste(over, (0, 0), over)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    img.save(OUT, "PNG")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    make()
