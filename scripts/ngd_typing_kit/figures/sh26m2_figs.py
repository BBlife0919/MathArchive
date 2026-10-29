# -*- coding: utf-8 -*-
"""소하고 sh26m2 Q06 해설용(본문) 그림: 불연속점 x=-1,0,1을 갖는 조각함수 그래프.
f(x)=-x (x<-1), f(-1)=0(고립), 혹모양(-1<x<0, 양끝 열린원 (-1,1)~(0,-1)),
f(x)=2 (0<=x<1), f(x)=(x-1)^2+1 (x>=1). 실행: python3 sh26m2_figs.py"""
import numpy as np
from figlib import Fig


def q06():
    f = Fig('sh26m2_q06', 20000, (-2.6, 2.6), (-2.3, 4.6))
    xs1 = np.linspace(-2.4, -1, 80)
    f.ax.plot(xs1, -xs1, color='k', lw=1.2, zorder=3)
    f.circle((-1, 1), 0.06, fill='white', z=4)
    f.dot((-1, 0))
    xs2a = np.linspace(-1, -0.5, 60)
    xs2b = np.linspace(-0.5, 0, 60)
    ys2a = 1 + (xs2a + 1) * ((1.6 - 1) / 0.5)
    ys2b = 1.6 + (xs2b + 0.5) * ((-1 - 1.6) / 0.5)
    f.ax.plot(xs2a, ys2a, color='k', lw=1.2, zorder=3)
    f.ax.plot(xs2b, ys2b, color='k', lw=1.2, zorder=3)
    f.circle((0, -1), 0.06, fill='white', z=4)
    f.seg((0, 2), (1, 2), lw=1.2)
    f.dot((0, 2))
    f.circle((1, 2), 0.06, fill='white', z=4)
    xs4 = np.linspace(1, 2.2, 80)
    f.ax.plot(xs4, (xs4 - 1) ** 2 + 1, color='k', lw=1.2, zorder=3)
    f.dot((1, 1))
    f.ax.annotate('', xy=(2.5, 0), xytext=(-2.5, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 4.4), xytext=(0, -2.1),
                  arrowprops=dict(arrowstyle='-|>', lw=1.0, color='k'), zorder=2)
    f.lab('$x$', (2.5, 0), dx=10, dy=-10, fs=10, italic=True)
    f.lab('$y$', (0.3, 4.1), fs=10, italic=True)
    f.lab('$O$', (0, 0), dx=-11, dy=-11, fs=10)
    f.lab('$-1$', (-1, 0), dx=0, dy=-15, fs=9)
    f.lab('$1$', (1, 0), dx=0, dy=-15, fs=9)
    f.lab('$2$', (0, 2), dx=-13, dy=0, fs=9)
    f.lab('$y=f(x)$', (1.5, 2.9), fs=9.5, ha='left')
    f.save()


if __name__ == '__main__':
    q06()
    print('done')
