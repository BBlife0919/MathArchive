# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 4쪽(원과 접선 정리) 그림. 실행: python3 cs26_p04_figs.py [q02 ...]  (없으면 전부)
그림 파일명: cs26_p04_qMM.  #1 은 그림 없음.
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def fit(name, w_hwp, xmin, xmax, ymin, ymax, mpt=12):
    """도형 범위(데이터 단위)와 여백(pt)으로 Fig 생성."""
    wpt = w_hwp / 100.0
    ppu = (wpt - 2 * mpt) / (xmax - xmin)
    m = mpt / ppu
    return Fig(name, w_hwp, (xmin - m, xmax + m), (ymin - m, ymax + m))


def outv(p, q, ref):
    """선분 pq에 수직이고 ref 반대쪽을 향하는 벡터."""
    u = np.subtract(q, p)
    n = np.array([-u[1], u[0]])
    mid = (np.array(p) + np.array(q)) / 2
    if np.dot(n, mid - np.array(ref)) < 0:
        n = -n
    return n


def dm(f, p, q, ref, text, pt=15):
    """길이 표시(점선 곡선 사이 숫자) — ref 반대쪽(바깥)으로."""
    dimo(f, p, q, outv(p, q, ref), text, pt)


def lb(f, text, p, vec, d=9, **kw):
    v = np.array(vec, float)
    v = v / np.hypot(*v)
    f.lab(text, p, v[0] * d, v[1] * d, **kw)


def tang_poly(ts):
    """내접원(반지름 r, 중심 원점)을 가진 볼록다각형. ts[i] = 꼭짓점 i의 접선 길이(반시계 순서).
    반환: r, 꼭짓점 리스트, 접점 리스트(T[i]=꼭짓점 i와 i+1 사이 변의 접점)."""
    lo, hi = 1e-6, 1e4
    for _ in range(200):
        r = (lo + hi) / 2
        if sum(np.arctan(r / t) for t in ts) > (len(ts) - 2) * np.pi / 2:
            hi = r
        else:
            lo = r
    n = len(ts)
    phi = [np.pi - 2 * np.arctan(r / t) for t in ts]
    ang0 = 0.0
    start = [ang0]
    for i in range(n - 1):
        start.append(start[-1] + phi[i])
    V, T = [], []
    for i in range(n):
        a0, a1 = start[i], start[i] + phi[i]
        mid = (a0 + a1) / 2
        d = np.hypot(r, ts[i])
        V.append(P(d * np.cos(mid), d * np.sin(mid)))
        T.append(P(r * np.cos(a1), r * np.sin(a1)))     # 변 i(꼭짓점 i -> i+1)의 접점
    return r, V, T


def rotate_all(pts, deg):
    return [rot(p, deg) for p in pts]


@reg
def q02():
    """#2 두 접선 PA, PB (PA=6, ∠APB=50°). 접선은 접점 너머로 연장, 현 AB."""
    f = fit('cs26_p04_q02', 15500, -1.2, 9.6, -4.4, 4.4, 14)
    pa = np.radians(25)
    r = 6 * np.tan(pa); OP = 6 / np.cos(pa)
    Pp = P(0, 0); O = P(OP, 0)
    ang = np.radians(180 - (90 - 25))      # ∠POA = 65°
    A = O + r * P(np.cos(np.radians(115)), np.sin(np.radians(115)))
    B = O + r * P(np.cos(np.radians(245)), np.sin(np.radians(245)))
    f.circle(O, r)
    ea = Pp + (A - Pp) * 1.5; eb = Pp + (B - Pp) * 1.5
    f.seg(Pp, ea); f.seg(Pp, eb); f.seg(A, B); f.dot(O)
    dm(f, Pp, A, B, '6 cm', 15)
    f.angle(Pp, A, B, 1.3, '50°', fs=FS_A if False else 7.5)
    f.angle(A, Pp, B, 0.55, '$x$', fs=8)
    nm(f, 'P', Pp, O, 10); lb(f, 'A', A, (0, 1), 9); lb(f, 'B', B, (0, -1), 9)
    f.lab('O', O, 10, -4)
    f.ngd_on(A + (ea - A) * 0.35, A + (ea - A) * 0.95, 0.5)
    return f.save()


