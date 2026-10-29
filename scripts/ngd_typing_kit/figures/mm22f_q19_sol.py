# -*- coding: utf-8 -*-
"""mm22f Q19 해설용 그림: y=3cos(theta) 한 주기(theta=pi/2^n * x, 0<=theta<=2pi)와
직선 y=1/(3n) 교점 2개(alpha, 2pi-alpha), 대칭성 설명용. x축은 theta 단위로 표시.
실행: python3 mm22f_q19_sol.py"""
import numpy as np
from figlib import Fig


def make():
    f = Fig('mm22f_q19_sol', 20000, (-1.7, 7.2), (-4.1, 4.4))
    thetas = np.linspace(0, 2 * np.pi, 300)
    ys = 3 * np.cos(thetas)
    f.ax.plot(thetas, ys, color='k', lw=1.2, zorder=3)
    c = 0.55  # 1/(3n) 대표값
    f.dashed((-1.5, c), (6.6, c), lw=0.6)
    alpha = np.arccos(c / 3)
    for th in (alpha, 2 * np.pi - alpha):
        f.dot((th, c))
    f.ax.annotate('', xy=(7.0, 0), xytext=(-0.6, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 4.1), xytext=(0, -3.8),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab(r'$\theta$', (6.6, -0.75), fs=10, italic=True)
    f.lab('$y$', (0.3, 3.8), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab(r'$\frac{1}{3n}$', (0.25, c), dx=0, dy=16, fs=9, ha='left')
    f.lab(r'$\alpha$', (alpha, 0), dx=0, dy=-16, fs=10, italic=True)
    f.lab(r'$2\pi-\alpha$', (2 * np.pi - alpha, 0), dx=0, dy=-16, fs=9)
    f.lab(r'$2\pi$', (2 * np.pi - 0.15, 0.85), fs=9, ha='right')
    f.lab('$y=3\\cos\\theta$', (3.6, -3.3), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    make()
    print('done')
