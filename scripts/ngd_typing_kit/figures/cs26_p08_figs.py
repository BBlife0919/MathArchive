# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 8쪽(원주각의 활용 정리 #1~#10) 그림. 실행: python3 cs26_p08_figs.py [q02 ...]  (없으면 전부)"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}
FS_A = 7.5


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def arcticks(f, c, r, deg, n=2, half=0.05, gap_deg=3.0):
    """원 위 호의 같은 길이 표시(방사 방향 짧은 눈금 n개)."""
    for i in range(n):
        a = deg + (i - (n - 1) / 2) * gap_deg
        f.seg(cp(c, r - half, a), cp(c, r + half, a), lw=0.8)


def incircle(A, B, C):
    a = np.hypot(*(B - C)); b = np.hypot(*(A - C)); c = np.hypot(*(A - B))
    I = (a * A + b * B + c * C) / (a + b + c)
    s = (a + b + c) / 2
    area = abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1])) / 2
    r = area / s
    def foot(p, q):
        u = unit(q - p)
        return p + u * np.dot(I - p, u)
    return I, r, foot(B, C), foot(A, C), foot(A, B)     # I, r, E(BC), F(AC), D(AB)


def tline(f, pt, c=P(0, 0), ext=0.6):
    u = unit(pt - c)
    t = np.array([-u[1], u[0]])
    return pt - t * ext, pt + t * ext


@reg
def q02():
    """#2 (1)(2) 접선과 현이 이루는 각."""
    f = Fig('cs26_p08_q02', 29000, (-1.5, 4.5), (-1.45, 1.3))
    # (1)
    O = P(0, 0)
    A = cp(O, 1, -90); B = cp(O, 1, 70); C = cp(O, 1, 190); T = P(0.85, -1)
    f.circle(O, 1)
    f.seg(P(-1.3, -1), P(1.3, -1))
    f.seg(A, B); f.seg(A, C); f.seg(B, C); f.dot(O); f.dot(T)
    f.angle(A, B, T, 0.22, '80°', fs=FS_A)
    f.angle(C, A, B, 0.2, '$x$')
    nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('A', A, 0, -10); f.lab('T', T, 0, -10)
    f.lab('O', O, 8, 8)
    f.lab('(1)', P(-1.4, 1.2), 0, 0)
    f.ngd_on(P(-1.28, -1), P(-0.3, -1), 0.5)
    # (2)
    O2 = P(3.1, 0)
    A = cp(O2, 1, -90); B = cp(O2, 1, 50); C = cp(O2, 1, 190); T = P(3.95, -1)
    f.circle(O2, 1)
    f.seg(P(1.8, -1), P(4.4, -1))
    f.seg(A, B); f.seg(A, C); f.seg(B, C); f.dot(O2); f.dot(T)
    f.angle(B, A, C, 0.24, '40°', fs=FS_A)
    f.angle(A, C, B, 0.28, '$x$')
    f.angle(A, B, T, 0.28, '70°', fs=FS_A)
    nm(f, 'B', B, O2, 9); nm(f, 'C', C, O2, 9)
    f.lab('A', A, 0, -10); f.lab('T', T, 0, -10)
    f.lab('O', O2, 8, 8)
    f.lab('(2)', P(1.6, 1.2), 0, 0)
    return f.save()


def rotpts(angles, off):
    return [cp(P(0, 0), 1, a + off) for a in angles]


@reg
def q03():
    """#3 (1)(2) 한 원 위의 네 점(원은 그리지 않음)."""
    f = Fig('cs26_p08_q03', 29000, (-1.3, 4.7), (-1.3, 1.25))
    # (1) 호 AB=70, BC=120, CD=90, DA=80 (ccw A,B,C,D). BC가 수평이 되도록 회전.
    off = 20
    A, B, C, D = [cp(P(0, 0), 1, a + off) for a in (120, 190, 310, 40)]
    def E_of(A, B, C, D):
        d1 = C - A; d2 = D - B
        M = np.array([d1, -d2]).T
        s = np.linalg.solve(M, B - A)
        return A + s[0] * d1
    E = E_of(A, B, C, D)
    f.poly([A, B, C, D]); f.seg(A, C); f.seg(B, D)
    f.angle(A, B, C, 0.2, '60°', fs=FS_A)
    f.angle(C, A, D, 0.22, '40°', fs=FS_A)
    f.angle(E, A, B, 0.14, '$x$')
    nm(f, 'A', A, E, 9); nm(f, 'B', B, E, 9); nm(f, 'C', C, E, 9); nm(f, 'D', D, E, 9)
    f.lab('(1)', P(-1.2, 1.05), 0, 0)
    f.ngd_on(B, C, 0.5)
    # (2) 호 AB=70, BC=60, CD=70, DA=160.
    sh = P(3.2, 0)
    A, B, C, D = [cp(P(0, 0), 1.2, a + 20) + sh for a in (150, 220, 280, 350)]
    E = E_of(A, B, C, D)
    f.poly([A, B, C, D]); f.seg(A, C); f.seg(B, D)
    f.angle(A, B, C, 0.22, '$x$')
    f.angle(E, B, C, 0.17, '110°', fs=FS_A)
    f.angle(C, A, D, 0.18, '80°', fs=FS_A)
    nm(f, 'A', A, E, 9); nm(f, 'B', B, E, 9); nm(f, 'C', C, E, 9); nm(f, 'D', D, E, 9)
    f.lab('(2)', P(1.8, 1.1), 0, 0)
    return f.save()


