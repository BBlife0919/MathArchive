# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 6쪽(원주각 정리) 그림. 실행: python3 cs26_p06_figs.py [q02 ...]  (없으면 전부)
규칙(/타이핑): NGD 마크=직선과 나란히 겹치기, 길이=점선 '사이' 숫자, 각도 숫자=호 바로 바깥, 원본에 인쇄된 것만(손글씨 제외).
"""
import sys
from figlib import *
from cs26_figs import dimo, nm, cp, chord

REG = {}


def reg(fn):
    REG[fn.__name__] = fn
    return fn


FS_A = 7.5
UNIT = 'cm'


def arcticks(f, c, r, deg, n=1, half=0.07, gap=4.0, lw=0.8):
    """원 위 호의 같은 길이 표시(눈금 n개): 호의 deg 위치에 반지름 방향 짧은 선을 호 바깥으로 비스듬히 걸쳐 그린다."""
    for i in range(n):
        a = deg + (i - (n - 1) / 2.0) * gap
        p1 = cp(c, r - half, a)
        p2 = cp(c, r + half, a)
        f.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='k', lw=lw, zorder=3)


def arc_dim(f, c, r, a0, a1, text, fs=8.5, pad=3.0, ticks=(True, True), tickhalf=0.06, text_side=None):
    """원 바깥 호 길이 표시(반지름 r, a0->a1 도). text가 있으면 호 가운데를 끊고 글자를 넣는다. text_side가 있으면 끊지 않고
    그 방향(데이터 단위 벡터)으로 글자를 호 바깥에 둔다. 양 끝에 눈금."""
    ts = np.linspace(a0, a1, 400)
    pts = np.array([cp(c, r, t) for t in ts])
    seglen = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seglen)])
    mid_t = (a0 + a1) / 2.0
    pm = cp(c, r, mid_t)
    keep = np.ones(len(ts), bool)
    if text and text_side is None:
        w, h = f.text_size(text, fs)
        tang = np.array([-np.sin(np.radians(mid_t)), np.cos(np.radians(mid_t))])
        half = (abs(tang[0]) * w / 2 + abs(tang[1]) * h / 2 + pad) / f.pt_per_unit
        keep = np.abs(cum - cum[-1] / 2.0) >= half
    start = 0
    parts = []
    cur = []
    for i in range(len(ts)):
        if keep[i]:
            cur.append(pts[i])
        else:
            if len(cur) > 1:
                parts.append(np.array(cur))
            cur = []
    if len(cur) > 1:
        parts.append(np.array(cur))
    for part in parts:
        f.ax.plot(part[:, 0], part[:, 1], color='k', lw=0.8, zorder=2)
    if text and text_side is None:
        f.lab(text, pm, 0, 0, fs=fs)
    elif text:
        f.lab(text, pm, text_side[0], text_side[1], fs=fs)
    for flag, t in zip(ticks, (a0, a1)):
        if flag:
            p1 = cp(c, r - tickhalf, t)
            p2 = cp(c, r + tickhalf, t)
            f.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='k', lw=0.8, zorder=3)


def arrowmark(f, p, direction, size=0.07):
    """평행 표시 화살표(작은 삼각형)."""
    u = unit(direction)
    n = np.array([-u[1], u[0]])
    tip = np.array(p) + u * size
    b1 = np.array(p) - u * size + n * size * 0.7
    b2 = np.array(p) - u * size - n * size * 0.7
    f.ax.add_patch(Polygon([tip, b1, b2], closed=True, fc='k', ec='k', lw=0.4, zorder=4))


def ptlab(f, text, p, dx=0, dy=0, fs=None):
    f.lab(text, p, dx, dy, fs=fs)


@reg
def p06_q02():
    """#2 오각형 ABCDE 모든 대각선(별 모양)."""
    f = Fig('cs26_p06_q02', 12000, (-1.45, 1.45), (-1.35, 1.4))
    O = P(0, 0)
    deg = dict(A=90, B=162, C=234, D=306, E=18)
    pt = {k: cp(O, 1, v) for k, v in deg.items()}
    f.circle(O, 1)
    ks = list(pt)
    for i in range(5):
        for j in range(i + 1, 5):
            f.seg(pt[ks[i]], pt[ks[j]])
    for k in ks:
        nm(f, k, pt[k], O, 10)
    f.ngd_on(pt['B'], pt['E'], 0.5)
    return f.save()


