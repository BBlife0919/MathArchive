# -*- coding: utf-8 -*-
"""소하고 sh26f(2026 1학기기말 대수) 그림: Q6 원-현, Q13 두 건물, Q19 원에 내접하는 사각형.
실행: python3 sh26f_figs.py"""
import math
import numpy as np
from figlib import Fig


def q06():
    f = Fig('sh26f_q06', 18000, (-6.4, 6.4), (-6.0, 6.6))
    O = (0, 0)
    R = 5
    f.circle(O, R, lw=1.2)
    f.dot(O)
    f.lab('$O$', O, dx=10, dy=10, fs=10)
    A = (-4, -3)
    B = (4, -3)
    H = (0, -3)
    f.seg(A, B, lw=1.2)
    f.seg(O, H, lw=0.9)
    f.rightangle(H, O, A, 0.35)
    f.dot(A); f.dot(B)
    f.lab('$3$', (0, -1.5), dx=10, dy=0, fs=9.5)
    f.lab('$A$', A, dx=-12, dy=-10, fs=10)
    f.lab('$B$', B, dx=12, dy=-10, fs=10)
    ang_c = 105
    C = (R * math.cos(math.radians(ang_c)), R * math.sin(math.radians(ang_c)))
    f.dot(C)
    f.lab('$C$', C, dx=-4, dy=14, fs=10)
    f.save()


def q13():
    f = Fig('sh26f_q13', 24000, (-5.2, 29.5), (-2.0, 46.0))
    h1 = 20 * math.sqrt(3)
    H = 15 * math.sqrt(3) + 15
    d = H / math.sqrt(3)
    x1 = 0.0
    w1 = 3.0
    x2 = d
    w2 = 4.2
    # 건물1 (왼쪽, 낮음)
    f.poly([(x1, 0), (x1 + w1, 0), (x1 + w1, h1), (x1, h1)], lw=1.2)
    for gy in np.arange(4, h1 - 2, 4.5):
        f.seg((x1 + 0.5, gy), (x1 + w1 - 0.5, gy), lw=0.5)
    # 건물2 (오른쪽, 높음)
    f.poly([(x2, 0), (x2 + w2, 0), (x2 + w2, H), (x2, H)], lw=1.2)
    for gy in np.arange(4, H - 2, 4.5):
        f.seg((x2 + 0.5, gy), (x2 + w2 - 0.5, gy), lw=0.5)
    base1 = (x1 + w1, 0)
    roof1 = (x1 + w1, h1)
    top2 = (x2, H)
    f.dashed(base1, top2, lw=0.7)
    f.dashed(roof1, top2, lw=0.7)
    f.dashed(roof1, (x2, roof1[1]), lw=0.6)
    f.angle(base1, (x1 + w1 + 3, 0), top2, 3.2, text=r'$60^{\circ}$', fs=9)
    f.angle(roof1, (x2, roof1[1]), top2, 2.6, text=r'$15^{\circ}$', fs=9)
    f.lab(r'$20\sqrt{3}$', (x1, h1 / 2), dx=-10, dy=0, fs=9.5, ha='right')
    f.save()


def q19():
    f = Fig('sh26f_q19', 20000, (-2.2, 6.0), (-2.6, 5.4))
    O = (1.6, 1.4)
    R = 2.55
    f.circle(O, R, lw=1.1)

    def pt(ang):
        r = math.radians(ang)
        return (O[0] + R * math.cos(r), O[1] + R * math.sin(r))

    A = pt(160)
    B = pt(230)
    C = pt(320)
    D = pt(70)
    for p, q in [(A, B), (B, C), (C, D), (D, A), (A, C), (B, D)]:
        f.seg(p, q, lw=1.1)

    def line_intersect(p1, p2, p3, p4):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
        return (px, py)

    E = line_intersect(A, C, B, D)
    for p in (A, B, C, D):
        f.dot(p)
    f.dot(E)
    f.lab('$A$', A, dx=-14, dy=0, fs=10)
    f.lab('$B$', B, dx=-6, dy=-14, fs=10)
    f.lab('$C$', C, dx=10, dy=-10, fs=10)
    f.lab('$D$', D, dx=6, dy=12, fs=10)
    f.lab('$E$', E, dx=-4, dy=13, fs=9.5)
    f.save()


if __name__ == '__main__':
    q06()
    q13()
    q19()
    print('done')
