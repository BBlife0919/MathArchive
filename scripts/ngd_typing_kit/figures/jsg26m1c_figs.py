# -*- coding: utf-8 -*-
"""진성고 2026 1학기중간 공통수학1 Q22 그림: 담장+정사각형/직사각형 구역 끈 배치도.
실행: python3 jsg26m1c_figs.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import Fig


def q22():
    f = Fig('jsg26m1c_q22', 16000, (-0.6, 10.5), (-0.6, 5.0))
    # 담장(위쪽, 회색 굵은 선)
    f.ax.plot([0, 8], [4, 4], color='#999999', lw=6, solid_capstyle='butt', zorder=1)
    f.ax.text(8.3, 4.3, '담장', fontfamily='AppleGothic', fontsize=8, ha='left', va='center', zorder=6)

    # 끈: 좌/중/우 세로선 + 바닥 가로선
    f.seg((0, 0), (0, 4), lw=1.2)
    f.seg((3, 0), (3, 4), lw=1.2)
    f.seg((8, 0), (8, 4), lw=1.2)
    f.seg((0, 0), (8, 0), lw=1.2)

    f.ax.text(1.5, 2, '정사각형', fontfamily='AppleGothic', fontsize=7.5, ha='center', va='center', zorder=6)
    f.ax.text(5.5, 2, '직사각형', fontfamily='AppleGothic', fontsize=7.5, ha='center', va='center', zorder=6)
    f.save()


if __name__ == '__main__':
    q22()
    print('done')
