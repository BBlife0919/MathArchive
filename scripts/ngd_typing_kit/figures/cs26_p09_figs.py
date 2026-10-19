# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 9쪽(원주각의 활용 정리 #11~#16) 그림. 실행: python3 cs26_p09_figs.py [q11 ...]  (없으면 전부)"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}
FS_A = 7.5


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def arcticks(f, c, r, deg, n=2, half=0.05, gap_deg=3.0):
    for i in range(n):
        a = deg + (i - (n - 1) / 2) * gap_deg
        f.seg(cp(c, r - half, a), cp(c, r + half, a), lw=0.8)


@reg
def q11():
    """#11 호 AB=호 BC, ∠BRC=35°."""
    f = Fig('cs26_p09_q11', 13500, (-1.3, 2.0), (-1.3, 1.4))
    O = P(0, 0)
    C, R, Q, Pp, A, B = [cp(O, 1, a) for a in (-15, 60, 100, 155, 205, 275)]
    f.circle(O, 1)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(Q, A); f.seg(Q, C); f.seg(R, B); f.seg(R, C)
    arcticks(f, O, 1, 240, 2); arcticks(f, O, 1, 310, 2)
    f.angle(Q, A, C, 0.2, '$x$')
    f.angle(R, B, C, 0.3, None)
    tx = R + P(1.0, -0.12)
    f.lab('35°', tx, 0, 0, fs=FS_A)
    f.seg(tx + P(-0.2, 0.0), R + 0.3 * unit(unit(B - R) + unit(C - R)), lw=0.6)
    nm(f, 'Q', Q, O, 9); nm(f, 'R', R, O, 9); nm(f, 'P', Pp, O, 9)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.ngd_on(Pp, B, 0.72)
    return f.save()


@reg
def q12():
    """#12 직사각형 ABCD(AB=4, BC=6), 내접원 r=2, 접선 DE."""
    f = Fig('cs26_p09_q12', 17500, (-2.0, 6.9), (-1.8, 4.75))
    A = P(0, 4); B = P(0, 0); C = P(6, 0); D = P(6, 4)
    O = P(2, 2); Pp = P(0, 2); Qp = P(2, 0); S = P(2, 4); E = P(3, 0); R = P(3.6, 0.8)
    f.poly([A, B, C, D]); f.circle(O, 2); f.seg(D, E); f.dot(O)
    dimo(f, B, A, (-1, 0), '4 cm', 20)
    dimo(f, B, C, (0, -1), '6 cm', 24)
    f.lab('A', A, -9, 8); f.lab('B', B, -9, -8); f.lab('C', C, 9, -8); f.lab('D', D, 9, 8)
    f.lab('S', S, 0, 9); f.lab('P', Pp, 8, 0); f.lab('Q', Qp, 0, 9); f.lab('E', E, 0, -9)
    f.lab('R', R, 10, -6); f.lab('O', O, 0, -10)
    f.ngd_on(C, D, 0.5)
    return f.save()


@reg
def q13():
    """#13 AB 지름, ∠ACB=60°, x=∠DOE."""
    f = Fig('cs26_p09_q13', 11000, (-1.4, 1.4), (-1.25, 2.1))
    O = P(0, 0); A = P(-1, 0); B = P(1, 0); C = P(0, np.sqrt(3))
    D = P(-0.5, np.sqrt(3) / 2); E = P(0.5, np.sqrt(3) / 2)
    f.circle(O, 1)
    f.seg(A, B); f.seg(A, C); f.seg(B, C); f.seg(O, D); f.seg(O, E); f.dot(O)
    f.angle(C, A, B, 0.35, '60°', fs=FS_A)
    f.angle(O, D, E, 0.28, '$x$')
    f.lab('A', A, -9, -2); f.lab('B', B, 9, -2); f.lab('C', C, 0, 9)
    f.lab('D', D, -9, 4); f.lab('E', E, 9, 4); f.lab('O', O, 0, -10)
    f.ngd_on(A, O, 0.5)
    return f.save()


