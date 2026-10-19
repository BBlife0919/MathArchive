# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트(원의 성질) 그림. 실행: python3 cs26_figs.py [c1_01 ...]  (없으면 전부)
규칙(/타이핑): NGD 마크=직선과 나란히 겹치기, 길이=점선 '사이' 숫자, 각도 숫자=호 바로 바깥, 원본에 인쇄된 것만(손글씨 제외).
"""
import sys
from figlib import *

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


def nm(f, text, p, ref, d=9, **kw):
    v = np.array(p, float) - np.array(ref, float)
    v = v / np.hypot(*v)
    f.lab(text, p, v[0] * d, v[1] * d, **kw)


def cp(c, r, deg):
    a = np.radians(deg)
    return P(c[0] + r * np.cos(a), c[1] + r * np.sin(a))


def chord(c, r, d, dir_deg):
    """중심 c, 반지름 r, 중심에서 거리 d, 수선 방향 dir_deg인 현. (수선의 발, 시계방향쪽 끝, 반시계방향쪽 끝) 반환."""
    a = np.radians(dir_deg)
    foot = P(c[0] + d * np.cos(a), c[1] + d * np.sin(a))
    h = np.sqrt(r * r - d * d)
    t = np.array([np.sin(a), -np.cos(a)])      # 시계방향 접선
    return foot, foot + h * t, foot - h * t


FS_A = 7.5


def dimo(f, p, q, out, text, pt=8):
    """길이 표시: 점선 곡선이 out 방향(바깥)으로 부풀도록 side를 자동 결정."""
    u = np.subtract(q, p)
    left = np.array([-u[1], u[0]])
    side = 1 if np.dot(left, out) > 0 else -1
    return f.dimarc_pt(p, q, side, text, pt=pt)


@reg
def c1_01():
    """#1 (1)(2) 나란히."""
    f = Fig('cs26_c1_01', 29000, (-1.2, 4.05), (-1.6, 1.4))
    O = P(0, 0); d = 0.62; h = np.sqrt(1 - d * d)
    f.circle(O, 1)
    A = P(-h, -d); F = P(0, -d); B = P(h, -d)
    f.seg(A, B); f.seg(O, F); f.dot(O)
    f.rightangle(F, O, B, 0.07)
    dimo(f, A, F, (0, 1), '$x$ cm', 8)
    dimo(f, F, B, (0, -1), '6 cm', 8)
    f.lab('O', O, 0, 10)
    f.lab('(1)', P(-1.12, 1.2), 0, 0)
    O2 = P(2.75, 0); d = 0.8; h = 0.6
    f.circle(O2, 1)
    A2 = P(O2[0] - h, -d); F2 = P(O2[0], -d); B2 = P(O2[0] + h, -d)
    f.seg(A2, B2); f.seg(O2, F2); f.seg(O2, A2); f.dot(O2)
    f.rightangle(F2, O2, B2, 0.07)
    dimo(f, O2, A2, (-1, 0.5), '5 cm', 16)
    dimo(f, F2, O2, (1, 0), '4 cm', 16)
    dimo(f, A2, B2, (0, -1), '$x$ cm', 20)
    f.lab('O', O2, 0, 10)
    f.lab('(2)', P(1.65, 1.2), 0, 0)
    f.ngd_on(P(O2[0] + 0.1, -d), B2, 0.6)
    return f.save()

@reg
def c1_02():
    """#2 깨진 접시: AM=6, CM=2 (축척은 원본처럼 개략)."""
    f = Fig('cs26_c1_02', 17000, (-2.5, 4.9), (-3.9, 3.9))
    A = P(0, -3); B = P(0, 3); C = P(-1.4, 0); M = P(0, 0)
    r = (9 + 1.4 ** 2) / (2 * 1.4); O = P(-1.4 + r, 0)
    aB = np.degrees(np.arctan2(3, -O[0])); aA = np.degrees(np.arctan2(-3, -O[0])) + 360
    arc_pts = [cp(O, r, t) for t in np.linspace(aB, aA, 60)][::-1]   # A -> B 가 아니라 B -> A 순서
    arc_pts = arc_pts[::-1]
    jag = [P(0.9, -3.6), P(1.8, -3.1), P(2.3, -2.0), P(3.4, -1.6), P(4.1, -0.4), P(4.2, 0.9), P(3.3, 1.6), P(2.2, 2.3), P(1.7, 3.2), P(0.7, 3.5)]
    f.poly(arc_pts + jag, fill='#B8B8B8', lw=LW)
    f.seg(A, B); f.seg(C, M)
    f.rightangle(M, B, C, 0.2)
    dimo(f, C, M, (0, 1), '2 cm', 13)
    dimo(f, M, A, (1, 0), '6 cm', 17)
    nm(f, 'B', B, M, 9); nm(f, 'A', A, M, 9); nm(f, 'C', C, M, 9)
    f.lab('M', M, 8, 8)
    f.ngd_on(P(0.9, -3.6), P(1.8, -3.1), 0.5)
    return f.save()

@reg
def c1_03():
    """#3 빈칸 박스 안 그림: OM⊥AB, ON⊥CD, OM=ON."""
    f = Fig('cs26_c1_03', 9500, (-1.3, 1.4), (-1.3, 1.3))
    O = P(0, 0); d = 0.45
    M, B, A = chord(O, 1, d, 115)
    N, C2, D2 = chord(O, 1, d, -65)
    C, D = D2, C2
    f.circle(O, 1)
    f.fill_poly([O, A, M], '#BBBBBB'); f.fill_poly([O, D, N], '#BBBBBB')
    f.seg(A, B); f.seg(C, D); f.seg(O, M); f.seg(O, N); f.seg(O, A); f.seg(O, D); f.dot(O)
    f.rightangle(M, O, B, 0.08); f.rightangle(N, O, C, 0.08)
    nm(f, 'A', A, O, 8); nm(f, 'B', B, O, 8); nm(f, 'C', C, O, 8); nm(f, 'D', D, O, 8)
    nm(f, 'M', M, O, 7); nm(f, 'N', N, O, 7)
    f.lab('O', O, 8, -3)
    return f.save()