@reg
def q03():
    """#3 △ABC 내접원 O, AP=4, BQ=8, CR=5."""
    ts = [8, 5, 4]                                  # B, C, A (반시계)
    r, V, T = tang_poly(ts)
    ang = np.degrees(np.arctan2(V[1][1] - V[0][1], V[1][0] - V[0][0]))
    V = rotate_all(V, -ang); T = rotate_all(T, -ang)
    Bp, Cp, Ap = V
    Q, R, Pp = T                                    # T0=BC접점(Q), T1=CA접점(R), T2=AB접점(P)
    O = rot(P(0, 0), 0)
    O = P(0, 0)
    # 원점이 회전된 도형의 내심이므로 그대로 사용
    f = fit('cs26_p04_q03', 15500, min(Bp[0], Ap[0]) - 0.2, Cp[0] + 0.2, Bp[1] - 0.2, Ap[1] + 0.2, 16)
    f.circle(O, r)
    f.poly([Ap, Bp, Cp]); f.dot(O)
    dm(f, Ap, Pp, O, '4 cm', 16)
    dm(f, Bp, Q, O, '8 cm', 14)
    dm(f, Cp, R, O, '5 cm', 16)
    lb(f, 'A', Ap, (0, 1), 9); lb(f, 'B', Bp, (-1, -0.6), 9); lb(f, 'C', Cp, (1, -0.6), 9)
    lb(f, 'P', Pp, (-1, 0.5), 9); lb(f, 'Q', Q, (0, -1), 9); lb(f, 'R', R, (1, 0.5), 9)
    f.lab('O', O, 0, -10)
    f.ngd_on(Bp, Pp, 0.4)
    return f.save()


@reg
def q04():
    """#4 □ABCD 외접원, AB=8, BC=10, CD=12 (AD=10)."""
    a = 3.15
    ts = [8 - a, a + 2, 10 - a, a]                  # B, C, D, A (반시계)
    r, V, T = tang_poly(ts)
    ang = np.degrees(np.arctan2(V[1][1] - V[0][1], V[1][0] - V[0][0]))
    V = rotate_all(V, -ang); T = rotate_all(T, -ang)
    Bp, Cp, Dp, Ap = V
    O = P(0, 0)
    xs = [v[0] for v in V]; ys = [v[1] for v in V]
    f = fit('cs26_p04_q04', 12500, min(xs), max(xs), min(ys), max(ys), 34)
    f.circle(O, r)
    f.poly([Ap, Bp, Cp, Dp]); f.dot(O)
    dm(f, Ap, Bp, O, '8 cm', 18)
    dm(f, Bp, Cp, O, '10 cm', 14)
    dm(f, Cp, Dp, O, '12 cm', 18)
    lb(f, 'A', Ap, (-1, 0.6), 9); lb(f, 'B', Bp, (-1, -0.8), 9); lb(f, 'C', Cp, (1, -0.8), 9); lb(f, 'D', Dp, (0.6, 1), 9)
    f.lab('O', O, 0, -10)
    f.ngd_on(Ap, Dp, 0.82)
    return f.save()


@reg
def q05():
    """#5 PA, PB, CD 접선. AC=3, CD=7, PC=10 (PA=PB=13, PD=9)."""
    r = np.sqrt(13 * 3 * 6 * 4) / 6
    OP = np.hypot(13, r)
    th = np.arccos(r / OP)
    O = P(0, 0); Pp = P(OP, 0)
    A = r * P(np.cos(th), np.sin(th)); B = r * P(np.cos(th), -np.sin(th))
    C = Pp + (A - Pp) * 10 / 13
    D = Pp + (B - Pp) * 9 / 13
    u = (D - C) / np.hypot(*(D - C))
    E = C + u * 3
    assert abs(np.hypot(*E) - r) < 1e-6, np.hypot(*E)
    f = fit('cs26_p04_q05', 19000, -r, Pp[0], -r - 0.3, r + 0.3, 14)
    f.circle(O, r)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(C, D); f.dot(O)
    dm(f, A, C, Pp + (Pp - O), '3 cm', 15) if False else dimo(f, A, C, (0, 1), '3 cm', 14)
    dimo(f, C, Pp, (0.3, 1), '10 cm', 15)
    dimo(f, C, D, (1, 0), '7 cm', 15)
    lb(f, 'A', A, (-0.6, 1), 9); lb(f, 'B', B, (-0.6, -1), 9)
    lb(f, 'C', C, (1, 1), 15); lb(f, 'D', D, (0.2, -1), 9); lb(f, 'E', E, (-1, 0), 9)
    lb(f, 'P', Pp, (1, 0), 10)
    f.lab('O', O, 0, -10)
    f.ngd_on(B, D, 0.7)
    return f.save()


@reg
def q06():
    """#6 두 접선 PA, PB, ∠APB=60°, AP=2√3 (r=2), 색칠=부채꼴 OAB."""
    f = fit('cs26_p04_q06', 19500, -4.8, 2.4, -2.4, 2.4, 14)
    O = P(0, 0); Pp = P(-4, 0)
    A = cp(O, 2, 120); B = cp(O, 2, 240)
    f.wedge_fill(O, 2, 120, 240, '#B8B8B8')
    f.circle(O, 2)
    f.seg(Pp, A); f.seg(Pp, B); f.seg(O, A); f.seg(O, B); f.dot(O)
    dimo(f, Pp, A, (-0.6, 1), '$2\\sqrt{3}$ cm', 14)
    f.angle(Pp, A, B, 0.8, '60°', fs=7.5)
    lb(f, 'A', A, (0, 1), 9); lb(f, 'B', B, (0, -1), 9); nm(f, 'P', Pp, O, 10)
    f.lab('O', O, 10, 0)
    f.ngd_on(Pp, B, 0.5)
    return f.save()


