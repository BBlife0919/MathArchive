# -*- coding: utf-8 -*-
"""2022 개정교육과정 대단원·중단원 통합 분류표 PDF.

세 장의 원본(중등 / 고등 공통·선택 / 고등 진로선택)을 하나로 재편집.
크롭이 아니라 통일된 디자인으로 재작업.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from pdf_engine import html_to_pdf_bytes  # noqa: E402


# ── 데이터: (과정명, [(letter, 대단원, [중단원...]) ...]) ──────────────
# 중단원은 (번호, 이름) — 원본 번호 그대로 유지.

MIDDLE = [
    ("중등 1", [
        ("A", "소인수분해", [(1, "소수와 합성수 및 소인수분해"), (2, "최대공약수 및 최소공배수")]),
        ("B", "정수와 유리수", [(1, "정수와 유리수"), (2, "정수와 유리수의 계산")]),
        ("C", "문자와 식·일차방정식", [(1, "문자의 사용과 식의 계산"), (2, "일차방정식의 풀이"), (3, "일차방정식의 활용")]),
        ("D", "그래프와 비례 관계", [(1, "좌표평면과 그래프"), (2, "정비례와 반비례")]),
        ("G", "도형의 기초", [(1, "기본 도형"), (2, "작도와 합동")]),
        ("H", "도형의 성질", [(1, "평면도형의 성질"), (2, "입체도형의 성질")]),
        ("I", "자료와 문제 해결", [(1, "대푯값과 도수분포표"), (2, "상대도수")]),
    ]),
    ("중등 2", [
        ("J", "수와 식의 계산", [(1, "유리수와 순환소수"), (2, "식의 계산")]),
        ("K", "부등식과 연립방정식", [(1, "일차부등식"), (2, "일차부등식 활용"), (3, "연립방정식"), (4, "연립방정식 활용")]),
        ("L", "일차함수", [(1, "일차함수와 그래프"), (2, "일차함수와 일차방정식")]),
        ("M", "삼각형의 성질", [(1, "이등변삼각형과 직각삼각형"), (2, "삼각형의 외심과 내심")]),
        ("N", "사각형의 성질", [(4, "평행사변형"), (5, "여러 가지 사각형")]),
        ("O", "도형의 닮음", [(4, "도형의 닮음"), (5, "닮음의 활용")]),
        ("P", "피타고라스 정리", [(1, "피타고라스 정리"), (2, "평면도형에의 활용"), (3, "입체도형에의 활용")]),
        ("Q", "확률", [(1, "경우의 수"), (2, "확률")]),
    ]),
    ("중등 3", [
        ("R", "실수와 근호", [(1, "제곱근과 실수"), (2, "근호를 포함한 식의 계산")]),
        ("S", "다항식과 인수분해", [(1, "다항식의 곱셈"), (2, "인수분해")]),
        ("T", "이차방정식", [(1, "이차방정식의 풀이"), (2, "이차방정식의 활용")]),
        ("U", "이차함수", [(1, "이차함수와 그래프"), (3, "이차함수의 활용")]),
        ("V", "삼각비", [(1, "삼각비"), (2, "삼각비의 활용")]),
        ("W", "원의 성질", [(1, "원과 직선"), (2, "원주각")]),
        ("X", "산포도와 상관관계", [(1, "산포도"), (2, "산점도와 상관관계")]),
    ]),
]

HIGH_COMMON = [
    ("공통수학 1", [
        ("A", "다항식", [(1, "다항식의 연산"), (2, "항등식과 나머지정리"), (3, "인수분해")]),
        ("B", "방정식과 부등식", [(1, "복소수"), (2, "이차방정식"), (3, "이차함수"), (4, "고차방정식"), (5, "연립방정식"), (6, "일차부등식"), (7, "이차부등식")]),
        ("C", "경우의 수", [(1, "경우의 수"), (2, "순열"), (3, "조합")]),
        ("D", "행렬", [(1, "행렬의 뜻"), (2, "행렬의 연산")]),
    ]),
    ("공통수학 2", [
        ("E", "도형의 방정식", [(1, "평면좌표"), (2, "직선의 방정식"), (3, "원의 방정식"), (4, "도형의 이동")]),
        ("F", "집합과 명제", [(1, "집합"), (2, "명제"), (3, "절대부등식")]),
        ("G", "함수", [(1, "함수"), (2, "유리식과 유리함수"), (3, "무리식과 무리함수")]),
    ]),
    ("대수", [
        ("H", "지수함수와 로그함수", [(1, "지수"), (2, "로그"), (3, "지수함수와 로그함수"), (4, "지수함수와 로그함수의 활용")]),
        ("I", "삼각함수", [(1, "일반각과 호도법"), (2, "삼각함수와 그래프"), (3, "사인법칙과 코사인법칙")]),
        ("J", "수열", [(1, "등차수열"), (2, "등비수열"), (3, "수열의 합"), (4, "수학적 귀납법")]),
    ]),
    ("미적분 1", [
        ("K", "함수의 극한과 연속", [(1, "함수의 극한"), (2, "함수의 연속")]),
        ("L", "미분법", [(1, "미분계수와 도함수"), (2, "접선의 방정식"), (3, "함수의 그래프"), (4, "도함수의 활용")]),
        ("M", "적분법", [(1, "부정적분"), (2, "정적분"), (3, "정적분의 활용")]),
    ]),
    ("확률과 통계", [
        ("N", "경우의 수", [(1, "중복순열"), (2, "중복조합"), (3, "이항정리")]),
        ("O", "확률", [(1, "확률의 정의와 덧셈정리"), (2, "조건부 확률"), (3, "독립시행")]),
        ("P", "통계", [(1, "확률분포"), (2, "이항분포"), (3, "정규분포"), (4, "통계적 추정")]),
    ]),
    ("미적분 2", [
        ("Q", "수열의 극한", [(1, "수열의 극한"), (2, "급수")]),
        ("R", "미분법", [(1, "여러 가지 함수의 미분"), (2, "여러 가지 미분법"), (3, "접선의 방정식"), (4, "함수의 그래프"), (5, "도함수의 활용")]),
        ("S", "적분법", [(1, "여러 가지 적분법"), (2, "정적분의 활용")]),
    ]),
    ("기하", [
        ("T", "이차곡선", [(1, "이차곡선"), (2, "이차곡선의 접선")]),
        ("U", "공간도형과 공간좌표", [(1, "공간도형"), (2, "공간좌표")]),
        ("V", "평면벡터", [(1, "벡터의 연산"), (2, "벡터의 성분과 내적"), (3, "도형의 방정식")]),
    ]),
]

HIGH_CAREER = [
    ("경제 수학", [
        ("A", "수와 경제", [(1, "수와 생활경제"), (2, "수열과 금융")]),
        ("B", "함수와 경제", [(1, "함수와 경제 현상"), (2, "함수의 활용")]),
        ("C", "행렬과 경제", [(1, "행렬과 경제 현상"), (2, "행렬의 활용")]),
        ("D", "미분과 경제", [(1, "미분과 경제 현상"), (2, "미분의 활용")]),
        ("E", "인공지능과 빅데이터", [(1, "인공지능의 개념과 역사"), (2, "빅데이터와 인공지능")]),
    ]),
    ("인공지능 수학", [
        ("F", "텍스트 데이터 처리", [(1, "텍스트 데이터 표현"), (2, "텍스트 데이터 분석")]),
        ("G", "이미지 데이터 처리", [(1, "이미지 데이터 표현"), (2, "이미지 데이터 분석")]),
        ("H", "예측과 최적화", [(1, "경향성과 예측"), (2, "최적화")]),
        ("I", "인공지능과 수학탐구", [(1, "합리적 의사 결정"), (2, "인공지능과 수학 탐구")]),
    ]),
    ("직무 수학", [
        ("J", "수와 연산", [(1, "수와 사칙연산"), (2, "단위 환산")]),
        ("K", "변화와 관계", [(1, "비율과 백분율"), (2, "규칙성과 변화"), (3, "식과 문제해결")]),
        ("L", "도형과 측정", [(1, "도형의 관찰과 표현"), (2, "도형의 측정")]),
        ("M", "자료와 가능성", [(1, "경우의 수와 가능성"), (2, "자료의 정리와 해석")]),
    ]),
]

SECTIONS = [
    ("중학교", "중등 · 2022 개정교육과정", "mid", MIDDLE),
    ("고등학교 · 공통 / 일반선택", "고등 · 2022 개정교육과정", "com", HIGH_COMMON),
    ("고등학교 · 진로선택", "고등 · 2022 개정교육과정", "car", HIGH_CAREER),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_course(course_name, units):
    rows = []
    for letter, unit, subs in units:
        chips = "".join(
            f'<span class="sub"><i>{n}</i>{esc(name)}</span>' for n, name in subs
        )
        rows.append(
            f'<tr><td class="unit"><span class="badge">{letter}</span>'
            f'<span class="uname">{esc(unit)}</span></td>'
            f'<td class="subs">{chips}</td></tr>'
        )
    return (
        f'<div class="course">'
        f'<div class="chead">{esc(course_name)}</div>'
        f'<table class="ctab">{"".join(rows)}</table>'
        f'</div>'
    )


def render_section(idx, title, sub, key, courses):
    blocks = "".join(render_course(c, u) for c, u in courses)
    return (
        f'<section class="sec {key}">'
        f'<div class="shead">'
        f'<span class="snum">{idx:02d}</span>'
        f'<span class="stexts"><span class="stitle">{esc(title)}</span>'
        f'<span class="ssub">{esc(sub)}</span></span></div>'
        f'<div class="grid">{blocks}</div>'
        f'</section>'
    )


CSS = """
@page { size: A4; margin: 12mm 11mm 11mm 11mm; }
* { box-sizing: border-box; }
body {
  font-family: 'Apple SD Gothic Neo', 'Pretendard', 'Noto Sans KR', sans-serif;
  color: #1f2430; margin: 0; -webkit-print-color-adjust: exact;
  font-feature-settings: "tnum";
}
.cover { height: 252mm; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; page-break-after: always; }
.cover .kline { width: 52px; height: 4px; background:#2f6f5e; margin: 0 auto 18px; border-radius:2px; }
.cover .ey { font-size: 12px; font-weight:700; letter-spacing:5px; color:#9aa2ad; margin-bottom:10px; }
.cover h1 { font-size: 34px; font-weight: 800; letter-spacing:-.6px; margin: 0 0 10px; }
.cover .sub { font-size: 13.5px; color:#6b7280; letter-spacing:.4px; }
.cards { display:flex; gap:14px; margin-top:34px; }
.card { width: 150px; border:1px solid #e5e7eb; border-top:3px solid var(--cc); border-radius:9px; padding:16px 12px; }
.card .cn { font-size: 13px; font-weight:800; color:#2b303b; }
.card .cd { font-size: 10px; color:#8a929e; margin:3px 0 12px; word-break: keep-all; line-height:1.45; }
.card .cstat { display:flex; justify-content:center; gap:14px; }
.card .cstat b { display:block; font-size:19px; font-weight:800; color:var(--cc); font-variant-numeric:tabular-nums; }
.card .cstat span { font-size:9.5px; color:#9aa2ad; }
.card.mid { --cc:#2f8f74; } .card.com { --cc:#3d5aa9; } .card.car { --cc:#c8892f; }
.cover .foot { margin-top:30px; font-size:10px; color:#b3b9c2; letter-spacing:.3px; }

.sec { margin-bottom: 14px; break-inside: avoid; }
.shead { display:flex; align-items:center; gap:11px; margin: 0 0 9px; padding-bottom:7px; border-bottom:2px solid var(--ac); }
.snum { font-size: 22px; font-weight:800; color:var(--ac); font-variant-numeric: tabular-nums; }
.stexts { display:flex; flex-direction:column; }
.stitle { font-size: 15px; font-weight:800; letter-spacing:-.3px; color:#1f2430; }
.ssub { font-size: 10.5px; color:#8a929e; margin-top:1px; }
.sec.mid { --ac:#2f8f74; --acbg:#eaf5f1; --acsub:#3f6f5f; }
.sec.com { --ac:#3d5aa9; --acbg:#eef1f9; --acsub:#42517c; }
.sec.car { --ac:#c8892f; --acbg:#faf2e5; --acsub:#8a6320; }

.grid { column-count: 2; column-gap: 9px; }
.course { break-inside: avoid; margin-bottom: 9px; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden; }
.chead {
  background: var(--acbg); color: var(--acsub);
  font-size: 12px; font-weight:800; padding: 6px 10px;
  border-bottom:1px solid var(--ac); letter-spacing:-.2px;
}
.ctab { width:100%; border-collapse:collapse; }
.ctab td { vertical-align: middle; padding: 5px 8px; border-top:1px solid #f0f1f3; }
.ctab tr:first-child td { border-top:none; }
.unit { width: 33%; white-space:nowrap; }
.badge {
  display:inline-block; width:17px; height:17px; line-height:17px; text-align:center;
  border-radius:5px; background:var(--ac); color:#fff; font-size:10px; font-weight:800;
  margin-right:6px; vertical-align:middle;
}
.uname { font-size: 11.5px; font-weight:700; color:#2b303b; vertical-align:middle; }
.subs { line-height: 1.9; }
.sub { display:inline-block; font-size: 10.5px; color:#3a4150; margin: 1px 4px 1px 0; white-space:nowrap; }
.sub i {
  font-style:normal; display:inline-block; min-width:13px; height:13px; line-height:13px;
  text-align:center; font-size:8.5px; font-weight:700; color:var(--acsub);
  background:var(--acbg); border-radius:3px; margin-right:3px; vertical-align:middle;
}
"""


def build_html():
    secs = "".join(
        render_section(i + 1, t, s, k, c)
        for i, (t, s, k, c) in enumerate(SECTIONS)
    )
    def counts(courses):
        u = sum(len(units) for _, units in courses)
        s = sum(len(subs) for _, units in courses for *_, subs in units)
        return u, s

    stats = {
        "mid": ("중학교", "중등 1 · 2 · 3", counts(MIDDLE)),
        "com": ("고등 · 공통 / 일반선택", "공통수학 · 대수 · 미적분 · 확통 · 기하", counts(HIGH_COMMON)),
        "car": ("고등 · 진로선택", "경제 · 인공지능 · 직무 수학", counts(HIGH_CAREER)),
    }
    cards = "".join(
        f'<div class="card {k}"><div class="cn">{esc(nm)}</div>'
        f'<div class="cd">{esc(sub)}</div>'
        f'<div class="cstat"><span><b>{u}</b>대단원</span><span><b>{s}</b>중단원</span></div></div>'
        for k, (nm, sub, (u, s)) in stats.items()
    )
    cover = (
        '<div class="cover">'
        '<div class="kline"></div>'
        '<div class="ey">2022 개정교육과정</div>'
        '<h1>수학 교육과정 단원 체계표</h1>'
        '<div class="sub">중학교 &amp; 고등학교 전 과정 통합 정리</div>'
        f'<div class="cards">{cards}</div>'
        '<div class="foot">MathArchive · 대단원(과정별 A~) / 중단원 체계</div>'
        '</div>'
    )
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{cover}{secs}</body></html>"


def main():
    html = build_html()
    pdf = html_to_pdf_bytes(html)
    out = Path("/Users/youngwoolee/클로드교재/수학_교육과정_단원체계표_2022개정.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf)
    print(f"저장: {out}  ({len(pdf)//1024} KB)")


if __name__ == "__main__":
    main()
