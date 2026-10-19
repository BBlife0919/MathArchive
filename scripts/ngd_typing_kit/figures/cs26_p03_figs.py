# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 PDF 3쪽((2) 원과 접선) 그림. 실행: python3 cs26_p03_figs.py [q01 ...]  (없으면 전부)
공용 헬퍼는 cs26_p02_figs.py 의 것을 가져다 쓴다(dimf, tri_incircle, circ_quad ...).
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord
from cs26_p02_figs import dimf, tri_incircle, out_of, inlab, circ_quad, FS_A

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def tangents(Pt, c, r):
    """외점 Pt 에서 원(c,r)에 그은 접점 두 개 (위쪽 먼저가 아니라 각도 +, -)."""
    Pt, c = np.array(Pt, float), np.array(c, float)
    v = Pt - c
    d = np.hypot(*v)
    base = np.degrees(np.arctan2(v[1], v[0]))
    th = np.degrees(np.arccos(r / d))
    return cp(c, r, base + th), cp(c, r, base - th)


@reg
def q01():
    """#1 (1) PA=x, PB=7. (2) PA=x-4, PB=10."""
    f = Fig('cs26_p03_q01', 29000, (-1.25, 7.3), (-1.45, 1.45))
    O = P(0, 0); Pp = P(2.6, 0)
    A, B = tangents(Pp, O, 1)
    f.circle(O, 1); f.seg(A, Pp); f.seg(B, Pp); f.dot(O)
    dimo(f, A, Pp, (0.5, 1), '$x$ cm', 10)
    dimo(f, B, Pp, (0.5, -1), '7 cm', 10)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'P', Pp, O, 9)
    f.lab('O', O, -12, 0)
    f.ngd_on(A, Pp, 0.3) if False else f.ngd_on(P(1.2, 0.25), P(1.8, 0.14), 0.5) if False else None
    f.lab('(1)', P(-1.15, 1.3), 0, 0)
    O2 = P(4.3, 0)
    B2 = P(4.3, -1); P2 = P(6.5, -1)
    A2 = tangents(P2, O2, 1)[0]
    f.circle(O2, 1); f.seg(A2, P2); f.seg(B2, P2); f.dot(O2)
    dimf(f, A2, P2, (1, 0.5), '($x$−4) cm', 26, frac=0.5)
    dimo(f, B2, P2, (0, -1), '10 cm', 9)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'P', P2, O2, 9)
    f.lab('O', O2, -12, 0)
    f.lab('(2)', P(3.15, 1.3), 0, 0)
    f.ngd_on(B2, P2, 0.45)
    return f.save()


@reg
def q02():
    """#2 OA=9, OP=15, PA=12 (색칠 □APBO)."""
    f = Fig('cs26_p03_q02', 14500, (-3.3, 1.9), (-1.95, 1.95))
    O = P(0, 0); Pp = P(-2.5, 0); r = 1.5
    B, A = tangents(Pp, O, r)
    f.fill_poly([A, Pp, B, O], '#C8C8C8', z=0.5)
    f.circle(O, r); f.seg(A, Pp); f.seg(B, Pp); f.seg(O, A); f.seg(O, B); f.seg(Pp, O); f.dot(O)
    dimf(f, Pp, O, (0, 1), '15 cm', 9, frac=0.72)
    dimo(f, A, O, (0.5, 1), '9 cm', 10)
    nm(f, 'A', A, P(-1.2, 0), 9); nm(f, 'B', B, P(-1.2, 0), 9); nm(f, 'P', Pp, O, 9); f.lab('O', O, 10, 0)
    f.ngd_on(Pp, A, 0.5)
    return f.save()


def _tri(name, B, C, A, w, dims, labs, ngd, xlim, ylim, inl):
    """삼각형+내접원 공통. dims: [(p,q,text,pt,frac)], 점 라벨 자동."""
    f = Fig(name, w, xlim, ylim)
    I, r, D, E, F = tri_incircle(A, B, C)
    f.circle(I, r); f.poly([A, B, C]); f.dot(I)
    for p, q, t, pt, fr in dims:
        dimf(f, p, q, out_of(I, p, q), t, pt, frac=fr)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 10); nm(f, 'C', C, I, 10)
    f.lab('O', I, 0, -10)
    for text, T, V in inl:
        inlab(f, text, T, V, I, 9, 6)
    f.ngd_on(*ngd)
    return f, (I, D, E, F)


