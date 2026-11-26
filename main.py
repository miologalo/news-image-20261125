#!/usr/bin/env python3
"""news-image-20261125: draw a newspaper front page for Wednesday 25 November 2026.

Deterministic: no randomness, no wall-clock, no network. Writes one PNG to
/output/entry.png (or argv[1] / $MAKEFUN_OUTPUT_DIR/entry.png for local tests).
Standard library + Pillow only.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 768, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # content width = 712

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (178, 24, 24)
NAVY = (18, 38, 66)
GREY = (90, 90, 90)
LIGHT = (238, 238, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=BLACK, leading=None):
    """Draw wrapped text starting at (x, y); returns the y just below it."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_centered(draw, cx, y, text, fnt, fill=BLACK):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.25)


def rule(draw, y, x0=None, x1=None, width=2):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=BLACK, width=width)
    return y + width + 2


def draw_skyline(draw, x0, y0, x1, y1):
    """A stylised Shanghai skyline: navy towers, a red sun, gold windows."""
    draw.rectangle([x0, y0, x1, y1], fill=(214, 228, 240))
    # red sun
    cx, cy, r = x0 + 120, y0 + 52, 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    # tower silhouettes (deterministic heights)
    base = y1
    towers = [
        (x0 + 30, 96), (x0 + 86, 128), (x0 + 142, 78), (x0 + 196, 118),
        (x0 + 252, 62), (x0 + 308, 104), (x0 + 364, 86), (x0 + 420, 122),
        (x0 + 476, 70), (x0 + 532, 108), (x0 + 588, 92), (x0 + 644, 126),
    ]
    for tx, th in towers:
        tw = 44
        draw.rectangle([tx, base - th, tx + tw, base], fill=NAVY)
        # antenna on the tallest tower
        if th == 62:
            draw.line([(tx + tw // 2, base - th), (tx + tw // 2, base - th - 26)],
                      fill=NAVY, width=4)
            draw.ellipse([tx + tw // 2 - 4, base - th - 32,
                          tx + tw // 2 + 4, base - th - 24], fill=RED)
    # gold windows, fixed grid
    for tx, th in towers:
        for row in range(2, th // 14):
            wy = base - row * 14
            for col in range(2):
                wx = tx + 8 + col * 20
                draw.rectangle([wx, wy, wx + 8, wy + 6], fill=(255, 196, 0))
    draw.rectangle([x0, y0, x1, y1], outline=BLACK, width=2)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([8, 8, W - 9, H - 9], outline=BLACK, width=3)

    f_mast = font("DejaVuSans-Bold.ttf", 58)
    f_date = font("DejaVuSans-Bold.ttf", 27)
    f_tag = font("DejaVuSans.ttf", 15)
    f_kick = font("DejaVuSans-Bold.ttf", 17)
    f_lead = font("DejaVuSans-Bold.ttf", 44)
    f_stand = font("DejaVuSans.ttf", 19)
    f_head = font("DejaVuSans-Bold.ttf", 25)
    f_body = font("DejaVuSans.ttf", 16)
    f_cap = font("DejaVuSans.ttf", 14)

    y = 26
    # masthead
    y = draw_centered(d, W // 2, y, "THE WORLD TODAY", f_mast)
    y = draw_centered(d, W // 2, y + 2, "WEDNESDAY 25 NOVEMBER 2026", f_date, fill=RED)
    y = draw_centered(d, W // 2, y + 2,
                      "THE DAY'S NEWS FROM AROUND THE WORLD  |  PRICE FREE", f_tag, fill=GREY)
    y = rule(d, y + 8, width=3)
    y = rule(d, y + 2, width=1)

    # lead story
    y += 6
    d.text((MARGIN, y), "CHINA IN TURMOIL", font=f_kick, fill=RED)
    y += 24
    y = draw_wrapped(d, MARGIN, y, "XI PROBES SHANGHAI BOSS IN SHOCK PURGE",
                     f_lead, CW, leading=52)
    y += 4
    y = draw_wrapped(
        d, MARGIN, y,
        "Politburo member Chen Jining, party chief of Shanghai since 2022 and a "
        "touted future leader, is under investigation for \"serious violations\" "
        "of discipline — the biggest shake-up of China's leadership in years.",
        f_stand, CW, leading=25)
    y += 8

    # skyline illustration + caption
    draw_skyline(d, MARGIN, y, W - MARGIN, y + 168)
    y += 168 + 8
    y = draw_wrapped(
        d, MARGIN, y,
        "Shanghai: Chen, 62, is the fourth Politburo member to fall since 2025 "
        "and the first serving Shanghai boss probed in two decades.",
        f_cap, CW, fill=GREY, leading=18)
    y += 6
    y = rule(d, y, width=2)

    # supporting stories
    y += 6
    y = draw_wrapped(d, MARGIN, y, "HUAWEI GUILTY OF STEALING TRADE SECRETS",
                     f_head, CW, leading=30)
    y = draw_wrapped(d, MARGIN, y,
                     "US jury convicts the tech giant on 10 of 12 counts, including bank "
                     "fraud and sanctions violations; acquitted of racketeering.",
                     f_body, CW, leading=21)
    y += 8
    y = draw_wrapped(d, MARGIN, y, "CIA HIT BY CYBER BREACH, NYT REPORTS",
                     f_head, CW, leading=30)
    y = draw_wrapped(d, MARGIN, y,
                     "Hackers breach an unclassified intelligence network used by the CIA "
                     "and ODNI; no classified systems affected, officials say.",
                     f_body, CW, leading=21)
    y += 8
    y = draw_wrapped(d, MARGIN, y, "YEMEN STRIKE KILLS 26",
                     f_head, CW, leading=30)
    y = draw_wrapped(d, MARGIN, y,
                     "Airstrike on buses and trucks in Lahj province kills 26, including "
                     "14 civilians, as Houthis and government forces trade blame.",
                     f_body, CW, leading=21)
    y += 10
    y = rule(d, y, width=2)

    # bottom strip: three smaller items in columns
    f_small_h = font("DejaVuSans-Bold.ttf", 16)
    f_small_b = font("DejaVuSans.ttf", 13)
    col_w = (CW - 40) // 3
    y += 8
    strip_top = y
    items = [
        ("HANOI BLAST KILLS 7",
         "Suspected gas blast at a hot-pot restaurant; nine hurt."),
        ("SENEGAL REGAIN AFCON TITLE",
         "CAS overturns ruling; Senegal take the crown back."),
        ("TRUMP PLANS NEW TARIFFS",
         "US eyes duties on 16 economies after capacity probe."),
    ]
    for i, (h, b) in enumerate(items):
        x = MARGIN + i * (col_w + 20)
        yy = strip_top
        yy = draw_wrapped(d, x, yy, h, f_small_h, col_w, leading=20)
        yy = draw_wrapped(d, x, yy + 2, b, f_small_b, col_w, leading=17)
        if i:
            d.line([(x - 10, strip_top), (x - 10, strip_top + 78)],
                   fill=GREY, width=1)
    y = strip_top + 92
    y = rule(d, y, width=1)
    draw_centered(d, W // 2, y + 4,
                  "THE WORLD TODAY  ·  Wednesday 25 November 2026", f_cap, fill=GREY)

    img.save(out, "PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
