# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 5쪽(원주각) 그림. 실행: python3 cs26_p05_figs.py [q01 ...]  (없으면 전부)
그림 파일명: cs26_p05_qMM.
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def lb(f, text, p, vec, d=9, **kw):
    v = np.array(vec, float)
    v = v / np.hypot(*v)
    f.lab(text, p, v[0] * d, v[1] * d, **kw)


def outl(f, text, c, deg, d=10, **kw):
    """원 둘레 위 각도 deg 점에 이름(원 바깥 방향)."""
    a = np.radians(deg)
    lb(f, text, cp(c, 1, deg), (np.cos(a), np.sin(a)), d, **kw)


@reg
def q01():
    """#1 (1)(2) 나란히. (1) ∠APB=60° → x=120, (2) ∠APB=100° → x=200(우각)."""
    f = Fig('cs26_p05_q01', 26000, (-1.4, 4.3), (-1.4, 1.35))
    # (1)
    O = P(0, 0)
    A = cp(O, 1, 198); B = cp(O, 1, 318); Pp = cp(O, 1, 78)
    f.circle(O, 1)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(O, A); f.seg(O, B); f.dot(O)
    f.angle(Pp, A, B, 0.2, '60°', fs=7.5)
    f.angle(O, A, B, 0.2, '$x$°', fs=8)
    outl(f, 'A', O, 198); outl(f, 'B', O, 318); outl(f, 'P', O, 78)
    f.lab('O', O, 8, 8)
    f.lab('(1)', P(-1.28, 1.2), 0, 0, ha='left')
    # (2)
    O2 = P(2.9, 0)
    A2 = cp(O2, 1, 180); B2 = cp(O2, 1, 340); P2 = cp(O2, 1, 270)
    f.circle(O2, 1)
    f.seg(P2, A2); f.seg(P2, B2); f.seg(O2, A2); f.seg(O2, B2); f.dot(O2)
    f.angle(P2, A2, B2, 0.22, '100°', fs=7.5)
    f.arc(O2, 0.2, -20, 180, lw=0.7)
    f.lab('$x$°', O2 + P(0, 0.42), 0, 0, fs=8)
    outl(f, 'A', O2, 180); outl(f, 'B', O2, 340); outl(f, 'P', O2, 270)
    f.lab('O', O2, 0, -10)
    f.lab('(2)', P(1.7, 1.2), 0, 0)
    f.ngd_on(P2, A2, 0.4)
    return f.save()


@reg
def q02():
    """#2 (1) ∠RLBt=40° → x=50, (2) ∠S=65° (SW 지름) → x=25."""
    f = Fig('cs26_p05_q02', 26000, (-1.4, 4.3), (-1.35, 1.35))
    # (1)
    O = P(0, 0)
    L = cp(O, 1, 180); R = cp(O, 1, 0); T = cp(O, 1, 88); Bt = cp(O, 1, 280)
    f.circle(O, 1)
    f.seg(L, R); f.seg(L, T); f.seg(T, Bt); f.seg(L, Bt); f.seg(R, Bt); f.dot(O)
    f.angle(T, L, Bt, 0.22, '$x$°', fs=8)
    f.angle(L, R, Bt, 0.4, '40°', fs=7.5)
    f.lab('O', O, 0, -10)
    f.lab('(1)', P(-1.28, 1.2), 0, 0, ha='left')
    # (2)
    O2 = P(2.9, 0)
    S = cp(O2, 1, 127); W = cp(O2, 1, -53); T2 = cp(O2, 1, 77)
    f.circle(O2, 1)
    f.seg(S, W); f.seg(S, T2); f.seg(T2, W); f.seg(O2, T2); f.dot(O2)
    f.angle(S, T2, W, 0.28, '65°', fs=7.5)
    f.angle(T2, O2, W, 0.35, '$x$°', fs=8)
    f.lab('O', O2, -9, -9)
    f.lab('(2)', P(1.7, 1.2), 0, 0)
    f.ngd_on(L, R, 0.78)
    return f.save()


@reg
def q03():
    """#3 (1) ∠25° ↔ 호 8 cm ↔ x°, (2) 4 cm/x cm."""
    f = Fig('cs26_p05_q03', 26000, (-1.55, 4.55), (-1.5, 1.4))
    # (1)
    O = P(0, 0)
    L = cp(O, 1, 180); T = cp(O, 1, 90)
    R1 = cp(O, 1, 25); R2 = cp(O, 1, -25); B1 = cp(O, 1, 245); B2 = cp(O, 1, 295)
    f.circle(O, 1)
    f.seg(L, R1); f.seg(L, R2); f.seg(T, B1); f.seg(T, B2); f.dot(O)
    f.angle(L, R1, R2, 0.35, None)
    f.lab('25°', L + P(-0.02, 0), -3, 0, ha='right', fs=7.5)
    f.angle(T, B1, B2, 0.5, '$x$°', fs=8)
    dimo(f, R2, R1, (1, 0), '8 cm', 15)
    dimo(f, B1, B2, (0, -1), '8 cm', 15)
    f.lab('O', O, 15, 0)
    f.lab('(1)', P(-1.5, 1.25), 0, 0, ha='left')
    # (2)
    O2 = P(3.1, 0)
    T2 = cp(O2, 1, 120); W = cp(O2, 1, 300); R = cp(O2, 1, 0); P1 = cp(O2, 1, 210); P2 = cp(O2, 1, 270)
    f.circle(O2, 1)
    f.seg(T2, P1); f.seg(T2, P2); f.seg(T2, R); f.seg(T2, W); f.seg(W, R); f.dot(O2)
    f.angle(T2, P1, P2, 0.5, '30°', tr=0.95, fs=7.5)
    f.angle(W, T2, R, 0.3, '60°', fs=7.5)
    dimo(f, P1, P2, (-1, -1), '$x$ cm', 16)
    dimo(f, W, R, (1, -0.6), '4 cm', 15)
    f.lab('O', O2, 10, 4)
    f.lab('(2)', P(1.75, 1.25), 0, 0)
    f.ngd_on(T2, R, 0.5)
    return f.save()


