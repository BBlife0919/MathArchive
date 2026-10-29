# -*- coding: utf-8 -*-
"""jsg24m2 Q19 해설용 그림: f(x)=3x+6+|x-2| 꺾인 그래프 (x<2: 2x+8, x>=2: 4x+4), 꺾이는 점(2,12).
실행: python3 jsg24m2_q19_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('jsg24m2_q19_sol', 20000, (-3.4, 4.6), (-1.5, 9.2))
    xs1 = np.linspace(-3.0, 2, 80)
    ys1 = xs1 + 5
    xs2 = np.linspace(2, 4.2, 80)
    ys2 = 2 * xs2 + 3
    f.ax.plot(xs1, ys1, color='k', lw=1.3, zorder=3)
    f.ax.plot(xs2, ys2, color='k', lw=1.3, zorder=3)
    f.dot((2, 7))
    f.dashed((-3.2, 7), (2, 7), lw=0.6)
    f.dashed((2, -1.3), (2, 7), lw=0.6)
    f.ax.annotate('', xy=(4.5, 0), xytext=(-3.3, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 8.9), xytext=(0, -1.3),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (4.5, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.35, 8.6), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$2$', (2, 0), dx=10, dy=-13, fs=9)
    f.lab('$12$', (0, 7), dx=-17, dy=0, fs=9)
    f.lab('$y=f(x)$', (-3.0, 1.8), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
