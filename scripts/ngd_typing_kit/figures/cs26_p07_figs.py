# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 7쪽(원주각의 활용) 그림. 실행: python3 cs26_p07_figs.py [p07_q01 ...]  (없으면 전부)
#1은 손글씨 낙서를 제외하고 인쇄된 그림(원에 내접하는 사각형 ABCD)만 그린다.
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


FS_A = 7.5


def line_dot(f, p, name, dx=0, dy=-10):
    f.dot(p)
    f.lab(name, p, dx, dy)


def tangent(f, A, O, a, b):
    """A에서의 접선: 방향 t(반지름에 수직). A + a*t ~ A + b*t."""
    r = unit(A - O)
    t = np.array([-r[1], r[0]])
    f.seg(A + a * t, A + b * t)
    return t


@reg
def p07_q01():
    """#1 원에 내접하는 사각형 ABCD (네 각에 호 표시)."""
    f = Fig('cs26_p07_q01', 11500, (-1.4, 1.4), (-1.35, 1.35))
    O = P(0, 0)
    A, D, C, B = cp(O, 1, 120), cp(O, 1, 50), cp(O, 1, 320), cp(O, 1, 215)
    f.circle(O, 1)
    f.poly([A, B, C, D])
    f.angle(A, B, D, 0.16, None); f.angle(B, A, C, 0.16, None)
    f.angle(C, B, D, 0.16, None); f.angle(D, A, C, 0.16, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.ngd_on(B, C, 0.5)
    return f.save()


@reg
def p07_q02():
    """#2 (1)(2) 내접사각형과 외각."""
    f = Fig('cs26_p07_q02', 29000, (-1.5, 6.2), (-1.5, 1.4))
    # (1)
    O = P(0, 0)
    A, D, C, B = cp(O, 1, 127), cp(O, 1, 25), cp(O, 1, 325), cp(O, 1, 215)
    E = P(1.55, B[1])
    f.circle(O, 1)
    f.poly([A, B, C, D])
    f.seg(C, E); f.dot(E)
    f.angle(A, D, B, 0.22, '85°', fs=FS_A)
    f.angle(C, D, E, 0.20, '$x$°', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('E', E, 0, -10)
    f.lab('(1)', P(-1.3, 1.25), 0, 0)
    f.ngd_on(A, D, 0.5)
    # (2)
    O2 = P(3.7, 0)
    A2, D2, B2, C2 = cp(O2, 1, 152), cp(O2, 1, 62), cp(O2, 1, 222), cp(O2, 1, 318)
    E2 = P(O2[0] + 1.55, B2[1])
    f.circle(O2, 1)
    f.poly([A2, B2, C2, D2]); f.seg(A2, C2 * 0 + B2 * 0 + D2) if False else None
    f.seg(B2, D2)
    f.seg(B2 + np.array([-0.25, 0]), E2) if False else f.seg(C2, E2)
    f.dot(E2)
    f.angle(D2, A2, B2, 0.26, '35°', fs=FS_A)
    f.angle(B2, A2, D2, 0.28, '$x$°', fs=FS_A)
    f.angle(C2, D2, E2, 0.24, None)
    f.lab('100°', C2 + P(0.58, 0.24), 0, 0, fs=FS_A)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9); nm(f, 'D', D2, O2, 9)
    f.lab('E', E2, 0, -10)
    f.lab('(2)', P(2.3, 1.25), 0, 0)
    f.ngd_on(B2 + P(-0.0, 0), C2, 0.62)
    return f.save()


@reg
def p07_q03():
    """#3 접선 AT, 40°=∠BAT, 25°=접선 아래쪽과 AC가 이루는 각, x=∠ACB, y=∠ABC."""
    f = Fig('cs26_p07_q03', 12500, (-1.35, 2.2), (-1.55, 1.3))
    O = P(0, 0)
    A, B, C = cp(O, 1, -10), cp(O, 1, 70), cp(O, 1, -60)
    f.circle(O, 1); f.dot(O)
    f.seg(B, A); f.seg(B, C); f.seg(C, A)
    t = unit(np.array([-(A - O)[1], (A - O)[0]]))
    T = A + 0.55 * t
    f.seg(A - 1.05 * t, A + 0.95 * t)
    f.dot(T)
    f.lab('T', T, 9, 4)
    f.angle(A, T, B, 0.20, None)
    f.lab('40°', A + 0.32 * t + np.array([0.28, 0.0]), 0, 0, fs=FS_A)
    f.angle(A, A - t, C, 0.18, None)
    f.lab('25°', A - 0.45 * t + np.array([0.30, 0.0]), 0, 0, fs=FS_A)
    f.angle(B, A, C, 0.22, None)
    f.lab('$y$°', B + P(-0.20, -0.30), 0, 0, fs=FS_A)
    f.angle(C, A, B, 0.24, '$x$°', fs=FS_A)
    nm(f, 'A', A, O, 11); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('O', O, 0, -10)
    f.ngd_on(B, C, 0.5)
    print('   q03: BAT, angle(A-t) check', np.degrees(np.arccos(np.dot(unit(B - A), t))), np.degrees(np.arccos(np.dot(unit(C - A), -t))))
    return f.save()


@reg
def p07_q04():
    """#4 (1)(2) 내접사각형."""
    f = Fig('cs26_p07_q04', 29000, (-1.5, 6.4), (-1.5, 1.4))
    # (1) A,D,B,C ; 각 D=95, C=88, x=∠A, y=∠B
    O = P(0, 0)
    A, B, C, D = cp(O, 1, 124), cp(O, 1, 228), cp(O, 1, 314), cp(O, 1, 52)
    f.circle(O, 1); f.dot(O)
    f.poly([A, B, C, D])
    f.angle(A, D, B, 0.18, '$x$°', fs=FS_A)
    f.angle(D, A, C, 0.18, '95°', fs=FS_A)
    f.angle(B, A, C, 0.20, '$y$°', fs=FS_A)
    f.angle(C, B, D, 0.18, '88°', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('O', O, 0, -10)
    f.lab('(1)', P(-1.3, 1.25), 0, 0)
    f.ngd_on(B, C, 0.5)
    # (2)
    O2 = P(4.0, 0)
    A2, D2, B2, C2 = cp(O2, 1, 104), cp(O2, 1, 66), cp(O2, 1, 216), cp(O2, 1, 324)
    E2 = P(O2[0] + 1.55, B2[1])
    f.circle(O2, 1); f.dot(O2)
    f.poly([A2, B2, C2, D2]); f.seg(C2, E2); f.dot(E2)
    f.angle(A2, D2, B2, 0.20, None); f.angle(D2, A2, C2, 0.22, None)
    f.lab('105°', A2 + P(0.12, -0.42), 0, 0, fs=FS_A); f.lab('$x$°', D2 + P(-0.05, -0.42), 0, 0, fs=FS_A)
    f.angle(B2, A2, C2, 0.26, '70°', fs=FS_A)
    f.angle(C2, D2, E2, 0.26, '$y$°', fs=FS_A)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9); nm(f, 'D', D2, O2, 9)
    f.lab('E', E2, 0, -10)
    f.lab('O', O2, 0, -10)
    f.lab('(2)', P(2.6, 1.25), 0, 0)
    f.ngd_on(B2, C2, 0.5)
    return f.save()


@reg
def p07_q05():
    """#5 □ABCD 원에 내접, ∠BCD=120°, 호 AB=호 AD, BD=8cm."""
    f = Fig('cs26_p07_q05', 12500, (-1.5, 1.5), (-1.4, 1.4))
    O = P(0, 0)
    A, B, C, D = cp(O, 1, 90), cp(O, 1, 210), cp(O, 1, 270), cp(O, 1, 330)
    f.circle(O, 1)
    f.fill_poly([A, B, D], '#B8B8B8')
    f.poly([A, B, D]); f.seg(B, C); f.seg(C, D); f.dot(O)
    dimo(f, B, D, (0, 1), '8 cm', 12)
    f.angle(C, B, D, 0.18, '120°', fs=FS_A)
    arcticks(f, O, 1, 150, 1)
    arcticks(f, O, 1, 30, 1)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 10); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 10)
    f.lab('O', O, 0, 10)
    f.ngd_on(A, B, 0.5)
    return f.save()


