from gbm26_common import *
def make():
    t = 0.62
    f = Fig('gbm26_q20', 15000, (-1.25, 4.75), (-1.4, 2.95))
    Pp, Qq, H, O = P(t, t * t - t), P(t, np.sqrt(3 * t + 1) - 1), P(t, 0), P(0, 0)
    f.fill_poly([O, Pp, H], '#D9D9D9'); f.fill_poly([O, H, Qq], '#D9D9D9')
    axes(f, -1.05, 2.9, -1.2, 2.45)
    curve(f, lambda x: x ** 2 - x, -0.8, 2.05)
    curve(f, lambda x: np.sqrt(3 * x + 1) - 1, -0.15, 2.4)
    f.seg(P(t, -0.75), P(t, 2.35), lw=1.0)
    f.seg(O, Pp, lw=0.8); f.seg(O, Qq, lw=0.8)
    f.lab('$x$', P(2.9, 0), 6, -7, fs=7.6); f.lab('$y$', P(0, 2.45), -7, 5, fs=7.6)
    f.lab('O', P(0, 0), -10, -8, fs=7.6)
    f.lab('$x=t$', P(t, 2.35), 0, 9, fs=7.6)
    f.lab('P', Pp, 7, -8, fs=7.6); f.lab('Q', Qq, -8, 9, fs=7.6); f.lab('H', H, 8, 7, fs=7.6)
    f.lab('$y=x^{2}-x$', P(2.15, 2.32), 2, 1, ha='left', fs=7.6)
    f.lab('$y=\\sqrt{3x+1}-1$', P(2.05, 0.95), 0, 0, ha='left', fs=7.6)
    f.ngd_on(P(-1.0, 0), P(-0.45, 0), 0.5)
    return f.save()
if __name__ == '__main__':
    print(make())
