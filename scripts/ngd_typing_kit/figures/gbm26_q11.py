from gbm26_common import *
def make():
    f = Fig('gbm26_q11', 12500, (-3.4, 3.7), (-2.85, 3.0))
    axes(f, -3.1, 2.65, -2.6, 2.75)
    curve(f, lambda x: x ** 2 + x - 2, -2.55, 1.55)
    f.lab('$x$', P(2.65, 0), 6, -7); f.lab('$y$', P(0, 2.75), -7, 2)
    f.lab('O', P(0, 0), -8, -9)
    f.lab('$-2$', P(-2, 0), -9, -9); f.lab('1', P(1, 0), 6, -9)
    f.lab("$y=f'(x)$", P(0.25, 2.62), 0, 0, ha='left')
    f.ngd_on(P(1.2, 0), P(2.0, 0), 0.5)
    return f.save()
if __name__ == '__main__':
    print(make())