def arcticks(f, c, r, deg, n=1, half=0.07, gap=4.0, lw=0.8):
    for i in range(n):
        a = deg + (i - (n - 1) / 2.0) * gap
        p1, p2 = cp(c, r - half, a), cp(c, r + half, a)
        f.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='k', lw=lw, zorder=3)


def right(f, v, p1, p2, s=0.08):
    f.rightangle(v, p1, p2, s)


@reg
def p07_q06():
    """#6 (1)~(4) 네 점 A, B, C, D 그림(원본 인쇄 그림, 2x2 배치)."""
    f = Fig('cs26_p07_q06', 19000, (-0.9, 9.8), (-0.6, 6.3))
    # (1)
    o = P(0.1, 3.5)
    A, D, B, C = o + P(0.16, 1.63), o + P(2.61, 1.98), o + P(0, 0), o + P(3.42, 0)
    f.seg(A, B); f.seg(A, C); f.seg(B, D); f.seg(D, C); f.seg(B, C)
    f.angle(A, B, C, 0.40, '70°', fs=FS_A)
    f.angle(D, B, C, 0.40, '75°', fs=FS_A)
    nm(f, 'A', A, B, 10); nm(f, 'D', D, B, 10); nm(f, 'B', B, C, 10); nm(f, 'C', C, B, 10)
    f.lab('(1)', P(-0.45, 5.6), 0, 0)
    f.ngd_on(B, C, 0.5)
    # (2): BC를 지름으로 하는 원 위의 A, D (직각)
    B2 = P(5.4, 3.5); C2 = P(8.9, 3.5); M = (B2 + C2) / 2; r = 1.75
    A2, D2 = cp(M, r, 115), cp(M, r, 52)
    f.seg(A2, B2); f.seg(A2, C2); f.seg(B2, D2); f.seg(D2, C2); f.seg(B2, C2)
    f.rightangle(A2, B2, C2, 0.16); f.rightangle(D2, B2, C2, 0.16)
    nm(f, 'A', A2, M, 10); nm(f, 'D', D2, M, 10); nm(f, 'B', B2, M, 10); nm(f, 'C', C2, M, 10)
    f.lab('(2)', P(5.0, 5.6), 0, 0)
    # (3): AC와 BD가 수직, ∠ABD=35°, ∠BDC=60°
    L = 3.0
    B3 = P(0.1, 0.0); C3 = B3 + P(L, 0)
    th = np.radians(44)
    dB = P(np.cos(th), np.sin(th))
    u79 = P(np.cos(np.radians(79)), np.sin(np.radians(79)))
    a = np.dot(C3 - B3, dB) / np.dot(u79, dB)
    A3 = B3 + a * u79
    BD = L * np.sin(np.radians(76)) / np.sin(np.radians(60))
    D3 = B3 + BD * dB
    X = intersect(A3, C3, B3, D3)
    f.seg(A3, B3); f.seg(A3, C3); f.seg(B3, D3); f.seg(D3, C3); f.seg(B3, C3)
    f.rightangle(X, A3, D3, 0.12)
    f.angle(B3, A3, D3, 0.50, '35°', tr=0.85, fs=7)
    f.angle(D3, B3, C3, 0.40, '60°', fs=FS_A)
    nm(f, 'A', A3, X, 10); nm(f, 'D', D3, X, 10); nm(f, 'B', B3, X, 10); nm(f, 'C', C3, X, 10)
    f.lab('(3)', P(-0.45, 3.0), 0, 0)
    # (4): ∠ADC=75°, ∠ACD=40°, ∠DBC=65°(A, B, C, D가 한 원 위)
    o4 = P(5.0, 0.0)
    C4 = o4 + P(2.5, 0); D4 = o4 + P(1.5, 2.75)
    angDC = np.arctan2(*(C4 - D4)[::-1]); angCD = np.arctan2(*(D4 - C4)[::-1])
    dA = P(np.cos(angDC - np.radians(75)), np.sin(angDC - np.radians(75)))
    cA = P(np.cos(angCD + np.radians(40)), np.sin(angCD + np.radians(40)))
    A4 = intersect(D4, D4 + dA, C4, C4 + cA)
    ax_, ay_ = A4; bx_, by_ = D4; cx_, cy_ = C4
    dd = 2 * (ax_ * (by_ - cy_) + bx_ * (cy_ - ay_) + cx_ * (ay_ - by_))
    ux = ((ax_**2 + ay_**2) * (by_ - cy_) + (bx_**2 + by_**2) * (cy_ - ay_) + (cx_**2 + cy_**2) * (ay_ - by_)) / dd
    B4 = P(2 * ux - C4[0], C4[1])
    f.seg(D4, A4); f.seg(D4, B4); f.seg(D4, C4); f.seg(A4, C4); f.seg(B4, C4)
    f.angle(D4, A4, C4, 0.55, None)
    f.lab('75°', D4 + P(0.0, -1.02), 0, 0, fs=7)
    f.angle(B4, D4, C4, 0.40, '65°', fs=FS_A)
    f.angle(C4, A4, D4, 0.60, '40°', fs=FS_A)
    nm(f, 'D', D4, A4, 10); nm(f, 'A', A4, C4, 10); nm(f, 'B', B4, D4, 10); nm(f, 'C', C4, B4, 10)
    f.lab('(4)', P(5.0, 3.0), 0, 0)
    f.ngd_on(B4, C4, 0.5)
    print('   q06(4): B,A', B4, A4)
    return f.save()


