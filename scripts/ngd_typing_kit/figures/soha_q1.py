from figlib import *
def make():
    f = Fig('soha_q1', 15500, (-2.5, 2.9), (-1.5, 3.55))
    # axes
    f.ax.annotate('', xy=(2.6,0), xytext=(-2.35,0), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'))
    f.ax.annotate('', xy=(0,3.25), xytext=(0,-1.3), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'))
    f.lab('x', (2.6,0), 6, -2)
    f.lab('y', (0,3.25), 8, 4)
    f.lab('O', (0,0), -9, -9)
    f.lab('$-1$', (-1,0), -10, -14, ha='right')

    a1 = 1.5   # a+1
    a0 = 0.5   # a
    am1 = -0.5 # a-1

    # horizontal ray for x < -1 at height a+1
    f.seg((-2.15, a1), (-1, a1))
    f.lab('$y=f(x)$', (-2.15, a1), 4, 14, ha='left')

    # dashed guide lines to y-axis
    f.dashed((-1, a1), (0, a1))
    f.dashed((-1, a0), (0, a0))
    f.dashed((-1, am1), (0, am1))
    f.dashed((-1, am1), (-1, a1))
    f.lab('$a+1$', (0, a1), 10, 2, ha='left')
    f.lab('$a$', (0, a0), 10, 2, ha='left')
    f.lab('$a-1$', (0, am1), 12, 2, ha='left')

    # open circle at (-1, a+1), filled dot at (-1,a), open circle at (-1,a-1)
    f.ax.plot([-1],[a1], marker='o', mfc='white', mec='k', ms=5, zorder=5)
    f.dot((-1, a0))
    f.ax.plot([-1],[am1], marker='o', mfc='white', mec='k', ms=5, zorder=5)

    # curve for -1 <= x <= 0 : from open circle (-1,a-1) down to a trough then rising to origin area
    xs1 = np.linspace(-1, 0.05, 100)
    ys1 = 0.55*(xs1+0.15)**2 - 0.62
    f.ax.plot(xs1, ys1, color='k', lw=1.0, zorder=2)

    # curve for x>=0 rising steeply (parabola-like) through to upper right
    xs2 = np.linspace(0.0, 2.25, 100)
    ys2 = 0.78*xs2**2 - 0.05
    f.ax.plot(xs2, ys2, color='k', lw=1.0, zorder=2)

    f.ngd_on((-1.75, a1), (-1, a1), 0.5)
    return f.save()
if __name__=='__main__': print(make())
