"""NGD 문제 그림 공용 라이브러리 (matplotlib).

규칙
- 그림은 '최종 삽입 크기'(HWPUNIT) 그대로 그린다. 1인치=7200 HWPUNIT. 글자는 실제 pt 크기(기본 9.5pt).
- 좌표는 equal aspect. xlim/ylim에 라벨 여백까지 포함해서 준다.
- 점 라벨은 정체(serif), 변수(x,y,r)는 이탤릭, 각도·길이 숫자는 정체.
- 선 굵기: 도형 변 1.0pt, 보조선(점선) 0.7pt.
- NGD 마크: 회색 #CCCCCC, 6pt, 그림 선 위에 살짝 걸치게(ngd()).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, Polygon, Wedge
import numpy as np
import os, json

plt.rcParams["font.family"] = "STIXGeneral"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "png")
os.makedirs(OUT, exist_ok=True)

FS = 9.5          # 라벨 기본 글자크기(pt)
LW = 1.0          # 실선 굵기
LW_D = 0.7        # 점선 굵기
DPI = 600


def P(x, y):
    return np.array([float(x), float(y)])


def unit(v):
    v = np.asarray(v, float)
    return v / np.hypot(*v)


def rot(v, deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


class Fig:
    def __init__(self, name, w_hwp, xlim, ylim):
        self.name = name
        self.w_hwp = w_hwp
        self.xlim, self.ylim = xlim, ylim
        dx, dy = xlim[1] - xlim[0], ylim[1] - ylim[0]
        self.w_in = w_hwp / 7200.0
        self.h_in = self.w_in * dy / dx
        self.h_hwp = round(self.h_in * 7200)
        self.fig = plt.figure(figsize=(self.w_in, self.h_in), dpi=DPI)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.pt_per_unit = 72.0 * self.w_in / dx   # 데이터 1단위가 몇 pt인가

    # ---- 기본 도형 ----
    def seg(self, p, q, lw=LW, ls="-", color="k", z=2):
        self.ax.plot([p[0], q[0]], [p[1], q[1]], ls=ls, lw=lw, color=color,
                     solid_capstyle="round", dash_capstyle="butt", zorder=z)

    def dashed(self, p, q, lw=LW_D):
        self.seg(p, q, lw=lw, ls=(0, (3.2, 2.6)))

    def poly(self, pts, lw=LW, fill=None, z=1.5, close=True):
        pts = [tuple(p) for p in pts]
        if fill:
            self.ax.add_patch(Polygon(pts, closed=True, fill=True, fc=fill, ec="none", zorder=z - 0.5))
        xs = [p[0] for p in pts] + ([pts[0][0]] if close else [])
        ys = [p[1] for p in pts] + ([pts[0][1]] if close else [])
        self.ax.plot(xs, ys, color="k", lw=lw, solid_joinstyle="round", zorder=z)

    def circle(self, c, r, lw=LW, fill=None, z=1.5):
        if fill:
            self.ax.add_patch(Circle(c, r, fc=fill, ec="none", zorder=z - 0.5))
        self.ax.add_patch(Circle(c, r, fill=False, ec="k", lw=lw, zorder=z))

    def arc(self, c, r, a0, a1, lw=LW, ls="-", z=2):
        self.ax.add_patch(Arc(c, 2 * r, 2 * r, theta1=a0, theta2=a1, lw=lw, ls=ls, ec="k", zorder=z))

    def wedge_fill(self, c, r, a0, a1, fc, z=0.5):
        self.ax.add_patch(Wedge(c, r, a0, a1, fc=fc, ec="none", zorder=z))

    def fill_poly(self, pts, fc, z=0.5):
        self.ax.add_patch(Polygon([tuple(p) for p in pts], closed=True, fc=fc, ec="none", zorder=z))

    def dot(self, p, r_pt=1.6):
        self.ax.plot([p[0]], [p[1]], "o", ms=r_pt * 2, color="k", zorder=5)

    # ---- 라벨 ----
    def lab(self, text, p, dx=0, dy=0, ha="center", va="center", italic=False, fs=None, weight="normal"):
        """p: 데이터 좌표, dx/dy: pt 단위 오프셋. text는 mathtext 허용 ($..$)."""
        style = "italic" if italic else "normal"
        self.ax.annotate(text, xy=p, xytext=(dx, dy), textcoords="offset points",
                         ha=ha, va=va, fontsize=fs or FS, fontstyle=style, fontweight=weight, zorder=6)

    def name_pt(self, text, p, dx, dy, **kw):
        """점 이름(대문자)."""
        self.lab(text, p, dx, dy, **kw)

    def deg(self, value):
        return f"{value}°"

    # ---- 각도/직각/눈금 ----
    def angle(self, v, p1, p2, r, text=None, tr=None, lw=0.7, double=False, dtext=(0, 0), fs=None, italic=False):
        """꼭짓점 v에서 반직선 v->p1, v->p2 사이 각에 호(반지름 r, 데이터 단위)를 그린다.
        p1에서 p2로 반시계 방향 최소각을 잡는다. text가 있으면 각의 이등분선 위 거리 tr에 놓는다."""
        a1 = np.degrees(np.arctan2(p1[1] - v[1], p1[0] - v[0]))
        a2 = np.degrees(np.arctan2(p2[1] - v[1], p2[0] - v[0]))
        d = (a2 - a1) % 360
        if d > 180:
            a1, a2 = a2, a1
            d = 360 - d
        self.arc(v, r, a1, a1 + d, lw=lw)
        if double:
            self.arc(v, r * 1.25, a1, a1 + d, lw=lw)
        if text is not None:
            mid = np.radians(a1 + d / 2)
            if tr is None:
                # 규칙(2026-09-21): 각도 숫자는 호 바로 바깥에 붙인다(글자 가장자리가 호에서 ~2.5pt).
                w, h = self.text_size(text, fs, italic)
                half = abs(np.cos(mid)) * w / 2 + abs(np.sin(mid)) * h / 2
                tr = r + (half + 2.5) / self.pt_per_unit
            pos = (v[0] + tr * np.cos(mid), v[1] + tr * np.sin(mid))
            self.lab(text, pos, dtext[0], dtext[1], fs=fs, italic=italic)
        return a1, d

    def text_size(self, text, fs=None, italic=False):
        """텍스트 실제 크기(pt): (폭, 높이)."""
        t = self.ax.text(0, 0, text, fontsize=fs or FS, fontstyle="italic" if italic else "normal")
        self.fig.canvas.draw()
        bb = t.get_window_extent(self.fig.canvas.get_renderer())
        t.remove()
        return bb.width * 72.0 / DPI, bb.height * 72.0 / DPI

    def dimarc(self, p, q, bulge, text=None, fs=None, italic=False, lw=LW_D, pad=2.5, n=400):
        """길이 표시 점선 곡선. 규칙(2026-09-21): 길이 숫자는 점선 '사이'(곡선 중앙의 끊긴 자리)에 들어간다.
        bulge: p->q 진행방향 왼쪽 법선으로 부푼 정도(데이터 단위, 곡선 정점 기준). 곡선 정점 좌표를 반환."""
        p, q = np.array(p, float), np.array(q, float)
        u = q - p
        nrm = np.array([-u[1], u[0]]) / np.hypot(*u)
        ctrl = (p + q) / 2 + nrm * bulge * 2
        t = np.linspace(0, 1, n)[:, None]
        pts = (1 - t) ** 2 * p + 2 * (1 - t) * t * ctrl + t ** 2 * q
        seg = np.hypot(*np.diff(pts, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        mid_s = cum[-1] / 2
        top = (p + q) / 2 + nrm * bulge
        if text:
            w, h = self.text_size(text, fs, italic)
            tang = unit(u)
            half = (abs(tang[0]) * w / 2 + abs(tang[1]) * h / 2 + pad) / self.pt_per_unit
            keep = np.abs(cum - mid_s) >= half
        else:
            keep = np.ones(len(cum), bool)
        # 두 구간으로 나눠 각각 점선으로(대시 패턴이 끊긴 자리에서 다시 시작)
        left = pts[keep & (cum < mid_s)]
        right = pts[keep & (cum >= mid_s)]
        for part in (left, right):
            if len(part) > 1:
                self.ax.plot(part[:, 0], part[:, 1], ls=(0, (3.2, 2.6)), lw=lw, color="k", zorder=2, dash_capstyle="butt")
        if text:
            self.ax.annotate(text, xy=top, xytext=(0, 0), textcoords="offset points", ha="center", va="center",
                             fontsize=fs or FS, fontstyle="italic" if italic else "normal", zorder=6)
        return top

    def dimarc_pt(self, p, q, side, text=None, pt=9.0, **kw):
        """dimarc의 bulge를 pt 단위로 지정(side=+1 왼쪽/-1 오른쪽 법선). 숫자가 실선과 겹치지 않도록 pt>=8 권장."""
        return self.dimarc(p, q, side * pt / self.pt_per_unit, text, **kw)

    def ngd_on(self, p, q, frac=0.5, fs=6):
        """NGD 마크 규칙(2026-09-21): 직선(변·현·축·접선) 하나와 나란하게(각도 일치), 글자 중심을 그 선 위에 정확히 얹어
        선과 겹치게 한다. 선을 가로지르거나 곡선(원) 위에 비스듬히 놓지 말 것."""
        p, q = np.array(p, float), np.array(q, float)
        c = p + frac * (q - p)
        ang = np.degrees(np.arctan2(q[1] - p[1], q[0] - p[0]))
        while ang > 90:
            ang -= 180
        while ang <= -90:
               ang += 180
        th = np.radians(ang)
        up = np.array([-np.sin(th), np.cos(th)])          # 글자 '위' 방향
        cap = 0.68 * fs                                    # 대문자 높이(pt)
        base = c - up * (cap / 2.0) / self.pt_per_unit    # 기준선을 내려서 글자 잉크의 세로 중심을 선 위에 맞춤
        self.ax.text(base[0], base[1], "NGD", color="#CCCCCC", fontsize=fs, rotation=ang, rotation_mode="anchor",
                     ha="center", va="baseline", fontweight="bold", zorder=4)

    def rightangle(self, v, p1, p2, s, lw=0.7):
        u1, u2 = unit(np.subtract(p1, v)), unit(np.subtract(p2, v))
        a = np.add(v, s * u1)
        b = np.add(v, s * (u1 + u2))
        c = np.add(v, s * u2)
        self.ax.plot([a[0], b[0], c[0]], [a[1], b[1], c[1]], color="k", lw=lw, zorder=3)

    def ticks(self, p, q, n=1, size=0.07, gap=0.05, lw=0.8, frac=0.5):
        """선분 pq 위에 같은 길이 표시(눈금 n개)."""
        p, q = np.array(p, float), np.array(q, float)
        m = p + frac * (q - p)
        u = unit(q - p)
        nrm = np.array([-u[1], u[0]])
        for i in range(n):
            off = (i - (n - 1) / 2) * gap
            c = m + u * off
            a, b = c + nrm * size / 2, c - nrm * size / 2
            # 눈금은 선분에 비스듬히(슬래시) 표시
            a2, b2 = a + u * size * 0.25, b - u * size * 0.25
            self.ax.plot([a2[0], b2[0]], [a2[1], b2[1]], color="k", lw=lw, zorder=3)

    def ngd(self, p, ang=0, fs=6):
        """NGD 마크(#CCCCCC, 6pt) — 그림 선 위에 걸치도록 p를 선 위 좌표로 준다."""
        self.ax.text(p[0], p[1], "NGD", color="#CCCCCC", fontsize=fs, rotation=ang,
                     ha="center", va="center", fontweight="bold", zorder=4)

    # ---- 저장 ----
    def save(self):
        path = os.path.join(OUT, f"{self.name}.png")
        self.fig.savefig(path, dpi=DPI, transparent=False, facecolor="white")
        plt.close(self.fig)
        from PIL import Image
        im = Image.open(path)
        info = dict(name=self.name, file=path, w_px=im.size[0], h_px=im.size[1],
                    w_hwp=self.w_hwp, h_hwp=self.h_hwp)
        with open(os.path.join(OUT, f"{self.name}.json"), "w") as f:
            json.dump(info, f)
        return info