def intersect(p1, p2, p3, p4):
    M = np.array([[p2[0] - p1[0], -(p4[0] - p3[0])], [p2[1] - p1[1], -(p4[1] - p3[1])]])
    s, t = np.linalg.solve(M, np.array([p3[0] - p1[0], p3[1] - p1[1]]))
    return p1 + s * (p2 - p1)



@reg
def p07_q07():
    """#7 (1)(2) 접선 AT와 현이 이루는 각."""
    f = Fig('cs26_p07_q07', 29000, (-1.5, 6.0), (-1.75, 1.45))
    # (1): A=-90, B=50, C=178, ∠BAT=70
    O = P(0, 0)
    A, B, C = cp(O, 1, -90), cp(O, 1, 50), cp(O, 1, 178)
    f.circle(O, 1); f.dot(O)
    f.seg(C, B); f.seg(C, A); f.seg(A, B)
    f.seg(A + P(-1.2, 0), A + P(1.7, 0))
    T = A + P(1.35, 0); f.dot(T); f.lab('T', T, 0, -10)
    f.angle(A, T, B, 0.20, '70°', fs=FS_A)
    f.angle(C, A, B, 0.22, '$x$', fs=FS_A)
    nm(f, 'A', A, O, 10); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('O', O, 0, -11)
    f.lab('(1)', P(-1.35, 1.25), 0, 0)
    f.ngd_on(A + P(-1.2, 0), A, 0.5)
    # (2): A=-95, B=-15, C=105, ∠ACB=40, 80°=∠(좌측 접선, AC)
    O2 = P(3.9, 0)
    A2, B2, C2 = cp(O2, 1, -95), cp(O2, 1, -15), cp(O2, 1, 105)
    f.circle(O2, 1); f.dot(O2)
    f.seg(C2, A2); f.seg(C2, B2); f.seg(A2, B2)
    t = unit(P(np.sin(np.radians(-95)) * -1, np.cos(np.radians(-95))))   # 접선 방향
    f.seg(A2 - 1.35 * t, A2 + 1.35 * t)
    T2 = A2 + 1.05 * t; f.dot(T2); f.lab('T', T2, 0, -10)
    f.angle(C2, A2, B2, 0.24, '40°', fs=FS_A)
    f.angle(A2, A2 - t, C2, 0.22, '80°', fs=FS_A)
    f.angle(A2, C2, B2, 0.26, '$x$°', fs=FS_A)
    nm(f, 'A', A2, O2, 10); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9)
    f.lab('O', O2, 10, 0)
    f.lab('(2)', P(2.5, 1.25), 0, 0)
    return f.save()


