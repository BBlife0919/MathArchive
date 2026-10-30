# -*- coding: utf-8 -*-
"""진성고 jsg26f1(1학년 공통수학1) Q25 본문 그림.
실행: python3 jsg26f1_figs.py"""
import numpy as np
from figlib import Fig


def q25():
    f = Fig('jsg26f1_q25', 12000, (-0.3, 6.3), (-0.3, 6.3))
    f.poly([(0, 0), (6, 0), (6, 6), (0, 6)], lw=1.1)
    r = 1.3
    cx, cy = 3.0, 3.0
    f.circle((cx, cy), r, lw=1.0)
    angs = [162, 90, 18, -54, -126]
    labels_out = ['B', 'C', 'D', 'E', 'F']
    for a0, a1 in zip(angs, angs[1:] + [angs[0] - 360]):
        mid = (a0 + a1) / 2
        x0 = cx + r * np.cos(np.radians(a0))
        y0 = cy + r * np.sin(np.radians(a0))
        far = 6.0
        t = min((6 - cx) / (np.cos(np.radians(a0)) + 1e-9) if np.cos(np.radians(a0)) > 0 else 1e9,
                (0 - cx) / (np.cos(np.radians(a0)) - 1e-9) if np.cos(np.radians(a0)) < 0 else 1e9,
                (6 - cy) / (np.sin(np.radians(a0)) + 1e-9) if np.sin(np.radians(a0)) > 0 else 1e9,
                (0 - cy) / (np.sin(np.radians(a0)) - 1e-9) if np.sin(np.radians(a0)) < 0 else 1e9)
        x1 = cx + t * np.cos(np.radians(a0))
        y1 = cy + t * np.sin(np.radians(a0))
        f.seg((x0, y0), (x1, y1), lw=0.9)
    f.hytext('A', (cx, cy), dx=0, dy=0, fs=11)
    label_pos = {
        'B': (1.3, 5.0), 'C': (4.6, 5.0), 'D': (4.5, 1.7),
        'E': (1.9, 0.9), 'F': (0.75, 3.0),
    }
    for lab, pos in label_pos.items():
        f.hytext(lab, pos, dx=0, dy=0, fs=11)
    f.save()


if __name__ == '__main__':
    q25()
    print('done')
