# -*- coding: utf-8 -*-
"""철산중 기말프린트 16쪽(산점도와 상관관계 정리) 그림. 실행: python3 cs26_p16_figs.py [p16_q03 ...]"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord
from cs26_p15_figs import (kr, num, newfig, arrow, brk, Grid, table, cloud, ell, band, panel_axes)

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


@reg
def p16_q03():
    """#3 최고 기온과 수돗물의 사용량 표."""
    W, H = 224, 46
    f = newfig('cs26_p16_q03', W, H)
    kr(f, '최고 기온과 수돗물의 사용량', W / 2, H - 6, fs=9)
    rows = [['기온(°C)', '25', '26', '31', '33', '29', '28', '27'],
            ['사용량(L)', '560', '640', '930', '980', '920', '850', '720']]
    x1, yb, xs, ys = table(f, 2, H - 13, [46] + [25] * 7, 15, rows, shade_cols=(0,), fs=9)
    f.ngd_on(P(xs[2], ys[1]), P(xs[3], ys[1]), 0.5)
    return f.save()


@reg
def p16_q04():
    """#4 양궁 1차·2차 산점도(점 10개)."""
    W, H = 150, 108
    f = newfig('cs26_p16_q04', W, H)
    g = Grid(f, 34, 18, 14, 11.5, 5, 5, list(range(6, 12)), list(range(6, 12)), 11, 11)
    o, e = g.draw(range(6, 11), range(6, 11), fs=9)
    num(f, '0', o[0] - 6, o[1] - 2, fs=9)
    brk(f, o[0] + 6, o[1])
    brk(f, o[0], o[1] + 5.5, horizontal=False)
    for x, y in [(7, 10), (8, 10), (9, 10), (7, 9), (8, 9), (9, 9), (10, 9), (6, 6), (7, 7), (8, 8)]:
        f.dot(P(*g.m(x, y)), r_pt=1.8)
    kr(f, '2차', o[0] - 8, e[1] + 17, fs=8.5)
    kr(f, '(점)', o[0] - 8, e[1] + 8, fs=8)
    kr(f, '1차(점)', e[0] + 8, o[1] - 12, fs=8.5, ha='center')
    f.ngd_on(P(g.m(6, 5)[0], o[1]), P(g.m(8, 5)[0], o[1]), 0.5)
    return f.save()


@reg
def p16_q05():
    """#5 표(좌) + 빈 격자(우)."""
    W, H = 290, 124
    f = newfig('cs26_p16_q05', W, H)
    kr(f, '수면으로부터의 깊이와', 2, H - 6, fs=8.5, ha='left')
    kr(f, '바닷물 속의 산소 함유량', 2, H - 16, fs=8.5, ha='left')
    rows = [['깊이(m)', '5', '10', '15', '20', '25', '30'],
            ['함유량(mg/L)', '6.5', '5.6', '5.4', '5.0', '4.6', '4.0']]
    x1, yb, xs, ys = table(f, 2, H - 26, [55] + [18.5] * 6, 16, rows, shade_cols=(0,), fs=8)
    g = Grid(f, 202, 22, 1.9, 22, 0, 3.5, list(range(5, 41, 5)), [4 + 0.5 * i for i in range(8)], 40, 7.5)
    o, e = g.draw(range(5, 36, 5), [4 + 0.5 * i for i in range(7)], fs=6.8, fmt=lambda v: ('%g' % v))
    num(f, '0', o[0] - 6, o[1] - 2, fs=8)
    brk(f, o[0] + 5, o[1])
    brk(f, o[0], o[1] + 5.5, horizontal=False)
    num(f, 'x', e[0] + 7, o[1] - 5, fs=9, italic=True)
    num(f, 'y', o[0] - 6, e[1] + 9, fs=9, italic=True)
    f.ngd_on(P(xs[0] + 20, ys[2]), P(xs[1] - 4, ys[2]), 0.5) if False else f.ngd_on(P(xs[2], ys[2]), P(xs[3], ys[2]), 0.5)
    return f.save()


@reg
def p16_q06():
    """#6 음의 상관관계 산점도."""
    W, H = 124, 92
    f = newfig('cs26_p16_q06', W, H)
    ox, oy, L, Hh = 12, 12, 104, 70
    panel_axes(f, ox, oy, L, Hh)
    cloud(f, 85, lambda rng: (lambda p: (p[0] + ox, p[1] + oy))(band((10, 60), (92, 14), 7.5)(rng)), None, 5.2, 21, r_pt=1.0)
    f.ngd_on(P(ox + 12, oy), P(ox + 50, oy), 0.5)
    return f.save()


@reg
def p16_q07():
    """#7 표(위) + 빈 격자(아래)."""
    W, H = 204, 140
    f = newfig('cs26_p16_q07', W, H)
    kr(f, '잎의 길이와 너비', 80, H - 6, fs=8.5)
    kr(f, '(단위: cm)', W - 2, H - 6, fs=7.5, ha='right')
    rows = [['길이', '15', '12', '7', '20', '10', '17', '12', '14'],
            ['너비', '10', '7', '4', '19', '8', '13', '10', '8']]
    x1, yb, xs, ys = table(f, 2, H - 13, [30] + [21.5] * 8, 14, rows, shade_cols=(0,), fs=8.5)
    g = Grid(f, 62, 14, 3.4, 3.2, 0, 0, list(range(1, 22)), list(range(1, 22)), 21, 21)
    o, e = g.draw([5, 10, 15], [5, 10, 15], fs=8)
    for k in range(1, 21):   # 1칸 격자(원본 촘촘한 격자)
        pass
    kr(f, '너비', o[0] - 30, e[1] - 10, fs=8)
    kr(f, '(cm)', o[0] - 30, e[1] - 20, fs=8)
    kr(f, '길이(cm)', e[0] + 14, o[1] - 3, fs=8, ha='left')
    num(f, 'y', o[0] - 6, e[1] + 7, fs=9, italic=True) if False else None
    f.ngd_on(P(xs[3], ys[2]), P(xs[4], ys[2]), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