@reg
def c1_04():
    """#4 (1)(2)."""
    f = Fig('cs26_c1_04', 29000, (-1.85, 4.7), (-1.55, 1.4))
    O = P(0, 0); d = 0.76
    FL, L1, L2 = chord(O, 1, d, 188)
    FR, R1, R2 = chord(O, 1, d, -8)
    f.circle(O, 1)
    f.seg(L1, L2); f.seg(R1, R2); f.seg(O, FL); f.seg(O, FR); f.dot(O)
    topL, botL = (L1, L2) if L1[1] > L2[1] else (L2, L1)
    topR, botR = (R1, R2) if R1[1] > R2[1] else (R2, R1)
    f.rightangle(FL, O, topL, 0.07); f.rightangle(FR, O, topR, 0.07)
    dimo(f, O, FL, (0, 1), '3 cm', 8); dimo(f, FR, O, (0, 1), '3 cm', 8)
    dimo(f, botL, topL, (-1, 0), '$x$ cm', 26)
    dimo(f, botR, topR, (1, 0), '4 cm', 26)
    f.lab('O', O, 0, -10)
    f.lab('(1)', P(-1.6, 1.2), 0, 0)
    O2 = P(3.1, 0); d = 0.75
    FL2, a1, a2 = chord(O2, 1, d, 225)
    FR2, b1, b2 = chord(O2, 1, d, -45)
    f.circle(O2, 1)
    f.seg(a1, a2); f.seg(b1, b2); f.seg(O2, FL2); f.seg(O2, FR2); f.dot(O2)
    f.rightangle(FL2, O2, a1 if a1[0] < a2[0] else a2, 0.07)
    f.rightangle(FR2, O2, b1 if b1[0] > b2[0] else b2, 0.07)
    dimo(f, O2, FL2, (-0.7, 0.7), '5 cm', 15); dimo(f, O2, FR2, (0.7, 0.7), '$x$ cm', 15)
    dimo(f, a1, a2, (-0.707, -0.707), '7 cm', 34)
    dimo(f, b1, b2, (0.707, -0.707), '7 cm', 34)
    f.lab('O', O2, 0, 10)
    f.lab('(2)', P(1.9, 1.2), 0, 0)
    f.ngd_on(P(2.4, -0.25), P(3.8, -0.25), 0.5) if False else None
    return f.save()

@reg
def c1_05():
    """#5 꽃밭: 큰 원 안에 작은 원(접선 AB)."""
    f = Fig('cs26_c1_05', 11500, (-1.3, 1.3), (-1.3, 1.1))
    O = P(0, 0); r = 0.7; h = np.sqrt(1 - r * r)
    f.circle(O, 1, fill='#9A9A9A')
    f.circle(O, r, fill='white', z=2.2)
    A = P(-h, -r); B = P(h, -r)
    f.seg(A, B, z=3); f.dot(O)
    f.dimarc_pt(A, B, -1, '8 m', pt=10)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9)
    f.lab('O', O, 0, 10)
    f.ngd_on(P(-0.05, -r), B, 0.75)
    return f.save()


@reg
def c1_06():
    """#6 삼각형 ABC 외접원, OM=ON, ∠B=65°."""
    f = Fig('cs26_c1_06', 11000, (-1.3, 1.3), (-1.3, 1.3))
    O = P(0, 0)
    A = cp(O, 1, 90); B = cp(O, 1, 220); C = cp(O, 1, 320)
    M = (A + B) / 2; N = (A + C) / 2
    f.circle(O, 1)
    f.poly([A, B, C])
    f.seg(O, M); f.seg(O, N); f.dot(O)
    f.rightangle(M, O, A, 0.07); f.rightangle(N, O, A, 0.07)
    f.ticks(O, M, 2, 0.07); f.ticks(O, N, 2, 0.07)
    f.angle(B, C, A, 0.26, '65°', fs=FS_A)
    f.angle(A, B, C, 0.16, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    nm(f, 'M', M, O, 8); nm(f, 'N', N, O, 8)
    f.lab('O', O, 2, -9)
    f.ngd_on(B, C, 0.62)
    return f.save()


@reg
def c1_07():
    """#7 AB=CD, OM=4, CN=5."""
    f = Fig('cs26_c1_07', 15500, (-1.5, 1.5), (-1.45, 1.4))
    O = P(0, 0); d = 0.55
    M, B, A = chord(O, 1, d, 100)
    N, C, D = chord(O, 1, d, 250)
    f.circle(O, 1)
    f.seg(A, B); f.seg(C, D); f.seg(O, M); f.seg(O, N); f.seg(O, B); f.dot(O)
    f.rightangle(M, O, B, 0.08); f.rightangle(N, O, D, 0.08)
    dimo(f, M, O, (-1, 0), '4 cm', 16)
    dimo(f, O, N, (1, 0), '$x$ cm', 16)
    dimo(f, C, N, (0, 1), '5 cm', 15)
    dimo(f, O, B, (0.3, -1), '$y$ cm', 12)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    nm(f, 'M', M, O, 8); nm(f, 'N', N, O, 8)
    f.lab('O', O, 6, 17)
    f.ngd_on(N, D, 0.6)
    return f.save()

if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
