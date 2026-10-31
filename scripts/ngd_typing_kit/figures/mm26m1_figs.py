# -*- coding: utf-8 -*-
"""명문고 2학년 2026 1학기중간 대수 그림 2종 (Q15 그래프 개형 5지선다, Q20 지수함수 그래프).
실행: python3 mm26m1_figs.py"""
import numpy as np
from figlib import Fig


def mini_axis(f, cx, cy, hx=1.3, hy=1.3):
    f.ax.annotate('', xy=(cx + hx, cy), xytext=(cx - hx, cy),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=2)
    f.ax.annotate('', xy=(cx, cy + hy), xytext=(cx, cy - hy),
                  arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'), zorder=2)
    f.hytext('O', (cx, cy), dx=-6, dy=-7, fs=6.5, ha='right', va='top')
    f.hytext('x', (cx + hx, cy), dx=6, dy=0, fs=6.5, italic=True, ha='left')
    f.hytext('y', (cx, cy + hy), dx=0, dy=6, fs=6.5, italic=True, va='bottom')


def q15():
    f = Fig('mm26m1_q15', 20000, (-1.3, 5.0), (-10.6, 3.8))

    # --- 상단: 문제에 주어진 그래프 y=a^{x-2}+b (0<a<1, 점근선 y=-1, 점(2,0) 통과) ---
    f.ax.annotate('', xy=(4.6, 0), xytext=(-1.2, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 3.5), xytext=(0, -1.9),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.hytext('O', (0, 0), dx=-6, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (4.6, 0), dx=7, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 3.5), dx=0, dy=5, italic=True, fs=8.5, va='bottom')
    a0, b0 = 0.6, -1.0
    xs = np.linspace(-0.7, 5.6, 300)
    xs = xs[xs <= 4.5]
    ys = a0 ** (xs - 2) + b0
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)
    f.dashed((-1.2, -1.0), (4.0, -1.0))
    f.hytext('y=-1', (3.3, -1.0), dx=0, dy=-9, fs=7.5, ha='left', va='top')
    f.dot((2, 0))
    f.lab('$(2,~0)$', (2, 0), dx=4, dy=12, fs=7.5, ha='left')
    f.lab(r'$y=a^{x-2}+b$', (-0.5, a0 ** (-2.5) + b0), dx=-2, dy=10, fs=7.5, ha='left')

    # --- 하단: 그래프 개형 5지선다 (2열 x 3행, ⑤는 중앙) ---
    panels = {
        '①': (0.0, -3.8), '②': (2.6, -3.8),
        '③': (0.0, -6.4), '④': (2.6, -6.4),
        '⑤': (1.3, -9.0),
    }
    for lab, (cx, cy) in panels.items():
        mini_axis(f, cx, cy, hx=1.1, hy=1.1)
        f.ax.annotate(lab, xy=(cx - 1.1, cy + 1.1), xytext=(-2, 3), textcoords='offset points',
                      fontsize=10, fontfamily='DejaVu Sans', ha='left', va='bottom', zorder=6)

    cx, cy = panels['①']
    xs = np.linspace(-0.95, -0.3, 200)
    ys = 0.5 * np.log2(-xs)
    f.ax.plot(cx + xs, cy + ys, color='k', lw=1.0, zorder=3)

    cx, cy = panels['②']
    xs = np.linspace(0.3, 0.95, 200)
    ys = -0.5 * np.log2(xs)
    f.ax.plot(cx + xs, cy + ys, color='k', lw=1.0, zorder=3)

    cx, cy = panels['③']
    xs = np.linspace(-0.95, -0.5, 200)
    ys = 0.5 / (-xs)
    f.ax.plot(cx + xs, cy + ys, color='k', lw=1.0, zorder=3)

    cx, cy = panels['④']
    xs = np.linspace(0.5, 0.95, 200)
    ys = 0.5 / xs
    f.ax.plot(cx + xs, cy + ys, color='k', lw=1.0, zorder=3)

    cx, cy = panels['⑤']
    xs = np.linspace(0.3, 0.95, 200)
    ys = 0.5 * np.log2(xs)
    f.ax.plot(cx + xs, cy + ys, color='k', lw=1.0, zorder=3)

    f.save()


def q20():
    a = 1.70  # = log2(13/4), 실제 풀이값(약 1.700)을 그대로 사용한 개형도
    f = Fig('mm26m1_q20', 25500, (-1.5, 4.55), (-0.7, 6.1))
    f.ax.annotate('', xy=(4.1, 0), xytext=(-1.4, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 5.8), xytext=(0, -0.5),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.hytext('O', (0, 0), dx=-6, dy=-7, fs=8, ha='right', va='top')
    f.hytext('x', (4.1, 0), dx=10, dy=-1, italic=True, fs=9, ha='left')
    f.hytext('y', (0, 5.8), dx=0, dy=6, italic=True, fs=9, va='bottom')

    xs1 = np.linspace(-1.4, 2.1, 300)
    ys1 = 2 ** xs1 + 1
    f.ax.plot(xs1, ys1, color='k', lw=1.1, zorder=3)
    xs2 = np.linspace(-1.4 + a, 2.3 + a, 300)
    xs2 = xs2[xs2 <= 4.0]
    ys2 = 2 ** (xs2 - a) + 1
    f.ax.plot(xs2, ys2, color='k', lw=1.1, zorder=3)

    A = (a, 2 ** a + 1)
    B = (a, 2.0)
    C = (0.0, 2.0)
    D = (0.0, 2 ** (-a) + 1)
    f.dashed((a, 0), (a, A[1] + 0.15))
    f.seg(C, B, lw=0.9)
    f.rightangle(B, A, C, 0.13)
    for p in (A, B, C, D):
        f.dot(p)
    f.lab('A', A, dx=10, dy=8, fs=9)
    f.lab('B', B, dx=10, dy=-10, fs=9)
    f.lab('C', C, dx=-10, dy=8, fs=9)
    f.lab('D', D, dx=-10, dy=-9, fs=9)
    f.hytext('a', (a, 0), dx=0, dy=-10, fs=8, italic=True, va='top')
    f.lab(r'$y=2^{x}+1$', (1.55, 2 ** 1.55 + 1), dx=16, dy=10, fs=8, ha='left')
    f.lab(r'$y=2^{x-b}+1$', (1.15 + a, 2 ** 1.15 + 1), dx=10, dy=12, fs=8, ha='left')
    f.save()


if __name__ == '__main__':
    q15()
    q20()
    print('done')
