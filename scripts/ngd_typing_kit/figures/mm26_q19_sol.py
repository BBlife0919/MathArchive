# -*- coding: utf-8 -*-
"""mm26 Q19 해설용 그림: h(x)=|x^2-4x|-2x 그래프. 실행: python3 mm26_q19_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('mm26_q19_sol', 22000, (-2.8, 7.2), (-9.3, 6.2))

    def h(x):
        return np.where((x <= 0) | (x >= 4), x ** 2 - 6 * x, -x ** 2 + 2 * x)

    xs1 = np.linspace(-0.75, 0, 60)
    xs2 = np.linspace(0, 4, 60)
    xs3 = np.linspace(4, 4.75, 60)
    for xs in (xs1, xs2, xs3):
        f.ax.plot(xs, h(xs), color='k', lw=1.3, zorder=3)

    for p in [(0, 0), (1, 1), (4, -8)]:
        f.dot(p)

    f.ax.annotate('', xy=(7.0, 0), xytext=(-2.6, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.0), xytext=(0, -9.0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (6.6, -1.1), fs=10, italic=True)
    f.lab('$y$', (0.8, 5.5), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$1$', (1, 0), dx=0, dy=-14, fs=9)
    f.lab('$4$', (4, 0), dx=0, dy=-14, fs=9)
    f.lab(r'$(1,\,1)$', (1, 1), dx=10, dy=10, fs=9)
    f.lab(r'$(4,\,-8)$', (4, -8), dx=14, dy=0, fs=9, ha='left')
    f.lab('$y=h(x)$', (-0.75, -0.3), dx=-10, dy=10, fs=9.5, ha='right')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
