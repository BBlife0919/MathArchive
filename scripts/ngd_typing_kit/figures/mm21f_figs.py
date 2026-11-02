# -*- coding: utf-8 -*-
"""명문고 2021 2학기중간 수학(하) Q5 그림: X->X 사상도(f).
실행: python3 mm21f_figs.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import Fig
import matplotlib.patches as mpatches


def q05():
    f = Fig('mm21f_q05', 20000, (-2.2, 7.0), (-2.6, 3.0))
    cx1, cx2 = 0.0, 5.0
    f.ax.add_patch(mpatches.Ellipse((cx1, 0), 1.5, 4.6, fill=False, lw=1.1))
    f.ax.add_patch(mpatches.Ellipse((cx2, 0), 1.5, 4.6, fill=False, lw=1.1))
    f.hytext('X', (cx1, 2.66), fs=11, italic=True)
    f.hytext('X', (cx2, 2.66), fs=11, italic=True)
    f.ax.annotate('', xy=(cx2 - 1.0, 2.15), xytext=(cx1 + 1.0, 2.15),
                  arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.hytext('f', ((cx1 + cx2) / 2, 2.4), fs=11, italic=True)

    labs = ['1', '2', '3', '4', '5']
    ys = [1.6, 0.8, 0.0, -0.8, -1.6]
    for lab, y in zip(labs, ys):
        f.dot((cx1, y), r_pt=1.3)
        f.hytext(lab, (cx1, y), dx=-16, fs=9.5, italic=True, ha='right')
        f.dot((cx2, y), r_pt=1.3)
        f.hytext(lab, (cx2, y), dx=16, fs=9.5, italic=True, ha='left')

    pos = dict(zip(labs, ys))
    fmap = {'1': '2', '2': '4', '3': '1', '4': '5', '5': '3'}
    for src, dst in fmap.items():
        p = (cx1 + 0.62, pos[src])
        q = (cx2 - 0.62, pos[dst])
        f.ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', lw=0.9, color='k'))
    f.save()


if __name__ == '__main__':
    q05()
    print('done')
