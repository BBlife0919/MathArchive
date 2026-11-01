# -*- coding: utf-8 -*-
"""진성고 2025 2학기기말 공통수학2 Q12 그림: 이차함수 f(x)=x^2-2ax와 직선 g(x)=x/a.
실행: python3 jsg25f2_figs.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import Fig
import numpy as np


def q12():
    # 대표값 a=1로 형태만 재현: f(x)=x^2-2x (꼭짓점 (1,-1)), g(x)=x, 교점 O(0,0), A(3,3)
    f = Fig('jsg25f2_q12', 17000, (-1.0, 4.6), (-1.8, 4.8))
    f.ax.annotate('', xy=(4.0, 0), xytext=(-0.8, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 4.2), xytext=(0, -1.6),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.hytext('x', (4.0, 0), dx=10, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 4.2), dx=0, dy=12, italic=True, fs=8.5, va='bottom')

    xs = np.linspace(-0.6, 3.6, 300)
    ys = xs ** 2 - 2 * xs
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)
    w = f.hyrun([('f', True), ('(', False), ('x', True), (')', False)],
                (2.5, 2.5 ** 2 - 2 * 2.5), dx=8, dy=-4, fs=8, ha='left')

    ls = np.linspace(-0.6, 3.6, 50)
    f.ax.plot(ls, ls, color='k', lw=1.0, zorder=3)
    f.hyrun([('g', True), ('(', False), ('x', True), (')', False)],
            (1.8, 1.8), dx=-6, dy=10, fs=8, ha='right')

    f.dot((0, 0))
    f.hytext('O', (0, 0), dx=-8, dy=-2, fs=9, ha='right')
    f.dot((3, 3))
    f.hytext('A', (3, 3), dx=6, dy=6, fs=9, ha='left')
    f.save()


if __name__ == '__main__':
    q12()
    print('done')
