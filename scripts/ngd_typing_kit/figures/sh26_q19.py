from figlib import *
def make():
    A, B, C = P(0, 0), P(12, 0), P(12, 12)
    D, E = P(12, 8), P(12, 3)
    F, G = P(7, 7), P(5.5, 0)
    f = Fig('sh26_q19', 13000, (-2.6, 15.4), (-2.8, 14.6))
    f.poly([A, B, C], lw=1.0)
    f.seg(D, F, lw=2.0); f.seg(F, G, lw=2.0); f.seg(G, E, lw=2.0)
    f.rightangle(B, A, C, 0.9)
    for p in (D, E, F, G):
        f.dot(p, r_pt=1.1)
    f.lab('A', A, -8, -4)
    f.lab('B', B, 8, -7)
    f.lab('C', C, 0, 9)
    f.lab('D', D, 8, 2)
    f.lab('E', E, 8, 0)
    f.lab('F', F, -4, 8)
    f.lab('G', G, 0, -10)
    f.ngd_on(P(0.6, 0.6), P(7, 7), 0.5)
    return f.save()
if __name__ == '__main__':
    print(make())
