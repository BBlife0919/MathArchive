from figlib import *
import math
def make():
    O = P(0, 0)
    A = P(6.4, 4.8); r = 4.0
    n = np.array([0.8, 0.6]); d = np.array([-0.6, 0.8])
    P1, P2 = P(3.2, 2.4), P(9.6, 7.2)
    s = math.sqrt(7500)
    m1, m2 = (96 - s) / 78, (96 + s) / 78
    def onl(c):   # n·X=c 와 y=m1 x 의 교점
        x = c / (0.8 + 0.6 * m1); return P(x, m1 * x)
    Q1, Q2 = onl(4), onl(12)
    f = Fig('sh26_q21', 15000, (-1.8, 18.2), (-2.5, 11.2))
    ax = f.ax
    ax.annotate('', xy=(16.4, 0), xytext=(-1.2, 0), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'))
    ax.annotate('', xy=(0, 10.5), xytext=(0, -1.2), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'))
    f.lab('$x$', (16.4, 0), 6, -3)
    f.lab('$y$', (0, 10.5), 7, 3)
    f.circle(A, r)
    f.seg(O, P(13.2, 9.9))                              # y = 3/4 x
    f.seg(O, P(15.0, 15.0 * m1))                        # l
    f.seg(P1 + 5 * d, P1 - 3 * d)                    # P1 접선
    f.seg(P2 + 3 * d, P2 - 9 * d)                       # P2 접선
    f.seg(A, Q1, lw=0.8); f.seg(A, Q2, lw=0.8)
    for p in (A, P1, P2, Q1, Q2):
        f.dot(p, r_pt=1.1)
    f.lab('O', O, -7, -8)
    f.lab('A', A, -7, 6)
    f.lab('$\\mathrm{P}_{1}$', P(1.3, 2.5), 0, 0)
    f.lab('$\\mathrm{P}_{2}$', P(9.7, 9.2), 0, 0)
    f.lab('$\\mathrm{Q}_{1}$', P(Q1[0], -1.35), 0, 0)
    f.lab('$\\mathrm{Q}_{2}$', P(14.1, 3.1), 0, 0)
    f.lab('C', P(2.9, 8.4), 0, 0, italic=True)
    f.lab('$l$', P(15.0, 15.0 * m1), 10, 0)
    f.lab('$y=\\frac{3}{4}x$', P(13.2, 9.9), 4, 2, ha='left')
    f.ngd_on(O, P(15.0, 15.0 * m1), 0.64)
    return f.save()
if __name__ == '__main__':
    print(make())
