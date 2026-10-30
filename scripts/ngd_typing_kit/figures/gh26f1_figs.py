# -*- coding: utf-8 -*-
"""광휘고 gh26f1(1학년 공통수학1) Q11 본문 그림 (계단형 정육면체 5개, 입체 느낌의 2.5D).
실행: python3 gh26f1_figs.py"""
from figlib import Fig

SK = 0.42  # 입체감을 위한 평행사변형 스큐 비율


def cube_front(f, x, y, s=1.0):
    """정면에서 본 정사각형 + 윗면/옆면을 평행사변형으로 덧붙여 입체감을 낸다."""
    p00 = (x, y)
    p10 = (x + s, y)
    p11 = (x + s, y + s)
    p01 = (x, y + s)
    f.poly([p00, p10, p11, p01], lw=1.0)
    # 윗면(평행사변형)
    q00 = p01
    q10 = p11
    q11 = (p11[0] + s * SK, p11[1] + s * SK)
    q01 = (p01[0] + s * SK, p01[1] + s * SK)
    f.poly([q00, q10, q11, q01], lw=1.0)
    # 옆면(평행사변형)
    r00 = p10
    r10 = (p10[0] + s * SK, p10[1] + s * SK)
    r11 = (p11[0] + s * SK, p11[1] + s * SK)
    r01 = p11
    f.poly([r00, r10, r11, r01], lw=1.0)


def q11():
    f = Fig('gh26f1_q11', 15000, (-0.6, 4.4), (-0.9, 3.5))
    cells = [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)]
    for (cx, cy) in cells:
        cube_front(f, cx, cy, s=1.0)
    f.lab('x cm', (0.5, 0), dx=0, dy=-14, fs=9, italic=True)
    f.save()


def q18():
    f = Fig('gh26f1_q18', 13000, (-0.4, 3.4), (-0.4, 2.4))
    labels = {(0, 1): '1', (1, 1): '2', (2, 1): '3', (0, 0): '4', (1, 0): '5', (2, 0): '6'}
    for cx in range(3):
        for cy in range(2):
            f.poly([(cx, cy), (cx + 1, cy), (cx + 1, cy + 1), (cx, cy + 1)], lw=1.1)
    for (cx, cy), lab in labels.items():
        f.lab(lab, (cx + 0.5, cy + 0.5), dx=0, dy=0, fs=10)
    f.save()


if __name__ == '__main__':
    q11()
    q18()
    print('done')
