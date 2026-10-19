# -*- coding: utf-8 -*-
"""철산중 기말프린트 15쪽(산점도와 상관관계) 그림 + 16쪽이 재사용하는 표/격자 도우미.
실행: python3 cs26_p15_figs.py [p15_q01 ...]  (없으면 전부)
모든 그림은 1pt = 1 데이터단위(= 100 HWPUNIT)로 그린다(xlim=(0,W), ylim=(0,H), w_hwp=W*100).
"""
import sys
from figlib import *
from matplotlib.font_manager import FontProperties
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


KRF = '/Users/youngwoolee/.fonts/HCRBatang.ttf'
KRP = FontProperties(fname=KRF)


def kr(f, text, x, y, fs=9, ha='center', va='center', rot=0, italic=False):
    """한글(HCR Batang)/숫자 글자. 좌표는 pt."""
    f.ax.text(x, y, text, fontproperties=KRP, fontsize=fs, ha=ha, va=va, rotation=rot,
              rotation_mode='anchor', zorder=6, fontstyle='italic' if italic else 'normal')


def num(f, text, x, y, fs=9, ha='center', va='center', italic=False):
    """STIX 숫자/영문 글자."""
    f.ax.text(x, y, text, fontsize=fs, ha=ha, va=va, zorder=6, fontstyle='italic' if italic else 'normal')


def newfig(name, W, H):
    return Fig(name, int(round(W * 100)), (0, W), (0, H))


def arrow(f, p, q, lw=0.9):
    f.ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', lw=lw, color='k',
                  mutation_scale=7, shrinkA=0, shrinkB=0), zorder=3)


def brk(f, x, y, horizontal=True, s=2.2):
    """축 꺾임표시(//): 두 개의 짧은 사선."""
    for k in (-1.3, 1.3):
        if horizontal:
            f.seg((x + k - s * 0.5, y - s), (x + k + s * 0.5, y + s), lw=0.7, z=4)
        else:
            f.seg((x - s, y + k - s * 0.5), (x + s, y + k + s * 0.5), lw=0.7, z=4)


class Grid:
    """산점도 격자. (x0,y0)=축 위치의 자료값, 격자선은 xlines/ylines, 눈금 글자는 xlabels/ylabels."""

    def __init__(self, f, ox, oy, sx, sy, x0, y0, xlines, ylines, xend, yend):
        self.f, self.ox, self.oy, self.sx, self.sy, self.x0, self.y0 = f, ox, oy, sx, sy, x0, y0
        self.xlines, self.ylines, self.xend, self.yend = xlines, ylines, xend, yend

    def m(self, x, y):
        return (self.ox + (x - self.x0) * self.sx, self.oy + (y - self.y0) * self.sy)

    def draw(self, xlabels, ylabels, zero=True, grid_lw=0.4, fs=8.5, fmt=str, ytop_box=True):
        f = self.f
        xe, ye = self.m(self.xend, self.yend)
        for gx in self.xlines:
            a, b = self.m(gx, self.y0), self.m(gx, self.yend)
            f.seg(a, b, lw=grid_lw, color='#9A9A9A', z=1)
        for gy in self.ylines:
            a, b = self.m(self.x0, gy), self.m(self.xend, gy)
            f.seg(a, b, lw=grid_lw, color='#9A9A9A', z=1)
        o = self.m(self.x0, self.y0)
        # 바깥 테두리(격자 오른쪽·위)
        f.seg((xe, o[1]), (xe, ye), lw=grid_lw, color='#9A9A9A', z=1)
        f.seg((o[0], ye), (xe, ye), lw=grid_lw, color='#9A9A9A', z=1)
        arrow(f, o, (xe + 6, o[1]))
        arrow(f, o, (o[0], ye + 6))
        for gx in xlabels:
            p = self.m(gx, self.y0)
            num(f, fmt(gx), p[0], p[1] - 7, fs=fs)
        for gy in ylabels:
            p = self.m(self.x0, gy)
            num(f, fmt(gy), p[0] - 3, p[1], fs=fs, ha='right')
        return o, (xe, ye)