@reg
def q03():
    """#3 (1) AD=x, DB=5, AC=6, BC=8 → x=3 (그림은 1.6배 확대). (2) AB=15, AC=10, BC=17, EC=x → 6."""
    f = Fig('cs26_p03_q03', 29000, (-1.8, 36.8), (-5.4, 10.8))
    k = 1.6
    B, C, A = P(0, 0), P(8 * k, 0), P(5.75 * k, np.sqrt(64 - 5.75 ** 2) * k)
    I, r, D, E, F = tri_incircle(A, B, C)
    f.circle(I, r); f.poly([A, B, C]); f.dot(I)
    dimf(f, A, D, out_of(I, A, D), '$x$ cm', 10)
    dimf(f, D, B, out_of(I, D, B), '5 cm', 10)
    dimf(f, A, C, out_of(I, A, C), '6 cm', 12)
    dimf(f, B, C, (0, -1), '8 cm', 12)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 11); nm(f, 'C', C, I, 11)
    inlab(f, 'D', D, A, I, 17, 3); inlab(f, 'E', E, C, I, 17, 3); inlab(f, 'F', F, A, I, 17, 3)
    f.lab('O', I, 0, -10)
    f.ngd_on(P(1.0, 0), P(4.5, 0), 0.5)
    f.lab('(1)', P(-1.2, 10.0), 0, 0)
    off = np.array([17.6, 0.0])
    B, C, A = P(0, 0) + off, P(17, 0) + off, P(12.176, 8.76) + off
    I, r, D, E, F = tri_incircle(A, B, C)
    f.circle(I, r); f.poly([A, B, C]); f.dot(I)
    dimf(f, B, A, out_of(I, B, A), '15 cm', 12)
    dimf(f, A, C, out_of(I, A, C), '10 cm', 12)
    dimf(f, B, C, (0, -1), '17 cm', 31)
    dimf(f, E, C, (0, -1), '$x$ cm', 9)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 11); nm(f, 'C', C, I, 11)
    inlab(f, 'D', D, A, I, 17, 3); inlab(f, 'E', E, B, I, 17, 3); inlab(f, 'F', F, A, I, 17, 3)
    f.lab('O', I, 0, -10)
    f.ngd_on(B + P(1.5, 0), B + P(5.5, 0), 0.5)
    f.lab('(2)', P(16.0, 10.0), 0, 0)
    return f.save()


@reg
def q04():
    """#4 AF=3, BD=8, CE=4 (AB=11, AC=7, BC=12)."""
    f = Fig('cs26_p03_q04', 14500, (-3.2, 14.3), (-2.9, 8.3))
    B, C, A = P(0, 0), P(12, 0), P(9, np.sqrt(121 - 81))
    I, r, D, E, F = tri_incircle(A, B, C)
    f.circle(I, r); f.poly([A, B, C]); f.dot(I)
    dimf(f, B, D, out_of(I, B, D), '8 cm', 12)
    dimf(f, A, F, out_of(I, A, F), '3 cm', 24)
    dimf(f, E, C, (0, -1), '4 cm', 9)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 11); nm(f, 'C', C, I, 11)
    uD = unit(D - I); uF = unit(F - I)
    f.lab('D', D, uD[0] * 9, uD[1] * 9); inlab(f, 'E', E, B, I, 17, 3); f.lab('F', F, uF[0] * 8 + unit(C - F)[0] * 11, uF[1] * 8 + unit(C - F)[1] * 11)
    f.lab('O', I, 0, -10)
    f.ngd_on(B, P(3.5, 0), 0.5) if False else f.ngd_on(P(0.6, 0), P(2.8, 0), 0.5)
    return f.save()


def _quad(name, lens, dims, w, xlim, ylim, s_deg=95.0, ngd=('BC', 0.5), tl='out'):
    f = Fig(name, w, xlim, ylim)
    A, B, C, D, Pp, Q, R, S = circ_quad(*lens, s_deg=s_deg)
    O = P(0, 0)
    f.circle(O, 1); f.poly([A, B, C, D]); f.dot(O)
    V = dict(A=A, B=B, C=C, D=D, P=Pp, Q=Q, R=R, S=S)
    for p, q, t, pt, fr, out in dims:
        dimf(f, V[p], V[q], out if out is not None else out_of(O, V[p], V[q]), t, pt, frac=fr)
    for k in 'ABCD':
        nm(f, k, V[k], O, 10)
    for k in ('PQRS' if tl else ''):
        if tl == 'out':
            nm(f, k, V[k], O, 9)
        else:                                     # 안쪽(원 안, 접점에서 중심 쪽으로 11pt)
            u = unit(O - V[k])
            f.lab(k, V[k], u[0] * 11, u[1] * 11)
    f.lab('O', O, 0, -10)
    s, e = {'BC': (B, C), 'AB': (A, B)}[ngd[0]]
    f.ngd_on(s, e, ngd[1])
    return f, V