@reg
def q04():
    """#4 (1)(2) 원에 내접하는 사각형."""
    f = Fig('cs26_p08_q04', 29000, (-1.35, 4.65), (-1.35, 1.35))
    O = P(0, 0)
    f.circle(O, 1)
    A, B, C, D = [cp(O, 1, a) for a in (100, 210, 300, 20)]
    f.poly([A, B, C, D]); f.dot(O)
    f.angle(A, D, B, 0.2, '85°', fs=FS_A)
    f.angle(B, A, C, 0.2, '80°', fs=FS_A)
    f.angle(C, B, D, 0.18, '$x$')
    f.angle(D, C, A, 0.18, '$y$')
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('O', O, 0, -10)
    f.lab('(1)', P(-1.25, 1.2), 0, 0)
    f.ngd_on(B, C, 0.5)
    O2 = P(3.1, 0)
    f.circle(O2, 1)
    th = 190
    B2, C2, D2, A2 = [cp(O2, 1, a) for a in (th, th + 110, th + 180, th + 260)]
    f.poly([A2, B2, C2, D2]); f.dot(O2)
    f.angle(B2, A2, C2, 0.2, '75°', fs=FS_A)
    f.rightangle(C2, B2, D2, 0.1)
    f.angle(A2, B2, D2, 0.18, '$x$')
    f.angle(D2, C2, A2, 0.18, '$y$')
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9); nm(f, 'D', D2, O2, 9)
    f.lab('O', O2, 0, -10)
    f.lab('(2)', P(1.85, 1.2), 0, 0)
    return f.save()


@reg
def q05():
    """#5 접선 AT, 호 AB=호 BP."""
    f = Fig('cs26_p08_q05', 11000, (-1.45, 1.55), (-1.35, 1.25))
    O = P(0, 0)
    A = cp(O, 1, -90); B = cp(O, 1, 40); Pp = cp(O, 1, 170); T = P(0.9, -1)
    f.circle(O, 1)
    f.seg(P(-1.4, -1), P(1.5, -1))
    f.seg(A, B); f.seg(A, Pp); f.dot(O); f.dot(T)
    arcticks(f, O, 1, -25, 2); arcticks(f, O, 1, 105, 2)
    f.angle(A, B, T, 0.24, '65°', fs=FS_A)
    nm(f, 'B', B, O, 9); nm(f, 'P', Pp, O, 9)
    f.lab('A', A, 0, -10); f.lab('T', T, 0, -10); f.lab('O', O, 8, 8)
    f.ngd_on(P(-1.35, -1), P(-0.4, -1), 0.5)
    return f.save()


@reg
def q06():
    """#6 반직선 PT 접선, AB 지름, ∠ATP=36°."""
    f = Fig('cs26_p08_q06', 17500, (-1.35, 3.4), (-1.35, 1.2))
    O = P(0, 0); T = P(0, -1); Pp = P(1 / np.tan(np.radians(18)), -1)
    u = unit(Pp - O)
    A = O + u; B = O - u
    f.circle(O, 1)
    f.seg(P(-1.3, -1), Pp)
    f.seg(B, Pp); f.seg(T, A); f.seg(T, B); f.dot(O)
    f.angle(T, Pp, A, 0.6, None)
    f.lab('36°', T + P(1.0, 0.11), 0, 0, fs=FS_A)
    f.angle(A, B, T, 0.16, None)
    nm(f, 'B', B, O, 9)
    f.lab('A', A, 6, 8)
    f.lab('T', T, 0, -10); f.lab('P', Pp, 9, -2); f.lab('O', O, 6, 9)
    f.ngd_on(P(-1.25, -1), P(-0.3, -1), 0.5)
    return f.save()


