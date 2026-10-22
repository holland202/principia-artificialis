#!/usr/bin/env python3
"""Animated PA logo: the 600-cell turning in four dimensions, as a seamless loop.

The 600-cell's 120 vertices are the unit quaternions of the binary icosahedral group 2I:
  8 of the form (+-1,0,0,0) permuted, 16 of the form (+-1/2,+-1/2,+-1/2,+-1/2), and 96 even
  permutations of (+-phi/2, +-1/2, +-1/(2 phi), 0). Its 720 edges join vertices at distance 1/phi.

Motion: every vertex v is left-multiplied by q(t) = exp(t * pi/5 * u), an isoclinic ("Clifford")
rotation of 4-space. u is chosen so that q(1) = phi/2 + (1/2) i + (1/(2 phi)) j, which is itself an
element of 2I (order 10). Left multiplication by a group element permutes the vertex set, so the frame
at t = 1 is the frame at t = 0: the loop closes exactly, by group theory, not by fading.
Points then move along great circles (Hopf fibres). Projection: 4D -> 3D perspective in w, 3D -> 2D
perspective after a fixed tilt. Colours follow 4D depth, magenta (near) to cyan (far), matching the static logo.

Writes figures/principia_hero_animated.webp (animated WebP) (the banner with the polytope animated; the right-hand text is
copied unchanged from figures/principia_hero.png) and prints the checks it relies on.
Requires numpy and Pillow.
"""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PHI = (1 + 5 ** 0.5) / 2
ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "figures" / "principia_hero.png"
OUT = ROOT / "figures" / "principia_hero_animated.webp"
CENTER, RADIUS = (491, 318), 150            # where the static logo sits in the banner
CLEAR_BOX = (325, 155, 660, 482)            # region repainted each frame
FRAMES, MS_PER_FRAME, SS = 60, 50, 3        # 3 s loop; 3x supersampling for smooth lines
BG = (7, 10, 18)
NEAR, FAR = np.array([217, 70, 239]), np.array([34, 211, 238])   # magenta (near, outer) -> cyan (far, inner), as in the static logo


def even_perms(seq):
    out = []
    for p in itertools.permutations(range(4)):
        inv = sum(1 for i in range(4) for j in range(i + 1, 4) if p[i] > p[j])
        if inv % 2 == 0:
            out.append(tuple(seq[i] for i in p))
    return out


def vertices():
    v = set()
    for i in range(4):
        for s in (1, -1):
            e = [0.0] * 4
            e[i] = s
            v.add(tuple(e))
    for signs in itertools.product((0.5, -0.5), repeat=4):
        v.add(signs)
    base = (PHI / 2, 0.5, 1 / (2 * PHI), 0.0)
    for signs in itertools.product((1, -1), repeat=3):
        b = (base[0] * signs[0], base[1] * signs[1], base[2] * signs[2], 0.0)
        for p in even_perms(b):
            v.add(tuple(round(x, 12) + 0.0 for x in p))
    return np.array(sorted(v))


def qmul(a, b):
    """Hamilton product, rows of a times quaternion b... here: q (single) times each row of b."""
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b.T
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                     w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], axis=1)


def checks(V, E):
    n_ok = len(V) == 120
    unit = np.allclose(np.linalg.norm(V, axis=1), 1)
    e_ok = len(E) == 720
    deg = np.bincount(E.ravel(), minlength=len(V))
    q1 = np.array([PHI / 2, 0.5, 1 / (2 * PHI), 0.0])
    W = qmul(q1, V)
    closes = all(np.min(np.linalg.norm(V - w, axis=1)) < 1e-9 for w in W)
    # control: a rotation by a generic angle must NOT map the vertex set to itself
    ang = 0.37
    u = q1[1:] / np.linalg.norm(q1[1:])
    qg = np.concatenate([[math.cos(ang)], math.sin(ang) * u])
    G = qmul(qg, V)
    control_moves = not all(np.min(np.linalg.norm(V - w, axis=1)) < 1e-9 for w in G)
    print(f"vertices {len(V)} (expect 120), all unit norm: {unit}")
    print(f"edges {len(E)} (expect 720), every vertex degree 12: {bool(np.all(deg == 12))}")
    print(f"loop closes (q(1) in 2I permutes vertices): {closes}")
    print(f"control: generic angle 0.37 rad does not close: {control_moves}")
    return n_ok and unit and e_ok and bool(np.all(deg == 12)) and closes and control_moves


def project(P):
    w = P[:, 0]
    s4 = 1.0 / (2.2 - w)                              # 4D -> 3D perspective
    X = P[:, 1:] * s4[:, None]
    tilt = math.radians(22)
    c, s = math.cos(tilt), math.sin(tilt)
    y, z = X[:, 1] * c - X[:, 2] * s, X[:, 1] * s + X[:, 2] * c
    s3 = 1.0 / (2.6 - z)                               # 3D -> 2D perspective
    return np.stack([X[:, 0] * s3, y * s3], axis=1), w


def main():
    V = vertices()
    D = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=2)
    E = np.argwhere(np.triu(np.abs(D - 1 / PHI) < 1e-9))
    if not checks(V, E):
        print("CHECK FAILED: not writing the animation")
        return 1
    hero = Image.open(HERO).convert("RGB")
    q1 = np.array([PHI / 2, 0.5, 1 / (2 * PHI), 0.0])
    u = q1[1:] / np.linalg.norm(q1[1:])
    theta = math.acos(q1[0])                           # = pi/5
    # scale so the t=0 picture has the same radius as the static logo
    xy0, _ = project(V)
    scale = RADIUS / np.max(np.linalg.norm(xy0, axis=1))
    bw, bh = CLEAR_BOX[2] - CLEAR_BOX[0], CLEAR_BOX[3] - CLEAR_BOX[1]
    cx, cy = (CENTER[0] - CLEAR_BOX[0]) * SS, (CENTER[1] - CLEAR_BOX[1]) * SS
    frames = []
    for k in range(FRAMES):
        t = k / FRAMES
        q = np.concatenate([[math.cos(t * theta)], math.sin(t * theta) * u])
        P = qmul(q, V)
        xy, w = project(P)
        pts = np.stack([cx + xy[:, 0] * scale * SS, cy - xy[:, 1] * scale * SS], axis=1)
        depth = (w + 1) / 2                              # 0 far .. 1 near
        tile = Image.new("RGB", (bw * SS, bh * SS), BG)
        dr = ImageDraw.Draw(tile)
        order = np.argsort([depth[a] + depth[b] for a, b in E])   # far edges first
        for idx in order:
            a, b = E[idx]
            d = (depth[a] + depth[b]) / 2
            col = FAR + (NEAR - FAR) * d
            col = tuple(int(c * (0.35 + 0.45 * d) + BG[i] * (0.65 - 0.45 * d)) for i, c in enumerate(col))
            dr.line([tuple(pts[a]), tuple(pts[b])], fill=col, width=SS)
        for i in np.argsort(depth):
            d = depth[i]
            col = tuple(int(c) for c in FAR + (NEAR - FAR) * d)
            r = (1.2 + 2.6 * d) * SS
            x, y = pts[i]
            dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
        tile = tile.resize((bw, bh), Image.LANCZOS)
        frame = hero.copy()
        frame.paste(tile, CLEAR_BOX[:2])
        frames.append(frame)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=MS_PER_FRAME, loop=0,
                   quality=78, method=6, minimize_size=True)
    print(f"wrote {OUT.relative_to(ROOT)}: {FRAMES} frames x {MS_PER_FRAME} ms, {OUT.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