@reg
def p06_q03():
    """#3 (1)(2)(3) 나란히."""
    f = Fig('cs26_p06_q03', 29000, (-1.45, 7.1), (-1.45, 1.4))
    # (1) 같은 호에 대한 두 원주각
    O1 = P(0, 0)
    TL, TR, BL, BR = cp(O1, 1, 130), cp(O1, 1, 50), cp(O1, 1, 230), cp(O1, 1, 310)
    f.circle(O1, 1)
    f.seg(TL, BL); f.seg(TL, BR); f.seg(TR, BL); f.seg(TR, BR); f.dot(O1)
    f.angle(TL, BL, BR, 0.30, '40°', fs=FS_A)
    f.angle(TR, BR, BL, 0.30, '$x$', fs=FS_A)
    f.lab('O', O1, 12, 0)
    f.lab('(1)', P(-1.3, 1.2), 0, 0)
    # (2) 중심각 140°
    O2 = P(2.9, 0)
    L, R, T = cp(O2, 1, 160), cp(O2, 1, 20), cp(O2, 1, 90)
    f.circle(O2, 1)
    f.seg(O2, L); f.seg(O2, R); f.seg(T, L); f.seg(T, R); f.dot(O2)
    f.angle(O2, R, L, 0.22, '140°', fs=FS_A)
    f.angle(T, L, R, 0.2, '$x$', fs=FS_A)
    f.lab('O', O2, 0, -10)
    f.lab('(2)', P(1.75, 1.2), 0, 0)
    # (3) AC는 지름
    O3 = P(5.8, 0)
    A, C, B, D = cp(O3, 1, 125), cp(O3, 1, 305), cp(O3, 1, 245), cp(O3, 1, 40)
    f.circle(O3, 1)
    f.seg(A, D); f.seg(A, B); f.seg(B, C); f.seg(A, C); f.seg(B, D); f.dot(O3)
    f.angle(A, B, C, 0.30, None)
    f.lab('30°', A + 0.56 * unit(C - A) + 0.24 * np.array([0.82, 0.57]), 0, 0, fs=FS_A)
    f.angle(D, A, B, 0.25, '$x$°', fs=FS_A)
    nm(f, 'A', A, O3, 9); nm(f, 'B', B, O3, 9); nm(f, 'C', C, O3, 9); nm(f, 'D', D, O3, 9)
    f.lab('O', O3, -13, -4)
    f.lab('(3)', P(4.65, 1.2), 0, 0)
    f.ngd_on(A, D, 0.5)
    return f.save()


@reg
def p06_q04():
    """#4 (1)(2) 나란히."""
    f = Fig('cs26_p06_q04', 29000, (-1.5, 6.4), (-1.5, 1.5))
    # (1)
    O = P(0, 0)
    p1, p2, p3, p4, p5, p6 = (cp(O, 1, v) for v in (95, 45, 177, -43, 250, -93))
    f.circle(O, 1)
    f.seg(O, p1); f.seg(O, p2); f.seg(p1, p5); f.seg(p2, p5); f.seg(p3, p4); f.seg(p3, p6); f.dot(O)
    f.angle(O, p1, p2, 0.30, '$x$°', fs=FS_A)
    f.angle(p3, p4, p6, 0.30, None)
    f.lab('25°', p3 + np.array([0.27, 0.15]), 0, 0, fs=FS_A)
    arcticks(f, O, 1, 70, 1)
    arcticks(f, O, 1, -68, 2)
    f.lab('O', O, -11, 10)
    f.lab('(1)', P(-1.4, 1.3), 0, 0)
    f.ngd_on(p3, p4, 0.78)
    # (2)
    O2 = P(4.0, 0)
    Lp, Up, Rp = cp(O2, 1, 162), cp(O2, 1, 42), cp(O2, 1, -18)
    f.circle(O2, 1)
    f.seg(Lp, Rp); f.seg(Lp, Up); f.seg(Up, Rp); f.dot(O2)
    f.angle(Rp, Up, Lp, 0.30, '60°', fs=FS_A)
    arc_dim(f, O2, 1.2, 162, 42, '12 cm', fs=8.5)
    arc_dim(f, O2, 1.2, 42, -18, '$x$ cm', fs=8.5, ticks=(False, True), text_side=(17, 0))
    f.lab('O', O2, 0, -10)
    f.lab('(2)', P(2.7, 1.3), 0, 0)
    f.ngd_on(Lp, Up, 0.45)
    return f.save()


