# -*- coding: utf-8 -*-
"""진성고 jsg26f Q5, Q7, Q8 본문 그림.
실행: python3 jsg26f_figs.py"""
import numpy as np
from figlib import Fig


def q05():
    f = Fig('jsg26f_q05', 15000, (-1.5, 1.5), (-1.6, 1.4))
    th_D, th_C, th_A, th_B = 150, 70, -140, -30
    D = (np.cos(np.radians(th_D)), np.sin(np.radians(th_D)))
    C = (np.cos(np.radians(th_C)), np.sin(np.radians(th_C)))
    A = (np.cos(np.radians(th_A)), np.sin(np.radians(th_A)))
    B = (np.cos(np.radians(th_B)), np.sin(np.radians(th_B)))
    f.circle((0, 0), 1.0, lw=1.0)
    f.seg(A, B, lw=0.9)
    f.seg(B, C, lw=0.9)
    f.seg(A, C, lw=0.9)
    f.seg(A, D, lw=0.9)
    f.seg(D, C, lw=0.8, ls=(0, (2.5, 2.2)))
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(D)
    f.hytext('A', A, dx=-12, dy=-6, fs=10)
    f.hytext('B', B, dx=12, dy=-8, fs=10)
    f.hytext('C', C, dx=12, dy=8, fs=10)
    f.hytext('D', D, dx=-14, dy=4, fs=10)
    f.lab('3', ((A[0] + D[0]) / 2, (A[1] + D[1]) / 2), dx=-10, dy=2, fs=8.5, italic=True)
    f.lab('6', ((D[0] + C[0]) / 2, (D[1] + C[1]) / 2), dx=0, dy=12, fs=8.5, italic=True)
    f.save()


def q07():
    f = Fig('jsg26f_q07', 15000, (-2.8, 2.8), (-1.0, 5.8))
    cy = 0.0
    rx, ry = 2.0, 0.55
    h = 5.2
    O = (0, h)
    A = (-rx, cy)
    B = (rx, cy)
    Ap = (O[0] + 0.5 * (A[0] - O[0]), O[1] + 0.5 * (A[1] - O[1]))
    th_back = np.linspace(0, 180, 100)
    th_front = np.linspace(180, 360, 100)
    f.ax.plot(rx * np.cos(np.radians(th_back)), cy + ry * np.sin(np.radians(th_back)),
              color='k', lw=0.8, ls=(0, (2.5, 2.2)), zorder=2)
    f.ax.plot(rx * np.cos(np.radians(th_front)), cy + ry * np.sin(np.radians(th_front)),
              color='k', lw=0.9, zorder=2)
    f.seg(O, A, lw=0.9, ls=(0, (2.5, 2.2)))
    f.seg(O, B, lw=1.0)
    f.dot(O)
    f.dot(A)
    f.dot(B)
    f.dot(Ap)
    f.hytext('O', O, dx=0, dy=14, fs=10)
    f.hytext('A', A, dx=-12, dy=-8, fs=10)
    f.hytext('B', B, dx=12, dy=-8, fs=10)
    f.hytext("A'", Ap, dx=-22, dy=-4, fs=9)
    f.lab('6', ((O[0] + A[0]) / 2, (O[1] + A[1]) / 2), dx=18, dy=6, fs=9, italic=True)
    f.lab('2', (-rx / 2, cy), dx=0, dy=-14, fs=8.5, italic=True)
    f.save()


def q08():
    f = Fig('jsg26f_q08', 17000, (-1.2, 7.6), (-1.2, 3.4))
    B = (0, 0)
    A = (1.3077, 2.2822)
    C = (6.0, 0)
    P = (2.2222, 0.6565)
    Q = (1.3333 / 2 * 1.0, 0)
    Qpt = (20 / 9 * (1.3077) / 3, 20 / 9 * (2.2822) / 3)
    f.seg(B, C, lw=1.0)
    f.seg(B, A, lw=1.0)
    f.seg(A, C, lw=1.0)
    f.seg(B, P, lw=0.8)
    r1c = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    r1 = ((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2) ** 0.5 / 2
    r2c = ((P[0] + B[0]) / 2, (P[1] + B[1]) / 2)
    r2 = ((P[0] - B[0]) ** 2 + (P[1] - B[1]) ** 2) ** 0.5 / 2
    f.circle(r1c, r1, lw=0.8)
    f.circle(r2c, r2, lw=0.8)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.dot(P)
    f.dot(Qpt)
    f.hytext('A', A, dx=-4, dy=14, fs=10)
    f.hytext('B', B, dx=-4, dy=-14, fs=10)
    f.hytext('C', C, dx=14, dy=-10, fs=10)
    f.hytext('P', P, dx=14, dy=8, fs=10)
    f.hytext('Q', Qpt, dx=-14, dy=8, fs=10)
    f.save()


if __name__ == '__main__':
    q05()
    q07()
    q08()
    print('done')
