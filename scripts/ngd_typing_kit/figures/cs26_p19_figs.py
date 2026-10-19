# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 PDF 19쪽 그림(표 3개·과녁·등고선). 실행: python3 cs26_p19_figs.py [q15 ...]  (없으면 전부)
표는 그림(PNG)으로: 헤더 음영 #E0E0E0, 한글은 함초롬바탕, 수식은 mathtext(cm).
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord
from matplotlib.font_manager import FontProperties

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


KFP = FontProperties(fname='/Users/youngwoolee/.fonts/HCRBatang.ttf')


def ktext(f, s, x, y, fs=9.5):
    if '$' in s and any('가' <= c <= '힣' for c in s):
        raise ValueError(s)
    if '$' in s:
        f.lab(s, P(x, y), 0, 0, fs=fs)
    else:
        f.ax.text(x, y, s, fontproperties=KFP, fontsize=fs, ha='center', va='center', zorder=6)


def table(name, head, vals, cw0, cw, rh, w_hwp, ngd_col):
    """2행 표. 단위는 pt(1데이터=1pt). head=[(첫칸, 나머지...)], vals=[(첫칸, ...)]."""
    n = len(head) - 1
    W = cw0 + n * cw
    pad = 2
    f = Fig(name, w_hwp, (-pad, W + pad), (-pad, 2 * rh + pad))
    xs = [0, cw0] + [cw0 + (i + 1) * cw for i in range(n)]
    # 헤더 음영(윗행 전체 + 첫열)
    f.fill_poly([P(0, rh), P(W, rh), P(W, 2 * rh), P(0, 2 * rh)], '#E0E0E0')
    f.fill_poly([P(0, 0), P(cw0, 0), P(cw0, rh), P(0, rh)], '#E0E0E0')
    for y in (0, rh, 2 * rh):
        f.seg(P(0, y), P(W, y), lw=1.0)
    for x in xs:
        f.seg(P(x, 0), P(x, 2 * rh), lw=1.0)
    for i, s in enumerate(head):
        x = cw0 / 2 if i == 0 else cw0 + (i - 0.5) * cw
        ktext(f, s, x, 1.5 * rh)
    for i, s in enumerate(vals):
        x = cw0 / 2 if i == 0 else cw0 + (i - 0.5) * cw
        ktext(f, s, x, 0.5 * rh)
    f.ngd_on(P(cw0 + (ngd_col - 1) * cw + 4, rh), P(cw0 + ngd_col * cw - 4, rh), 0.5)
    return f.save()


@reg
def q15():
    return table('cs26_p19_q15', ['학생', '동은', '주은', '두리', '순애'],
                 ['편차(mm)', '$2x^{2}+1$', '$x$', '$2x^{2}-3$', '$2$'], 58, 44, 24, 27000, 2)


@reg
def q16():
    return table('cs26_p19_q16', ['변량', '$A$', '$B$', '$C$', '$D$', '$E$'],
                 ['편차', '$6x-3$', '$-x^{2}+1$', '$-3x-11$', '$2x^{2}-5$', '$-10$'], 40, 50, 24, 29000, 2)


@reg
def q17():
    return table('cs26_p19_q17', ['학생', '수애', '효리', '은주', '선덕', '현정'],
                 ['편차(점)', '$-5$', '$x$', '$x^{2}+1$', '$2$', '$x^{2}-1$'], 52, 44, 24, 27000, 2)