@reg
def p06_q05():
    """#5 평행한 두 현 AB // CD."""
    f = Fig('cs26_p06_q05', 10500, (-1.4, 1.4), (-1.3, 1.3))
    O = P(0, 0)
    A, B, C, D = cp(O, 1, 135), cp(O, 1, 45), cp(O, 1, 210), cp(O, 1, 330)
    f.circle(O, 1)
    f.seg(A, B); f.seg(C, D); f.dot(O)
    arrowmark(f, (A + B) / 2 + np.array([0.05, 0]), (1, 0))
    arrowmark(f, (C + D) / 2 + np.array([0.05, 0]), (1, 0))
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('O', O, -9, -6)
    f.ngd_on(A, B, 0.2)
    return f.save()


@reg
def p06_q06():
    """#6 삼각형 ABC 외접원, 호 AB:BC:CA = 3:4:5 (a°, b°, c° 표시)."""
    f = Fig('cs26_p06_q06', 11000, (-1.4, 1.4), (-1.3, 1.3))
    O = P(0, 0)
    A, B, C = cp(O, 1, 120), cp(O, 1, 210), cp(O, 1, 330)
    f.circle(O, 1)
    f.poly([A, B, C])
    f.angle(A, B, C, 0.20, '$a$°', fs=FS_A)
    f.angle(B, C, A, 0.24, '$b$°', fs=FS_A)
    f.angle(C, A, B, 0.24, '$c$°', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9)
    f.ngd_on(B, C, 0.3)
    return f.save()


@reg
def p06_q07():
    """#7 ∠AEC=64°, ∠AOB=54°, x=∠BDC (=37°)."""
    f = Fig('cs26_p06_q07', 11500, (-1.4, 1.4), (-1.35, 1.35))
    O = P(0, 0)
    A, B, C, D, E = cp(O, 1, 216), cp(O, 1, 270), cp(O, 1, 344), cp(O, 1, 49), cp(O, 1, 87)
    f.circle(O, 1)
    f.seg(E, A); f.seg(E, C); f.seg(D, B); f.seg(D, C); f.seg(O, A); f.seg(O, B); f.dot(O)
    f.angle(E, A, C, 0.22, '64°', fs=FS_A)
    f.angle(O, A, B, 0.30, '54°', fs=FS_A)
    f.angle(D, B, C, 0.20, '$x$', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9); nm(f, 'E', E, O, 9)
    f.lab('O', O, 9, 6)
    f.ngd_on(E, A, 0.55)
    return f.save()


@reg
def p06_q08():
    """#8 호 AB=3cm, 호 BC=9cm (바깥 호 길이 표시), ∠BOC=120°, x=∠APC."""
    f = Fig('cs26_p06_q08', 15500, (-2.15, 1.7), (-1.75, 1.8))
    O = P(0, 0)
    A, B, C, Pp = cp(O, 1, 80), cp(O, 1, 120), cp(O, 1, 240), cp(O, 1, -14)
    f.circle(O, 1)
    f.seg(O, B); f.seg(A, Pp); f.seg(O, C); f.seg(C, Pp); f.dot(O)
    # 바깥 호 길이 표시: 반지름 1.40, B-C는 9cm, A-B는 3cm
    arc_dim(f, O, 1.40, 120, 240, '9 cm', fs=8.5)
    arc_dim(f, O, 1.40, 80, 120, '3 cm', fs=8.5, ticks=(True, False))
    f.angle(O, B, C, 0.30, '120°', fs=FS_A)
    f.angle(Pp, A, C, 0.22, '$x$', fs=FS_A)
    nm(f, 'A', cp(O, 1.40, 80), O, 11); nm(f, 'B', cp(O, 1.40, 120), O, 11); nm(f, 'C', cp(O, 1.40, 240), O, 11)
    nm(f, 'P', Pp, O, 9)
    f.lab('O', O, 9, 0)
    f.ngd_on(A, Pp, 0.5)
    return f.save()


