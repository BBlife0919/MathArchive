# -*- coding: utf-8 -*-
"""운산고 2025 2학기기말 공통수학2 그림: Q1(사상도), Q2(함수그래프 5종),
Q13(계단형/거미줄 다이어그램), Q15(유리함수 점근선+수선).
실행: python3 us25f2_figs.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import Fig
import matplotlib.patches as mpatches
import numpy as np


def q01():
    f = Fig('us25f2_q01', 20000, (-2.2, 7.0), (-2.6, 3.0))
    cx1, cx2 = 0.0, 5.0
    f.ax.add_patch(mpatches.Ellipse((cx1, 0), 1.5, 4.6, fill=False, lw=1.1))
    f.ax.add_patch(mpatches.Ellipse((cx2, 0), 1.5, 4.6, fill=False, lw=1.1))
    f.hytext('X', (cx1, 2.66), fs=11, italic=True)
    f.hytext('Y', (cx2, 2.66), fs=11, italic=True)
    f.ax.annotate('', xy=(cx2 - 1.0, 2.15), xytext=(cx1 + 1.0, 2.15),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.hytext('f', ((cx1 + cx2) / 2, 2.4), fs=11, italic=True)

    xs_lab = ['1', '2', '3', '4', '5']
    xs_y = [1.6, 0.8, 0.0, -0.8, -1.6]
    for lab, y in zip(xs_lab, xs_y):
        f.dot((cx1, y), r_pt=1.3)
        f.hytext(lab, (cx1, y), dx=-16, fs=9.5, italic=True, ha='right')

    ys_lab = ['1', '3', '5', '7', '9']
    ys_y = [1.6, 0.8, 0.0, -0.8, -1.6]
    for lab, y in zip(ys_lab, ys_y):
        f.dot((cx2, y), r_pt=1.3)
        f.hytext(lab, (cx2, y), dx=16, fs=9.5, italic=True, ha='left')

    xpos = dict(zip(xs_lab, xs_y))
    ypos = dict(zip(ys_lab, ys_y))
    fmap = {'1': '3', '2': '5', '3': '7', '4': '1', '5': '9'}
    for src, dst in fmap.items():
        p = (cx1 + 0.62, xpos[src])
        q = (cx2 - 0.62, ypos[dst])
        f.ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.save()


def q02():
    f = Fig('us25f2_q02', 28500, (-1.6, 27.0), (-2.0, 2.6))
    panels = [(0, '1'), (6, '2'), (12, '3'), (18, '4'), (24, '5')]
    for ox, num in panels:
        f.ax.annotate('', xy=(ox + 1.5, 0), xytext=(ox - 1.1, 0), arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'))
        f.ax.annotate('', xy=(ox, 1.6), xytext=(ox, -1.1), arrowprops=dict(arrowstyle='-|>', lw=0.7, color='k'))
        f.hytext('y', (ox, 1.6), dx=10, dy=4, fs=8, italic=True)
        f.hytext('x', (ox + 1.5, 0), dx=6, dy=-6, fs=8, italic=True)
        f.hytext(num, (ox - 1.3, 1.85), dx=0, dy=4, fs=9, ha='left')
        if num == '1':
            # x=3 자리에 y=1, y=3 두 값이 대응(수직선 판정법 위반, 함수 아님)
            f.dashed((ox + 1, -1.0), (ox + 1, 1.3))
            f.dot((ox + 1, 0.3))
            f.dot((ox + 1, 0.9))
            f.hytext('1', (ox + 1, 0.3), dx=13, dy=-3, fs=7.5, ha='left')
            f.hytext('3', (ox + 1, 0.9), dx=13, dy=3, fs=7.5, ha='left')
            f.hytext('3', (ox + 1, 0), dx=0, dy=-13, fs=7.5, ha='center', va='top')
        elif num == '2':
            circ = mpatches.Circle((ox, 0), 0.95, fill=False, lw=1.0)
            f.ax.add_patch(circ)
        elif num == '3':
            f.ax.plot([ox + 1.0, ox + 1.0], [-1.0, 1.4], color='k', lw=1.1, zorder=3)
            f.hytext('1', (ox + 1.0, 0), dx=8, dy=-14, fs=7.5, ha='left')
        elif num == '4':
            xs = np.linspace(-1.1, 1.1, 50)
            f.ax.plot(ox + xs, xs, color='k', lw=1.1, zorder=3)
        elif num == '5':
            ys = np.linspace(-1.2, 1.2, 60)
            xs = 0.55 * ys ** 2 - 0.2
            f.ax.plot(ox + xs, ys, color='k', lw=1.1, zorder=3)
    f.save()


def q13():
    f = Fig('us25f2_q13', 20000, (-1.0, 10.6), (-1.3, 9.6))
    f.ax.annotate('', xy=(10.3, 0), xytext=(-0.5, 0), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.ax.annotate('', xy=(0, 9.3), xytext=(0, -0.5), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.hytext('O', (0, 0), dx=-7, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (10.3, 0), dx=8, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 9.3), dx=0, dy=8, italic=True, fs=8.5, va='bottom')

    # y=x
    f.ax.plot([0, 8.3], [0, 8.3], color='k', lw=0.9, zorder=2)
    f.hyrun([('y', True), ('=', False), ('x', True)], (8.3, 8.3), dx=8, dy=2, fs=8, ha='left')

    # 점 a<b<c<d<e, f(b)=a, f(c)=b, f(d)=c (증가함수 y=f(x))
    pts = {'a': 1.0, 'b': 2.3, 'c': 3.9, 'd': 5.8, 'e': 8.0}
    # 곡선: 각 x=t에서 f(t)를 아래 staircase 구조에 맞게 통과하는 매끈한 증가곡선
    xs = np.array([pts['a'], pts['b'], pts['c'], pts['d'], pts['e']])
    ys = np.array([0.3, pts['a'], pts['b'], pts['c'], pts['d']])
    curve_x = np.linspace(xs[0], xs[-1], 300)
    curve_y = np.interp(curve_x, xs, ys)
    f.ax.plot(curve_x, curve_y, color='k', lw=1.1, zorder=3)
    f.hyrun([('y', True), ('=', False), ('f', True), ('(', False), ('x', True), (')', False)],
            (xs[-1], ys[-1]), dx=8, dy=-4, fs=8, ha='left')

    for lab, x in pts.items():
        f.dashed((x, 0), (x, x))
        f.hytext(lab, (x, 0), dx=0, dy=-9, fs=8.5, italic=True, ha='center', va='top')

    # 계단선: e -> d(곡선) -> d위에서 y=x로 수평 -> d(x축) ... 반복 (f(e)=d,f(d)=c,f(c)=b,f(b)=a)
    chain = ['e', 'd', 'c', 'b']
    for i in range(len(chain) - 1):
        hi, lo = chain[i], chain[i + 1]
        xh = pts[hi]
        yv = pts[lo]
        f.dashed((xh, 0), (xh, yv))
        f.dashed((xh, yv), (yv, yv))
    f.save()


def q15():
    f = Fig('us25f2_q15', 18000, (-2.0, 11.5), (-2.0, 14.0))
    f.ax.annotate('', xy=(11.2, 0), xytext=(-1.6, 0), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.ax.annotate('', xy=(0, 13.3), xytext=(0, -1.6), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.hytext('O', (0, 0), dx=-7, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (11.2, 0), dx=7, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 13.3), dx=0, dy=2, italic=True, fs=8.5, va='bottom')

    # f(x)=8x/(x-2)=8+16/(x-2), 점근선 x=2,y=8
    f.ax.plot([2, 2], [-1.6, 13.3], color='k', lw=0.6, ls=(0, (4, 3)), zorder=1)
    f.ax.plot([-1.6, 11.2], [8, 8], color='k', lw=0.6, ls=(0, (4, 3)), zorder=1)
    f.hytext('2', (2, 0), dx=0, dy=-9, fs=7.5, ha='center', va='top')
    f.hytext('8', (0, 8), dx=-6, dy=0, fs=7.5, ha='right', va='center')

    xs = np.linspace(2.35, 11.0, 300)
    ys = 8 + 16 / (xs - 2)
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)

    # 점 P: t=4 -> x=6, y=8+16/4=12
    P = (6, 12)
    Q = (2, 12)   # 세로점근선 위 수선의 발 R, 가로점근선 위 수선의 발 Q
    R = (6, 8)
    f.dot(P)
    f.hytext('P', P, dx=7, dy=7, fs=9, ha='left')
    f.dashed(P, Q)
    f.dashed(P, R)
    f.dot(Q)
    f.dot(R)
    f.hytext('Q', Q, dx=-8, dy=4, fs=9, ha='right')
    f.hytext('R', R, dx=6, dy=-10, fs=9, ha='left')
    f.save()


if __name__ == '__main__':
    q01()
    q02()
    q13()
    q15()
    print('done')
