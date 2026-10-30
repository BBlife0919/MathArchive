# -*- coding: utf-8 -*-
"""진성고 jsg26m1 Q14, Q21, Q22, Q23 본문 그림.
실행: python3 jsg26m1_figs.py"""
import numpy as np
from figlib import Fig


def q14():
    f = Fig('jsg26m1_q14', 20000, (-0.5, 4.7), (-1.6, 1.5))
    xs = np.linspace(0, 4, 400)
    ys = np.cos(np.pi * xs)
    f.ax.plot(xs, ys, color='k', lw=1.0, zorder=3)
    k = -0.55
    f.seg((-0.3, k), (4.5, k), lw=0.8)
    f.ax.annotate('', xy=(0, 1.4), xytext=(0, -1.5),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(4.6, 0), xytext=(-0.4, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 1.4), dx=8, dy=0, fs=9, italic=True)
    f.hytext('x', (4.6, 0), dx=8, dy=-8, fs=9, italic=True)
    f.hytext('O', (0, 0), dx=-10, dy=-10, fs=9)
    f.hytext('1', (0, 1), dx=-10, dy=0, fs=9)
    f.hytext('4', (4, 0), dx=0, dy=-14, fs=9)
    f.lab(r'$y=\cos\pi x$', (2.0, 1.05), dx=0, dy=14, fs=8.5)
    f.lab('$y=k$', (4.5, k), dx=18, dy=0, fs=8.5)
    # roots of cos(pi x) = k near x=1 (alpha,beta) and x=3 (gamma,delta)
    s = np.arccos(k) / np.pi  # cos(pi*(1-s)) = -cos(pi*s)... use direct solve
    ang = np.arccos(k)
    alpha = 1 - ang / np.pi
    beta = 1 + ang / np.pi
    gamma = 3 - ang / np.pi
    delta = 3 + ang / np.pi
    for x0, name in [(alpha, r'$\alpha$'), (beta, r'$\beta$'), (gamma, r'$\gamma$'), (delta, r'$\delta$')]:
        f.dashed((x0, 0), (x0, k), lw=0.6)
        f.dot((x0, k))
        f.lab(name, (x0, 0), dx=0, dy=10, fs=9)
    f.save()


def q21():
    f = Fig('jsg26m1_q21', 20000, (-5.2, 7.5), (-9.5, 10.2))
    xs = np.linspace(-5.0, 2.95, 300)
    ys_f = (xs + 4) * (xs - 2)
    f.ax.plot(xs, ys_f, color='k', lw=1.0, zorder=3)
    xg = np.linspace(-0.3, 6.3, 300)
    yg = -1.0 * xg * (xg - 6)
    f.ax.plot(xg, yg, color='k', lw=1.0, zorder=3)
    f.ax.annotate('', xy=(0, 10.0), xytext=(0, -9.3),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(7.3, 0), xytext=(-5.0, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 10.0), dx=8, dy=0, fs=9, italic=True)
    f.hytext('x', (7.3, 0), dx=8, dy=-8, fs=9, italic=True)
    f.hytext('O', (0, 0), dx=-10, dy=-10, fs=9)
    f.hytext('-4', (-4, 0), dx=0, dy=-14, fs=9)
    f.hytext('2', (2, 0), dx=0, dy=-14, fs=9)
    f.hytext('6', (6, 0), dx=0, dy=-14, fs=9)
    f.lab('$y=f(x)$', (2.6, 2.9), dx=10, dy=10, fs=8.5)
    f.lab('$y=g(x)$', (5.0, 7.3), dx=14, dy=6, fs=8.5)
    f.save()


def q22():
    f = Fig('jsg26m1_q22', 20000, (-4.8, 2.2), (-1.0, 6.8))
    xs = np.linspace(-4.5, 2.0, 300)
    y1 = (2 / 3) ** (xs + 3) + 1
    y2 = (2 / 3) ** (xs + 1) + 8 / 3
    f.ax.plot(xs, y1, color='k', lw=1.0, zorder=3)
    f.ax.plot(xs, y2, color='k', lw=1.0, zorder=3)
    k = 17 / 3
    xl = np.linspace(-3.2, -0.3, 10)
    f.ax.plot(xl, 2 * xl + k, color='k', lw=1.0, zorder=3)
    f.ax.annotate('', xy=(0, 6.6), xytext=(0, -0.8),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(2.1, 0), xytext=(-4.7, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 6.6), dx=8, dy=0, fs=9, italic=True)
    f.hytext('x', (2.1, 0), dx=8, dy=-8, fs=9, italic=True)
    f.hytext('O', (0, 0), dx=-10, dy=-10, fs=9)
    P = (-2, 5 / 3)
    Qp = (-1, 11 / 3)
    f.dot(P)
    f.dot(Qp)
    f.hytext('P', P, dx=-11, dy=-5, fs=9)
    f.hytext('Q', Qp, dx=8, dy=6, fs=9)
    f.lab(r'$y=\left(\frac{2}{3}\right)^{x+1}+\frac{8}{3}$', (-3.6, 4.4), dx=0, dy=0, fs=7.5)
    f.lab(r'$y=\left(\frac{2}{3}\right)^{x+3}+1$', (-3.9, 1.1), dx=0, dy=0, fs=7.5)
    f.lab('$y=2x+k$', (-0.3, 2 * -0.3 + k), dx=14, dy=6, fs=8)
    f.save()


def q23():
    xlim = (-0.55, 3.75)
    ylim = (-1.8, 6.0)
    f = Fig('jsg26m1_q23', 26000, xlim, ylim)
    # 스케마틱 그래프: 가로세로 동일축척 대신 보기 좋은 와이드 비율로 강제 조정
    f.ax.set_aspect('auto')
    dx = xlim[1] - xlim[0]
    f.h_in = f.w_in * 0.58
    f.h_hwp = round(f.h_in * 7200)
    f.fig.set_size_inches(f.w_in, f.h_in)
    a, b, c = 3, 4, 2
    xs = np.linspace(xlim[0], xlim[1], 1200)
    ys = np.abs(a * np.sin(b * xs) + c)
    f.ax.plot(xs, ys, color='k', lw=1.0, zorder=3)
    f.ax.annotate('', xy=(0, 5.8), xytext=(0, -0.3),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.ax.annotate('', xy=(3.3, 0), xytext=(-0.4, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'), zorder=1)
    f.hytext('y', (0, 5.8), dx=10, dy=0, fs=9, italic=True)
    f.hytext('x', (3.3, 0), dx=10, dy=-6, fs=9, italic=True)
    f.hytext('O', (0, 0), dx=-10, dy=-14, fs=9)
    f.dashed((-0.4, 5), (np.pi / 8, 5), lw=0.6)
    f.dashed((np.pi / 8, 0), (np.pi / 8, 5), lw=0.6)
    f.hytext('5', (0, 5), dx=-12, dy=0, fs=9)
    f.hytext('2', (0, 2), dx=-12, dy=0, fs=9)
    f.hytext('1', (0, 1), dx=-12, dy=0, fs=9)
    f.lab(r'$\frac{\pi}{8}$', (np.pi / 8, 0), dx=0, dy=-24, fs=9)
    f.lab(r'$\frac{7}{8}\pi$', (7 * np.pi / 8, 0), dx=0, dy=-24, fs=9)
    f.lab(r'$y=\left|f(x)\right|$', (2.1, 5.3), dx=0, dy=0, fs=8.5)
    f.save()


if __name__ == '__main__':
    q14()
    q21()
    q22()
    q23()
    print('done')
