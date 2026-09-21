from figlib import *
def dim_arc(f, p, q, bulge, n=60, lw=LW_D):
    """점선 곡선 치수선. bulge: 선분 pq에서 수직(왼쪽 법선 기준 +)으로 부푼 정도(데이터 단위)."""
    p, q = np.array(p, float), np.array(q, float)
    u = unit(q - p); nrm = np.array([-u[1], u[0]])
    ctrl = (p + q) / 2 + nrm * bulge * 2
    t = np.linspace(0, 1, n)[:, None]
    pts = (1 - t) ** 2 * p + 2 * (1 - t) * t * ctrl + t ** 2 * q
    f.ax.plot(pts[:, 0], pts[:, 1], color="k", lw=lw, ls=(0, (3.2, 2.6)), zorder=2)
    return (p + q) / 2 + nrm * bulge
