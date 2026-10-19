# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 14쪽(분산과 표준편차 정리) 그림. 실행: python3 cs26_p14_figs.py [q02 ...]"""
import sys
from cs26_p13_figs import *   # table_fig, bar_axes, T, GRAY ... (도우미 재사용)

REG14 = {}


def reg14(fn):
    REG14[fn.__name__] = fn
    return fn


@reg14
def q02():
    data = [['학생', 'A', 'B', 'C', 'D', 'E'],
            ['편차(점)', '$x$', '3', '1', '−1', '2']]
    f = table_fig('cs26_p14_q02', 27000, [1.5] + [1.0] * 5, 19, data, fs=10, ngd=(1, 3))
    # 변수 x 이탤릭
    return f.save()


@reg14
def q04():
    """줄기와 잎 그림(3|0은 30분)."""
    w = 15000
    W = w / 100.0
    rh = 17
    rows = [('3', '0   2   5'), ('4', '0   5'), ('5', '0'), ('6', '2')]
    H = 28 + rh * 5 + 2
    f = Fig('cs26_p14_q04', w, (0, W), (0, H))
    T(f, '캠페인에 참여한 시간', W / 2, H - 7, fs=9.5, weight='bold')
    T(f, '(3|0은 30분)', W / 2, H - 19, fs=8.5)
    ytop = H - 28
    xs = [1, 1 + 0.36 * (W - 2), W - 1]
    f.fill_poly([P(xs[0], ytop), P(xs[2], ytop), P(xs[2], ytop - rh), P(xs[0], ytop - rh)], GRAY, z=0.5)
    f.seg(P(xs[0], ytop), P(xs[2], ytop), lw=0.8)
    f.seg(P(xs[0], ytop - rh), P(xs[2], ytop - rh), lw=0.8)
    f.seg(P(xs[0], ytop - 5 * rh), P(xs[2], ytop - 5 * rh), lw=0.8)
    f.seg(P(xs[1], ytop), P(xs[1], ytop - 5 * rh), lw=0.8)
    T(f, '줄기', (xs[0] + xs[1]) / 2, ytop - rh / 2, fs=10)
    T(f, '잎', (xs[1] + xs[2]) / 2, ytop - rh / 2, fs=10)
    for i, (a, b) in enumerate(rows):
        yc = ytop - rh * (i + 1.5)
        T(f, a, (xs[0] + xs[1]) / 2, yc - 0.3, fs=10)
        T(f, b, xs[1] + 14, yc - 0.3, fs=10, ha='left')
    f.ngd_on(P(xs[1], ytop - 3.6 * rh), P(xs[1], ytop - 4.9 * rh), 0.5)
    return f.save()


@reg14
def q05():
    data = [['시각(시)', '3', '6', '9', '12', '15', '18', '21', '24'],
            ['서울', '2', '3', '3', '6', '8', '5', '3', '2'],
            ['제주도', '8', '9', '9', '10', '11', '9', '8', '8']]
    f = table_fig('cs26_p14_q05', 27000, [2.0] + [1.0] * 8, 19, data, title='서울과 제주도의 시간대별 기온', unit='(단위: °C)', fs=10, ngd=(2, 4))
    return f.save()


@reg14
def q06():
    data = [['', '1회', '2회', '3회', '4회'],
            ['편차(점)', '7', '−6', '', '8']]
    f = table_fig('cs26_p14_q06', 27000, [1.5] + [1.0] * 4, 19, data, title='수학 성적의 편차', fs=10, ngd=(1, 3))
    return f.save()


@reg14
def q08():
    data = [['종목', '평균', '표준편차'],
            ['마루운동', '12.550', '0.83'],
            ['도마', '12.283', '0.93'],
            ['안마', '14.050', '0.84'],
            ['링', '13.050', '0.97'],
            ['평행봉', '15.050', '0.79'],
            ['철봉', '13.750', '0.88']]
    f = table_fig('cs26_p14_q08', 22000, [1.1, 1.3, 1.3], 17, data, title='종목별 점수의 평균과 표준편차', unit='(단위: 점)', fs=10, shade_cols=(), ngd=(3, 1))
    return f.save()


@reg14
def q09():
    w = 22000
    W = w / 100.0
    uh = 14.0
    cellw = 27.0
    x0, y0 = 22, 16
    H = y0 + 7.4 * uh + 22
    f = Fig('cs26_p14_q09', w, (0, W), (0, H))
    T(f, '반별 수학 체험 동아리 회원 수', x0 + 3.5 * cellw, H - 5, fs=9.5, weight='bold')
    cx = bar_axes(f, x0, y0, 7, cellw, uh, 7.4, [f'{i}반' for i in range(1, 8)], [str(i) for i in range(0, 8)],
                  grid_to=7.4, ylab='(명)', xlab='')
    vals = [5, 7, 2, 1, 6, 4, 3]
    for k, v in enumerate(vals):
        xc = cx(k)
        x1, x2 = xc - 5.5, xc + 5.5
        f.poly([P(x1, y0), P(x2, y0), P(x2, y0 + v * uh), P(x1, y0 + v * uh)], fill='#9A9A9A', lw=0.8, z=2.5)
    f.ngd_on(P(x0, y0 + 5.0 * uh), P(x0, y0 + 6.0 * uh), 0.5)
    return f.save()


if __name__ == '__main__':
    for n in (sys.argv[1:] or list(REG14)):
        print(REG14[n]())
