"""Spero agent avatars, 512x512, bitsperity persona style (deep navy, fine grain, one gold symbol
with a soft glow). One symbol per agent of the Spero forest. Run: python3 spero/src/spero_art.py"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAVY_IN = np.array([22, 38, 72], float)
NAVY_OUT = np.array([11, 20, 42], float)
GOLD_HI = (240, 204, 120)
GOLD = (213, 166, 60)
GOLD_LO = (150, 104, 38)
S = 4
W = 512 * S
C = W / 2


def u(v):
    """Avatar units: -1..1 across the symbol box (0.30 W from the centre)."""
    return C + v * 0.30 * W


def base():
    yy, xx = np.mgrid[0:W, 0:W]
    d = np.clip(np.hypot(xx - C, yy - C) / (W * 0.72), 0, 1)[..., None]
    arr = NAVY_IN * (1 - d) + NAVY_OUT * d
    g = np.exp(-((xx - C) ** 2 + (yy - C) ** 2) / (2 * (W * 0.2) ** 2))[..., None]
    arr = arr + g * 0.20 * np.array([255, 160, 40], float) - g * 0.11 * np.array([0, 0, 60], float)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def line(d, pts, width=10, color=GOLD_HI, alpha=255):
    pts = [(u(x), u(y)) for x, y in pts]
    d.line(pts, fill=color + (alpha,), width=int(width * S), joint="curve")
    for x, y in (pts[0], pts[-1]):
        r = width * S / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))


def dot(d, x, y, r, color=GOLD_HI, alpha=255):
    d.ellipse([u(x) - r * S, u(y) - r * S, u(x) + r * S, u(y) + r * S], fill=color + (alpha,))


def ring(d, x, y, r, width=8, color=GOLD_HI, alpha=255):
    R = r * 0.30 * W
    d.ellipse([u(x) - R, u(y) - R, u(x) + R, u(y) + R], outline=color + (alpha,), width=int(width * S))


def arc(d, x, y, r, a0, a1, width=8, color=GOLD_HI, alpha=255):
    R = r * 0.30 * W
    d.arc([u(x) - R, u(y) - R, u(x) + R, u(y) + R], a0, a1, fill=color + (alpha,), width=int(width * S))


def rect(d, x0, y0, x1, y1, color=GOLD, alpha=255):
    d.rectangle([u(x0), u(y0), u(x1), u(y1)], fill=color + (alpha,))


# One symbol per agent. Coordinates in -1..1.
def floor(d):  # Desk: a speech bubble with three dots
    d.rounded_rectangle([u(-0.85), u(-0.6), u(0.85), u(0.45)], radius=int(0.09 * W), outline=GOLD_HI + (255,), width=int(10 * S))
    d.polygon([(u(-0.35), u(0.40)), (u(-0.55), u(0.85)), (u(-0.05), u(0.40))], fill=GOLD_HI + (255,))
    for x in (-0.38, 0, 0.38):
        dot(d, x, -0.07, 14, GOLD)


def notify(d):  # Wire: a mast sending waves
    line(d, [(0, -0.15), (0, 0.85)], 10)
    dot(d, 0, -0.2, 20)
    for r, a in ((0.42, 255), (0.70, 200), (0.98, 140)):
        arc(d, 0, -0.2, r, 215, 325, 9, alpha=a)
        arc(d, 0, -0.2, r, 35, 145, 9, alpha=a)


def scorecard(d):  # Scorecard: rising bars on a baseline
    for i, h in enumerate((0.35, 0.65, 0.5, 0.95)):
        x = -0.72 + i * 0.48
        rect(d, x - 0.15, 0.7 - h * 1.3, x + 0.15, 0.7, GOLD_HI if i == 3 else GOLD)
    line(d, [(-0.95, 0.82), (0.95, 0.82)], 7, GOLD_LO)


def macro(d):  # Macro: a globe
    ring(d, 0, 0, 0.9, 10)
    for k in (0.35, 0.7):
        d.ellipse([u(-k * 0.9), u(-0.9), u(k * 0.9), u(0.9)], outline=GOLD + (220,), width=int(6 * S))
    for y in (-0.45, 0, 0.45):
        w = math.sqrt(max(0, 0.81 - y * y))
        line(d, [(-w, y), (w, y)], 6, GOLD, 220)


def themes(d):  # Themes: three overlapping rings
    for x, y in ((-0.32, 0.22), (0.32, 0.22), (0, -0.33)):
        ring(d, x, y, 0.55, 9)
    dot(d, 0, 0.03, 16)


def hunt(d):  # Scout: a magnifying glass over a small star
    ring(d, -0.18, -0.18, 0.6, 11)
    line(d, [(0.26, 0.26), (0.82, 0.82)], 16)
    dot(d, -0.18, -0.18, 15, GOLD)


def depth(d):  # Dossier: stacked layers
    for i, a in enumerate((140, 200, 255)):
        y = 0.45 - i * 0.42
        pts = [(u(-0.85), u(y)), (u(0), u(y - 0.35)), (u(0.85), u(y)), (u(0), u(y + 0.35))]
        d.polygon(pts, outline=GOLD_HI + (a,), width=int(9 * S))


def hygiene(d):  # Watch: an eye
    arc(d, 0, 0.75, 1.2, 219, 321, 10)
    arc(d, 0, -0.75, 1.2, 39, 141, 10)
    ring(d, 0, 0, 0.33, 9)
    dot(d, 0, 0, 22, GOLD)


def book(d):  # Portfolio: a pie with one slice out
    R = 0.8 * 0.30 * W
    d.pieslice([C - R, C - R, C + R, C + R], -60, 260, fill=GOLD + (255,))
    off = 0.12 * 0.30 * W
    a = math.radians(-80)
    cx, cy = C + off * math.cos(a), C + off * math.sin(a)
    d.pieslice([cx - R, cy - R, cx + R, cy + R], -100, -60, fill=GOLD_HI + (255,))


def tape(d):  # Charts: candlesticks
    for i, (o, c, lo, hi) in enumerate(((0.3, -0.1, 0.55, -0.3), (-0.05, -0.45, 0.15, -0.7), (-0.35, 0.1, 0.3, -0.55), (0.0, -0.6, 0.2, -0.85))):
        x = -0.66 + i * 0.44
        line(d, [(x, lo), (x, hi)], 6, GOLD)
        up = c < o
        rect(d, x - 0.12, min(o, c), x + 0.12, max(o, c), GOLD_HI if up else GOLD_LO)
    line(d, [(-0.95, 0.8), (0.95, 0.8)], 6, GOLD_LO)


def plan(d):  # Plan: a target with an arrow in it
    for r, a in ((0.85, 160), (0.55, 210), (0.25, 255)):
        ring(d, 0, 0, r, 9, alpha=a)
    line(d, [(0.0, 0.0), (0.75, -0.75)], 9)
    d.polygon([(u(0.0), u(0.0)), (u(0.25), u(-0.08)), (u(0.08), u(-0.25))], fill=GOLD_HI + (255,))


def pulse(d):  # Pulse: a heartbeat line
    line(d, [(-0.95, 0.1), (-0.45, 0.1), (-0.3, -0.25), (-0.12, 0.6), (0.08, -0.75), (0.25, 0.3), (0.38, 0.1), (0.95, 0.1)], 11)


def thesis(d):  # Thesis: a small graph tree
    nodes = {"r": (0, -0.7), "a": (-0.55, -0.05), "b": (0.55, -0.05), "c": (-0.8, 0.65), "e": (-0.25, 0.65), "f": (0.55, 0.65)}
    for p, q in (("r", "a"), ("r", "b"), ("a", "c"), ("a", "e"), ("b", "f")):
        line(d, [nodes[p], nodes[q]], 7, GOLD, 230)
    for k, (x, y) in nodes.items():
        dot(d, x, y, 24 if k == "r" else 17, GOLD_HI if k == "r" else GOLD)


def committer(d):  # Committer: a seal with a check
    ring(d, 0, 0, 0.85, 9)
    for i in range(24):
        a = i * math.pi / 12
        line(d, [(0.85 * math.sin(a), 0.85 * math.cos(a)), (0.97 * math.sin(a), 0.97 * math.cos(a))], 5, GOLD, 200)
    line(d, [(-0.4, 0.02), (-0.1, 0.32), (0.45, -0.3)], 15)


AGENTS = [floor, notify, scorecard, macro, themes, hunt, depth, hygiene, book, tape, plan, pulse, thesis, committer]


def render(draw_symbol, seed):
    img = base()
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    draw_symbol(ImageDraw.Draw(layer))
    halo = layer.filter(ImageFilter.GaussianBlur(14 * S))
    img.alpha_composite(Image.fromarray((np.asarray(halo, float) * np.array([1, 1, 1, 0.55])).astype(np.uint8), "RGBA"))
    img.alpha_composite(layer)
    small = np.asarray(img.convert("RGB").resize((512, 512), Image.LANCZOS), float)
    noise = np.random.default_rng(seed).normal(0, 6, small.shape[:2])[..., None]
    return Image.fromarray(np.clip(small + noise, 0, 255).astype(np.uint8), "RGB")


if __name__ == "__main__":
    for i, fn in enumerate(AGENTS):
        render(fn, 100 + i).save(os.path.join(OUT, f"{fn.__name__}.jpg"), quality=90)
    print("ok")