@reg
def q14():
    """#14 ∠BAD=102°, ∠BDC=42°, 접선 EF."""
    f = Fig('cs26_p09_q14', 11500, (-1.5, 1.5), (-1.45, 1.45))
    O = P(0, 0)
    A, B, C, D = [cp(O, 1, a) for a in (100, 186, 270, 30)]
    E = P(-0.85, -1); F = P(0.85, -1)
    f.circle(O, 1)
    f.poly([A, B, C, D]); f.seg(B, D)
    f.seg(P(-1.4, -1), P(1.4, -1)); f.dot(O); f.dot(E); f.dot(F)
    f.angle(A, B, D, 0.22, '102°', fs=FS_A)
    f.angle(D, B, C, 0.32, '42°', fs=FS_A)
    f.angle(C, D, F, 0.2, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'D', D, O, 9)
    f.lab('C', C, 0, -10); f.lab('E', E, 0, -10); f.lab('F', F, 0, -10)
    f.lab('O', O, 0, -10)
    f.ngd_on(P(-1.38, -1), P(-0.95, -1), 0.5)
    return f.save()


@reg
def q15():
    """#15 □ABCD 내접, l·m 은 B, D 에서의 접선, ∠BCD=110°."""
    f = Fig('cs26_p09_q15', 16000, (-1.7, 1.7), (-1.55, 1.3))
    O = P(0, 0)
    A, B, C, D = [cp(O, 1, a) for a in (85, 200, 260, 340)]
    f.circle(O, 1)
    f.poly([A, B, C, D]); f.dot(O)
    tb = P(0.342, -0.94); td = P(-0.342, -0.94)    # B, D 에서 아래쪽으로 향하는 접선 방향
    Bl = B + 0.9 * tb; Bu = B - 0.9 * tb
    Dl = D + 0.9 * td; Du = D - 0.9 * td
    f.seg(Bu, Bl); f.seg(Du, Dl)
    f.angle(B, C, Bl, 0.28, '$x$')
    f.angle(D, C, Dl, 0.28, '$y$')
    f.angle(C, B, D, 0.25, '110°', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'D', D, O, 9); f.lab('C', C, 0, -10)
    f.lab('$l$', Bu, -6, 4); f.lab('$m$', Du, 6, 4); f.lab('O', O, 10, 0)
    f.ngd_on(A, B, 0.5)
    return f.save()


@reg
def q16():
    """#16 벨트로 연결된 두 바퀴: 두 원+공통 접선 벨트, 작은 바퀴 쪽 벨트가 이루는 각 36°."""
    f = Fig('cs26_p09_q16', 26000, (-4.5, 0.8), (-1.25, 1.25))
    a = np.radians(18)
    rs, rb = 0.4, 1.0
    V = P(0, 0)
    cs = P(-rs / np.sin(a), 0); cb = P(-rb / np.sin(a), 0)
    def tp(c, r, sgn):
        return c + r * P(np.sin(a), sgn * np.cos(a))
    Tsu, Tsl, Tbu, Tbl = tp(cs, rs, 1), tp(cs, rs, -1), tp(cb, rb, 1), tp(cb, rb, -1)
    f.circle(cs, rs); f.circle(cb, rb)
    f.arc(cs, rs, -72, 72, lw=2.6); f.arc(cb, rb, 72, 288, lw=2.6)
    f.seg(Tbu, Tsu, lw=2.6); f.seg(Tbl, Tsl, lw=2.6)
    f.dashed(Tsu, V); f.dashed(Tsl, V)
    f.dot(cs, 1.4); f.dot(cb, 1.8)
    f.angle(V, Tsu, Tsl, 0.45, None)
    f.lab('36°', V + P(0.28, 0), 0, 0, fs=FS_A)
    f.ngd_on(Tbu, Tsu, 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