@reg
def p06_q09():
    """#9 AB 지름, ∠COD=56°, P는 AD, BC의 연장선의 교점."""
    f = Fig('cs26_p06_q09', 13000, (-1.45, 1.8), (-1.4, 1.3))
    O = P(0, 0)
    A, B, D, C = cp(O, 1, 124), cp(O, 1, -56), cp(O, 1, 62), cp(O, 1, 6)
    # P: 직선 AD와 직선 BC의 교점
    M = np.array([[D[0] - A[0], -(C[0] - B[0])], [D[1] - A[1], -(C[1] - B[1])]])
    s, t = np.linalg.solve(M, np.array([B[0] - A[0], B[1] - A[1]]))
    Pp = A + s * (D - A)
    f.circle(O, 1)
    f.seg(A, B); f.seg(A, Pp); f.seg(B, Pp); f.seg(O, D); f.seg(O, C); f.dot(O)
    f.angle(O, D, C, 0.26, '56°', fs=FS_A)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9); nm(f, 'P', Pp, A, 9)
    f.lab('O', O, -9, -2)
    f.ngd_on(A, B, 0.28)
    return f.save()


@reg
def p06_q10():
    """#10 호 AB=호 BC(두 눈금), ∠ABD=55°, ∠BDC=43°."""
    f = Fig('cs26_p06_q10', 11500, (-1.4, 1.4), (-1.35, 1.3))
    O = P(0, 0)
    A, B, C, D = cp(O, 1, 150), cp(O, 1, 236), cp(O, 1, 322), cp(O, 1, 40)
    f.circle(O, 1)
    f.seg(A, B); f.seg(A, D); f.seg(D, C); f.seg(A, C); f.seg(B, D); f.dot(O)
    f.angle(B, A, D, 0.24, '55°', fs=FS_A)
    f.angle(D, B, C, 0.26, '43°', fs=FS_A)
    f.angle(A, C, D, 0.20, None)
    arcticks(f, O, 1, 193, 2)
    arcticks(f, O, 1, 279, 2)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9)
    f.lab('O', O, 0, 10)
    f.ngd_on(A, D, 0.5)
    return f.save()


@reg
def p06_q11():
    """#11 두 원(P, Q에서 만남), 큰 원 O: 호 BQP의 중심각 170°."""
    O = P(0, 0)
    A, B, Pp, Q = cp(O, 1, 139), cp(O, 1, 225), cp(O, 1, 35), cp(O, 1, -35)
    # 작은 원: P, Q와 직선 AP 위의 D를 지나는 원. D는 직선 AP의 연장선 위(x=1.8), C는 직선 BQ와의 두 번째 교점
    uAP = unit(Pp - A)
    D = Pp + uAP * ((1.8 - Pp[0]) / uAP[0])
    # 외심
    ax, ay = Pp; bx, by = Q; cx, cy = D
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
    uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d
    O2 = P(ux, uy); r2 = np.hypot(*(Pp - O2))
    uBQ = unit(Q - B)
    # 직선 B + s*uBQ 와 작은 원의 교점 중 Q가 아닌 쪽
    w = B - O2
    bq = 2 * np.dot(w, uBQ); cq = np.dot(w, w) - r2 ** 2
    disc = np.sqrt(bq ** 2 - 4 * cq)
    ss = [(-bq + disc) / 2, (-bq - disc) / 2]
    cands = [B + s * uBQ for s in ss]
    C = max(cands, key=lambda p: np.hypot(*(p - Q)))
    f = Fig('cs26_p06_q11', 14500, (-1.35, 3.05), (-1.35, 1.2))
    f.circle(O, 1)
    f.circle(O2, r2)
    f.seg(A, Pp); f.seg(Pp, D); f.seg(A, B); f.seg(B, Q); f.seg(Q, C); f.seg(D, C); f.seg(Pp, Q)
    f.seg(B, O); f.seg(O, Pp); f.dot(O)
    f.angle(O, Pp, B, 0.22, '170°', fs=FS_A)
    f.angle(D, Pp, C, 0.12, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); f.lab('P', Pp, 0, 11)
    f.lab('Q', Q, -9, -10); nm(f, 'C', C, O2, 9); nm(f, 'D', D, O2, 9)
    f.lab('O', O, -4, 10)
    f.ngd_on(A, B, 0.5)
    print('   q11 check: D, C =', D, C, ' AB.CD parallel dot =', np.cross(unit(B - A), unit(C - D)))
    return f.save()


