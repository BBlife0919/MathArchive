from gbm26_common import *
def make():
    f = Fig('gbm26_q07', 13000, (-1.3, 3.55), (-1.05, 2.9))
    axes(f, -1.05, 2.65, -0.9, 2.65)
    f.seg(P(-0.9, -0.9), P(1.62, 1.62))
    curve(f, lambda x: x ** 2, -0.3, 1.5)
    a, b = 0.55, 1.4
    for x in (a, 1, b):
        f.dashed(P(x, 0), P(x, x ** 2))
        f.dashed(P(0, x ** 2), P(x, x ** 2))
    f.lab('$y$', P(0, 2.65), 6, 2); f.lab('$x$', P(2.65, 0), 6, -6)
    f.lab('O', P(0, 0), 7, -9)
    f.lab('$a$', P(a, 0), 0, -10); f.lab('1', P(1, 0), 1, -10); f.lab('$b$', P(b, 0), 0, -10)
    f.lab('$f(a)$', P(0, a ** 2), -4, 3, ha='right'); f.lab('1', P(0, 1), -7, 0); f.lab('$f(b)$', P(0, b ** 2), -4, 0, ha='right')
    f.lab('$y=f(x)$', P(0.98, 2.0), 0, 6, ha='right') if False else None
    f.lab('$y=f(x)$', P(1.45, 2.5), 0, 0, ha='left')
    f.lab('$y=x$', P(1.72, 1.55), 3, 0, ha='left')
    f.ngd_on(P(-0.9, -0.9), P(-0.4, -0.4), 0.5)
    return f.save()
if __name__ == '__main__':
    print(make())
