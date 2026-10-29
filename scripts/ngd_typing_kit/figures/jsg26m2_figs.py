# -*- coding: utf-8 -*-
"""진성고 jsg26m2 Q16, Q25 본문 그림.
실행: python3 jsg26m2_figs.py"""
import numpy as np
from figlib import Fig


def q16():
    f = Fig('jsg26m2_q16', 20000, (-2.0, 4.5), (-6.0, 4.5))
    A = (3.2, 2.6)
    B = (2, -4.5)
    D = (0.8, 1.8)
    C = (0, -1.0)
    xs = np.linspace(-1.8, 4.3, 10)
    f.ax.plot(xs, xs + 1, color='k', lw=0.9, zorder=2)
    f.ax.annotate('', xy=(4.3, 0), xytext=(-1.8, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.ax.annotate('', xy=(0, 4.3), xytext=(0, -5.8),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.seg(A, D, lw=1.1)
    f.seg(D, C, lw=1.1)
    f.seg(C, B, lw=1.1)
    f.dot(A)
    f.dot(B)
    f.dot(D)
    f.dot(C)
    f.hytext('A', A, dx=10, dy=4, fs=10)
    f.hytext('B', B, dx=10, dy=-4, fs=10)
    f.hytext('D', D, dx=-14, dy=8, fs=10)
    f.hytext('C', C, dx=-13, dy=0, fs=10)
    f.hytext('O', (0, 0), dx=-11, dy=-12, fs=9)
    f.hytext('x', (4.3, 0), dx=8, dy=-10, fs=10, italic=True)
    f.hytext('y', (0, 4.3), dx=8, dy=0, fs=10, italic=True)
    f.lab(r'$y=x+1$', (3.6, 4.6), dx=0, dy=8, fs=9)
    f.save()


def q25():
    f = Fig('jsg26m2_q25', 20000, (-4.0, 4.5), (-1.0, 6.5))
    xs = np.linspace(-3.8, 4.3, 200)
    f.ax.plot(xs, 0.5 * xs ** 2, color='k', lw=1.0, zorder=2)
    O = (0.0, 0.0)
    A = (-1.0, 0.5)
    B = (3.6, 6.48)
    xs2 = np.linspace(-1.6, 4.0, 10)
    slope = (B[1] - A[1]) / (B[0] - A[0])
    intercept = A[1] - slope * A[0]
    f.ax.plot(xs2, slope * xs2 + intercept, color='k', lw=0.9, zorder=2)
    cx, cy = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    rad = ((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2) ** 0.5 / 2
    th = np.linspace(0, 2 * np.pi, 200)
    f.ax.plot(cx + rad * np.cos(th), cy + rad * np.sin(th), color='k', lw=0.9, zorder=1)
    P = (-2.6, 3.38)
    f.seg(O, A, lw=0.7)
    f.seg(O, B, lw=0.7)
    f.seg(A, P, lw=0.7)
    f.seg(B, P, lw=0.7)
    f.dot(O)
    f.dot(A)
    f.dot(B)
    f.dot(P)
    f.hytext('O', O, dx=10, dy=-10, fs=10)
    f.hytext('A', A, dx=-12, dy=-10, fs=10)
    f.hytext('B', B, dx=8, dy=8, fs=10)
    f.hytext('P', P, dx=-12, dy=6, fs=10)
    f.hytext('C', (cx + rad * 0.65, cy + rad * 0.55), dx=6, dy=6, fs=10)
    f.lab(r'$y=f(x)$', (-3.6, 4.6), dx=0, dy=10, fs=9)
    f.lab(r'$y=g(x)$', (2.2, 6.1), dx=0, dy=10, fs=9)
    f.save()


if __name__ == '__main__':
    q16()
    q25()
    print('done')
