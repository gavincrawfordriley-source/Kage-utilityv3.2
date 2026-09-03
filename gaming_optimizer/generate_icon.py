"""
Generates the Kage Utility app icon (icon.ico + icon.png).
Black + purple, sharp, premium-feeling.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH = os.path.join(OUT_DIR, "icon.png")
ICO_PATH = os.path.join(OUT_DIR, "icon.ico")


def draw_kage_icon(size=512):
    """
    Design: rounded-square black tile, glowing purple 'K' shuriken glyph.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Palette (matches Kage Purple theme)
    BG = (7, 4, 13, 255)
    BG_2 = (18, 10, 31, 255)
    PURPLE = (160, 90, 255, 255)
    PURPLE_HI = (210, 155, 255, 255)
    WHITE = (245, 235, 255, 255)

    c = size // 2
    corner = int(size * 0.24)

    # --- 1. tile: pure deep black ---
    d.rounded_rectangle([(0, 0), (size, size)], radius=corner, fill=BG)

    # tight, dim glow behind glyph
    for i in range(10, 0, -1):
        r = int(size * 0.22 * (i / 10))
        alpha = int(2 + 22 * (1 - i / 10))
        d.ellipse(
            [(c - r, c - r), (c + r, c + r)],
            fill=(90, 40, 180, alpha),
        )

    # --- 2. shuriken diamond (rotated square) ---
    r = int(size * 0.28)
    diamond = [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
    d.polygon(diamond, fill=BG_2)
    # sharp purple outline
    d.line(diamond + [diamond[0]], fill=PURPLE, width=max(4, size // 80),
           joint="curve")

    # --- 3. Stylised K inside diamond ---
    # K constructed from 3 strokes; positioned slightly left of centre
    kw = max(6, size // 60)  # stroke width
    kx = c - int(size * 0.09)   # left column of K
    kt = c - int(size * 0.13)   # top
    kb = c + int(size * 0.13)   # bottom
    kmid = c                    # centre where diagonals meet

    # vertical stroke
    d.line([(kx, kt), (kx, kb)], fill=PURPLE_HI, width=kw)
    # upper diagonal
    d.line([(kx, kmid), (kx + int(size * 0.13), kt)],
           fill=PURPLE_HI, width=kw)
    # lower diagonal
    d.line([(kx, kmid), (kx + int(size * 0.13), kb)],
           fill=PURPLE_HI, width=kw)

    # --- 4. shuriken points (small triangles on 4 tips) ---
    p = int(size * 0.055)
    tips = [
        [(c, c - r - p), (c - p // 2, c - r + p // 3), (c + p // 2, c - r + p // 3)],
        [(c, c + r + p), (c - p // 2, c + r - p // 3), (c + p // 2, c + r - p // 3)],
        [(c - r - p, c), (c - r + p // 3, c - p // 2), (c - r + p // 3, c + p // 2)],
        [(c + r + p, c), (c + r - p // 3, c - p // 2), (c + r - p // 3, c + p // 2)],
    ]
    for tri in tips:
        d.polygon(tri, fill=PURPLE)

    # --- 5. highlight dot ---
    hl_r = int(size * 0.014)
    hx, hy = kx - int(size * 0.02), kt + int(size * 0.02)
    d.ellipse([(hx - hl_r, hy - hl_r), (hx + hl_r, hy + hl_r)], fill=WHITE)

    # --- 6. tight outer glow ---
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.polygon(diamond, outline=(140, 70, 230, 180),
               width=max(4, size // 80))
    for tri in tips:
        gd.polygon(tri, fill=(140, 70, 230, 180))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=size // 45))
    final = Image.alpha_composite(img, glow_layer)
    # composite glyph back on top so it stays crisp
    final = Image.alpha_composite(final, img)

    return final


def main():
    img = draw_kage_icon(512)
    img.save(PNG_PATH, "PNG")

    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    resized = [img.resize(s, Image.LANCZOS) for s in sizes]
    resized[0].save(
        ICO_PATH, format="ICO",
        sizes=sizes,
        append_images=resized[1:],
    )
    print(f"Icon written: {ICO_PATH}  and  {PNG_PATH}")


if __name__ == "__main__":
    main()
