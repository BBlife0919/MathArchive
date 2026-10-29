# -*- coding: utf-8 -*-
"""충현고(공통수학2) ch26m2_2 Q12, Q15 본문 그림.
실행: python3 ch26m2_2_figs.py"""
import numpy as np
from figlib import Fig


def q12():
    f = Fig('ch26m2_2_q12', 20000, (-15.5, 13.5), (-4.5, 8.8))
    A = (9, 3)
    B = (-12, 6)
    C = (4, -2)
    O = (0, 0)
    xs1 = np.linspace(-14, 13.5, 10)
    f.ax.plot(xs1, xs1 / 3, color='k', lw=0.9, zorder=2)
    xs2 = np.linspace(-14.3, 9, 10)
    f.ax.plot(xs2, -xs2 / 2, color='k', lw=0.9, zorder=2)
    f.seg(A, B, lw=1.1)
    f.seg(A, C, lw=1.1)
    f.seg(B, C, lw=1.1)
    f.seg(A, O, lw=0.9)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(O)
    f.hytext('A', A, dx=8, dy=8, fs=10)
    f.hytext('B', B, dx=-14, dy=6, fs=10)
    f.hytext('C', C, dx=6, dy=-14, fs=10)
    f.hytext('O', O, dx=-13, dy=-13, fs=10)
    f.hytext('x', (13.3, 0), dx=8, dy=-10, fs=10, italic=True)
    f.hytext('y', (0, 7.6), dx=8, dy=0, fs=10, italic=True)
    f.lab(r'$y=\frac{1}{3}x$', (6, 2), dx=-4, dy=20, fs=9)
    f.lab(r'$y=-\frac{1}{2}x$', (-12, 6), dx=-20, dy=14, fs=9)
    f.ax.annotate('', xy=(13.3, 0), xytext=(-15.3, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.ax.annotate('', xy=(0, 8.6), xytext=(0, -4.3),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.save()


def q15():
    f = Fig('ch26m2_2_q15', 20000, (-1.5, 6.3), (-1.0, 7.0))
    P1 = (3, 0)
    P2 = (0, 4)
    k_start = (0, 7 if False else (4 * 0 - 12) / 3)
    k_pts = (6.5, (4 * 6.5 - 12) / 3)
    k_top = ((6.5 * 3 + 12) / 4, 6.5)
    f.seg(k_top, P1, lw=1.1)
    f.seg(P1, P2, lw=1.1)
    m_pts = (3.2, 4.0 / 3 * 3.2 + 4)
    f.seg(P2, m_pts, lw=1.1)
    n_end = (117 / 25, 56 / 25)
    f.seg(P2, n_end, lw=1.1)
    f.ax.annotate('', xy=(6.3, 0), xytext=(-1.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.ax.annotate('', xy=(0, 6.8), xytext=(0, -0.8),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.dot(P1)
    f.dot(P2)
    f.dot(n_end)
    f.hytext('O', (0, 0), dx=-11, dy=-13, fs=9)
    f.hytext('k', (4.8, (4 * 4.8 - 12) / 3), dx=10, dy=6, fs=10, italic=True)
    f.hytext('l', (1.5, 2.0), dx=6, dy=4, fs=10, italic=True)
    f.hytext('m', (1.0, 4.0 / 3 * 1.0 + 4), dx=-14, dy=0, fs=10, italic=True)
    f.hytext('n', n_end, dx=10, dy=-10, fs=10, italic=True)
    f.save()


if __name__ == '__main__':
    q12()
    q15()
    print('done')
