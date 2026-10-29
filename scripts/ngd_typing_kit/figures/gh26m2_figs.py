# -*- coding: utf-8 -*-
"""광휘고 gh26m2 Q05 해설용(본문) 그림: 조각함수 그래프(3군데 특이점).
line (x<0, slope~3.5) -> (0,3) filled; open(0,1)-filled line to open(1,2);
filled(1,1) start increasing curve. 실행: python3 gh26m2_figs.py"""
import numpy as np
from figlib import Fig


def q05():
    f = Fig('gh26m2_q05', 20000, (-2.0, 2.3), (-2.8, 3.6))
    xs1 = np.linspace(-1.75, 0, 60)
    f.ax.plot(xs1, 3 + 3.5 * xs1, color='k', lw=1.2, zorder=3)
    f.dot((0, 3))
    f.circle((0, 1), 0.06, fill='white', z=4)
    xs2 = np.linspace(0, 1, 60)
    f.ax.plot(xs2, 1 + xs2, color='k', lw=1.2, zorder=3)
    f.circle((1, 2), 0.06, fill='white', z=4)
    f.dot((1, 1))
    xs3 = np.linspace(1, 2.1, 60)
    f.ax.plot(xs3, 1 + 0.9 * (xs3 - 1) ** 2, color='k', lw=1.2, zorder=3)
    f.dashed((-1.9, 1), (0, 1), lw=0.6)
    f.dashed((0, 1), (0, 1), lw=0.6)
    f.dashed((0, 2), (1, 2), lw=0.6)
    f.dashed((1, 0), (1, 2), lw=0.6)
    f.dashed((1, 0), (1, 1), lw=0.6)
    f.ax.annotate('', xy=(2.2, 0), xytext=(-2.0, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 3.4), xytext=(0, -2.6),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (2.2, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.3, 3.1), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$-1$', (-1, 0), dx=-4, dy=-15, fs=9)
    f.lab('$1$', (1, 0), dx=0, dy=-15, fs=9)
    f.lab('$3$', (0, 3), dx=-13, dy=0, fs=9)
    f.lab('$2$', (0, 2), dx=-13, dy=0, fs=9)
    f.lab('$1$', (0, 1), dx=-13, dy=0, fs=9)
    f.save()


if __name__ == '__main__':
    q05()
    print('done')
