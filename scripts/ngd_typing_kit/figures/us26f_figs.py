# -*- coding: utf-8 -*-
"""운산고 us26f Q2, Q10, Q13, Q18, Q19 본문 그림.
실행: python3 us26f_figs.py"""
import numpy as np
from figlib import Fig


def q02():
    f = Fig('us26f_q02', 15000, (-1.3, 10.0), (-1.9, 5.9))
    B = (0.0, 0.0)
    C = (8.8, 0.0)
    D = (2.3, 0.0)
    A = (2.0, 4.6)
    f.seg(B, C, lw=1.1)
    f.seg(A, B, lw=1.0, ls=(0, (3.2, 2.6)))
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
    f.lab('6', ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), dx=-14, dy=0, fs=9, italic=True)
    f.lab('4', ((A[0] + D[0]) / 2, (A[1] + D[1]) / 2), dx=12, dy=0, fs=9, italic=True)
    f.save()


def q10():
    f = Fig('us26f_q10', 15000, (-1.3, 10.6), (-1.5, 6.6))
    B = (0.0, 0.0)
    C = (9.2, 0.0)
    A = (3.0, 5.2)
    f.seg(B, C, lw=1.1)
    f.seg(A, B, lw=1.0, ls=(0, (3.2, 2.6)))
    f.seg(A, C, lw=1.0)
    f.dot(A)
    f.dot(B)
    f.dot(C)
    f.hytext('A', A, dx=0, dy=14, fs=10)
    f.hytext('B', B, dx=-11, dy=-6, fs=10)
    f.hytext('C', C, dx=11, dy=-6, fs=10)
    f.lab(r'$8\sqrt{2}$', ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2), dx=-20, dy=0, fs=9)
    f.lab('60°', B, dx=20, dy=12, fs=8.5)
    f.lab('45°', C, dx=-22, dy=12, fs=8.5)
    f.save()


def q13():
    xlim = (-6.5, 31.0)
    ylim = (-200, 820)
    f = Fig('us26f_q13', 22000, xlim, ylim)
    f.ax.set_aspect('auto')
    f.h_in = f.w_in * 0.55
    f.h_hwp = round(f.h_in * 7200)
    f.fig.set_size_inches(f.w_in, f.h_in)
    t = np.linspace(0, 24, 400)
    y = 240 * np.sin(np.pi / 6 * (t - 6)) + 360
    f.ax.plot(t, y, color='k', lw=1.0, zorder=3)
    f.ax.annotate('', xy=(0, 750), xytext=(0, -150),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(30.5, 0), xytext=(-4.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.text(1.0, 760, 'y (cm)', fontsize=9, ha='left', va='center')
    f.ax.text(30.5, -60, 't', fontsize=9, ha='right', va='center', style='italic')
    f.ax.text(-1.2, -70, 'O', fontsize=9, ha='center', va='center')
    for tx in (3, 9, 15, 21, 24):
        f.ax.text(tx, -70, str(tx), fontsize=8.5, ha='center', va='center')
    f.dashed((-4.5, 600), (9, 600), lw=0.5)
    f.dashed((9, 0), (9, 600), lw=0.5)
    f.dashed((-4.5, 120), (3, 120), lw=0.5)
    f.dashed((3, 0), (3, 120), lw=0.5)
    f.ax.text(-4.8, 600, '600', fontsize=8.5, ha='right', va='center')
    f.ax.text(-4.8, 120, '120', fontsize=8.5, ha='right', va='center')
    f.save()


def q18():
    f = Fig('us26f_q18', 20000, (-1.0, 5.0), (-2.3, 2.3))
    a, b = np.sqrt(3), 4 / 9
    xs = np.linspace(0, 2 / b, 400)
    ys = a * np.cos(b * np.pi * xs)
    f.ax.plot(xs, ys, color='k', lw=1.0, zorder=3)
    f.ax.annotate('', xy=(0, 2.15), xytext=(0, -2.15),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(4.9, 0), xytext=(-0.3, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 2.15), dx=10, dy=0, fs=9, italic=True)
    f.hytext('x', (4.9, 0), dx=10, dy=-8, fs=9, italic=True)
    xB, xC = 1 / (3 * b), 5 / (3 * b)
    xA = 1 / b
    f.dashed((-0.3, np.sqrt(3) / 2), (xC, np.sqrt(3) / 2), lw=0.6)
    f.dashed((-0.3, -np.sqrt(3)), (xA, -np.sqrt(3)), lw=0.6)
    f.lab(r'$\frac{\sqrt{3}}{2}$', (0, np.sqrt(3) / 2), dx=-16, dy=0, fs=9)
    f.lab(r'$-\sqrt{3}$', (0, -np.sqrt(3)), dx=-18, dy=0, fs=9)
    f.dot((xB, np.sqrt(3) / 2))
    f.dot((xC, np.sqrt(3) / 2))
    f.dot((xA, -np.sqrt(3)))
    f.hytext('B', (xB, np.sqrt(3) / 2), dx=-10, dy=10, fs=9)
    f.hytext('C', (xC, np.sqrt(3) / 2), dx=10, dy=10, fs=9)
    f.hytext('A', (xA, -np.sqrt(3)), dx=0, dy=-14, fs=9)
    f.lab('$y=f(x)$', (xC - 0.4, 1.7), dx=0, dy=0, fs=8.5)
    f.save()


def q19():
    f = Fig('us26f_q19', 18000, (-1.3, 1.3), (-1.5, 1.3))
    th = np.linspace(0, 2 * np.pi, 200)
    f.ax.plot(np.cos(th), np.sin(th), color='k', lw=1.0, zorder=3)
    A = (-0.97, 0.26)
    C = (-0.1, 1.0)
    Bp = (0.97, 0.26)
    D = (-0.1, -1.0)
    O = (0, 0)
    f.seg(A, C, lw=0.8)
    f.seg(C, Bp, lw=0.8)
    f.seg(A, Bp, lw=0.8)
    f.seg(A, D, lw=0.8)
    f.seg(Bp, D, lw=0.8)
    f.seg(Bp, O, lw=0.6)
    f.seg(O, D, lw=0.6)
    for p in (A, C, Bp, D, O):
        f.dot(p)
    f.hytext('A', A, dx=-10, dy=4, fs=10)
    f.hytext('C', C, dx=0, dy=10, fs=10)
    f.hytext('B', Bp, dx=10, dy=4, fs=10)
    f.hytext('D', D, dx=0, dy=-14, fs=10)
    f.save()


if __name__ == '__main__':
    q02()
    q10()
    q13()
    q18()
    q19()
    print('done')