@reg
def q07():
    """#7 동심원 5 cm, 3 cm, 현 AB가 작은 원 접선(접점 H)."""
    f = fit('cs26_p04_q07', 11500, -5, 5, -5, 5, 14)
    O = P(0, 0); H = P(0, -3); A = P(-4, -3); B = P(4, -3)
    f.circle(O, 5); f.circle(O, 3)
    f.seg(A, B); f.seg(O, A); f.seg(O, H); f.dot(O)
    dimo(f, O, A, (-1, 1), '5 cm', 22)
    dimo(f, H, O, (1, 0), '3 cm', 16)
    lb(f, 'A', A, (-1, -0.6), 9); lb(f, 'B', B, (1, -0.6), 9); lb(f, 'H', H, (0, -1), 9)
    f.lab('O', O, 0, 10)
    f.ngd_on(P(1.0, -3), B, 0.6)
    return f.save()


@reg
def q08():
    """#8 반원 O, AD=4, BC=9 (r=6), AD·BC·CD 접선."""
    f = fit('cs26_p04_q08', 13500, 0, 12, 0, 9, 38)
    A = P(0, 0); B = P(12, 0); O = P(6, 0); D = P(0, 4); C = P(12, 9)
    u = (C - D) / np.hypot(*(C - D))
    E = D + u * np.dot(O - D, u)
    f.arc(O, 6, 0, 180)
    f.seg(A, B); f.seg(A, D); f.seg(B, C); f.seg(D, C); f.dot(O)
    f.rightangle(A, B, D, 0.5); f.rightangle(B, A, C, 0.5)
    dimo(f, A, D, (-1, 0), '4 cm', 17)
    dimo(f, B, C, (1, 0), '9 cm', 17)
    lb(f, 'A', A, (-0.7, -1), 9); lb(f, 'B', B, (0.7, -1), 9); lb(f, 'O', O, (0, -1), 9)
    lb(f, 'D', D, (-1, 0.6), 9); lb(f, 'C', C, (0.5, 1), 9); lb(f, 'E', E, (-0.3, 1), 9)
    f.ngd_on(A, P(4.5, 0), 0.5)
    return f.save()


@reg
def q09():
    """#9 동심원, 작은 원의 접선이 큰 원과 만나는 점 A, B (AB=14). 색칠 = 두 원 사이."""
    r = 3.0; R = np.hypot(r, 7)
    f = fit('cs26_p04_q09', 13500, -R, R, -R, R, 12)
    O = P(0, 0); A = P(-7, -r); B = P(7, -r)
    f.circle(O, R, fill='#B8B8B8')
    f.circle(O, r, fill='white', z=2.2)
    f.seg(A, B, z=3); f.dot(O)
    dimo(f, A, B, (0, -1), '14 cm', 12)
    lb(f, 'A', A, (-1, 0.3), 9); lb(f, 'B', B, (1, 0.3), 9)
    f.lab('O', O, 10, 4)
    f.ngd_on(P(-3.5, -r), P(-1.0, -r), 0.5) if False else f.ngd_on(P(-5.6, -r), P(-3.0, -r), 0.5)
    return f.save()


@reg
def q10():
    """#10 반원 O(지름 AB, 접선 AD=6, BC=9, CD)."""
    h = np.sqrt(6 * 9)                               # 반지름 = 3√6
    f = fit('cs26_p04_q10', 9500, -0.1, 9, -h, h, 30)
    A = P(0, h); B = P(0, -h); D = P(6, h); C = P(9, -h); O = P(0, 0)
    f.arc(O, h, -90, 90)
    f.seg(A, B); f.seg(A, D); f.seg(B, C); f.seg(D, C); f.dot(O)
    dimo(f, A, D, (0, 1), '6 cm', 14)
    dimo(f, B, C, (0, -1), '9 cm', 14)
    lb(f, 'A', A, (-1, 0.5), 9); lb(f, 'D', D, (1, 0.5), 9); lb(f, 'B', B, (-1, -0.5), 9); lb(f, 'C', C, (1, -0.5), 9)
    f.lab('O', O, -10, 0)
    f.ngd_on(D, C, 0.8)
    return f.save()


