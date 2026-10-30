# -*- coding: utf-8 -*-
"""충현고 ch26f Q15, Q16 본문 그림.
실행: python3 ch26f_figs.py"""
import numpy as np
from figlib import Fig


def q15():
    f = Fig('ch26f_q15', 18000, (-1.9, 10.9), (-1.7, 7.6))
    n2, n2b = 4.0, 8.0
    n, n2v = 2.0, 4.0
    f.ax.annotate('', xy=(0, 7.0), xytext=(0, -1.0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(9.8, 0), xytext=(-0.9, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 7.0), dx=12, dy=4, fs=10, italic=True)
    f.hytext('x', (9.8, 0), dx=12, dy=-10, fs=10, italic=True)
    xs = np.linspace(0, 7.0, 200)
    slope = n2v / n2
    f.ax.plot(xs, slope * xs, color='k', lw=1.0, zorder=3)
    f.lab(r'$y=\frac{1}{m}x$', (6.2, slope * 6.2), dx=12, dy=16, fs=9)
    f.seg((n2, n), (n2b, n), lw=1.1)
    f.seg((n2b, n), (n2b, n2v), lw=1.1)
    f.seg((n2b, n2v), (n2, n2v), lw=1.1)
    f.seg((n2, n2v), (n2, n), lw=1.1)
    f.dashed((-0.8, n), (n2, n))
    f.dashed((-0.8, n2v), (n2b, n2v))
    f.dashed((n2, -1.0), (n2, n2v))
    f.dashed((n2b, -1.0), (n2b, n2v))
    f.lab('n', (-0.9, n), dx=0, dy=0, fs=9, italic=True)
    f.lab('2n', (-0.9, n2v), dx=0, dy=0, fs=9, italic=True)
    f.lab('$n^{2}$', (n2, -0.2), dx=0, dy=-16, fs=9)
    f.lab('$2n^{2}$', (n2b, -0.2), dx=0, dy=-16, fs=9)
    f.dot((n2, n))
    f.dot((n2b, n2v))
    f.save()


def q16():
    f = Fig('ch26f_q16', 15000, (-1.5, 1.5), (-1.6, 1.4))
    th_A, th_B, th_C, th_D = -115, 165, 100, 30
    A = (np.cos(np.radians(th_A)), np.sin(np.radians(th_A)))
    B = (np.cos(np.radians(th_B)), np.sin(np.radians(th_B)))
    C = (np.cos(np.radians(th_C)), np.sin(np.radians(th_C)))
    D = (np.cos(np.radians(th_D)), np.sin(np.radians(th_D)))
    f.circle((0, 0), 1.0, lw=1.0)
    f.seg(A, B, lw=0.9)
    f.seg(B, C, lw=0.9)
    f.seg(C, D, lw=0.9)
    f.seg(D, A, lw=0.9)
    f.seg(A, C, lw=0.9)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(D)
    f.hytext('A', A, dx=-6, dy=-14, fs=10)
    f.hytext('B', B, dx=-14, dy=2, fs=10)
    f.hytext('C', C, dx=-4, dy=14, fs=10)
    f.hytext('D', D, dx=14, dy=6, fs=10)
    f.save()


if __name__ == '__main__':
    q15()
    q16()
    print('done')
