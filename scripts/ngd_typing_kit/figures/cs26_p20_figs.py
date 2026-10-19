# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 PDF 20쪽(단원평가 20~23번) 그림. 실행: python3 cs26_p20_figs.py [q21 ...] (없으면 전부)
격자 산점도 공용 함수(gridplot, ko, arrow)는 cs26_p21_figs.py 의 것을 재사용(같은 담당자 파일)."""
import sys
from figlib import *
from cs26_figs import nm, cp
from cs26_p21_figs import gridplot, ko, arrow

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


@reg
def q21():
    """#21 사분원: 반지름 r, 2r. 원점을 지나는 세 직선이 작은 원과 P1~P3, 큰 원과 Q1~Q3에서 만난다."""
    f = Fig('cs26_p20_q21', 12000, (-0.35, 2.75), (-0.4, 2.45))
    O = P(0, 0)
    f.arc(O, 1, 0, 90); f.arc(O, 2, 0, 90)
    arrow(f, (0, 0), (2.4, 0)); arrow(f, (0, 0), (0, 2.3))
    angs = [33, 59, 82]
    for i, a in enumerate(angs):
        f.seg(O, cp(O, 2, a))
    f.lab('$x$', (2.4, 0), 9, -3); f.lab('$y$', (0, 2.3), -7, 2)
    f.lab('O', O, -8, -8)
    f.lab('$r$', (1, 0), 0, -9); f.lab('$2r$', (2, 0), 0, -9)
    # 점 이름(P는 작은 원, Q는 큰 원)
    P1 = cp(O, 1, 33); P2 = cp(O, 1, 59); P3 = cp(O, 1, 82)
    Q1 = cp(O, 2, 33); Q2 = cp(O, 2, 59); Q3 = cp(O, 2, 82)
    for t, p, dx, dy in [('P$_1$', P1, 9, -7), ('P$_2$', P2, 13, -1), ('P$_3$', P3, 12, 5),
                         ('Q$_1$', Q1, 9, 4), ('Q$_2$', Q2, 8, 7), ('Q$_3$', Q3, 11, 5)]:
        f.lab(t, p, dx, dy)
    f.ngd_on((1.15, 0), (1.9, 0), 0.5)
    return f.save()


@reg
def q22():
    """#22 만들기(x)·그리기(y) 산점도 16명, A~E 표시. 격자 4~11, 눈금 5~10(축 생략 표시)."""
    f = Fig('cs26_p20_q22', 12000, (2.9, 11.7), (2.3, 12.1))
    pts = [(9, 10), (10, 10), (6, 9), (7, 9), (9, 9), (7, 8), (8, 8), (10, 8), (6, 7), (7, 7), (8, 7),
           (6, 6), (7, 6), (9, 6), (5, 5), (6, 5)]
    tk = {x: str(x) for x in range(5, 11)}
    gridplot(f, (4, 11), (4, 11), pts, tk, tk, '만들기(점)', '그리기(점)', (3.3, 11.65), (11.6, 2.75),
             brk_x=4.5, brk_y=4.5, fs=9)
    for t, p, dx, dy in [('A', (5, 5), -8, 7), ('B', (6, 9), -8, 7), ('C', (7, 6), 8, -7),
                         ('D', (9, 10), -8, 7), ('E', (10, 8), 8, -7)]:
        f.hytext(t, p, dx, dy, fs=9.5)
    f.ngd_on((8.0, 4), (10.0, 4), 0.5)
    return f.save()


@reg
def q23():
    """#23 농구부 12명: 2점 슛 개수(x)·3점 슛 개수(y) 산점도. 격자 0~7."""
    f = Fig('cs26_p20_q23', 11500, (-1.5, 7.8), (-2.0, 8.3))
    pts = [(1, 0), (1, 1), (2, 1), (2, 3), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3), (5, 3), (5, 5), (6, 4)]
    tk = {i: str(i) for i in range(1, 7)}
    gridplot(f, (0, 7), (0, 7), pts, tk, tk, '2점(개)', '3점(개)', (-1.0, 7.65), (7.7, -1.65), fs=9)
    f.ngd_on((2.4, 7), (5.6, 7), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
