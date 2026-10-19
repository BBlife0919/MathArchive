# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 11쪽(통계-대푯값) 그림. 실행: python3 cs26_p11_figs.py [q03 q05]  (없으면 전부)
표·막대그래프는 그림(PNG). 좌표 단위 = pt (1단위 = 1pt, w_hwp = 폭pt*100)."""
import sys
from figlib import *
from matplotlib.patches import Rectangle

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


KOR = 'Nanum Myeongjo'
HDR = '#E0E0E0'


def ktext(f, s, x, y, fs=10, ha='center', va='center'):
    """한글 포함 글자(나눔명조). 숫자만이면 STIX."""
    fam = KOR if any('가' <= c <= '힣' for c in s) else 'STIXGeneral'
    f.ax.text(x, y, s, fontsize=fs, ha=ha, va=va, family=fam, zorder=6)


def table(f, x0, y0, cw, rh, cells, hdr_rows=(), hdr_cols=(), fs=10.5):
    """좌상단 (x0,y0), 열폭 cw 리스트, 행높이 rh 리스트. cells[r][c] 문자열. 음영: 머리행/머리열."""
    W, H = sum(cw), sum(rh)
    ys = [y0]
    for h in rh:
        ys.append(ys[-1] - h)
    xs = [x0]
    for w in cw:
        xs.append(xs[-1] + w)
    for r in range(len(rh)):
        for c in range(len(cw)):
            if r in hdr_rows or c in hdr_cols:
                f.ax.add_patch(Rectangle((xs[c], ys[r + 1]), cw[c], rh[r], fc=HDR, ec='none', zorder=0.5))
    for y in ys:
        f.seg((x0, y), (x0 + W, y), lw=0.8)
    for x in xs:
        f.seg((x, y0), (x, y0 - H), lw=0.8)
    for r in range(len(rh)):
        for c in range(len(cw)):
            s = cells[r][c]
            if not s:
                continue
            lines = s.split('\n')
            cx, cy = (xs[c] + xs[c + 1]) / 2, (ys[r] + ys[r + 1]) / 2
            for i, ln in enumerate(lines):
                dy = (len(lines) - 1) / 2 * fs * 1.25 - i * fs * 1.25
                ktext(f, ln, cx, cy + dy, fs)
    return xs, ys


@reg
def q03():
    """#3 일주일 동안의 축구화 판매량."""
    cw = [58] + [30] * 7
    W = sum(cw)
    f = Fig('cs26_p11_q03', int(W * 100) + 400, (-2, W + 2), (-64, 20))
    ktext(f, '일주일 동안의 축구화 판매량', W / 2, 10, 10.5)
    cells = [['축구화의\n크기(mm)'] + ['250', '255', '260', '265', '270', '275', '280'],
             ['판매량(켤레)'] + ['2', '6', '10', '7', '20', '2', '3']]
    xs, ys = table(f, 0, 0, cw, [34, 26], cells, hdr_cols=(0,))
    f.ngd_on((xs[3] + 3, ys[1]), (xs[5] - 3, ys[1]), 0.5)
    return f.save()


@reg
def q05():
    """#5 운동복 크기 막대그래프: 75:1 80:2 85:4 90:9 95:3 100:2 105:9 (명)."""
    vals = [1, 2, 4, 9, 3, 2, 9]
    labs = ['75', '80', '85', '90', '95', '100', '105']
    cwid, hu = 25.0, 9.0                      # 칸 폭, 눈금 1칸 높이(pt)
    X0, Y0 = 0, 0
    XR = cwid * 7
    f = Fig('cs26_p11_q05', int((XR + 46) * 100), (-20, XR + 26), (-22, hu * 10 + 24))
    # 격자(연한 회색)
    for k in range(11):
        f.seg((X0, k * hu), (XR, k * hu), lw=0.4, color='#999999', z=1)
    for i in range(8):
        f.seg((i * cwid, 0), (i * cwid, hu * 10), lw=0.4, color='#999999', z=1)
    # 막대
    for i, v in enumerate(vals):
        f.ax.add_patch(Rectangle((i * cwid + cwid * 0.2, 0), cwid * 0.6, v * hu, fc='#B8B8B8', ec='k', lw=0.8, zorder=3))
    f.seg((0, 0), (XR, 0), lw=1.0); f.seg((0, 0), (0, hu * 10), lw=1.0)
    f.seg((XR, 0), (XR, hu * 10), lw=1.0); f.seg((0, hu * 10), (XR, hu * 10), lw=1.0)
    for k in range(1, 11):
        ktext(f, str(k), -5, k * hu, 9, ha='right')
    ktext(f, '0', -5, 0, 9, ha='right')
    for i, s in enumerate(labs):
        ktext(f, s, i * cwid + cwid / 2, -9, 9.5)
    ktext(f, '(호)', XR + 3, -9, 9.5, ha='left')
    ktext(f, '(명)', -2, hu * 10 + 11, 9.5, ha='right')
    ktext(f, '운동복 크기', XR / 2, hu * 10 + 12, 10.5)
    f.ngd_on((cwid * 0.5, hu * 6), (cwid * 3.0, hu * 6), 0.5)
    return f.save()


if __name__ == '__main__':
    for n in sys.argv[1:] or list(REG):
        print(REG[n]())
