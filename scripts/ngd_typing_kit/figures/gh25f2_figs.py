# -*- coding: utf-8 -*-
"""광휘고 2025 2학기기말 공통수학2 Q9 그림(무리함수 f(x)=-sqrt(x-2)+4, 원본 PDF 그래프 누락으로 재구성).
실행: python3 gh25f2_figs.py"""
import numpy as np
from figlib import Fig


def q09():
    f = Fig('gh25f2_q09', 17000, (-0.8, 10.5), (-1.3, 6.3))
    f.ax.annotate('', xy=(10.2, 0), xytext=(-0.6, 0),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.ax.annotate('', xy=(0, 6.0), xytext=(0, -0.6),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'), zorder=2)
    f.hytext('O', (0, 0), dx=-6, dy=-7, fs=7.5, ha='right', va='top')
    f.hytext('x', (10.2, 0), dx=7, dy=-1, italic=True, fs=8.5, ha='left')
    f.hytext('y', (0, 6.0), dx=0, dy=5, italic=True, fs=8.5, va='bottom')

    xs = np.linspace(2.0, 10.3, 300)
    ys = -np.sqrt(xs - 2) + 4
    f.ax.plot(xs, ys, color='k', lw=1.1, zorder=3)

    f.dot((2, 4))
    f.lab('$(2,~4)$', (2, 4), dx=-4, dy=8, fs=7.5, ha='right')
    f.dashed((0, 4), (2, 4))
    f.hytext('4', (0, 4), dx=-6, dy=0, fs=7.5, ha='right', va='center')
    f.dashed((2, 0), (2, 4))
    f.hytext('2', (2, 0), dx=0, dy=-9, fs=7.5, ha='center', va='top')

    # x=6일 때 y=-sqrt(4)+4=2 참고점
    f.dot((6, 2))
    f.lab('$(6,~2)$', (6, 2), dx=6, dy=-10, fs=7.5, ha='left')
    f.save()


if __name__ == '__main__':
    q09()
    print('done')
