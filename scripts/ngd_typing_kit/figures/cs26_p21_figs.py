# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 PDF 21쪽(24~27번) 그림. 실행: python3 cs26_p21_figs.py [q24 ...] (없으면 전부)
공용 격자 산점도 함수 gridplot 은 cs26_p20_figs.py 와 같은 코드(쪽별 독립 파일 규칙)."""
import sys
from figlib import *
from matplotlib.font_manager import FontProperties as _FP

REG = {}
KO = _FP(fname='/Users/youngwoolee/Library/Fonts/HANBatang.ttf')
GRID = '#9A9A9A'


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def ko(f, text, p, dx=0, dy=0, fs=9.5, ha='center', va='center'):
    f.ax.annotate(text, xy=p, xytext=(dx, dy), textcoords='offset points', ha=ha, va=va,
                  fontsize=fs, fontproperties=KO, zorder=6)


def arrow(f, p, q, lw=1.0):
    f.ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', lw=lw, color='k',
                                                      shrinkA=0, shrinkB=0, mutation_scale=7), zorder=3)


def gridplot(f, gx, gy, pts, xt, yt, xlab, ylab_chars, ylab_pos, xlab_pos, brk_x=None, brk_y=None,
             fs=9.5, r_pt=1.6, dot_names=None):
    """gx=(x0,x1), gy=(y0,y1): 격자 범위(칸 단위). xt/yt: {칸좌표: '글자'}. 축은 (x0,y0)에서 시작."""
    x0, x1 = gx; y0, y1 = gy
    for x in range(int(x0), int(x1) + 1):
        f.seg((x, y0), (x, y1), lw=0.4, color=GRID, z=1)
    for y in range(int(y0), int(y1) + 1):
        f.seg((x0, y), (x1, y), lw=0.4, color=GRID, z=1)
    f.seg((x1, y0), (x1, y1), lw=0.4, color=GRID, z=1); f.seg((x0, y1), (x1, y1), lw=0.4, color=GRID, z=1)
    arrow(f, (x0, y0), (x1, y0)); arrow(f, (x0, y0), (x0, y1))
    for x, t in xt.items():
        f.hytext(t, (x, y0), 0, -fs * 0.95, fs=fs)
    for y, t in yt.items():
        f.hytext(t, (x0, y), -4, 0, ha='right', fs=fs)
    f.hytext('O', (x0, y0), -3, -fs * 0.9, ha='right', fs=fs)
    # 축 생략 표시(≈ 모양 두 사선)
    if brk_x is not None:
        for d in (-1.6, 1.6):
            f.ax.plot([brk_x - 0.08 + d / f.pt_per_unit, brk_x + 0.08 + d / f.pt_per_unit], [y0 - 0.14, y0 + 0.14], color='k', lw=0.8, zorder=4)
    if brk_y is not None:
        for d in (-1.6, 1.6):
            f.ax.plot([x0 - 0.14, x0 + 0.14], [brk_y - 0.08 + d / f.pt_per_unit, brk_y + 0.08 + d / f.pt_per_unit], color='k', lw=0.8, zorder=4)
    for p in pts:
        f.dot(p, r_pt)
    ko(f, xlab, xlab_pos, fs=fs, ha='right')
    px, py = ylab_pos
    if isinstance(ylab_chars, str):
        ko(f, ylab_chars, (px, py), fs=fs, ha='left')
        ylab_chars = []
    for i, ch in enumerate(ylab_chars):
        ko(f, ch, (px, py), 0, -i * fs * 1.12, fs=fs, va='top')


@reg
def q24():
    """※ 공통 그림: 듣기(x)·말하기(y) 산점도 10명. 격자 칸=10점, 격자 범위 50~110."""
    f = Fig('cs26_p21_q24', 14000, (2.6, 11.0), (3.3, 11.4))
    s = lambda v: v / 10.0
    pts = [(100, 100), (60, 90), (80, 90), (90, 90), (80, 80), (100, 80), (60, 70), (90, 70), (60, 60), (70, 60)]
    gridplot(f, (5, 11), (5, 11), [(s(a), s(b)) for a, b in pts],
             {6: '60', 7: '70', 8: '80', 9: '90', 10: '100'},
             {6: '60', 7: '70', 8: '80', 9: '90', 10: '100'},
             '듣기(점)', ['말', '하', '기', '(점)'], (3.45, 11.3), (11.0, 3.85), brk_x=5.5, brk_y=5.5)
    f.ngd_on((5.1, 5), (5.9, 5), 0.5) if False else f.ngd_on((7.0, 11), (9.0, 11), 0.5)
    return f.save()


@reg
def q25():
    """작년(x)·올해(y) 읽은 책 수 산점도 25명. 격자 0~11, 눈금 2,4,..,10."""
    f = Fig('cs26_p21_q25', 13000, (-2.1, 11.6), (-2.2, 12.3))
    pts = [(1, 2), (1, 6), (2, 3), (3, 1), (3, 5), (4, 2), (4, 4), (4, 5), (4, 7), (4, 8), (5, 2), (5, 4), (5, 5),
           (5, 6), (6, 6), (6, 8), (7, 3), (7, 4), (7, 6), (7, 7), (8, 9), (9, 6), (9, 8), (10, 9), (10, 10)]
    tk = {2: '2', 4: '4', 6: '6', 8: '8', 10: '10'}
    gridplot(f, (0, 11), (0, 11), pts, tk, tk, '작년(권)', '올해(권)', (-1.3, 11.7), (11.5, -1.75), fs=8)
    f.ngd_on((6.0, 0), (9.0, 0), 0.5)
    return f.save()


@reg
def q26():
    """지혜네 반 25명: 중간고사(x)·기말고사(y) 산점도. 격자 칸=10점, 0~110. (원본에 인쇄된 점 26개 그대로)"""
    f = Fig('cs26_p21_q26', 13000, (-2.1, 11.6), (-2.2, 12.3))
    raw = [(60, 100), (90, 100), (100, 100), (70, 90), (80, 90), (90, 90), (50, 80), (60, 80), (70, 80),
           (30, 70), (60, 70), (70, 70), (80, 70), (40, 60), (70, 60), (50, 50), (60, 50), (70, 50), (90, 50),
           (30, 40), (50, 40), (10, 30), (20, 30), (30, 30), (90, 30), (40, 10)]
    tk = {2: '20', 4: '40', 6: '60', 8: '80', 10: '100'}
    gridplot(f, (0, 11), (0, 11), [(a / 10, b / 10) for a, b in raw], tk, tk, '중간고사(점)',
             '기말고사(점)', (-1.3, 11.7), (11.5, -1.75), fs=8)
    f.ngd_on((7.0, 0), (10.0, 0), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