@reg
def q05():
    """#5 설명(외접사각형): 길이 표시 없음."""
    f, V = _quad('cs26_p03_q05', (3, 5, 4, 4), [], 12500, (-1.6, 1.7), (-1.45, 1.55), ngd=('BC', 0.25))
    return f.save()


@reg
def q06():
    """#6 AB=8, AD=8, CD=10, BC=x (접선 길이 4,4,6,4)."""
    f, V = _quad('cs26_p03_q06', (4, 4, 6, 4), [
        ('A', 'D', '8 cm', 12, 0.5, None), ('A', 'B', '8 cm', 12, 0.5, None),
        ('C', 'D', '10 cm', 12, 0.5, None), ('B', 'C', '$x$ cm', 12, 0.5, None)],
        13500, (-2.1, 1.9), (-1.7, 1.75), ngd=('BC', 0.25), tl=None)
    return f.save()


@reg
def q07():
    """#7 ∠APB=80°, ∠ABP=?"""
    f = Fig('cs26_p03_q07', 13000, (-1.9, 1.9), (-1.35, 2.05))
    O = P(0, 0); d = 1 / np.sin(np.radians(40)); Pp = P(0, d)
    A, B = cp(O, 1, 140), cp(O, 1, 40)
    f.circle(O, 1); f.dot(O)
    for T in (A, B):
        u = unit(T - Pp)
        f.seg(Pp, T + u * 0.35)
    f.seg(A, B)
    f.angle(Pp, A, B, 0.33, '80°', fs=FS_A)
    f.angle(B, A, Pp, 0.2, None)
    nm(f, 'A', A, P(0, -0.1), 11); nm(f, 'B', B, P(0, -0.1), 11); f.lab('P', Pp, 0, 9); f.lab('O', O, 0, -10)
    f.ngd_on(A, B, 0.5)
    return f.save()


@reg
def q08():
    """#8 PA=8, PC=5, PD=6, CD=5. r=4 로 정확히 구성."""
    f = Fig('cs26_p03_q08', 15500, (-1.9, 12.5), (-1.9, 9.3))
    Pp = P(0, 0); O = P(8, 4); r = 4
    A = P(4.8, 6.4); B = P(8, 0); C = P(3, 4); D = P(6, 0); E = P(4.8, 1.6)
    f.circle(O, r); f.dot(O)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(C, D)
    dimf(f, Pp, A, (-1, 0.6), '8 cm', 26)
    dimf(f, Pp, C, (-1, 0.6), '5 cm', 10)
    dimf(f, Pp, D, (0, -1), '6 cm', 12)
    f.lab('A', A, -8, 8); f.lab('C', C, -5, 9)
    nm(f, 'P', Pp, P(1, 1), 9); f.lab('D', D, -3, -9); f.lab('B', B, 3, -9)
    f.lab('E', E, -9, -3); f.lab('O', O, 10, -3)
    f.ngd_on(Pp, D, 0.55) if False else f.ngd_on(P(0.5, 0), P(2.5, 0), 0.5)
    return f.save()


@reg
def q09():
    """#9 BD=6, CE=4, AF=3 (AB=9, AC=7, BC=10)."""
    f = Fig('cs26_p03_q09', 14500, (-2.6, 12.6), (-2.9, 8.4))
    B, C, A = P(0, 0), P(10, 0), P(6.6, np.sqrt(81 - 6.6 ** 2))
    I, r, D, E, F = tri_incircle(A, B, C)
    f.circle(I, r); f.poly([A, B, C]); f.dot(I)
    dimf(f, B, D, out_of(I, B, D), '6 cm', 12)
    dimf(f, E, C, (0, -1), '4 cm', 9)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 11); nm(f, 'C', C, I, 11)
    inlab(f, 'D', D, A, I, 17, 3); inlab(f, 'E', E, B, I, 17, 3); inlab(f, 'F', F, A, I, 17, 3)
    f.lab('O', I, 0, -10)
    f.ngd_on(P(0.5, 0), P(2.6, 0), 0.5)
    return f.save()


@reg
def q10():
    """#10 AD=7, BC=10, BQ=5, CD=9 (접선 길이 AP=3, BP=5, CQ=5, DR=4)."""
    f, V = _quad('cs26_p03_q10', (3, 5, 5, 4), [
        ('A', 'D', '7 cm', 12, 0.5, None), ('C', 'D', '9 cm', 12, 0.5, None),
        ('B', 'Q', '5 cm', 9, 0.5, (0, -1)), ('B', 'C', '10 cm', 24, 0.5, (0, -1))],
        14500, (-2.2, 2.2), (-2.0, 1.8), ngd=('BC', 0.78), tl='in')
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]()['name'])
