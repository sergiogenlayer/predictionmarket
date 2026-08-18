# -*- coding: utf-8 -*-
"""Rally x MetaMask Rewards in-wallet banner (distributed via theMiracle).

Brief: for one week Rally is featured inside MetaMask Rewards; new Rally users
who connect with MetaMask get 400 Rally Points. Key message:
"Connect with MetaMask. Join Rally. Get 400 Rally Points."

Spec (agreed with theMiracle):
  * in-wallet banner: 1080x720 px (3:2)
  * all key content inside the CENTRED 720x720 safe zone
  * PNG or JPG, 150 dpi recommended
  * list-card thumbnail is square -> a 720x720 cut is exported too

Design space is 675x450 (= the delivery size / 1.6); every coordinate below is
in that space and multiplied by SCALE at render time.
"""
import os
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

H = 450                            # design height; W varies with the aspect being rendered
W_3_2 = 675                        # 675x450 -> 1080x720 at 1.6x  (agreed in-wallet spec)
W_16_9 = 800                       # 800x450 -> 1280x720 at 1.6x  (Benefit Simulator: 16:9)
SAFE_W = 450                       # safe zone is the centred square, full height
DPI = (150, 150)

# headline = [(text, size), ...] rendered as stacked lines, auto-shrunk to the safe zone
VARIANTS = {
    "a": dict(headline=[("GET 400", 62), ("RALLY POINTS", 40)],
              sub="Connect with MetaMask", cta="Join Rally"),
    "b": dict(headline=[("CONNECT WITH", 34), ("METAMASK", 58)],
              sub="New Rally users get 400 Rally Points", cta="Join Rally"),
}


def make_px(s):
    return lambda v: int(round(v * s))


def font(path, size):
    return ImageFont.truetype(path, max(size, 1))


def text_size(d, txt, f, tracking=0):
    b = d.textbbox((0, 0), txt, font=f)
    return (b[2] - b[0]) + tracking * max(len(txt) - 1, 0), b[3] - b[1]


def draw_tracked(d, xy, txt, f, fill, tracking=0, centred=False):
    """Draw text with letter-spacing. xy is the ink-box top-left, or centre-x if centred."""
    x, y = xy
    if centred:
        x -= text_size(d, txt, f, tracking)[0] / 2
    b0 = d.textbbox((0, 0), txt, font=f)
    x -= b0[0]
    y -= b0[1]
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking


def background(s, W):
    """Diagonal violet gradient + glow + speed streaks + vignette + film grain."""
    px = make_px(s)
    w, h = px(W), px(H)

    g = Image.new("RGB", (32, 21))
    gd = ImageDraw.Draw(g)
    for y in range(21):
        for x in range(32):
            t = (x / 31 * 0.65 + (1 - y / 20) * 0.35) ** 1.7
            gd.point((x, y), tuple(int(DARK_VIOLET[i] + (RALLY_VIOLET[i] - DARK_VIOLET[i]) * t * 0.9)
                                   for i in range(3)))
    img = g.resize((w, h), Image.BICUBIC).convert("RGBA")

    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse([int(w * 0.20), int(h * 0.04), int(w * 0.80), int(h * 0.72)], fill=185)
    glow = glow.filter(ImageFilter.GaussianBlur(px(44)))
    img = Image.composite(Image.new("RGBA", (w, h), RALLY_VIOLET + (255,)), img, glow)

    streaks = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streaks)
    for i in range(-6, 20):
        x0 = px(i * 81)
        sd.polygon([(x0, h), (x0 + px(15), h), (x0 + px(15 + 127), 0), (x0 + px(127), 0)],
                   fill=(255, 255, 255, 7))
    img = Image.alpha_composite(img, streaks)

    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-int(w * 0.05), -int(h * 0.28), int(w * 1.05), int(h * 1.28)], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(px(53)))
    img = Image.composite(img, Image.new("RGBA", (w, h), DARK_VIOLET + (255,)), vig)

    noise = Image.effect_noise((w, h), 26).convert("L").point(lambda v: 128 + (v - 128) * 0.5)
    grained = ImageChops.overlay(img.convert("RGB"), noise.convert("RGB")).convert("RGBA")
    return Image.blend(img, grained, 0.30)