@reg
def q04():
    """#4 ∠AQB=38°, PB는 지름. x=∠APB=38°, y=∠AOB=76°."""
    f = Fig('cs26_p05_q04', 13000, (-1.35, 1.5), (-1.35, 1.35))
    O = P(0, 0)
    Pp = cp(O, 1, 125); B = cp(O, 1, -55); A = cp(O, 1, 229); Q = cp(O, 1, -12)
    f.circle(O, 1)
    f.seg(Pp, B); f.seg(Pp, A); f.seg(O, A); f.seg(A, Q); f.seg(Q, B); f.dot(O)
    f.angle(Pp, A, B, 0.3, '$x$', fs=8)
    f.angle(O, A, B, 0.3, '$y$', fs=8)
    f.angle(Q, A, B, 0.3, None)
    f.lab('38°', Q + P(0.3, -0.27), 0, 0, fs=7.5)
    outl(f, 'P', O, 125); outl(f, 'Q', O, -12); outl(f, 'A', O, 229); outl(f, 'B', O, -55)
    f.lab('O', O, 9, 5)
    f.ngd_on(Pp, A, 0.5)
    return f.save()


@reg
def q05():
    """#5 박스 안 그림: ∠APB=∠CQD → ∠AOB=∠COD → 호 AB=호 CD. 인쇄된 선은 PA, PB, QC, QD, OA, OB, OC, OD(검수에서 확인)."""
    f = Fig('cs26_p05_q05', 9500, (-1.4, 1.4), (-1.4, 1.35))
    O = P(0, 0)
    A = cp(O, 1, 190); B = cp(O, 1, 250); C = cp(O, 1, 290); D = cp(O, 1, 350)
    Pp = cp(O, 1, 120); Q = cp(O, 1, 60)
    f.circle(O, 1)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(Q, C); f.seg(Q, D); f.dot(O)
    f.seg(O, A); f.seg(O, B); f.seg(O, C); f.seg(O, D)
    f.angle(Pp, A, B, 0.2, None); f.angle(Q, C, D, 0.2, None)
    f.angle(O, A, B, 0.2, None); f.angle(O, C, D, 0.2, None)
    outl(f, 'A', O, 190); outl(f, 'B', O, 250); outl(f, 'C', O, 290); outl(f, 'D', O, 350)
    outl(f, 'P', O, 120); outl(f, 'Q', O, 60)
    f.lab('O', O, 0, 10)
    f.ngd_on(Q, D, 0.55)
    return f.save()


@reg
def q06():
    """#6 BD, AC 지름, ∠DAC=35° → ∠ABD=55°."""
    f = Fig('cs26_p05_q06', 12500, (-1.4, 1.45), (-1.35, 1.3))
    O = P(0, 0)
    A = cp(O, 1, 180); C = cp(O, 1, 0); D = cp(O, 1, 70); B = cp(O, 1, 250)
    f.circle(O, 1)
    f.seg(A, C); f.seg(A, D); f.seg(D, B); f.seg(A, B); f.dot(O)
    f.angle(A, C, D, 0.4, '35°', fs=7.5)
    f.angle(B, A, D, 0.2, None)
    outl(f, 'A', O, 180); outl(f, 'C', O, 0); outl(f, 'D', O, 70); outl(f, 'B', O, 250)
    f.lab('O', O, 9, -8)
    f.ngd_on(A, C, 0.75)
    return f.save()


@reg
def q07():
    """#7 호 BC = 2×호 AB, ∠AEB=25°, BD 지름 → x=50, y=50."""
    f = Fig('cs26_p05_q07', 13500, (-1.4, 1.4), (-1.4, 1.3))
    O = P(0, 0)
    A = cp(O, 1, 130); E = cp(O, 1, 50); B = cp(O, 1, 180); D = cp(O, 1, 0); C = cp(O, 1, 280)
    f.circle(O, 1)
    f.seg(A, E); f.seg(B, E); f.seg(A, O); f.seg(B, D); f.seg(D, C); f.dot(O)
    f.angle(E, A, B, 0.55, '25°', fs=7.5)
    f.angle(O, A, B, 0.3, '$x$', fs=8)
    f.angle(D, B, C, 0.3, '$y$', fs=8)
    outl(f, 'A', O, 130); outl(f, 'E', O, 50); outl(f, 'B', O, 180); outl(f, 'D', O, 0); outl(f, 'C', O, 280)
    f.lab('O', O, 0, -10)
    f.ngd_on(O, D, 0.3)
    return f.save()


@reg
def q08():
    """#8 PA, PB 접선, ∠APB=66° → x=57°."""
    f = Fig('cs26_p05_q08', 16000, (-1.35, 2.35), (-1.3, 1.3))
    O = P(0, 0)
    r = 1; OP = 1 / np.cos(np.radians(57))
    Pp = P(OP, 0)
    A = cp(O, 1, 57); B = cp(O, 1, -57); Q = cp(O, 1, 160)
    f.circle(O, 1)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(Q, A); f.seg(Q, B); f.dot(O)
    f.angle(Pp, A, B, 0.4, '66°', fs=7.5)
    f.angle(Q, A, B, 0.28, '$x$', fs=8)
    outl(f, 'A', O, 57); outl(f, 'B', O, -57); outl(f, 'Q', O, 160)
    lb(f, 'P', Pp, (1, 0), 10)
    f.lab('O', O, 9, -6)
    f.ngd_on(Pp, B, 0.45)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
