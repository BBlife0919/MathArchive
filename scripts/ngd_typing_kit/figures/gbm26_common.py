from figlib import *


def axes(f, x0, x1, y0, y1):
    f.ax.annotate('', xy=(x1, 0), xytext=(x0, 0), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k', shrinkA=0, shrinkB=0), zorder=2)
    f.ax.annotate('', xy=(0, y1), xytext=(0, y0), arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k', shrinkA=0, shrinkB=0), zorder=2)


def curve(f, fn, a, b, n=400, lw=LW):
    xs = np.linspace(a, b, n)
    f.ax.plot(xs, fn(xs), color='k', lw=lw, solid_capstyle='round', zorder=3)


def open_dot(f, p, ms=4.4):
    f.ax.plot([p[0]], [p[1]], 'o', ms=ms, mfc='white', mec='k', mew=0.9, zorder=6)