def table(f, x0, ytop, colw, rowh, rows, shade_rows=(), shade_cols=(), fs=9, outer_lw=1.0, in_lw=0.6):
    """표를 그린다. colw: 열 폭 리스트(pt). rows: 행 문자열 리스트. 반환: (x1, ybot)"""
    nr, nc = len(rows), len(colw)
    xs = [x0]
    for w in colw:
        xs.append(xs[-1] + w)
    ys = [ytop - i * rowh for i in range(nr + 1)]
    for r in range(nr):
        for c in range(nc):
            if r in shade_rows or c in shade_cols:
                f.fill_poly([(xs[c], ys[r]), (xs[c + 1], ys[r]), (xs[c + 1], ys[r + 1]), (xs[c], ys[r + 1])], '#E0E0E0')
    for i, y in enumerate(ys):
        f.seg((xs[0], y), (xs[-1], y), lw=outer_lw if i in (0, nr) else in_lw)
    for j, x in enumerate(xs):
        f.seg((x, ys[0]), (x, ys[-1]), lw=outer_lw if j in (0, nc) else in_lw)
    for r in range(nr):
        for c in range(nc):
            t = rows[r][c]
            if not t:
                continue
            kr(f, t, (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2, fs=fs)
    return xs[-1], ys[-1], xs, ys


def cloud(f, n, sampler, pts_box, dmin, seed, r_pt=1.0):
    """pt좌표 점구름: 균일 느낌이 나도록 최소간격 dmin 보장. sampler(rng)->(x,y) 또는 None."""
    rng = np.random.default_rng(seed)
    pts = []
    tries = 0
    while len(pts) < n and tries < 200000:
        tries += 1
        p = sampler(rng)
        if p is None:
            continue
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= dmin ** 2 for q in pts):
            pts.append(p)
    for p in pts:
        f.dot(P(*p), r_pt=r_pt)
    return pts


def ell(cx, cy, a, b, deg=0):
    t = np.radians(deg)

    def s(rng):
        u, v = rng.uniform(-1, 1, 2)
        if u * u + v * v > 1:
            return None
        x, y = a * u, b * v
        return (cx + x * np.cos(t) - y * np.sin(t), cy + x * np.sin(t) + y * np.cos(t))
    return s


def band(p, q, w):
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    L = np.hypot(*d)
    nrm = np.array([-d[1], d[0]]) / L

    def s(rng):
        t = rng.uniform(0, 1)
        o = rng.uniform(-w, w)
        return tuple(p + t * d + o * nrm)
    return s


def panel_axes(f, ox, oy, L, Hh):
    arrow(f, (ox, oy), (ox + L, oy))
    arrow(f, (ox, oy), (ox, oy + Hh))
    num(f, 'x', ox + L + 1, oy - 6, fs=9, italic=True)
    num(f, 'y', ox - 6, oy + Hh + 1, fs=9, italic=True)


@reg
def p15_q01():
    """#1 ㄱㄴㄷㄹ 산점도 2x2."""
    W, H = 290, 138
    f = newfig('cs26_p15_q01', W, H)
    L, Hh = 96, 50
    spec = [('ㄱ.', 26, 78, ell(50, 30, 35, 9), 55, 3),
            ('ㄴ.', 176, 78, band((16, 8), (84, 48), 6.5), 58, 11),
            ('ㄷ.', 26, 14, ell(50, 28, 40, 17, -33), 85, 7),
            ('ㄹ.', 176, 14, ell(52, 28, 25, 25), 95, 5)]
    for lab, ox, oy, smp, n, seed in spec:
        panel_axes(f, ox, oy, L, Hh)
        kr(f, lab, ox - 24, oy + Hh + 3, fs=9, ha='left')
        cloud(f, n, lambda rng, smp=smp, ox=ox, oy=oy: (lambda p: None if p is None else (p[0] + ox, p[1] + oy))(smp(rng)),
              None, 5.0, seed, r_pt=1.0)
    f.ngd_on(P(176 + 4, 14), P(176 + 40, 14), 0.5)
    return f.save()


