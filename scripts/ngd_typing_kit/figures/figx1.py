"""Q2~Q8용 보조 함수 (figlib 확장; figlib.py는 수정하지 않음)."""
from figlib import *

def darc(f, p, q, bulge, lw=LW_D, n=60):
    """p,q 사이를 잇는 점선 곡선(이차 베지어). bulge>0이면 p->q 진행방향의 왼쪽으로 부푼다(선분 길이 대비 비율)."""
    p, q = np.array(p, float), np.array(q, float)
    m = (p + q) / 2
    u = q - p
    nrm = np.array([-u[1], u[0]])
    c = m + nrm * bulge * 2   # 베지어 제어점(곡선 정점은 제어점의 절반 높이)
    t = np.linspace(0, 1, n)[:, None]
    pts = (1 - t) ** 2 * p + 2 * (1 - t) * t * c + t ** 2 * q
    f.ax.plot(pts[:, 0], pts[:, 1], ls=(0, (3.2, 2.6)), lw=lw, color="k", zorder=2, dash_capstyle="butt")
    return m + nrm * bulge      # 곡선 정점

def on_seg(p, q, frac):
    p, q = np.array(p, float), np.array(q, float)
    return p + frac * (q - p)

def seg_ang(p, q):
    return np.degrees(np.arctan2(q[1] - p[1], q[0] - p[0]))
