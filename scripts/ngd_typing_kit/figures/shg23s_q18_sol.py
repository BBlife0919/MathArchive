# -*- coding: utf-8 -*-
"""shg23s Q18 해설용 그림: y=6sin((x-pi)/4), 0<=x<=11pi, 직선 y=3sqrt3과 세 교점
(7/3pi, 11/3pi, 31/3pi), 점 P는 곡선의 최솟값(y=-6)에서. x축은 pi단위로 압축 표시.
실행: python3 shg23s_q18_sol.py"""
import math
import numpy as np
from figlib import Fig


def make():
    f = Fig('shg23s_q18_sol', 22000, (-1.0, 12.0), (-7.6, 7.2))
    PI = math.pi
    s3 = math.sqrt(3)
    xs = np.linspace(0, 11, 400)
    ys = 6 * np.sin((xs * PI - PI) / 4)
    f.ax.plot(xs, ys, color='k', lw=1.2, zorder=3)
    f.dashed((-0.8, 3 * s3), (11.6, 3 * s3), lw=0.6)
    for xv in [7 / 3, 11 / 3, 31 / 3]:
        f.dot((xv, 3 * s3))
    xmin = 7  # theta=(x-pi)/4=3pi/2 에서 sin최소(-1) -> x=7pi (압축단위=7)
    f.dot((xmin, -6))
    f.ax.annotate('', xy=(11.8, 0), xytext=(-0.8, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.9), xytext=(0, -7.3),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (11.6, -0.6), fs=10, italic=True)
    f.lab('$y$', (0.4, 6.6), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab(r'$3\sqrt{3}$', (-0.8, 3 * s3), dx=-4, dy=14, fs=9, ha='left')
    f.lab(r'$\frac{7}{3}\pi$', (7 / 3, 0), dx=-2, dy=-16, fs=9)
    f.lab(r'$\frac{11}{3}\pi$', (11 / 3, 0), dx=0, dy=14, fs=9)
    f.lab(r'$\frac{31}{3}\pi$', (31 / 3, 0), dx=0, dy=-16, fs=9)
    f.lab(r'$\mathrm{P}$', (xmin, -6), dx=0, dy=-16, fs=10)
    f.lab('$y=6\\sin\\left(\\frac{x-\\pi}{4}\\right)$', (8.3, 4.2), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
