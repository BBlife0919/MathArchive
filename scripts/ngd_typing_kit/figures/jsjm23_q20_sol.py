# -*- coding: utf-8 -*-
"""jsjm23 Q20 해설용 그림: f(x)=|x^2/2-2| 모양(바깥 포물선+안쪽 봉우리), 꺾이는 점 x=-2,2.
실행: python3 jsjm23_q20_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('jsjm23_q20_sol', 20000, (-4.6, 4.6), (-1.0, 6.4))
    xs_out_l = np.linspace(-4.3, -2, 100)
    xs_in = np.linspace(-2, 2, 100)
    xs_out_r = np.linspace(2, 4.3, 100)

    def fout(x):
        return x ** 2 / 2 - 2

    def fin(x):
        return 2 - x ** 2 / 2

    f.ax.plot(xs_out_l, fout(xs_out_l), color='k', lw=1.2, zorder=3)
    f.ax.plot(xs_in, fin(xs_in), color='k', lw=1.2, zorder=3)
    f.ax.plot(xs_out_r, fout(xs_out_r), color='k', lw=1.2, zorder=3)
    f.dot((-2, 0)); f.dot((2, 0)); f.dot((0, 2))
    f.ax.annotate('', xy=(4.5, 0), xytext=(-4.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.1), xytext=(0, -0.9),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (4.5, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.35, 5.8), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$-2$', (-2, 0), dx=-6, dy=-15, fs=9)
    f.lab('$2$', (2, 0), dx=6, dy=-15, fs=9)
    f.lab('$2$', (0, 2), dx=-13, dy=0, fs=9)
    f.lab('$y=f(x)$', (2.9, 4.2), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
