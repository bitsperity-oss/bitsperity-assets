"""Wayfinder persona art: avatar 512x512 and banner 1500x500, bitsperity persona style
(deep navy, fine grain, one gold symbol with a soft glow)."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAVY_IN = np.array([22, 38, 72], float)
NAVY_OUT = np.array([11, 20, 42], float)
GOLD_HI = (240, 204, 120)
GOLD = (213, 166, 60)
GOLD_LO = (150, 104, 38)


def background(w, h, cx, cy, radius):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.clip(np.hypot(xx - cx, yy - cy) / radius, 0, 1)[..., None]
    img = NAVY_IN * (1 - d) + NAVY_OUT * d
    return img


def glow(w, h, cx, cy, radius, strength):
    yy, xx = np.mgrid[0:h, 0:w]
    g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * radius ** 2))[..., None]
    return g * strength * np.array([255, 160, 40], float) - g * strength * 0.55 * np.array([0, 0, 60], float)


def grain(arr, amount, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, arr.shape[:2])[..., None]
    return np.clip(arr + n, 0, 255)


def to_img(arr):
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def star(draw, cx, cy, long, short, waist, rot=0.0):
    """Faceted eight-point compass star: each point is a kite split into a light and a dark half."""
    for i in range(8):
        a = rot + i * math.pi / 4
        length = long if i % 2 == 0 else short
        w = waist if i % 2 == 0 else waist * 0.75
        tip = (cx + length * math.sin(a), cy - length * math.cos(a))
        left = (cx + w * math.sin(a - math.pi / 2), cy - w * math.cos(a - math.pi / 2))
        right = (cx + w * math.sin(a + math.pi / 2), cy - w * math.cos(a + math.pi / 2))
        light, dark = (GOLD_HI, GOLD_LO) if i % 2 == 0 else (GOLD, GOLD_LO)
        draw.polygon([(cx, cy), left, tip], fill=light)
        draw.polygon([(cx, cy), right, tip], fill=dark)


def avatar():
    S = 4
    W = 512 * S
    c = W / 2
    arr = background(W, W, c, c, W * 0.72)
    arr = arr + glow(W, W, c, c, W * 0.16, 0.22)
    img = to_img(np.clip(arr, 0, 255))
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # plate ring and compass ticks
    r = 0.30 * W
    d.ellipse([c - r, c - r, c + r, c + r], outline=GOLD + (150,), width=int(2.2 * S))
    r2 = r - 9 * S
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=GOLD + (60,), width=int(1.2 * S))
    for i in range(32):
        a = i * math.pi / 16
        inner = r - (14 if i % 4 == 0 else 7) * S
        d.line([(c + inner * math.sin(a), c - inner * math.cos(a)),
                (c + r * math.sin(a), c - r * math.cos(a))],
               fill=GOLD + (170 if i % 4 == 0 else 90,), width=int((2 if i % 4 == 0 else 1.2) * S))
    star(d, c, c, long=0.235 * W, short=0.12 * W, waist=0.034 * W, rot=0)
    img = img.convert("RGBA")
    img.alpha_composite(layer)
    # bright core
    core = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse([c - 9 * S, c - 9 * S, c + 9 * S, c + 9 * S], fill=(255, 238, 200, 255))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(6 * S)))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(1.5 * S)))
    small = img.convert("RGB").resize((512, 512), Image.LANCZOS)
    out = to_img(grain(np.asarray(small, float), 6, 7))
    out.save(os.path.join(OUT, "wayfinder-avatar.jpg"), quality=92)


def banner():
    S = 3
    W, H = 1500 * S, 500 * S
    tx, ty = 0.74 * W, 0.46 * H  # destination star
    arr = background(W, H, tx, ty, W * 0.75)
    arr = arr + glow(W, H, tx, ty, H * 0.30, 0.26)
    img = to_img(np.clip(arr, 0, 255)).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # faint chart: meridian arcs and parallels
    for k in range(-6, 7):
        x0 = tx + k * 0.09 * W
        d.arc([x0 - 1.6 * H, -0.9 * H, x0 + 1.6 * H, 2.9 * H], 250, 290, fill=GOLD + (22,), width=int(1 * S))
    for k in range(1, 6):
        y = k * H / 6
        d.line([(0, y), (W, y)], fill=GOLD + (14,), width=int(1 * S))
    # background stars
    rnd = random.Random(11)
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        rr = rnd.choice([0.6, 0.8, 1.0, 1.4]) * S
        a = rnd.randint(40, 140)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(230, 220, 190, a))
    # route: a branching path of waypoints toward the destination star
    pts = [(0.30, 0.78), (0.38, 0.62), (0.47, 0.70), (0.55, 0.52), (0.63, 0.58), (0.74, 0.46)]
    pts = [(x * W, y * H) for x, y in pts]
    branches = [((0.47, 0.70), (0.52, 0.86)), ((0.55, 0.52), (0.58, 0.30)), ((0.58, 0.30), (0.66, 0.22)),
                ((0.63, 0.58), (0.69, 0.74)), ((0.38, 0.62), (0.41, 0.42))]

    def dashed(p, q, color, width, dash, gap):
        L = math.dist(p, q)
        n = int(L // (dash + gap)) + 1
        for i in range(n):
            s = i * (dash + gap) / L
            e = min(1, (i * (dash + gap) + dash) / L)
            d.line([(p[0] + (q[0] - p[0]) * s, p[1] + (q[1] - p[1]) * s),
                    (p[0] + (q[0] - p[0]) * e, p[1] + (q[1] - p[1]) * e)], fill=color, width=width)

    for (a, b) in branches:
        a, b = (a[0] * W, a[1] * H), (b[0] * W, b[1] * H)
        dashed(a, b, GOLD + (90,), int(1.4 * S), 7 * S, 6 * S)
        d.ellipse([b[0] - 3 * S, b[1] - 3 * S, b[0] + 3 * S, b[1] + 3 * S], outline=GOLD + (150,), width=int(1.2 * S))
    for p, q in zip(pts, pts[1:]):
        dashed(p, q, GOLD_HI + (200,), int(2.2 * S), 12 * S, 7 * S)
    for p in pts[:-1]:
        d.ellipse([p[0] - 5 * S, p[1] - 5 * S, p[0] + 5 * S, p[1] + 5 * S], fill=GOLD + (230,))
        d.ellipse([p[0] - 10 * S, p[1] - 10 * S, p[0] + 10 * S, p[1] + 10 * S], outline=GOLD + (80,), width=int(1 * S))
    # destination: ring and compass star
    r = 0.15 * H
    d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=GOLD + (120,), width=int(1.6 * S))
    star(d, tx, ty, long=0.19 * H, short=0.095 * H, waist=0.026 * H)
    img.alpha_composite(layer)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse([tx - 8 * S, ty - 8 * S, tx + 8 * S, ty + 8 * S], fill=(255, 238, 200, 255))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(7 * S)))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(1.5 * S)))
    small = img.convert("RGB").resize((1500, 500), Image.LANCZOS)
    out = to_img(grain(np.asarray(small, float), 6, 13))
    out.save(os.path.join(OUT, "wayfinder-banner.jpg"), quality=92)


if __name__ == "__main__":
    avatar()
    banner()
    print("ok")
