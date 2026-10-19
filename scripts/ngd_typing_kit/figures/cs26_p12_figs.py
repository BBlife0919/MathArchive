# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 12쪽(대푯값 정리) 그림(표 2개). 실행: python3 cs26_p12_figs.py [q04 q07]
좌표 단위 = pt (w_hwp = 폭pt*100)."""
import sys
from figlib import *
from cs26_p11_figs import ktext, table

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


@reg
def q04():
    """#4 티셔츠 치수 줄기와 잎 그림 (8|0은 80호)."""
    cw = [48, 170]
    W = sum(cw)
    f = Fig('cs26_p12_q04', int(W * 100) + 400, (-2, W + 2), (-84, 20))
    ktext(f, '티셔츠 치수', W / 2, 10, 10.5)
    ktext(f, '(8|0은 80호)', W, 10, 9, ha='right')
    leaves = ['0 0 0 0 5 5 5', '0 0 0 0 5 5 5 5 5', '0 0 5 5']
    cells = [['줄기', '잎']] + [[s, l] for s, l in zip(['8', '9', '10'], leaves)]
    xs, ys = table(f, 0, 0, cw, [20, 20, 20, 20], cells, hdr_rows=(0,))
    # 줄기|잎 구분선(세로 직선) 위에 NGD 마크
    f.ngd_on((xs[1], ys[2] - 2), (xs[1], ys[4] + 2), 0.5)
    return f.save()


@reg
def q07():
    """#7 턱걸이 개수."""
    cw = [36] + [32] * 6
    W = sum(cw)
    f = Fig('cs26_p12_q07', int(W * 100) + 400, (-2, W + 2), (-70, 20))
    ktext(f, '턱걸이 개수', W / 2, 10, 10.5)
    ktext(f, '(단위: 개)', W, 10, 9, ha='right')
    cells = [[''] + ['1회', '2회', '3회', '4회', '5회', '6회'],
             ['지안'] + ['0', '2', '3', '6', '3', '1'],
             ['민주'] + ['1', '2', '7', '4', '2', '8']]
    xs, ys = table(f, 0, 0, cw, [22, 22, 22], cells, hdr_rows=(0,), hdr_cols=(0,))
    f.ngd_on((xs[2] + 3, ys[2]), (xs[4] - 3, ys[2]), 0.5)
    return f.save()


if __name__ == '__main__':
    for n in sys.argv[1:] or list(REG):
        print(REG[n]())
