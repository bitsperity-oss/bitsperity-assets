"""Weaver agent avatars, 512x512, in the bitsperity persona style of the Spero avatars (deep navy, fine
grain, one gold symbol with a soft glow). One symbol per agent of the Weaver forest. The drawing helpers
are Spero's. Run: python3 weaver/src/weaver_art.py"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..")
_spec = importlib.util.spec_from_file_location("spero_art", os.path.join(HERE, "..", "..", "spero", "src", "spero_art.py"))
art = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(art)
u, line, dot, ring, GOLD, GOLD_HI, GOLD_LO, S, W = art.u, art.line, art.dot, art.ring, art.GOLD, art.GOLD_HI, art.GOLD_LO, art.S, art.W


def planner(d):  # Plan: a decision at the top, the work that follows from it below
    line(d, [(0, -0.72), (0, -0.2)], 8, GOLD, 230)
    line(d, [(-0.62, -0.2), (0.62, -0.2)], 8, GOLD, 230)
    for x in (-0.62, 0, 0.62):
        line(d, [(x, -0.2), (x, 0.32)], 8, GOLD, 230)
        d.rounded_rectangle([u(x - 0.2), u(0.32), u(x + 0.2), u(0.72)], radius=int(0.012 * W), outline=GOLD_HI + (255,), width=int(8 * S))
    d.polygon([(u(0), u(-0.98)), (u(0.26), u(-0.72)), (u(0), u(-0.46)), (u(-0.26), u(-0.72))], fill=GOLD_HI + (255,))


def builder(d):  # Build: a weave, three strands over and under three
    xs = ys = (-0.55, 0, 0.55)
    gap = 0.13
    for i, y in enumerate(ys):
        cuts = [x for j, x in enumerate(xs) if (i + j) % 2 == 0]
        edges = [-0.92] + [e for x in cuts for e in (x - gap, x + gap)] + [0.92]
        for a, b in zip(edges[0::2], edges[1::2]):
            line(d, [(a, y), (b, y)], 13, GOLD_HI)
    for j, x in enumerate(xs):
        cuts = [y for i, y in enumerate(ys) if (i + j) % 2 == 1]
        edges = [-0.92] + [e for y in cuts for e in (y - gap, y + gap)] + [0.92]
        for a, b in zip(edges[0::2], edges[1::2]):
            line(d, [(x, a), (x, b)], 13, GOLD)


def checker(d):  # Check: it is run, not read
    ring(d, 0, 0, 0.88, 10)
    d.polygon([(u(-0.28), u(-0.46)), (u(0.5), u(0)), (u(-0.28), u(0.46))], fill=GOLD_HI + (255,))


def merger(d):  # Merge: two branches become one line
    line(d, [(-0.55, -0.8), (-0.55, -0.35), (0, 0.15), (0, 0.8)], 12)
    line(d, [(0.55, -0.8), (0.55, -0.35), (0, 0.15)], 12, GOLD)
    dot(d, -0.55, -0.8, 22)
    dot(d, 0.55, -0.8, 22, GOLD)
    dot(d, 0, 0.8, 26)


def tester(d):  # Walk: a window and the pointer that uses it
    d.rounded_rectangle([u(-0.9), u(-0.7), u(0.9), u(0.62)], radius=int(0.03 * W), outline=GOLD + (255,), width=int(9 * S))
    line(d, [(-0.9, -0.36), (0.9, -0.36)], 7, GOLD, 230)
    for x in (-0.68, -0.5, -0.32):
        dot(d, x, -0.53, 8, GOLD)
    d.polygon([(u(0.02), u(-0.12)), (u(0.02), u(0.74)), (u(0.24), u(0.52)), (u(0.4), u(0.86)), (u(0.54), u(0.79)), (u(0.38), u(0.46)), (u(0.68), u(0.46))], fill=GOLD_HI + (255,))


def reader(d):  # Read: an eye that sees the plan and writes nothing
    upper = [(x / 20 * 0.9, -0.48 * (1 - (x / 20) ** 2)) for x in range(-20, 21)]
    lower = [(x, -y) for x, y in upper]
    line(d, upper, 10, GOLD_HI)
    line(d, lower, 10, GOLD)
    ring(d, 0, 0, 0.3, 9)
    dot(d, 0, 0, 30)


AGENTS = [planner, builder, checker, merger, tester, reader]

if __name__ == "__main__":
    for i, fn in enumerate(AGENTS):
        art.render(fn, 300 + i).save(os.path.join(OUT, f"{fn.__name__}.jpg"), quality=90)
    print("ok")
