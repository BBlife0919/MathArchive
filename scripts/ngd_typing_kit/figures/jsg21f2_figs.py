# -*- coding: utf-8 -*-
"""진성고 2021 2학기중간 수학2 그림: Q8(f,g 그래프), Q15(무리함수 접선 도형), Q21(계단형 넓이).
실행: python3 jsg21f2_figs.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import Fig
import numpy as np


def open_dot(f, p, ms=4.4):
    f.ax.plot([p[0]], [p[1]], 'o', ms=ms, mfc='white', mec='k', mew=0.9, zorder=6)


def _axes(f, xr, yr):
    f.ax.annotate('', xy=(xr, 0), xytext=(-xr, 0), arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'))
    f.ax.annotate('', xy=(0, yr), xytext=(0, -yr), arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'))
    f.hytext('x', (xr, 0), dx=7, dy=-2, italic=True, fs=8)
    f.hytext('y', (0, yr), dx=3, dy=5, italic=True, fs=8)
    f.hytext('O', (0, 0), dx=-6, dy=-6, fs=7.5, ha='right', va='top')


def q08():
    f = Fig('jsg21f2_q08', 28000, (-2.2, 6.6), (-2.0, 2.0))

    def axes_at(cx):
        f.ax.annotate('', xy=(cx + 1.8, 0), xytext=(cx - 1.8, 0), arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'))
        f.ax.annotate('', xy=(cx, 1.7), xytext=(cx, -1.7), arrowprops=dict(arrowstyle='-|>', lw=0.8, color='k'))
        f.hytext('x', (cx + 1.8, 0), dx=7, dy=-2, italic=True, fs=8)
        f.hytext('y', (cx, 1.7), dx=3, dy=5, italic=True, fs=8)
        f.hytext('O', (cx, 0), dx=-6, dy=-6, fs=7.5, ha='right', va='top')

    # 왼쪽: y=f(x), 중심 cx=0
    cx = 0.0
    axes_at(cx)
    for v in (-1, 1):
        f.dashed((cx + v, 0), (cx + v, 1)); f.hytext(str(v), (cx + v, 0), dx=0, dy=-9, fs=7, ha='center', va='top')
    f.dashed((cx, 1), (cx + 1, 1)); f.dashed((cx, -1), (cx + 1, -1))
    f.hytext('1', (cx, 1), dx=-7, dy=0, fs=7, ha='right'); f.hytext('-1', (cx, -1), dx=-10, dy=0, fs=7, ha='right')
    f.ax.plot([cx - 1.8, cx - 1], [1, 1], color='k', lw=1.1, zorder=3)
    f.dot((cx - 1, 1))
    f.ax.plot([cx - 1, cx + 1], [-1, 1], color='k', lw=1.1, zorder=3)
    open_dot(f, (cx - 1, -1)); open_dot(f, (cx + 1, 1))
    f.ax.plot([cx + 1, cx + 1.8], [-1, -1], color='k', lw=1.1, zorder=3)
    f.dot((cx + 1, -1))
    f.hyrun([('y', True), ('=', False), ('f', True), ('(', False), ('x', True), (')', False)],
            (cx + 1.0, 1.2), dx=4, dy=4, fs=8, ha='left')

    # 오른쪽: y=g(x), 중심 cx=4.4
    cx = 4.4
    axes_at(cx)
    for v in (-1, 1):
        f.dashed((cx + v, 0), (cx + v, 1)); f.hytext(str(v), (cx + v, 0), dx=0, dy=-9, fs=7, ha='center', va='top')
    f.dashed((cx, 1), (cx + 1, 1)); f.dashed((cx, -1), (cx + 1, -1))
    f.hytext('1', (cx, 1), dx=-7, dy=0, fs=7, ha='right'); f.hytext('-1', (cx, -1), dx=-10, dy=0, fs=7, ha='right')
    f.ax.plot([cx - 1.8, cx - 1], [-1, -1], color='k', lw=1.1, zorder=3)
    f.dot((cx - 1, -1))
    xs = np.linspace(-1, 1, 200)
    ys = 1 - 2 * xs ** 2
    f.ax.plot(cx + xs, ys, color='k', lw=1.1, zorder=3)
    open_dot(f, (cx + 1, -1))
    f.ax.plot([cx + 1, cx + 1.8], [1, 1], color='k', lw=1.1, zorder=3)
    f.dot((cx + 1, 1))
    f.hyrun([('y', True), ('=', False), ('g', True), ('(', False), ('x', True), (')', False)],
            (cx + 1.0, 1.2), dx=4, dy=4, fs=8, ha='left')

    f.save()


def q15():
    f = Fig('jsg21f2_q15', 14000, (-1.5, 6.3), (-1.3, 4.2))
    _axes(f, 5.8, 3.5)
    xs = np.linspace(0, 5.8, 200)
    f.ax.plot(xs, np.sqrt(xs), color='k', lw=1.1, zorder=3)
    f.lab(r'$y=\sqrt{x}$', (4.3, 4.3 ** 0.5), dx=0, dy=14, fs=9, ha='center', va='bottom')

    a = 1.2
    A = (a, a ** 0.5)
    L = (a ** 2 + a) ** 0.5
    B = (0, L)
    # BA 연장선과 x축 교점 C
    slope = (A[1] - B[1]) / (A[0] - B[0])
    xC = -B[1] / slope
    C = (xC, 0)

    f.dot(A); f.hytext('A', A, dx=6, dy=8, fs=8.5, ha='left')
    f.dot(B); f.hytext('B', B, dx=-8, dy=2, fs=8.5, ha='right')
    f.dot(C); f.hytext('C', C, dx=0, dy=-9, fs=8.5, ha='center', va='top')
    f.seg(B, C, lw=1.0)
    f.save()


def q21():
    f = Fig('jsg21f2_q21', 13000, (-0.6, 5.1), (-0.9, 4.2))
    _axes(f, 4.8, 3.6)
    for v in (1, 2, 3, 4):
        f.hytext(str(v), (v, 0), dx=0, dy=-9, fs=7.5, ha='center', va='top')
    for v in (1, 2, 3):
        f.hytext(str(v), (0, v), dx=-7, dy=0, fs=7.5, ha='right', va='center')
    f.dashed((0, 3), (3, 3)); f.dashed((0, 2), (2, 2))
    f.dashed((1, 0), (1, 1)); f.dashed((2, 0), (2, 2)); f.dashed((3, 0), (3, 3))

    xs = [0, 1, 2, 3, 3, 4]
    ys = [1, 1, 2, 2, 3, 3]
    poly = [(0, 0)] + list(zip(xs, ys)) + [(4, 0)]
    f.fill_poly(poly, fc='#dddddd', z=0.4)
    f.ax.plot([0, 1], [1, 1], color='k', lw=1.1, zorder=3)
    f.ax.plot([1, 2], [1, 2], color='k', lw=1.1, zorder=3)
    f.ax.plot([2, 3], [2, 2], color='k', lw=1.1, zorder=3)
    f.ax.plot([3, 3], [2, 3], color='k', lw=1.1, zorder=3)
    f.ax.plot([3, 4], [3, 3], color='k', lw=1.1, zorder=3)
    f.ax.plot([0, 0], [0, 1], color='k', lw=1.1, zorder=3)
    f.ax.plot([4, 4], [0, 3], color='k', lw=1.1, zorder=3)
    f.save()


if __name__ == '__main__':
    q08()
    q15()
    q21()
    print('done')
