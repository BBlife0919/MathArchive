# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 PDF 2쪽((1) 원과 현 정리) 그림. 실행: python3 cs26_p02_figs.py [q02 ...]  (없으면 전부)
공용 헬퍼(dimf, tri_incircle 등)는 cs26_p03_figs.py 도 가져다 쓴다.
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


FS_A = 7.5


def dimf(f, p, q, out, text, pt=12, frac=0.5, fs=None, pad=2.5, n=400):
    """dimo 와 같되, 숫자가 놓이는 자리(곡선 위 매개변수 frac)를 지정할 수 있다(선분이 가운데를 가로지를 때 frac 을 옮긴다).
    점선 곡선은 out 방향으로 pt 만큼 부풀고, 숫자 자리에서 끊긴다."""
    p, q = np.array(p, float), np.array(q, float)
    u = q - p
    left = np.array([-u[1], u[0]])
    side = 1 if np.dot(left, out) > 0 else -1
    nrm = left / np.hypot(*left)
    b = side * pt / f.pt_per_unit
    ctrl = (p + q) / 2 + nrm * b * 2
    t = np.linspace(0, 1, n)[:, None]
    pts = (1 - t) ** 2 * p + 2 * (1 - t) * t * ctrl + t ** 2 * q
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    i0 = int(round(frac * (n - 1)))
    s0 = cum[i0]
    pos = pts[i0]
    if text:
        w, h = f.text_size(text, fs)
        tang = u / np.hypot(*u)
        half = (abs(tang[0]) * w / 2 + abs(tang[1]) * h / 2 + pad) / f.pt_per_unit
        keep = np.abs(cum - s0) >= half
    else:
        keep = np.ones(len(cum), bool)
    for part in (pts[keep & (cum < s0)], pts[keep & (cum >= s0)]):
        if len(part) > 1:
            f.ax.plot(part[:, 0], part[:, 1], ls=(0, (3.2, 2.6)), lw=LW_D, color='k', zorder=2, dash_capstyle='butt')
    if text:
        f.ax.annotate(text, xy=pos, xytext=(0, 0), textcoords='offset points', ha='center', va='center',
                      fontsize=fs or FS, zorder=6)
    return pos


def tri_incircle(A, B, C):
    """삼각형 내접원: (중심 I, 반지름 r, 접점 D(AB), E(BC), F(CA))."""
    A, B, C = map(lambda v: np.array(v, float), (A, B, C))
    a, b, c = np.hypot(*(B - C)), np.hypot(*(C - A)), np.hypot(*(A - B))
    I = (a * A + b * B + c * C) / (a + b + c)
    s = (a + b + c) / 2
    r = np.sqrt((s - a) * (s - b) * (s - c) / s)

    def foot(V1, V2):
        u = (V2 - V1) / np.hypot(*(V2 - V1))
        return V1 + np.dot(I - V1, u) * u
    return I, r, foot(A, B), foot(B, C), foot(C, A)


def out_of(I, p, q):
    return (np.array(p, float) + np.array(q, float)) / 2 - np.array(I, float)


def inlab(f, text, T, V, I, al=9, nr=5):
    """접점 T 의 이름을 삼각형 안쪽(꼭짓점 V 쪽으로 al pt, 안쪽으로 nr pt)에 놓는다."""
    u = unit(np.array(V, float) - T)
    w = unit(np.array(I, float) - T)
    f.lab(text, T, (u * al + w * nr)[0] * 1.0, (u * al + w * nr)[1] * 1.0)


