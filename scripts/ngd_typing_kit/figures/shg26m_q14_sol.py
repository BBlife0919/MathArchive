# -*- coding: utf-8 -*-
"""소하고 shg26m Q14 해설용 그림: y=5cos(pi x/4) 그래프 일부. 실행: python3 shg26m_q14_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('shg26m_q14_sol', 22000, (-1.7, 17.6), (-6.6, 7.0))
    PI = np.pi
    xs = np.linspace(0, 16, 300)
    ys = 5 * np.cos(PI * xs / 4)
    f.ax.plot(xs, ys, color='k', lw=1.2, zorder=3)
    f.dashed((-0.8, 5), (16.3, 5), lw=0.7)
    f.ax.annotate('', xy=(17.2, 0), xytext=(-1.0, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.8), xytext=(0, -6.4),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (17.2, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.85, 6.5), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$5$', (0, 5), dx=-13, dy=0, fs=9)
    for z in [2, 6, 10, 14]:
        f.dot((z, 0))
    for p in [0, 8, 16]:
        f.dot((p, 5))
    f.lab('$2$', (2, 0), dx=0, dy=-14, fs=9)
    f.lab('$6$', (6, 0), dx=0, dy=-14, fs=9)
    f.lab('$8$', (8, 0), dx=-4, dy=14, fs=9)
    f.lab('$y=5\\cos\\left(\\frac{\\pi}{4}x\\right)$', (9.5, 1.9), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
