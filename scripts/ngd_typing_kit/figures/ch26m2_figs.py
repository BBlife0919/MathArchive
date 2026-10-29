# -*- coding: utf-8 -*-
"""충현고 ch26m2 그림: Q04(조각 그래프), Q17(원-직선 구성도). 실행: python3 ch26m2_figs.py"""
import math
import numpy as np
from figlib import Fig


def q04():
    f = Fig('ch26m2_q04', 20000, (-2.6, 2.3), (-0.6, 3.1))
    xs1 = np.linspace(-2.4, -1, 60)
    f.ax.plot(xs1, xs1 + 3, color='k', lw=1.2, zorder=3)
    f.dot((-1, 2))
    xs2 = np.linspace(-1, 1, 120)
    f.ax.plot(xs2, xs2 ** 2 + 1, color='k', lw=1.2, zorder=3)
    f.dot((0, 1))
    f.circle((1, 2), 0.06, fill='white', z=4)
    f.dot((1, 1))
    xs3 = np.linspace(1, 2.2, 40)
    f.ax.plot(xs3, np.ones_like(xs3), color='k', lw=1.2, zorder=3)
    f.dashed((-1, 0), (-1, 2), lw=0.6)
    f.dashed((-2.3, 2), (1, 2), lw=0.6)
    f.dashed((0, 0), (0, 1), lw=0.6)
    f.dashed((1, 0), (1, 1), lw=0.6)
    f.ax.annotate('', xy=(2.3, 0), xytext=(-2.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 3.0), xytext=(0, -0.5),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (2.3, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.3, 2.8), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$-1$', (-1, 0), dx=0, dy=-15, fs=9)
    f.lab('$1$', (1, 0), dx=0, dy=-15, fs=9)
    f.lab('$2$', (-2.3, 2), dx=-5, dy=0, fs=9, ha='right')
    f.lab('$1$', (0, 1), dx=-12, dy=0, fs=9)
    f.lab('$y=f(x)$', (1.4, 2.1), fs=9.5, ha='left')
    f.save()


def q17():
    scale = 0.42

    def S(p):
        return (p[0] * scale, p[1] * scale)

    f = Fig('ch26m2_q17', 20000, (-1.2, 7.8), (-1.2, 6.8))
    t = 4.6
    r = 2 * t - 2
    M = (r, t)
    f.circle(S(M), r * scale, lw=1.1)
    w = math.sqrt(max(r ** 2 - t ** 2, 0.01))
    A = (r - w, 0)
    B = (r + w, 0)
    for p in (A, B):
        f.dot(S(p))
    P = (0, t)
    f.dot(S(P))
    ux, uy = 2 / math.sqrt(5), 1 / math.sqrt(5)
    Q = (M[0] + r * ux, M[1] + r * uy)
    f.dot(S(Q))
    f.seg(S(M), S(Q), lw=0.9)
    xs = np.linspace(-0.5, 16.5, 2)
    ys = 0.5 * xs + 1
    f.ax.plot(xs * scale, ys * scale, color='k', lw=1.0, zorder=2)
    f.seg(S((0, 0)), S(A), lw=0.9)
    f.seg(S((0, 0)), S(B), lw=0.9)
    f.seg(S((0, 0)), S(Q), lw=0.9)
    f.seg(S(P), S(Q), lw=0.9)
    f.seg(S(A), S(Q), lw=0.9)
    f.seg(S(B), S(Q), lw=0.9)
    f.ax.annotate('', xy=(7.6, 0), xytext=(-1.0, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.6), xytext=(0, -1.0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$y$', (0.3, 6.3), fs=10, italic=True)
    f.lab('$x$', (7.6, 0), dx=0, dy=-14, fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-12, dy=-12, fs=10)
    f.lab('$P$', S(P), dx=-14, dy=0, fs=10)
    f.lab('$A$', S(A), dx=-4, dy=-15, fs=10)
    f.lab('$B$', S(B), dx=6, dy=-15, fs=10)
    f.lab('$Q$', S(Q), dx=10, dy=8, fs=10)
    f.lab(r'$y=\frac{1}{2}x+1$', S((12.3, 0.5 * 12.3 + 1)), dx=10, dy=-12, fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    q04()
    q17()
    print('done')
