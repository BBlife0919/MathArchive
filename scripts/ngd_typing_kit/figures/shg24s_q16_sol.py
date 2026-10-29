# -*- coding: utf-8 -*-
"""소하고 shg24s Q16 해설용 그림: 두 로그곡선 y=log_a x, y=log_3a x 와 y=±1 교점 A,B,C,D.
a=1/sqrt(3) 예시(ㄷ 조건 성립 케이스)로 직사각형 모양을 보여줌. 실행: python3 shg24s_q16_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('shg24s_q16_sol', 20000, (-1.0, 3.2), (-2.6, 2.6))
    a = 1 / np.sqrt(3)
    xs = np.linspace(0.15, 3.0, 200)
    ys1 = np.log(xs) / np.log(a)
    ys2 = np.log(xs) / np.log(3 * a)
    f.ax.plot(xs, ys1, color='k', lw=1.2, zorder=3)
    f.ax.plot(xs, ys2, color='k', lw=1.2, zorder=3)
    f.dashed((-0.8, 1), (3.0, 1), lw=0.6)
    f.dashed((-0.8, -1), (3.0, -1), lw=0.6)
    A = (a, 1); B = (3 * a, 1); C = (1 / a, -1); D = (1 / (3 * a), -1)
    for p in (A, B, C, D):
        f.dot(p)
    f.seg(A, D, lw=0.8)
    f.seg(B, C, lw=0.8)
    f.ax.annotate('', xy=(3.1, 0), xytext=(-0.9, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 2.0), xytext=(0, -2.0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (3.1, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.17, 1.95), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$1$', (0, 1), dx=-12, dy=0, fs=9)
    f.lab('$-1$', (0, -1), dx=-17, dy=0, fs=9)
    f.lab('$A$', A, dx=-12, dy=10, fs=10)
    f.lab('$B$', B, dx=14, dy=-10, fs=10)
    f.lab('$C$', C, dx=10, dy=-13, fs=10)
    f.lab('$D$', D, dx=-14, dy=-13, fs=10)
    f.lab('$y=\\log_a x$', (2.0, 0.55), fs=9.5, ha='left')
    f.lab('$y=\\log_{3a} x$', (2.0, 1.55), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