@reg
def p07_q08():
    """#8 접선 AT, ∠ABC=100°, ∠ACT=30°."""
    f = Fig('cs26_p07_q08', 14500, (-2.0, 1.6), (-1.5, 1.4))
    O = P(0, 0)
    A, C, B = cp(O, 1, -90), cp(O, 1, 70), cp(O, 1, -15)
    xT = C[0] - (C[1] + 1) / np.tan(np.radians(50))
    T = P(xT, -1)
    f.circle(O, 1); f.dot(O)
    f.seg(T, A); f.seg(T, C); f.seg(C, A); f.seg(C, B); f.seg(A, B)
    f.angle(B, A, C, 0.20, '100°', fs=FS_A)
    f.angle(C, T, A, 0.30, '30°', tr=0.66, fs=7)
    f.angle(T, C, A, 0.30, None)
    nm(f, 'A', A, O, 10); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('T', T, -4, -10)
    f.lab('O', O, -11, 0)
    f.ngd_on(T, A, 0.3)
    return f.save()


@reg
def p07_q09():
    """#9 접선 CA, BC는 중심 O를 지남, ∠BAT=60°."""
    f = Fig('cs26_p07_q09', 14500, (-2.3, 1.7), (-1.5, 1.35))
    O = P(0, 0)
    A = P(0, -1); B = cp(O, 1, 30); D = cp(O, 1, 210); C = P(-2 * np.cos(np.radians(30)), -1)
    T = P(0.8, -1)
    f.circle(O, 1); f.dot(O)
    f.seg(C, P(1.25, -1)); f.seg(C, B); f.seg(A, B); f.dot(T)
    f.angle(A, T, B, 0.20, '60°', fs=FS_A)
    f.angle(C, A, B, 0.45, None)
    nm(f, 'A', A, O, 10); nm(f, 'B', B, O, 9); f.lab('D', D, -11, 6)
    f.lab('C', C, -9, -4)
    f.lab('T', T, 0, -10)
    f.lab('O', O, 0, 10)
    f.ngd_on(C, A, 0.4)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