def circ_quad(a, b, c, d, s_deg=95.0):
    """원 O(원점, 반지름 1)에 외접하는 사각형 ABCD. 꼭짓점 A,B,C,D 의 접선 길이 a,b,c,d (AP=AS=a, BP=BQ=b, CQ=CR=c, DR=DS=d).
    반환: (A,B,C,D,P,Q,R,S)  P∈AB, Q∈BC, R∈CD, S∈DA."""
    lo, hi = 1e-6, 1e6
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(np.arctan(x / m) for x in (a, b, c, d)) > np.pi:
            lo = m
        else:
            hi = m
    r = (lo + hi) / 2
    half = [np.degrees(np.arctan(x / r)) for x in (a, b, c, d)]
    S = s_deg
    P = S + 2 * half[0]
    Q = P + 2 * half[1]
    R = Q + 2 * half[2]
    def vert(t0, t1, h):
        return cp((0, 0), 1 / np.cos(np.radians(h)), (t0 + t1) / 2)
    Av, Bv, Cv, Dv = vert(S, P, half[0]), vert(P, Q, half[1]), vert(Q, R, half[2]), vert(R, S + 360, half[3])
    return Av, Bv, Cv, Dv, cp((0, 0), 1, P), cp((0, 0), 1, Q), cp((0, 0), 1, R), cp((0, 0), 1, S)


def isosceles(base_deg):
    """원에 내접하는 이등변삼각형(AB=AC), 밑각 base_deg. A 는 위(90°). 반환 (A,B,C)."""
    arc = 2 * base_deg
    return cp((0, 0), 1, 90), cp((0, 0), 1, 90 + arc), cp((0, 0), 1, 90 - arc)


@reg
def q02():
    """#2 (1)(2) 나란히. (1) AB=24, OM=5, x=OA. (2) CO=15, OM=12, x=MB."""
    f = Fig('cs26_p02_q02', 29000, (-1.25, 4.2), (-1.12, 1.35))
    O = P(0, 0); r = 13.0
    d, h = 5 / r, 12 / r
    f.circle(O, 1)
    A, B, M = P(-h, d), P(h, d), P(0, d)
    f.seg(A, B); f.seg(O, M); f.seg(O, A); f.dot(O)
    f.rightangle(M, O, B, 0.07)
    dimo(f, A, B, (0, 1), '24 cm', 16)
    dimo(f, O, A, (-0.4, -1), '$x$ cm', 13)
    dimo(f, M, O, (1, 0), '5 cm', 16)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9)
    f.lab('M', M, -8, 6); f.lab('O', O, 0, -10)
    f.ngd_on(P(0.15, d), B, 0.5)
    f.lab('(1)', P(-1.15, 1.2), 0, 0)
    O2 = P(3.0, 0)
    f.circle(O2, 1)
    A2, B2, M2, C2 = O2 + P(0.8, 0.6), O2 + P(0.8, -0.6), O2 + P(0.8, 0), O2 + P(-1, 0)
    f.seg(A2, B2); f.seg(C2, M2); f.seg(O2, A2); f.seg(O2, B2); f.dot(O2)
    f.rightangle(M2, O2, B2, 0.07)
    dimo(f, C2, O2, (0, 1), '15 cm', 12)
    dimf(f, O2, M2, (0, 1), '12 cm', 5.5, frac=0.5, fs=7.5)
    dimf(f, M2, B2, (-1, 0), '$x$ cm', 14, frac=0.3, fs=8)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9)
    f.lab('M', M2, 3, -9); f.lab('O', O2, -4, -10)
    f.ngd_on(C2, P(O2[0] - 0.35, 0), 0.5)
    f.lab('(2)', P(1.9, 1.2), 0, 0)
    return f.save()