@reg
def q18():
    """#18 과녁 A,B,C: 3x3 칸, 점(화살) 위치는 원본 칸 안의 위치."""
    c = 22.0
    bx = [14, 106, 198]
    W = 270.0
    H = 3 * c + 8
    f = Fig('cs26_p19_q18', 27000, (0, W), (-4, 3 * c + 4))
    # 칸 안 점 위치(칸 중심 기준 비율, 위가 +)
    D = {
        'A': {1: [(-.28, 0)], 2: [(-.15, .32), (.22, -.28)], 3: [(.28, 0)], 4: [(-.25, .12)], 6: [(.28, 0)],
              7: [(-.28, 0)], 8: [(.30, -.02), (0, -.35)], 9: [(-.15, .30)]},
        'B': {1: [(-.30, 0), (.30, 0)], 2: [(.30, 0)], 3: [(.28, 0)], 5: [(-.25, -.12), (.25, .15)],
              7: [(.22, .20)], 8: [(-.28, 0)], 9: [(0, .30), (0, -.32)]},
        'C': {3: [(-.30, 0), (.30, 0)], 4: [(.25, .20), (-.25, -.25)], 5: [(-.28, 0), (.28, 0)],
              6: [(-.22, .25), (.10, -.32)], 7: [(.20, .20), (-.28, -.20)]},
    }
    for k, key in enumerate('ABC'):
        x0 = bx[k]
        for i in range(4):
            f.seg(P(x0, i * c), P(x0 + 3 * c, i * c), lw=1.6 if i in (0, 3) else 1.0)
            f.seg(P(x0 + i * c, 0), P(x0 + i * c, 3 * c), lw=1.6 if i in (0, 3) else 1.0)
        for n in range(1, 10):
            r, cc = divmod(n - 1, 3)
            cx = x0 + (cc + .5) * c; cy = 3 * c - (r + .5) * c
            f.lab(str(n), P(cx, cy), 0, 0, fs=9.5)
            for dx, dy in D[key].get(n, []):
                f.dot(P(cx + dx * c, cy + dy * c))
        f.lab(key, P(x0 - 10, 3 * c - 5), 0, 0, fs=10.5)
    f.ngd_on(P(bx[0] + c, 1 * c + 0), P(bx[0] + c, 2 * c), 0.5) if False else None
    f.ngd_on(P(bx[0] + c, c), P(bx[0] + c, 2 * c), 0.5)
    return f.save()


def blob(cx, cy, sx, sy, k, n=240):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    g = 1 + 0.07 * np.cos(2 * t + k) + 0.05 * np.sin(3 * t + 2 * k)
    return [P(cx + sx * g[i] * np.cos(t[i]), cy + sy * g[i] * np.sin(t[i])) for i in range(n)], t, g


@reg
def q19():
    """#19 등고선(단순 폐곡선 4개, 안쪽부터 A,B,C,D 지점)."""
    W, H = 190, 124
    f = Fig('cs26_p19_q19', 19000, (-3, W + 3), (-3, H + 3))
    f.seg(P(0, 0), P(W, 0), lw=1.2); f.seg(P(W, 0), P(W, H), lw=1.2)
    f.seg(P(W, H), P(0, H), lw=1.2); f.seg(P(0, H), P(0, 0), lw=1.2)
    specs = [(80, 56, 16, 12), (86, 58, 36, 28), (96, 60, 60, 44), (102, 62, 82, 54)]
    curves = []
    for i, (cx, cy, sx, sy) in enumerate(specs):
        pts, t, g = blob(cx, cy, sx, sy, 0.6 * i)
        f.ax.plot([p[0] for p in pts] + [pts[0][0]], [p[1] for p in pts] + [pts[0][1]], 'k-', lw=LW, zorder=2)
        curves.append((cx, cy, sx, sy, i))

    def on(i, deg):
        cx, cy, sx, sy, k = curves[i]
        tt = np.radians(deg)
        g = 1 + 0.07 * np.cos(2 * tt + 0.6 * k) + 0.05 * np.sin(3 * tt + 1.2 * k)
        return P(cx + sx * g * np.cos(tt), cy + sy * g * np.sin(tt))
    A = on(0, -95); B = on(1, -80); C = on(2, 5); D = on(3, -12)
    for p, s, off in ((A, 'A', (0, 12)), (B, 'B', (-8, -8)), (C, 'C', (10, 4)), (D, 'D', (-9, -8))):
        f.dot(p)
        f.lab(s, p, off[0], off[1], fs=9.5)
    # NGD: 틀 아래 변과 나란히 겹치게
    f.ngd_on(P(10, 0), P(W - 10, 0), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