@reg
def p06_q12():
    """#12 원 O에 내접하는 오각형 ABCDE, ∠B=110°, ∠COD=60°."""
    f = Fig('cs26_p06_q12', 11500, (-1.45, 1.45), (-1.35, 1.35))
    O = P(0, 0)
    A, B, C, D, E = cp(O, 1, 90), cp(O, 1, 175), cp(O, 1, 230), cp(O, 1, 290), cp(O, 1, 10)
    f.circle(O, 1)
    f.poly([A, B, C, D, E])
    f.seg(O, C); f.seg(O, D); f.dot(O)
    f.angle(B, A, C, 0.20, '110°', fs=FS_A)
    f.angle(O, C, D, 0.25, '60°', fs=FS_A)
    f.angle(E, D, A, 0.18, None)
    nm(f, 'A', A, O, 9); nm(f, 'B', B, O, 9); nm(f, 'C', C, O, 9); nm(f, 'D', D, O, 9); nm(f, 'E', E, O, 9)
    f.lab('O', O, 5, 9)
    f.ngd_on(A, E, 0.5)
    return f.save()


@reg
def p06_q13():
    """#13 박물관: 벽에 걸린 그림, 조명(그림 양 끝을 90°로 비춤)."""
    from matplotlib.font_manager import FontProperties
    KF = FontProperties(fname=os.path.expanduser('~/.fonts/HCRBatang.ttf'), size=9.5)
    f = Fig('cs26_p06_q13', 12000, (-3.4, 3.6), (-4.3, 2.1))
    W = 3.2; pw = 2.35
    f.poly([P(-W, 0), P(W, 0), P(W, 1.2), P(-W, 1.2)], fill='#D0D0D0', z=1.2)
    f.seg(P(-W, 0), P(W, 0))
    f.poly([P(-pw, 0), P(pw, 0), P(pw, -0.32), P(-pw, -0.32)], fill='#B0B0B0', z=1.4)
    apex = P(0, -0.32 - pw)
    f.poly([P(-pw, -0.32), P(pw, -0.32), apex], fill='white', z=1.3)
    # 조명(꼭짓점 아래 작은 부채꼴)
    f.poly([P(-0.14, apex[1] - 0.02), P(0, apex[1] + 0.1), P(0.14, apex[1] - 0.02), P(0, apex[1] - 0.14)], fill='#B0B0B0', z=2)
    th = np.linspace(np.radians(235), np.radians(305), 30)
    cc = P(0, apex[1] - 0.42)
    arc_pts = [P(cc[0] + 0.32 * np.cos(t), cc[1] + 0.32 * np.sin(t)) for t in th]
    f.poly([cc] + arc_pts, fill='#B0B0B0', z=2)
    f.ax.text(0, apex[1] - 1.05, '조명', fontproperties=KF, ha='center', va='center', zorder=6)
    f.ax.text(2.55, 1.0 + 0.0 + 0.55, '그림', fontproperties=KF, ha='center', va='center', zorder=6)
    f.ax.annotate('', xy=(0.45, -0.18), xytext=(2.1, 1.0), arrowprops=dict(arrowstyle='-|>', color='k', lw=0.8,
                  connectionstyle='arc3,rad=0.25', shrinkA=0, shrinkB=0), zorder=6)
    f.ngd_on(P(0.2, -0.32 - 0.2 * 0), P(pw, -0.32), 0.0) if False else None
    f.ngd_on(P(-pw, -0.32), apex, 0.5)
    return f.save()


if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        print(REG[n]())
