# -*- coding: utf-8 -*-
"""ghh24f Q18 해설용 그림: y=3tan((x-pi)/6), 0<=x<=15pi, 점근선 x=4pi,10pi,
직선 y=sqrt(3)과 세 교점(2pi,8pi,14pi), 점 P(9pi,3sqrt3).
x축은 pi 단위로 압축 표시(실제 x/pi 값을 데이터좌표로 사용). 실행: python3 ghh24f_q18_sol.py"""
import math
import numpy as np
from figlib import Fig


def make():
    f = Fig('ghh24f_q18_sol', 24000, (-1.9, 16.4), (-7.0, 7.6))
    PI = math.pi
    cap = 3.6
    xcap = (6 / PI * math.atan(cap)) / PI   # pi 단위

    def seg(x0, x1):
        xs = np.linspace(x0, x1, 150)
        ys = 3 * np.tan((xs * PI - PI) / 6)
        f.ax.plot(xs, ys, color='k', lw=1.2, zorder=3)

    seg(0, 4 - xcap)
    seg(4 + xcap, 10 - xcap)
    seg(10 + xcap, 15)
    for xa in [4, 10]:
        f.dashed((xa, -6.4), (xa, 6.4), lw=0.7)
    f.dashed((-0.8, math.sqrt(3)), (15.9, math.sqrt(3)), lw=0.6)
    for x0 in [2, 8, 14]:
        f.dot((x0, math.sqrt(3)))
    f.dot((9, 3 * math.sqrt(3)))
    f.ax.annotate('', xy=(16.1, 0), xytext=(-0.8, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 7.3), xytext=(0, -6.7),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (15.9, -0.6), fs=10, italic=True)
    f.lab('$y$', (0.45, 7.0), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab(r'$\sqrt{3}$', (0, math.sqrt(3)), dx=-18, dy=0, fs=9)
    f.lab(r'$2\pi$', (2, 0), dx=0, dy=-14, fs=9)
    f.lab(r'$4\pi$', (4, 0), dx=-4, dy=14, fs=9)
    f.lab(r'$8\pi$', (8, 0), dx=0, dy=-14, fs=9)
    f.lab(r'$9\pi$', (9, 0), dx=0, dy=14, fs=9)
    f.lab(r'$10\pi$', (10, 0), dx=6, dy=14, fs=9)
    f.lab(r'$14\pi$', (14, 0), dx=0, dy=-14, fs=9)
    f.lab(r'$\mathrm{P}(9\pi,\,3\sqrt{3})$', (9.15, 3 * math.sqrt(3) - 0.15), fs=9, ha='left', va='top')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