@reg
def q03():
    """#3 (1) AB=10, OM=x, ON=4, CN=5. (2) AO=6, OM=3, OM=ON(눈금), x=CD."""
    f = Fig('cs26_p02_q03', 29000, (-1.3, 4.3), (-1.3, 1.3))
    O = P(0, 0); r = np.sqrt(41); d, h = 4 / r, 5 / r
    M, B, A = chord(O, 1, d, 90)
    N, C2, D2 = chord(O, 1, d, -62)
    C, D = D2, C2
    # chord() 의 두 끝: foot, 시계방향끝, 반시계방향끝 → AB: A 왼쪽, CD: C 왼쪽아래
    if A[0] > B[0]: A, B = B, A
    if C[0] > D[0]: C, D = D, C
    f.circle(O, 1)
    f.seg(A, B); f.seg(C, D); f.seg(O, M); f.seg(O, N); f.dot(O)
    f.rightangle(M, O, B, 0.07); f.rightangle(N, O, D, 0.07)
    dimo(f, A, B, (0, 1), '10 cm', 9)
    dimo(f, M, O, (-1, 0), '$x$ cm', 14)
    dimo(f, O, N, (-1, 0), '4 cm', 14)
    dimf(f, C, N, (0.3, -1), '5 cm', 8, fs=8)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('M', M, 8, -6); f.lab('N', N, 9, -4); f.lab('O', O, 8, 3)
    f.ngd_on(N, D, 0.62)
    f.lab('(1)', P(-1.2, 1.2), 0, 0)
    O2 = P(3.0, 0)
    d2 = 0.5
    M2, B2, A2 = chord(O2, 1, d2, 112)
    N2, C2b, D2b = chord(O2, 1, d2, -68)
    A2, B2 = (A2, B2) if A2[0] < B2[0] else (B2, A2)
    C2, D2c = (C2b, D2b) if C2b[0] < D2b[0] else (D2b, C2b)
    f.circle(O2, 1)
    f.seg(A2, B2); f.seg(C2, D2c); f.seg(M2, N2); f.seg(O2, A2); f.dot(O2)
    f.rightangle(M2, O2, B2, 0.07); f.rightangle(N2, O2, C2, 0.07)
    f.ticks(O2, M2, 1, 0.07); f.ticks(O2, N2, 1, 0.07)
    dimf(f, M2, O2, (1, 0.3), '3 cm', 14)
    dimo(f, A2, O2, (-0.3, -1), '6 cm', 14)
    dimo(f, C2, D2c, (0, -1), '$x$ cm', 14)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9); nm(f, 'D', D2c, O2, 9)
    f.lab('M', M2, -8, 6); f.lab('N', N2, 8, -5); f.lab('O', O2, 10, -8)
    f.ngd_on(M2, B2, 0.72)
    f.lab('(2)', P(1.85, 1.2), 0, 0)
    return f.save()


