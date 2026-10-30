# -*- coding: utf-8 -*-
"""광휘고 gh26f Q14, Q18 본문 그림.
실행: python3 gh26f_figs.py"""
import numpy as np
from figlib import Fig


def q14():
    f = Fig('gh26f_q14', 16000, (-1.0, 9.6), (-1.3, 5.4))
    B = (0.0, 0.0)
    C = (8.3, 0.0)
    D = (3.1, 0.0)
    A = (3.1, 4.3)
    f.seg(B, C, lw=1.1)
    f.seg(A, B, lw=1.0)
    f.seg(A, D, lw=0.9)
    f.seg(A, C, lw=1.0)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(D)
    f.hytext('A', A, dx=0, dy=14, fs=10)
    f.hytext('B', B, dx=-11, dy=-6, fs=10)
    f.hytext('C', C, dx=11, dy=-6, fs=10)
    f.hytext('D', D, dx=0, dy=-14, fs=10)
    f.save()


def q18():
    f = Fig('gh26f_q18', 18000, (-1.3, 1.3), (-0.3, 1.5))
    th = np.linspace(0, np.pi, 200)
    f.ax.plot(np.cos(th), np.sin(th), color='k', lw=1.0, zorder=3)
    f.seg((-1, 0), (1, 0), lw=1.0)
    A = (-1, 0)
    B = (1, 0)
    C = (0, 0)
    thD = np.radians(141)
    thE = np.radians(58)
    D = (np.cos(thD), np.sin(thD))
    E = (np.cos(thE), np.sin(thE))
    f.seg(A, D, lw=0.8)
    f.seg(A, E, lw=0.8)
    f.seg(D, B, lw=0.8)
    f.seg(E, B, lw=0.8)
    f.seg(C, D, lw=0.7)
    f.seg(C, E, lw=0.7)
    f.seg(D, E, lw=0.8)
    for p in (A, B, C, D, E):
        f.dot(p)
    f.hytext('A', A, dx=-10, dy=-8, fs=10)
    f.hytext('B', B, dx=10, dy=-8, fs=10)
    f.hytext('C', C, dx=0, dy=-14, fs=10)
    f.hytext('D', D, dx=-10, dy=8, fs=10)
    f.hytext('E', E, dx=10, dy=8, fs=10)
    f.save()


if __name__ == '__main__':
    q14()
    q18()
    print('done')
