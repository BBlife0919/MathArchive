# -*- coding: utf-8 -*-
"""광휘고 gh26m1 Q07 본문 그림: y=a*cos(bx-c), 진폭7, 주기8pi, 최댓값 x=2pi,10pi.
실행: python3 gh26m1_figs.py"""
import numpy as np
from figlib import Fig


def q07():
    xmin, xmax = -2 * np.pi - 3.0, 10 * np.pi + 6.0
    f = Fig('gh26m1_q07', 20000, (xmin, xmax), (-9.5, 9.5))
    xs = np.linspace(xmin + 0.3, xmax - 0.3, 400)
    ys = 7 * np.cos((1 / 4) * xs - np.pi / 2)
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)
    f.ax.annotate('', xy=(xmax - 0.5, 0), xytext=(xmin + 0.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.ax.annotate('', xy=(0, 9.2), xytext=(0, -9.2),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=1)
    f.dashed((-2 * np.pi, 0), (-2 * np.pi, 7), lw=0.6)
    f.dashed((-2 * np.pi, 7), (2 * np.pi, 7), lw=0.6)
    f.dashed((2 * np.pi, 0), (2 * np.pi, 7), lw=0.6)
    f.dashed((6 * np.pi, 0), (6 * np.pi, -7), lw=0.6)
    f.dashed((10 * np.pi, 0), (10 * np.pi, 7), lw=0.6)
    f.hytext('x', (xmax - 0.5, 0), dx=10, dy=-10, fs=10, italic=True)
    f.hytext('y', (0, 9.2), dx=8, dy=0, fs=10, italic=True)
    f.hytext('O', (0, 0), dx=-11, dy=-12, fs=9)
    f.lab('$-2\\pi$', (-2 * np.pi, 0), dx=-4, dy=-14, fs=9)
    f.lab('$2\\pi$', (2 * np.pi, 0), dx=4, dy=-14, fs=9)
    f.lab('$6\\pi$', (6 * np.pi, 0), dx=4, dy=-14, fs=9)
    f.lab('$10\\pi$', (10 * np.pi, 0), dx=10, dy=-14, fs=9)
    f.lab('$7$', (0, 7), dx=-10, dy=0, fs=9)
    f.lab('$-7$', (0, -7), dx=-12, dy=0, fs=9)
    f.save()


if __name__ == '__main__':
    q07()
    print('done')
