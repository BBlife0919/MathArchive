from figlib import *
def make():
    f = Fig('soha_q19', 13000, (-2.05, 1.9), (-1.3, 2.8))
    xs = np.linspace(-1.75, 1.75, 300)
    ys = 4*xs**2 - 1
    mask = ys <= 2.75
    f.ax.plot(xs[mask], ys[mask], color='k', lw=1.0, zorder=2)
    f.lab('$y=4x^{2}-1$', (-1.55, 1.95), -4, 10, ha='right')

    m = 1.5
    a,b,c = 4.0, -m, -2.0
    disc = b*b-4*a*c
    xA = (-b + np.sqrt(disc))/(2*a)
    xB = (-b - np.sqrt(disc))/(2*a)
    A = P(xA, m*xA+1); B = P(xB, m*xB+1)
    dirv = unit(A-B)
    L1 = A + dirv*0.45
    L2 = B - dirv*0.55
    f.seg(L2, L1, lw=1.0)
    f.lab('$l$', L1, 10, 6)

    O = P(0,0)
    f.fill_poly([A,B,O], '#dce6f2', z=0.4)
    f.seg(O, A, lw=0.9); f.seg(O, B, lw=0.9)

    f.dot(A); f.dot(B); f.dot(O)
    f.lab('A', A, 11, 5)
    f.lab('B', B, -12, 2, ha='right')
    f.lab('O', O, -3, -12, ha='right')
    f.lab('$1$', (0,1), -9, 3, ha='right')
    f.dot((0,1))

    f.ngd_on(O, A, 0.62)
    return f.save()
if __name__=='__main__': print(make())