@reg
def q04():
    """#4 정삼각형 외접원, OL=OM=ON."""
    f = Fig('cs26_p02_q04', 11000, (-1.3, 1.3), (-1.3, 1.3))
    O = P(0, 0)
    A, B, C = cp(O, 1, 90), cp(O, 1, 210), cp(O, 1, 330)
    L, M, N = (A + B) / 2, (B + C) / 2, (A + C) / 2
    f.circle(O, 1)
    f.poly([A, B, C])
    f.seg(O, L); f.seg(O, M); f.seg(O, N); f.dot(O)
    f.rightangle(L, O, A, 0.07); f.rightangle(M, O, C, 0.07); f.rightangle(N, O, A, 0.07)
    f.ticks(O, L, 2, 0.07); f.ticks(O, M, 2, 0.07); f.ticks(O, N, 2, 0.07)
    f.angle(A, B, C, 0.2, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    nm(f, 'L', L, O, 8); nm(f, 'M', M, O, 8); nm(f, 'N', N, O, 8)
    f.lab('O', O, 8, -5)
    f.ngd_on(B, C, 0.2)
    return f.save()


@reg
def q05():
    """#5 깨진 접시(색칠된 조각). 반지름 비 r=1 의 원에서 아랫부분만 남은 모양."""
    f = Fig('cs26_p02_q05', 15000, (-1.15, 1.15), (-1.12, 0.62))
    O = P(0, 0)
    a0, a1 = 163, 17
    arc_pts = [cp(O, 1, t) for t in np.linspace(a0, 360 + a1, 80)]      # 왼쪽 위 끝에서 아래로 돌아 오른쪽 위 끝까지
    jag = [P(0.93, 0.31), P(0.83, 0.20), P(0.74, 0.30), P(0.62, 0.14), P(0.5, 0.2), P(0.36, 0.02), P(0.2, 0.13),
           P(0.05, -0.02), P(-0.12, 0.1), P(-0.28, -0.06), P(-0.42, 0.14), P(-0.55, 0.08), P(-0.7, 0.26), P(-0.82, 0.14)]
    start = arc_pts[0]; end = arc_pts[-1]
    pts = arc_pts + [P(0.93, 0.31)] + jag[1:] + [P(-0.95, 0.3)]
    f.poly(pts, fill='#B8B8B8', lw=LW)
    f.ngd_on(P(0.36, 0.02), P(0.5, 0.2), 0.5)
    return f.save()


@reg
def q06():
    """#6 현 AB 는 반지름 OC 의 수직이등분선, AB=10."""
    f = Fig('cs26_p02_q06', 11500, (-1.3, 1.3), (-1.3, 1.3))
    O = P(0, 0); C = P(0, -1); M = P(0, -0.5); h = np.sqrt(0.75)
    A, B = P(-h, -0.5), P(h, -0.5)
    f.circle(O, 1)
    f.seg(A, B); f.seg(O, C); f.dot(O)
    f.rightangle(M, O, B, 0.07)
    f.ticks(O, M, 1, 0.07); f.ticks(M, C, 1, 0.07)
    dimf(f, A, B, (0, 1), '10 cm', 13, frac=0.72, fs=8.5)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('O', O, 8, 4)
    f.ngd_on(A, P(-0.12, -0.5), 0.35) if False else f.ngd_on(P(-0.78, -0.5), P(-0.2, -0.5), 0.45)
    return f.save()


@reg
def q07():
    """#7 (1) AM=8, OB=10, x=OM. (2) CD=12, OM=4, ON=OM(눈금), x=OA."""
    f = Fig('cs26_p02_q07', 29000, (-1.25, 4.3), (-1.2, 1.3))
    O = P(0, 0); d, h = 0.6, 0.8
    A, M, B = P(-h, -d), P(0, -d), P(h, -d)
    f.circle(O, 1)
    f.seg(A, B); f.seg(O, M); f.seg(O, B); f.dot(O)
    f.rightangle(M, O, B, 0.07)
    dimf(f, A, M, (0, -1), '8 cm', 7, fs=8)
    dimo(f, M, O, (-1, 0), '$x$ cm', 14)
    dimo(f, O, B, (0.6, 1), '10 cm', 13)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); f.lab('O', O, 0, 10)
    f.ngd_on(P(0.1, -d), B, 0.55)
    f.lab('(1)', P(-1.15, 1.15), 0, 0)
    O2 = P(3.0, 0); r = np.sqrt(52)
    d2, h2 = 4 / r, 6 / r
    A2, B2, M2 = O2 + P(-h2, -d2), O2 + P(h2, -d2), O2 + P(0, -d2)
    N2, Cx, Dx = chord(O2, 1, d2, 50)
    C2, D2 = (Cx, Dx) if Cx[0] < Dx[0] else (Dx, Cx)
    f.circle(O2, 1)
    f.seg(A2, B2); f.seg(C2, D2); f.seg(O2, M2); f.seg(O2, N2); f.seg(O2, A2); f.dot(O2)
    f.rightangle(M2, O2, B2, 0.07); f.rightangle(N2, O2, D2, 0.07)
    f.ticks(O2, M2, 1, 0.07); f.ticks(O2, N2, 1, 0.07)
    dimo(f, C2, D2, (1, 1), '12 cm', 10)
    dimo(f, O2, A2, (-0.4, 1), '$x$ cm', 13)
    dimf(f, O2, M2, (1, 0), '4 cm', 14, frac=0.45)
    nm(f, 'A', A2, O2, 9); nm(f, 'B', B2, O2, 9); nm(f, 'C', C2, O2, 9); nm(f, 'D', D2, O2, 9)
    f.lab('O', O2, -7, 6)
    f.ngd_on(P(O2[0] + 0.1, -d2), B2, 0.55)
    f.lab('(2)', P(1.85, 1.15), 0, 0)
    return f.save()


