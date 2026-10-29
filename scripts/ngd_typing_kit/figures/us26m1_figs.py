# -*- coding: utf-8 -*-
"""운산고 us26m1 Q8, Q15, Q17 본문 그림.
실행: python3 us26m1_figs.py"""
import numpy as np
from figlib import Fig


def q08():
    f = Fig('us26m1_q08', 20000, (-2.5, 9.5), (-4.3, 4.3))
    # cone (left)
    apex = (0.5, 4.0)
    bl = (-1.5, -4.0)
    br = (2.5, -4.0)
    f.seg(apex, bl, lw=1.1)
    f.seg(apex, br, lw=1.1)
    f.dashed(bl, br, lw=0.7)
    f.lab('$3$', (0.5, -4.0), dx=-18, dy=4, fs=9)
    # unfolded sector (right)
    cx, cy = 6.3, 1.5
    R = 2.8
    ang0, ang1 = -70, 70
    th = np.linspace(np.radians(ang0), np.radians(ang1), 100)
    xs = cx + R * np.cos(th)
    ys = cy + R * np.sin(th)
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)
    A = (cx + R * np.cos(np.radians(ang1)), cy + R * np.sin(np.radians(ang1)))
    B = (cx + R * np.cos(np.radians(ang0)), cy + R * np.sin(np.radians(ang0)))
    f.seg((cx, cy), A, lw=1.0)
    f.seg((cx, cy), B, lw=1.0)
    f.dot((cx, cy))
    f.hytext('O', (cx, cy), dx=-6, dy=10, fs=9)
    f.hytext('A', A, dx=8, dy=0, fs=9)
    f.hytext('B', B, dx=0, dy=-14, fs=9)
    f.save()


def q15():
    f = Fig('us26m1_q15', 20000, (-0.6, 8.6), (-1.6, 4.2))
    B = (0.0, 0.0)
    C = (8.0, 0.0)
    H = (1.5, 0.0)
    A = (1.5, 3.6)
    f.seg(B, C, lw=1.1)
    f.seg(A, B, lw=1.0)
    f.seg(A, C, lw=1.0)
    f.seg(A, H, lw=0.9)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(H)
    f.hytext('A', A, dx=0, dy=14, fs=10)
    f.hytext('B', B, dx=-11, dy=-6, fs=10)
    f.hytext('C', C, dx=11, dy=-6, fs=10)
    f.hytext('H', H, dx=0, dy=-14, fs=10)
    f.lab('$27$', (A[0] + H[0], A[1] + H[1]), dx=10, dy=0, fs=9)
    f.lab('$x$', ((B[0] + H[0]) / 2, 0), dx=0, dy=-32, fs=9, italic=True)
    f.lab('$y$', ((H[0] + C[0]) / 2, 0), dx=0, dy=-32, fs=9, italic=True)
    f.save()


def q17():
    f = Fig('us26m1_q17', 20000, (-2.0, 2.3), (-1.6, 2.9))
    th = np.linspace(0, 2 * np.pi, 200)
    f.ax.plot(np.cos(th), np.sin(th), color='k', lw=1.0, zorder=2)
    P = (-np.sqrt(2), np.sqrt(6))
    Pp = (-0.5, np.sqrt(3) / 2)
    A = (1, 0)
    B = (-1, 0)
    H = (-0.5, 0)
    O = (0, 0)
    f.seg(O, P, lw=0.8)
    f.seg(Pp, H, lw=0.7)
    f.dot(P)
    f.dot(Pp)
    f.dot(A)
    f.dot(B)
    f.dot(H)
    f.dot(O)
    f.ax.annotate('', xy=(0, 2.7), xytext=(0, -1.4),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(2.1, 0), xytext=(-1.9, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 2.7), dx=8, dy=0, fs=9, italic=True)
    f.hytext('x', (2.1, 0), dx=8, dy=-8, fs=9, italic=True)
    f.hytext('O', O, dx=8, dy=-10, fs=9)
    f.hytext('A', A, dx=8, dy=6, fs=9)
    f.hytext('B', B, dx=-10, dy=6, fs=9)
    f.hytext('H', H, dx=-10, dy=-10, fs=9)
    f.lab("$P'$", Pp, dx=-8, dy=10, fs=9)
    f.lab(r'$P(-\sqrt{2},\sqrt{6})$', P, dx=4, dy=10, fs=8)
    f.save()


if __name__ == '__main__':
    q08()
    q15()
    q17()
    print('done')
