from gbm26_common import *
def make():
    f = Fig('uv26_s17', 11500, (-0.9, 5.6), (-0.8, 3.0))
    axes(f, -0.55, 5.0, -0.45, 2.75)
    f.seg(P(-0.4, 2), P(1, 2)); f.seg(P(3, 2), P(4.6, 2))
    f.seg(P(1, 0), P(3, 0), lw=2.2)
    f.dashed(P(1, 0), P(1, 2)); f.dashed(P(3, 0), P(3, 2)); f.dashed(P(0, 1), P(3, 1)); f.dashed(P(0, 2), P(1, 2))
    f.dot(P(1, 1), 1.5); f.dot(P(3, 1), 1.5)
    open_dot(f, P(1, 2)); open_dot(f, P(1, 0)); open_dot(f, P(3, 0)); open_dot(f, P(3, 2))
    f.lab('O', P(0, 0), -7, -9); f.lab('1', P(1, 0), 0, -11); f.lab('3', P(3, 0), 0, -11)
    f.lab('1', P(0, 1), -10, 0); f.lab('2', P(0, 2), -10, 2)
    f.lab('$t$', P(5.0, 0), 6, -7); f.lab('$y$', P(0, 2.75), -7, 2)
    f.lab('$y=f(t)$', P(3.2, 2.5), 0, 0, ha='left')
    f.ngd_on(P(3.35, 2), P(4.45, 2), 0.5)
    return f.save()
if __name__ == '__main__':
    print(make())