def compose(variant, s, W):
    px = make_px(s)
    cfg = VARIANTS[variant]
    img = background(s, W)
    d = ImageDraw.Draw(img)
    cx = px(W) // 2

    # --- official Rally lockup (iso + wordmark), white
    logo = Image.open(os.path.join(BASE, "assets", "rally_logo_blanco.png")).convert("RGBA")
    lh = px(30)
    logo = logo.resize((max(int(logo.width * lh / logo.height), 1), lh), Image.LANCZOS)
    img.paste(logo, (cx - logo.width // 2, px(18)), logo)

    # --- mascot, cropped to its alpha box so the artwork actually fills the layout
    m = Image.open(os.path.join(BASE, "assets", "paloma03.png")).convert("RGBA")
    m = m.crop(m.getbbox())
    th = px(184)
    m = m.resize((max(int(m.width * th / m.height), 1), th), Image.LANCZOS)
    my = px(58)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", m.size, (10, 2, 22, 255)),
                 (cx - m.width // 2, my + px(10)), m.split()[3].point(lambda v: int(v * 0.5)))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(px(16))))
    img.paste(m, (cx - m.width // 2, my), m)
    d = ImageDraw.Draw(img)

    # --- headline, each line auto-fitted to the safe zone
    y = 250
    for text, size in cfg["headline"]:
        while size > 20:
            f_h = font(DISPLAY, px(size))
            if text_size(d, text, f_h, px(0.5))[0] <= px(SAFE_W - 40):
                break
            size -= 1
        draw_tracked(d, (cx, px(y)), text, f_h, WHITE, tracking=px(0.5), centred=True)
        y += size * 0.86 + 6

    # --- sub
    draw_tracked(d, (cx, px(354)), cfg["sub"], font(UI, px(15)), LIGHT_VIOLET, tracking=px(0.4), centred=True)

    # --- CTA pill
    f_c = font(UI, px(19))
    tw, th_ = text_size(d, cfg["cta"], f_c)
    pw, ph = tw + px(58), px(46)
    x0, y0 = cx - pw // 2, px(382)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([x0, y0, x0 + pw, y0 + ph], ph // 2, fill=ORANGE + (150,))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(px(11))))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], ph // 2, fill=ORANGE + (255,))
    draw_tracked(d, (cx, y0 + (ph - th_) // 2 - px(1)), cfg["cta"], f_c, WHITE, centred=True)
    return img


def safezone_proof(banner):
    """Red outline of the centred square safe zone, for review only."""
    p = banner.convert("RGBA").copy()
    d = ImageDraw.Draw(p)
    side = p.height
    x0 = (p.width - side) // 2
    d.rectangle([x0, 0, x0 + side - 1, side - 1], outline=(255, 0, 0, 255), width=4)
    d.text((x0 + 12, 10), f"safe zone {side}x{side}", font=font(UI, 20), fill=(255, 0, 0, 255))
    return p


def main():
    for v in VARIANTS:
        # --- 3:2, the agreed in-wallet banner spec
        master = compose(v, 3.2, W_3_2)                             # 2160x1440
        master.convert("RGB").save(f"{OUT}/rally_inwallet_2160x1440_{v}.png", dpi=DPI)

        banner = master.resize((1080, 720), Image.LANCZOS).convert("RGB")
        banner.save(f"{OUT}/rally_inwallet_1080x720_{v}.png", dpi=DPI)
        banner.save(f"{OUT}/rally_inwallet_1080x720_{v}.jpg", quality=92, dpi=DPI)

        # --- 16:9, the ratio the Benefit Simulator asks for
        wide = compose(v, 3.2, W_16_9).resize((1280, 720), Image.LANCZOS).convert("RGB")
        wide.save(f"{OUT}/rally_benefit_1280x720_{v}.png", dpi=DPI)
        wide.save(f"{OUT}/rally_benefit_1280x720_{v}.jpg", quality=92, dpi=DPI)

        # square list-card thumbnail = exactly the safe zone
        banner.crop(((1080 - 720) // 2, 0, (1080 + 720) // 2, 720)).save(
            f"{OUT}/rally_inwallet_720x720_{v}.png", dpi=DPI)

    safezone_proof(Image.open(f"{OUT}/rally_inwallet_1080x720_a.png")).convert("RGB").save(
        f"{OUT}/proof_safezone_a.png", dpi=DPI)
    safezone_proof(Image.open(f"{OUT}/rally_benefit_1280x720_a.png")).convert("RGB").save(
        f"{OUT}/proof_safezone_wide_a.png", dpi=DPI)

    a = Image.open(f"{OUT}/rally_inwallet_1080x720_a.png").resize((810, 540), Image.LANCZOS)
    b = Image.open(f"{OUT}/rally_inwallet_1080x720_b.png").resize((810, 540), Image.LANCZOS)
    sheet = Image.new("RGB", (810, 1122), (245, 243, 250))
    sheet.paste(a, (0, 0))
    sheet.paste(b, (0, 582))
    sd = ImageDraw.Draw(sheet)
    f = font(UI, 18)
    sd.text((10, 552), "Variante A", font=f, fill=DARK_VIOLET)
    sd.text((10, 1134 - 12 - 30), "Variante B", font=f, fill=DARK_VIOLET)
    sheet.save(f"{OUT}/preview_sheet.png")

    for n in sorted(os.listdir(OUT)):
        im = Image.open(os.path.join(OUT, n))
        print(f"{n:38} {im.size[0]}x{im.size[1]}  {os.path.getsize(os.path.join(OUT, n)) // 1024}KB")


if __name__ == "__main__":
    main()