@reg
def q11():
    """#11 ∠B=90° 직각삼각형 ABC(3,4,5)의 내접원 O(r=1), AF=2, CF=3."""
    f = fit('cs26_p04_q11', 12500, -0.2, 4.2, 0, 3, 22)
    B = P(0, 0); C = P(4, 0); A = P(0, 3); O = P(1, 1)
    D = P(0, 1); E = P(1, 0); F = P(1.6, 1.8)
    f.circle(O, 1)
    f.poly([A, B, C]); f.dot(O)
    f.rightangle(B, A, C, 0.18)
    dimo(f, A, F, (0.6, 0.8), '2 cm', 15)
    dimo(f, F, C, (0.6, 0.8), '3 cm', 15)
    lb(f, 'A', A, (0, 1), 9); lb(f, 'B', B, (-1, -1), 9); lb(f, 'C', C, (1, -0.5), 9)
    lb(f, 'D', D, (-1, 0), 9); lb(f, 'E', E, (0, -1), 9); lb(f, 'F', F, (1, 1), 15)
    f.lab('O', O, 9, 0)
    f.ngd_on(B, P(0.0, 2.0), 0.55) if False else f.ngd_on(P(1.6, 0), C, 0.5)
    return f.save()


@reg
def q12():
    """#12 △ABC(AB=8, BC=9, CA=7) 내접원 O, PQ는 접선(접점 R)."""
    ts = [5, 4, 3]                                  # B, C, A
    r, V, T = tang_poly(ts)
    ang = np.degrees(np.arctan2(V[1][1] - V[0][1], V[1][0] - V[0][0]))
    V = rotate_all(V, -ang); T = rotate_all(T, -ang)
    Bp, Cp, Ap = V
    E, F, D = T                                     # BC 접점 E, CA 접점 F, AB 접점 D
    O = P(0, 0)
    # R: D~E 사이 작은 호(B쪽) 위의 점
    aD = np.arctan2(D[1], D[0]); aE = np.arctan2(E[1], E[0])
    aR = aD + 0.5 * ((aE - aD) % (2 * np.pi))
    R = r * P(np.cos(aR), np.sin(aR))
    tdir = P(-np.sin(aR), np.cos(aR))

    def inter(p0, d0, p1, d1):
        M = np.array([d0, -np.array(d1)]).T
        s = np.linalg.solve(M, np.subtract(p1, p0))
        return np.array(p0) + s[0] * np.array(d0)
    Pp = inter(R, tdir, Bp, Ap - Bp)
    Q = inter(R, tdir, Bp, Cp - Bp)
    f = fit('cs26_p04_q12', 15500, Bp[0], Cp[0], Bp[1], Ap[1], 40)
    f.circle(O, r)
    f.poly([Ap, Bp, Cp]); f.dot(O)
    f.seg(Pp, Q)
    dm(f, Ap, Bp, O, '8 cm', 28)
    dm(f, Bp, Cp, O, '9 cm', 24)
    dm(f, Cp, Ap, O, '7 cm', 28)
    lb(f, 'A', Ap, (0, 1), 9); lb(f, 'B', Bp, (-1, -0.6), 9); lb(f, 'C', Cp, (1, -0.6), 9)
    lb(f, 'D', D, (-1, 0.5), 9); lb(f, 'E', E, (0, -1), 9); lb(f, 'F', F, (1, 0.5), 9)
    lb(f, 'P', Pp, (-1, 0.3), 9); lb(f, 'Q', Q, (-0.3, -1), 9); lb(f, 'R', R, (-0.7, -0.7), 9)
    f.lab('O', O, 0, -10)
    f.ngd_on(Ap, Cp, 0.7) if False else f.ngd_on(Cp, F, 0.45)
    return f.save()


@reg
def q13():
    """#13 직사각형 9×6, 세 변(AB, AD, BC)에 내접하는 원 O(r=3), 접선 DE (E=(4.5,0))."""
    f = fit('cs26_p04_q13', 14500, 0, 9, 0, 6, 36)
    A = P(0, 6); D = P(9, 6); B = P(0, 0); C = P(9, 0); O = P(3, 3); E = P(4.5, 0)
    f.circle(O, 3)
    f.poly([A, D, C, B]); f.seg(D, E); f.dot(O)
    dimo(f, A, D, (0, 1), '9 cm', 14)
    dimo(f, B, A, (-1, 0), '6 cm', 17)
    lb(f, 'A', A, (-1, 0.6), 9); lb(f, 'D', D, (1, 0.6), 9); lb(f, 'B', B, (-1, -0.6), 9); lb(f, 'C', C, (1, -0.6), 9)
    lb(f, 'E', E, (0, -1), 9)
    f.lab('O', O, -9, -2)
    f.ngd_on(P(5.2, 0), C, 0.5)
    return f.save()


FS_A = 7.5

if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
