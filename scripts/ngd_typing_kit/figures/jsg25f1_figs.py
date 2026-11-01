# -*- coding: utf-8 -*-
"""진성고 2025 1학기기말 공통수학1 Q2 그림(네 학교 A,B,C,D 연결망).
실행: python3 jsg25f1_figs.py"""
import numpy as np
from matplotlib.patches import Circle
from figlib import Fig


def curve(f, p, q, bend, lw=1.0):
    """p-q를 잇는 2차 베지어 곡선(bend: 수직 방향 휨 정도, 0이면 직선)."""
    p = np.array(p, float)
    q = np.array(q, float)
    mid = (p + q) / 2
    d = q - p
    n = np.array([-d[1], d[0]])
    n = n / np.hypot(*n)
    ctrl = mid + n * bend
    t = np.linspace(0, 1, 60)
    pts = (1 - t)[:, None] ** 2 * p + 2 * (1 - t)[:, None] * t[:, None] * ctrl + t[:, None] ** 2 * q
    f.ax.plot(pts[:, 0], pts[:, 1], color='k', lw=lw, zorder=2)


def q02():
    f = Fig('jsg25f1_q02', 16000, (-1.6, 1.6), (-1.6, 1.6))
    R = 0.28
    A = (-1.1, 0.0)
    B = (0.0, 1.0)
    C = (0.0, -1.0)
    D = (1.1, 0.0)
    pts = {'A': A, 'B': B, 'C': C, 'D': D}

    # A-B: 2 lines
    curve(f, A, B, 0.07)
    curve(f, A, B, -0.07)
    # A-C: 1 line
    curve(f, A, C, 0.0)
    # B-C: 1 line
    curve(f, B, C, 0.0)
    # B-D: 3 lines
    curve(f, B, D, 0.10)
    curve(f, B, D, 0.0)
    curve(f, B, D, -0.10)
    # C-D: 2 lines
    curve(f, C, D, 0.07)
    curve(f, C, D, -0.07)

    for name, p in pts.items():
        f.ax.add_patch(Circle(p, R, facecolor='white', edgecolor='k', lw=1.1, zorder=3))
        f.hytext(name, p, fs=11, zorder=4)
    f.save()


if __name__ == '__main__':
    q02()
    print('done')