def _iso(name, base, label_deg):
    f = Fig(name, 11500, (-1.3, 1.3), (-1.3, 1.3))
    O = P(0, 0)
    A, B, C = isosceles(base)
    M, N = (A + B) / 2, (A + C) / 2
    f.circle(O, 1)
    f.poly([A, B, C])
    f.seg(O, M); f.seg(O, N); f.dot(O)
    f.rightangle(M, O, A, 0.07); f.rightangle(N, O, A, 0.07)
    f.ticks(O, M, 2, 0.07); f.ticks(O, N, 2, 0.07)
    f.angle(B, C, A, 0.3, label_deg, fs=FS_A)
    f.angle(A, B, C, 0.2, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    nm(f, 'M', M, O, 8); nm(f, 'N', N, O, 8)
    f.lab('O', O, 0, 10)
    f.ngd_on(B, C, 0.72)
    return f.save()


@reg
def q08():
    """#8 ∠B=50°, OM=ON."""
    return _iso('cs26_p02_q08', 50, '50°')


@reg
def q10():
    """#10 ∠B=66°, OM=ON."""
    return _iso('cs26_p02_q10', 66, '66°')


@reg
def q09():
    """#9 원기둥 탱크 단면: 반지름 1 m, 액체 높이 0.5 m (색칠 = 액체 단면)."""
    f = Fig('cs26_p02_q09', 11000, (-2.6, 1.2), (-1.25, 1.2))
    O = P(0, 0)
    y = -0.5; hh = np.sqrt(0.75)
    th0 = np.degrees(np.arctan2(y, -hh)); th1 = np.degrees(np.arctan2(y, hh))
    seg_pts = [cp(O, 1, t) for t in np.linspace(180 + 30, 360 - 30, 60)]
    f.poly(seg_pts, fill='#B8B8B8', lw=0.01, z=0.6)
    f.circle(O, 1)
    A, B = P(-hh, y), P(hh, y)
    f.seg(A, B)
    f.seg(P(-1.5, -1), P(0.25, -1), lw=0.6)
    f.seg(P(-1.5, y), A, lw=0.6)
    S1, S2 = P(-1.35, -1), P(-1.35, y)
    dimf(f, S1, S2, (-1, 0), '0.5 m', 13)
    f.ngd_on(A, B, 0.35) if False else f.ngd_on(P(-0.1, y), B, 0.5)
    return f.save()


@reg
def q11():
    """#11 OM=ON, MB=3, x=CD."""
    f = Fig('cs26_p02_q11', 12500, (-1.35, 1.35), (-1.3, 1.3))
    O = P(0, 0); d = 0.55
    M, Ax, Bx = chord(O, 1, d, 205)
    A, B = (Ax, Bx) if Ax[1] > Bx[1] else (Bx, Ax)
    N = P(d, 0); hh = np.sqrt(1 - d * d); Dp, Cp = P(d, hh), P(d, -hh)
    f.circle(O, 1)
    f.seg(A, B); f.seg(Cp, Dp); f.seg(O, M); f.seg(O, N); f.dot(O)
    f.rightangle(M, O, B, 0.07); f.rightangle(N, O, Dp, 0.07)
    f.ticks(O, M, 2, 0.07); f.ticks(O, N, 2, 0.07)
    dimf(f, M, B, (1, 0.4), '3 cm', 14)
    dimf(f, Dp, Cp, (-1, 0), '$x$ cm', 9, frac=0.25)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', Cp, O, 9); nm(f, 'D', Dp, O, 9)
    nm(f, 'M', M, O, 8); f.lab('N', N, 9, -4); f.lab('O', O, -3, -9)
    f.ngd_on(A, P(M[0] - 0.02, M[1] + 0.02), 0.5)
    return f.save()


@reg
def q12():
    """#12 AB⊥OC, BD=6, CD=4. 반지름 6.5 기준."""
    f = Fig('cs26_p02_q12', 11500, (-1.3, 1.3), (-1.3, 1.3))
    O = P(0, 0); r = 6.5
    d, h = 2.5 / r, 6 / r
    A, B, D, C = P(-h, -d), P(h, -d), P(0, -d), P(0, -1)
    f.circle(O, 1)
    f.seg(A, B); f.seg(O, C); f.seg(O, A); f.dot(O)
    f.rightangle(D, O, B, 0.07)
    dimf(f, D, B, (0, 1), '6 cm', 12)
    dimf(f, D, C, (-1, 0), '4 cm', 14)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.lab('O', O, 8, 5); f.lab('D', D, 7, -9)
    f.ngd_on(A, P(-0.25, -d), 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
