# -*- coding: utf-8 -*-
"""광문고 2학년 2026 1학기중간 대수 그림 2종 (Q12 지수함수 그래프+삼각형, 서술형3 평행사변형).
실행: python3 gmun26m1_figs.py"""
import numpy as np
from figlib import Fig


def q12():
    f = Fig('gmun26m1_q12', 17000, (-4.0, 1.2), (-0.6, 8.6))
    f.ax.annotate('', xy=(1.1, 0), xytext=(-3.9, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 8.4), xytext=(0, -0.4),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.hytext('O', (0, 0), dx=-6, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (1.1, 0), dx=7, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 8.4), dx=0, dy=5, italic=True, fs=8.5, va='bottom')

    xs = np.linspace(-3.9, 1.1, 300)
    ys1 = (0.5) ** xs
    f.ax.plot(xs[ys1 <= 8.2], ys1[ys1 <= 8.2], color='k', lw=1.1, zorder=3)
    ys2 = (0.25) ** xs
    f.ax.plot(xs[ys2 <= 8.2], ys2[ys2 <= 8.2], color='k', lw=1.1, zorder=3)
    f.lab('$y=(1/2)^{x}$', (-1.1, 0.5 ** (-1.1)), dx=-4, dy=6, fs=7, ha='right')
    f.lab('$y=(1/4)^{x}$', (-0.55, 0.25 ** (-0.55)), dx=6, dy=-2, fs=7, ha='left')

    f.dashed((-3.9, 8), (0, 8))
    f.hytext('y=8', (-2.4, 8), dx=0, dy=4, fs=7.5, ha='center', va='bottom')

    A = (-3.0, 8.0)
    B = (-1.5, 8.0)
    O = (0.0, 0.0)
    for p in (A, B, O):
        f.dot(p)
    f.seg(O, A, lw=0.9)
    f.seg(O, B, lw=0.9)
    f.lab('A', A, dx=-9, dy=6, fs=8.5)
    f.lab('B', B, dx=9, dy=6, fs=8.5)
    f.save()


def q20():
    f = Fig('gmun26m1_q20', 20000, (-0.8, 7.3), (-0.9, 9.8))
    x = 6.0
    A = (2.0, 2.0)
    B = (4.0, 6.0)
    P = (x, 0.0)
    Q = (6.0 - x, 8.0)
    O = (0.0, 0.0)

    f.ax.annotate('', xy=(7.1, 0), xytext=(-0.6, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 9.6), xytext=(0, -0.7),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.hytext('O', O, dx=-6, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (7.1, 0), dx=7, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 9.6), dx=0, dy=5, italic=True, fs=8.5, va='bottom')

    f.poly([A, P, B, Q], lw=1.1, close=True)
    f.seg(A, B, lw=0.7, ls='--')
    f.seg(P, Q, lw=0.7, ls='--')

    for p in (A, B, P, Q):
        f.dot(p)
    f.lab('A(2, 2)', A, dx=-10, dy=-10, fs=8, ha='right')
    f.lab('B(4, 6)', B, dx=10, dy=6, fs=8, ha='left')
    f.lab('P(x, 0)', P, dx=0, dy=-12, fs=8, va='top')
    f.lab('Q', Q, dx=0, dy=10, fs=8.5, va='bottom')
    f.save()


if __name__ == '__main__':
    q12()
    q20()
    print('done')