@reg
def p15_q02():
    """#2 표(좌) + 빈 격자(우). 점은 학생이 찍는 것이므로 격자만."""
    W, H = 290, 138
    f = newfig('cs26_p15_q02', W, H)
    kr(f, '한 달 동안의 전기 사용량과 수도 사용량', 2, H - 7, fs=8.5, ha='left')
    kr(f, '(단위: kWh, m³)', 2, H - 17, fs=7.5, ha='left')
    rows = [['전기', '수도', '전기', '수도'],
            ['241', '26', '116', '13'],
            ['188', '23', '159', '18'],
            ['199', '21', '220', '24'],
            ['196', '18', '199', '20'],
            ['241', '29', '135', '19']]
    x1, yb, xs, ys = table(f, 2, H - 24, [27, 27, 27, 27], 15, rows, shade_rows=(0,), fs=8.5)
    # 격자: x 105(축)~250, y 10(축)~31
    g = Grid(f, 160, 22, 0.78, 4.9, 105, 10, list(range(110, 251, 10)), list(range(12, 31, 2)), 250, 31)
    o, e = g.draw(range(120, 241, 20), range(12, 31, 2), fs=8)
    num(f, '0', o[0] - 6, o[1] - 2, fs=8)
    brk(f, o[0] + 4, o[1])
    brk(f, o[0], o[1] + 8, horizontal=False)
    kr(f, '수도 사용량(m³)', 128, (o[1] + e[1]) / 2, fs=8, rot=90)
    kr(f, '전기 사용량(kWh)', (o[0] + e[0]) / 2 + 8, 5, fs=8.5)
    num(f, 'x', e[0] + 10, o[1] - 5, fs=9, italic=True)
    num(f, 'y', o[0] - 6, e[1] + 9, fs=9, italic=True)
    f.ngd_on(P(g.m(125, 10)[0], o[1]), P(g.m(160, 10)[0], o[1]), 0.5)
    return f.save()


@reg
def p15_q03():
    """#3 제동거리 산점도(점 15개)."""
    W, H = 175, 136
    f = newfig('cs26_p15_q03', W, H)
    g = Grid(f, 40, 24, 2.1, 1.45, 30, 0, list(range(35, 86, 5)), list(range(5, 66, 5)), 87, 68)
    o, e = g.draw(range(35, 86, 5), range(5, 66, 5), fs=8)
    num(f, 'O', o[0] - 8, o[1] - 6, fs=8)
    brk(f, o[0] + 4, o[1])
    brk(f, o[0], o[1] + 5, horizontal=False)
    pts = [(40, 13), (45, 15), (50, 18), (55, 26), (60, 27), (60, 30), (60, 37), (65, 33), (65, 37),
           (70, 41), (70, 44), (75, 43), (75, 49), (80, 54), (85, 65)]
    for x, y in pts:
        f.dot(P(*g.m(x, y)), r_pt=1.7)
    kr(f, '제동', 12, e[1] - 6, fs=8)
    kr(f, '거리', 12, e[1] - 16, fs=8)
    kr(f, '(m)', 12, e[1] - 28, fs=8)
    kr(f, '차량 속력(km/h)', (o[0] + e[0]) / 2 + 10, 5, fs=8.5)
    num(f, 'x', e[0] + 10, o[1] - 5, fs=9, italic=True)
    num(f, 'y', o[0] - 6, e[1] + 9, fs=9, italic=True)
    f.ngd_on(P(g.m(50, 0)[0], o[1]), P(g.m(65, 0)[0], o[1]), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
