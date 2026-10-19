# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 13쪽(분산과 표준편차) 그림. 실행: python3 cs26_p13_figs.py [q01 ...]
표·막대그래프는 그림(PNG)으로. 좌표 단위=pt(1pt=100 HWPUNIT)이므로 글자는 그린 크기 그대로 삽입된다.
공용 도우미(table_fig, bar_axes)는 14쪽 그림에서도 import 해서 쓴다.
"""
import sys, re
from matplotlib import font_manager
from figlib import *
from cs26_figs import dimo, nm, cp, chord  # noqa: F401  (지침: 보조함수 재사용)

_KO = os.path.expanduser('~/.fonts/HCRBatang.ttf')
if os.path.exists(_KO):
    font_manager.fontManager.addfont(_KO)
plt.rcParams['font.family'] = ['STIXGeneral', 'HCR Batang']

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


GRAY = '#E0E0E0'
FSZ = 9.5


def T(f, text, x, y, fs=FSZ, ha='center', va='center', weight='normal'):
    f.ax.text(x, y, text, fontsize=fs, ha=ha, va=va, fontweight=weight, zorder=6)


def new_fig(name, w_hwp, h_pt):
    """pt 좌표 그림: xlim=(0,W pt), ylim=(0,H pt)."""
    W = w_hwp / 100.0
    return Fig(name, w_hwp, (0, W), (0, h_pt)), W


def draw_table(f, x0, ytop, colw, rowh, data, fs=FSZ, shade_rows=(0,), shade_cols=(0,), lw=0.7):
    """data: 행 리스트(문자열). 반환 (바닥 y, 열 경계 x 목록, 행 경계 y 목록)."""
    nr, nc = len(data), len(colw)
    xs = [x0]
    for w in colw:
        xs.append(xs[-1] + w)
    ys = [ytop - i * rowh for i in range(nr + 1)]
    for r in range(nr):
        for c in range(nc):
            if r in shade_rows or c in shade_cols:
                f.fill_poly([P(xs[c], ys[r]), P(xs[c + 1], ys[r]), P(xs[c + 1], ys[r + 1]), P(xs[c], ys[r + 1])], GRAY, z=0.5)
    for y in ys:
        f.seg(P(xs[0], y), P(xs[-1], y), lw=lw)
    for x in xs:
        f.seg(P(x, ys[0]), P(x, ys[-1]), lw=lw)
    for r in range(nr):
        for c in range(nc):
            t = data[r][c]
            if t:
                T(f, t, (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2 - 0.3, fs=fs)
    return ys[-1], xs, ys


def table_fig(name, w_hwp, colfr, rowh, data, title=None, unit=None, fs=FSZ, tfs=9.5, shade_rows=(0,), shade_cols=(0,), ngd=None):
    """colfr: 열 폭 비율. 표 폭은 그림 폭 전체(좌우 1pt 여백)."""
    W = w_hwp / 100.0
    top_h = 16 if (title or unit) else 2
    H = top_h + rowh * len(data) + 2
    f = Fig(name, w_hwp, (0, W), (0, H))
    tot = float(sum(colfr))
    colw = [(W - 2) * c / tot for c in colfr]
    if title:
        T(f, title, W / 2, H - 7, fs=tfs, weight='bold')
    if unit:
        T(f, unit, W - 1, H - 7, fs=8.5, ha='right')
    yb, xs, ys = draw_table(f, 1, H - top_h, colw, rowh, data, fs=fs, shade_rows=shade_rows, shade_cols=shade_cols)
    if ngd:
        r, c = ngd          # 행 경계 r(위에서 r번째 가로선)과 열 c 가운데
        f.ngd_on(P(xs[c], ys[r]), P(xs[c + 1], ys[r]), 0.5)
    return f


def bar_axes(f, x0, y0, ncell, cellw, uh, ymax, xlabels, ylabels, brk=False, grid_to=None, ylab='(도수)', xlab='(점)', lw=0.9):
    """막대그래프 틀. (x0,y0)=원점. x는 셀 ncell개(셀 가운데에 xlabels), y는 단위높이 uh, 최대 ymax.
    brk=True 이면 첫 셀은 생략(≈) 칸이고 xlabels 는 두 번째 셀부터. 반환: 셀 가운데 x 함수."""
    top = y0 + ymax * uh
    gl = '#9A9A9A'
    gt = grid_to if grid_to is not None else ymax
    for i in range(1, int(gt) + 1):
        f.seg(P(x0, y0 + i * uh), P(x0 + ncell * cellw, y0 + i * uh), lw=0.4, color=gl, z=1)
    for j in range(1, ncell + 1):
        f.seg(P(x0 + j * cellw, y0), P(x0 + j * cellw, y0 + gt * uh), lw=0.4, color=gl, z=1)
    f.seg(P(x0, y0), P(x0, y0 + gt * uh), lw=lw, z=2)
    f.seg(P(x0, y0), P(x0 + ncell * cellw, y0), lw=lw, z=2)
    for i, lb in enumerate(ylabels):
        T(f, lb, x0 - 4, y0 + i * uh, fs=FSZ, ha='right')
    off = 1 if brk else 0
    for k, lb in enumerate(xlabels):
        T(f, lb, x0 + (k + off + 0.5) * cellw, y0 - 7, fs=FSZ)
    if brk:   # 꺾은선(≈) 표시
        cx = x0 + 0.5 * cellw
        f.ax.plot([cx - 4, cx - 1, cx + 1, cx + 4], [y0 - 2.2, y0 + 2.2, y0 - 2.2, y0 + 2.2], color='k', lw=0.7, zorder=3)
    T(f, ylab, x0 + 4, y0 + gt * uh + 7, fs=8.5, ha='center')
    T(f, xlab, x0 + ncell * cellw + 3, y0 - 7, fs=8.5, ha='left')
    return lambda k: x0 + (k + off + 0.5) * cellw


@reg
def q01():
    """#1 경기에서 얻은 점수 표 + (A 선수)(B 선수) 빈 도수 막대그래프(그리는 문제이므로 격자·축만)."""
    w = 29000
    W = w / 100.0
    uh = 11.0
    ymax = 4.4
    rowh = 13
    tbl_h = 16 + 3 * rowh
    y0 = 21
    H = tbl_h + y0 + ymax * uh + 13
    f = Fig('cs26_p13_q01', w, (0, W), (0, H))
    T(f, '경기에서 얻은 점수', W / 2, H - 7, fs=9.5, weight='bold')
    T(f, '(단위: 점)', W - 1, H - 7, fs=8.5, ha='right')
    data = [['경기 회차(회)'] + [str(i) for i in range(1, 9)],
            ['A', '6', '10', '9', '10', '8', '9', '10', '10'],
            ['B', '9', '7', '9', '9', '8', '7', '8', '7']]
    colfr = [3.2] + [1.0] * 8
    tot = sum(colfr)
    colw = [(W - 2) * c / tot for c in colfr]
    yb, xs, ys = draw_table(f, 1, H - 16, colw, rowh, data, fs=9, shade_rows=(0,), shade_cols=(0,))
    f.ngd_on(P(xs[3], ys[2]), P(xs[4], ys[2]), 0.5)
    # 두 막대그래프(빈 틀)
    cellw = 16.5
    for k, (x0, cap) in enumerate([(22, '〈A 선수〉'), (22 + 6 * cellw + 38, '〈B 선수〉')]):
        bar_axes(f, x0, y0, 6, cellw, uh, ymax, ['6', '7', '8', '9', '10'], ['0', '1', '2', '3', '4'],
                 brk=True, grid_to=4.4, ylab='(도수)')
        T(f, cap, x0 + 3.5 * cellw, 4.5, fs=9)
    return f.save()


@reg
def q03():
    """#3 학생 6명의 국제 수학 올림피아드 점수 표(빈칸 있음: B·D·E·F 점수, A·C 편차)."""
    data = [['', 'A', 'B', 'C', 'D', 'E', 'F'],
            ['점수', '28', '', '31', '', '', ''],
            ['편차', '', '1.5', '', '−1.5', '2.5', '−2.5']]
    f = table_fig('cs26_p13_q03', 27000, [1.2] + [1.0] * 6, 19, data, title='학생 6명의 국제 수학 올림피아드 점수', unit='(단위: 점)',
                  fs=10, ngd=(2, 3))
    return f.save()


@reg
def q06():
    """#6 평균·표준편차 표."""
    data = [['', '영지', '준서', '지은', '현영', '서영'],
            ['평균', '2', '3', '0.8', '1.6', '1.2'],
            ['표준편차', '0.4', '1.2', '0.5', '1.8', '0.3']]
    f = table_fig('cs26_p13_q06', 27000, [1.4] + [1.0] * 5, 19, data, unit='(단위: 시간)', fs=10, ngd=(2, 2))
    return f.save()


if __name__ == '__main__':
    for n in (sys.argv[1:] or list(REG)):
        print(REG[n]())