@reg
def q07():
    """#7 직각삼각형 ABC의 내접원, BE=6, CE=4 (r=2)."""
    f = Fig('cs26_p08_q07', 15500, (-1.0, 11.0), (-1.7, 5.9))
    B = P(0, 0); C = P(10, 0); A = P(6.4, 4.8)
    I = P(6, 2); E = P(6, 0); D = B + 0.75 * (A - B); F = C + (4 / 6) * (A - C)
    f.circle(I, 2); f.poly([A, B, C]); f.dot(I)
    f.rightangle(A, B, C, 0.4)
    f.dimarc_pt(B, E, -1, '6 cm', pt=14); f.dimarc_pt(E, C, -1, '4 cm', pt=14)
    nm(f, 'A', A, I, 9); nm(f, 'B', B, I, 9); nm(f, 'C', C, I, 9)
    nm(f, 'D', D, I, 9); nm(f, 'F', F, I, 9)
    f.lab('E', E, 0, 9)
    f.lab('O', I, 9, 8)
    f.ngd_on(B, D, 0.4)
    return f.save()


@reg
def q08():
    """#8 ABC의 내접원 = DEF의 외접원, ∠A=60, ∠B=50."""
    f = Fig('cs26_p08_q08', 14500, (-0.6, 4.6), (-0.6, 3.95))
    Bp = P(0, 0); Cp = P(4, 0)
    AB = 4 * np.sin(np.radians(70)) / np.sin(np.radians(60))
    A = P(AB * np.cos(np.radians(50)), AB * np.sin(np.radians(50)))
    I, r, E, F, D = incircle(A, Bp, Cp)
    f.circle(I, r); f.poly([A, Bp, Cp]); f.poly([D, E, F])
    f.angle(A, Bp, Cp, 0.45, '60°', fs=FS_A)
    f.angle(Bp, A, Cp, 0.5, '50°', fs=FS_A)
    f.angle(E, F, Cp, 0.28, None)
    nm(f, 'A', A, I, 9); nm(f, 'B', Bp, I, 9); nm(f, 'C', Cp, I, 9)
    nm(f, 'D', D, I, 9); nm(f, 'F', F, I, 9)
    f.lab('E', E, 0, -10)
    f.ngd_on(A, Bp, 0.3)
    return f.save()


def para(f, p, q, frac=0.5, s=0.09):
    """평행 표시(화살표 모양 >)."""
    p, q = np.array(p, float), np.array(q, float)
    m = p + frac * (q - p); u = unit(q - p); n = np.array([-u[1], u[0]])
    for a in (m - u * s * 0.5, ):
        f.seg(a + u * s * 0.7, a - n * s * 0.6 - u * 0.0, lw=0.9)
        f.seg(a + u * s * 0.7, a + n * s * 0.6 - u * 0.0, lw=0.9)
    return None


@reg
def q09():
    """#9 접선 PA, PB, □APBC 평행사변형 (∠P=60)."""
    global f
    f = Fig('cs26_p08_q09', 13500, (-2.45, 1.55), (-1.3, 1.3))
    O = P(0, 0); Pp = P(-2, 0); A = P(-0.5, np.sqrt(3) / 2); B = P(-0.5, -np.sqrt(3) / 2); C = P(1, 0)
    f.circle(O, 1)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(A, C); f.seg(B, C); f.dot(O)
    for p, q in ((Pp, A), (B, C)):
        pass
    def chev(p, q, frac):
        p, q = np.array(p, float), np.array(q, float)
        m = p + frac * (q - p); u = unit(q - p); n = np.array([-u[1], u[0]]); s = 0.09
        f.seg(m - u * s - n * s * 0.7, m, lw=0.9); f.seg(m - u * s + n * s * 0.7, m, lw=0.9)
    chev(Pp, A, 0.55); chev(B, C, 0.55); chev(Pp, B, 0.55); chev(A, C, 0.55)
    f.angle(Pp, A, B, 0.35, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('P', Pp, -9, 0); f.lab('O', O, -2, -12)
    f.ngd_on(Pp, A, 0.3)
    return f.save()


@reg
def q10():
    """#10 통나무 단면: 현 BC=80, 높이 AD=20 (r=50)."""
    f = Fig('cs26_p08_q10', 16500, (-1.45, 1.5), (-0.55, 0.8))
    B = P(-1, 0); C = P(1, 0); D = P(0, 0); A = P(0, 0.5); Oc = P(0, -0.75); r = 1.25
    a0 = np.degrees(np.arcsin(0.75 / 1.25)); lo = a0; hi = 180 - a0
    pts = [cp(Oc, r, t) for t in np.linspace(lo, hi, 80)]
    f.poly(pts, fill='#B8B8B8', lw=LW)
    f.seg(B, C); f.seg(A, D)
    f.rightangle(D, A, C, 0.07)
    f.ticks(B, D, 1, 0.07); f.ticks(D, C, 1, 0.07)
    dimo(f, A, D, (-1, 0), '20 cm', 24)
    dimo(f, B, D, (0, -1), '40 cm', 12)
    nm(f, 'A', A, D, 9); nm(f, 'B', B, D, 9); nm(f, 'C', C, D, 9)
    f.lab('D', D, 4, -10)
    f.ngd_on(D, C, 0.7)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
