# -*- coding: utf-8 -*-
"""Rally x Solflare in-wallet benefit banner.
Specs (themiracle.io Benefit Simulator -> Solflare Asset Requirements):
  ratio 16:9, min width 400px (800px+ recommended), JPG/PNG,
  safe zone = centred 450x450 square of an 800x450 image.
All logos/text stay inside the safe zone; only decoration bleeds outside.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

BASE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "out")
os.makedirs(OUT, exist_ok=True)

# --- Rally brand palette (rally.fun/brand) ---
DARK_VIOLET  = (0x25, 0x04, 0x3A)
RALLY_VIOLET = (0x6D, 0x37, 0xD5)
LIGHT_VIOLET = (0xE5, 0xD6, 0xFF)
ORANGE       = (0xFF, 0x4E, 0x00)
WHITE        = (0xFF, 0xFF, 0xFF)

DISPLAY = os.path.join(F, "archivo_it900.ttf")   # Archivo Condensed Black Italic
UI      = os.path.join(F, "archivo_600.ttf")     # Archivo SemiBold

W, H = 800, 450                 # design space
SAFE = (175, 0, 625, 450)       # centred 450x450 safe zone

VARIANTS = {
    "a": dict(headline="JOIN THE RALLY", sub="Prediction markets, in your wallet", cta="Enter App"),
    "b": dict(headline="TRADE THE FUTURE", sub="Live markets \u00b7 rally.fun", cta="Claim your reward"),
}


def font(path, px):
    return ImageFont.truetype(path, px)


def text_size(d, txt, f, tracking=0):
    b = d.textbbox((0, 0), txt, font=f)
    return (b[2] - b[0]) + tracking * max(len(txt) - 1, 0), b[3] - b[1]


def draw_tracked(d, xy, txt, f, fill, tracking=0, anchor_center=False):
    """Draw text with letter-spacing; xy is left/top of the ink box (or centre-x if anchor_center)."""
    x, y = xy
    if anchor_center:
        w, _ = text_size(d, txt, f, tracking)
        x = x - w / 2
    b0 = d.textbbox((0, 0), txt, font=f)
    x -= b0[0]
    y -= b0[1]
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking


def background(s):
    """Diagonal violet gradient + glow + grain + speed streaks."""
    w, h = W * s, H * s
    # gradient (rendered small, upscaled = perfectly smooth)
    g = Image.new("RGB", (32, 18))
    gd = ImageDraw.Draw(g)
    for y in range(18):
        for x in range(32):
            t = (x / 31 * 0.65 + (1 - y / 17) * 0.35)
            c = tuple(int(DARK_VIOLET[i] + (RALLY_VIOLET[i] - DARK_VIOLET[i]) * (t ** 1.7) * 0.9) for i in range(3))
            gd.point((x, y), c)
    img = g.resize((w, h), Image.BICUBIC)

    # radial glow behind the mascot
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse(
        [int(w * 0.5 - 0.30 * w), int(h * 0.04), int(w * 0.5 + 0.30 * w), int(h * 0.72)], fill=185)
    glow = glow.filter(ImageFilter.GaussianBlur(70 * s))
    img = Image.composite(Image.new("RGB", (w, h), RALLY_VIOLET), img, glow)

    # diagonal speed streaks (decoration, allowed to bleed outside the safe zone)
    streaks = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streaks)
    for i in range(-6, 18):
        x0 = i * 96 * s
        sd.polygon([(x0, h), (x0 + 18 * s, h), (x0 + 18 * s + 150 * s, 0), (x0 + 150 * s, 0)],
                   fill=(255, 255, 255, 7))
    img = Image.alpha_composite(img.convert("RGBA"), streaks)

    # vignette
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-int(w * 0.05), -int(h * 0.28), int(w * 1.05), int(h * 1.28)], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(85 * s))
    img = Image.composite(img, Image.new("RGBA", (w, h), DARK_VIOLET + (255,)), vig)

    # film grain
    noise = Image.effect_noise((w, h), 26).convert("L").point(lambda v: 128 + (v - 128) * 0.5)
    img = Image.blend(img, ImageChops.overlay(img.convert("RGB"), noise.convert("RGB")).convert("RGBA"), 0.30)
    return img


def compose(variant, s=2, square=False):
    cfg = VARIANTS[variant]
    img = background(s)
    d = ImageDraw.Draw(img)
    cx = W * s // 2

    # --- wordmark (placeholder type-set; swap for the official Rally SVG when available)
    f_mark = font(DISPLAY, int(31 * s))
    draw_tracked(d, (cx, int(20 * s)), "RALLY", f_mark, WHITE, tracking=int(2.5 * s), anchor_center=True)

    # --- mascot (cropped to its alpha box so the artwork fills the layout)
    m = Image.open(os.path.join(BASE, "assets", "paloma03.png")).convert("RGBA")
    m = m.crop(m.getbbox())
    target_h = int(226 * s)
    m = m.resize((int(m.width * target_h / m.height), target_h), Image.LANCZOS)
    my = int(56 * s)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    alpha = m.split()[3].point(lambda v: int(v * 0.5))
    sh.paste(Image.new("RGBA", m.size, (10, 2, 22, 255)), (cx - m.width // 2, my + int(10 * s)), alpha)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(16 * s)))
    img.paste(m, (cx - m.width // 2, my), m)
    d = ImageDraw.Draw(img)

    # --- headline (auto-fit inside the safe zone)
    size = 48
    while size > 26:
        f_h = font(DISPLAY, int(size * s))
        if text_size(d, cfg["headline"], f_h, int(0.5 * s))[0] <= 410 * s:
            break
        size -= 1
    draw_tracked(d, (cx, int(298 * s)), cfg["headline"], f_h, WHITE, tracking=int(0.5 * s), anchor_center=True)

    # --- sub
    f_s = font(UI, int(15 * s))
    draw_tracked(d, (cx, int(352 * s)), cfg["sub"], f_s, LIGHT_VIOLET, tracking=int(0.4 * s), anchor_center=True)

    # --- CTA pill
    f_c = font(UI, int(19 * s))
    tw, th = text_size(d, cfg["cta"], f_c)
    pw, ph = tw + int(58 * s), int(46 * s)
    px0, py0 = cx - pw // 2, int(382 * s)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([px0, py0, px0 + pw, py0 + ph], ph // 2, fill=ORANGE + (150,))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(11 * s)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], ph // 2, fill=ORANGE + (255,))
    draw_tracked(d, (cx, py0 + (ph - th) // 2 - int(1 * s)), cfg["cta"], f_c, WHITE, anchor_center=True)

    if square:  # 1:1 crop, subject centred — allowed fallback per the spec
        side = H * s
        img = img.crop((cx - side // 2, 0, cx + side // 2, side))
    return img


def safezone_proof(img800):
    p = img800.convert("RGBA").copy()
    d = ImageDraw.Draw(p)
    d.rectangle([SAFE[0], SAFE[1], SAFE[2] - 1, SAFE[3] - 1], outline=(255, 0, 0, 255), width=3)
    f = font(UI, 13)
    d.text((SAFE[0] + 8, 6), "safe zone 450x450", font=f, fill=(255, 0, 0, 255))
    return p


for v in VARIANTS:
    master = compose(v, s=2)                                   # 1600x900
    master.convert("RGB").save(f"{OUT}/rally_solflare_1600x900_{v}.png")
    small = master.resize((W, H), Image.LANCZOS).convert("RGB")
    small.save(f"{OUT}/rally_solflare_800x450_{v}.png")
    small.save(f"{OUT}/rally_solflare_800x450_{v}.jpg", quality=92)
    sq = compose(v, s=2, square=True).resize((900, 900), Image.LANCZOS).convert("RGB")
    sq.save(f"{OUT}/rally_solflare_900x900_{v}.png")

safezone_proof(Image.open(f"{OUT}/rally_solflare_800x450_a.png")).convert("RGB").save(f"{OUT}/proof_safezone_a.png")

# side-by-side preview sheet
a = Image.open(f"{OUT}/rally_solflare_800x450_a.png"); b = Image.open(f"{OUT}/rally_solflare_800x450_b.png")
sheet = Image.new("RGB", (800, 930), (245, 243, 250))
sheet.paste(a, (0, 0)); sheet.paste(b, (0, 480))
sd = ImageDraw.Draw(sheet)
f = font(UI, 18)
sd.text((10, 455), "Variante A", font=f, fill=(0x25, 0x04, 0x3A))
sd.text((10, 452 + 483), "Variante B", font=f, fill=(0x25, 0x04, 0x3A))
sheet.save(f"{OUT}/preview_sheet.png")
print("\n".join(sorted(os.listdir(OUT))))
