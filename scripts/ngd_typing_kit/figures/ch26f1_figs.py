# -*- coding: utf-8 -*-
"""충현고 ch26f1(1학년 공통수학1) Q12, Q19 본문 그림.
실행: python3 ch26f1_figs.py"""
import numpy as np
from figlib import Fig


def q12():
    f = Fig('ch26f1_q12', 16000, (-7.0, 5.5), (-1.9, 1.6))
    f.ax.annotate('', xy=(5.0, 0), xytext=(-6.8, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=1)
    f.ax.plot([-6.8, -4], [0.55, 0.55], color='k', lw=3.0, solid_capstyle='butt', zorder=2)
    f.ax.plot([-4, -4], [0, 0.55], color='k', lw=0.8, zorder=2)
    f.ax.plot([-4, 2], [0, 0], color='k', lw=3.0, solid_capstyle='butt', zorder=2)
    f.ax.plot([2, 2], [0, 0.55], color='k', lw=0.8, zorder=2)
    f.ax.plot(-4, 0, 'o', mfc='white', mec='k', ms=6, zorder=3)
    f.ax.plot(2, 0, 'o', mfc='k', mec='k', ms=6, zorder=3)
    f.lab('-4', (-4, 0), dx=0, dy=-16, fs=9)
    f.lab('3', (2, 0), dx=0, dy=-16, fs=9)
    f.hytext('x', (5.0, 0), dx=12, dy=-6, fs=10, italic=True)
    f.save()


def q19():
    f = Fig('ch26f1_q19', 15000, (-1.4, 11.4), (-2.1, 6.8))
    A = (0.0, 0.0)
    B = (10.0, 0.0)
    r = 5.0
    th_P = 130.0
    P = (5 + r * np.cos(np.radians(th_P)), r * np.sin(np.radians(th_P)))
    th = np.linspace(0, 180, 200)
    f.ax.plot(5 + r * np.cos(np.radians(th)), r * np.sin(np.radians(th)), color='k', lw=1.1, zorder=2)
    f.seg(A, B, lw=1.0)
    f.seg(A, P, lw=1.0)
    f.seg(P, B, lw=1.0)
    f.dashed(A, (5, 0))
    f.dashed((5, 0), P)
    f.dashed(B, P)
    f.dot(A)
    f.dot(B)
    f.dot(P)
    f.dot((5, 0))
    f.hytext('A', A, dx=-12, dy=-4, fs=10)
    f.hytext('B', B, dx=12, dy=-4, fs=10)
    f.hytext('P', P, dx=-8, dy=14, fs=10)
    f.lab(r'$4\sqrt{5}$', (5, 0), dx=0, dy=-18, fs=9)
    f.lab('x', ((A[0] + (5, 0)[0]) / 2, (A[1] + (5, 0)[1]) / 2), dx=0, dy=16, fs=9, italic=True)
    f.lab('y', (((5, 0)[0] + P[0]) / 2, ((5, 0)[1] + P[1]) / 2), dx=12, dy=4, fs=9, italic=True)
    f.save()


if __name__ == '__main__':
    q12()
    q19()
    print('done')
