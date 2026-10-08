"""21-A(숫자변형) 그림: 직선 y=(6/5)x 위의 점 A, 반지름 6, OA=12, OP1=6. 접선 2개(P1, P2에서)와 l, AQ1, AQ2."""
from figlib import *
import figlib
figlib.DPI = 2200
import math
def make():
    u = unit(P(5, 6)); w = np.array([u[1], -u[0]])          # u: y=6/5x 방향, w: u에 수직(오른쪽 아래)
    beta = math.atan2(6, 5); m1 = math.tan(beta - math.radians(30))
    L = unit(P(1, m1))                                         # l 방향
    O = P(0, 0); A = 12 * u; P1 = 6 * u; P2 = 18 * u
    def onl(P0):                                               # P0 + s*w 와 l 의 교점
        # P0 + s w = t L
        M = np.array([[w[0], -L[0]], [w[1], -L[1]]]); s, t = np.linalg.solve(M, -P0); return P0 + s * w
    Q1, Q2 = onl(P1), onl(P2)
    f = Fig('n21a', 9050, (-2.6, 21.9), (-2.6, 23.9))
    lw = 0.55; fs = 5.4
    ax = f.ax
    ax.annotate('', xy=(20.4, 0), xytext=(-1.6, 0), arrowprops=dict(arrowstyle='-|>', lw=lw, color='k', mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.annotate('', xy=(0, 22.0), xytext=(0, -1.6), arrowprops=dict(arrowstyle='-|>', lw=lw, color='k', mutation_scale=5, shrinkA=0, shrinkB=0))
    f.circle(A, 6.0, lw=lw)
    f.seg(O, 21.4 * u, lw=lw)                                   # y = 6/5 x
    f.seg(O, 21.0 * L, lw=lw)                                   # l
    f.seg(P1 - 5.2 * w, Q1 + 1.6 * w, lw=lw)                    # P1 에서의 접선 (위 왼쪽 ~ Q1 너머)
    f.seg(P2 - 4.0 * w, Q2 + 1.4 * w, lw=lw)                    # P2 에서의 접선 (… Q2 너머)
    f.seg(A, Q1, lw=lw); f.seg(A, Q2, lw=lw)
    for p in (A, P1, P2, Q1, Q2):
        f.dot(p, r_pt=0.85)
    f.lab('$x$', P(20.4, 0), 4, -4, fs=fs); f.lab('$y$', P(0, 22.0), -4, 3, fs=fs)
    f.lab('O', O, -4.5, -5.5, fs=fs)
    f.lab('A', A, -5, 3.5, fs=fs)
    f.lab('$\\mathrm{P}_{1}$', P1 - 0.9 * w + 0.15 * u, -7, 2, fs=fs)
    f.lab('$\\mathrm{P}_{2}$', P2 + 0.8 * u + 0.9 * w, 4, 4, fs=fs)
    f.lab('$\\mathrm{Q}_{1}$', P(9.0, 1.35), 0, 0, fs=fs)
    f.lab('$\\mathrm{Q}_{2}$', Q2, 2, -7, fs=fs)
    f.lab('$C$', A + 7.4 * unit(P(-1, 1)), 0, 0, fs=fs)
    f.lab('$l$', 21.0 * L, 5, 0, fs=fs)
    f.lab('$y=\\frac{6}{5}x$', 21.4 * u, 2, 1, ha='left', fs=fs)
    f.ngd_on(P(1.0, 1.0 * m1), 12.5 * L, 0.75, fs=3.6)
    return f.save(), (Q1, Q2, m1)
if __name__ == '__main__':
    print(make())
