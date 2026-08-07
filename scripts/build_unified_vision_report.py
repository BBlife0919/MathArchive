#!/usr/bin/env python3
"""통합 비전 v3 PDF 리포트 생성 (대치동 노하우 + 5에이전트 교차검증 결합).

실행:
    python3 scripts/build_unified_vision_report.py

출력:
    output/통합비전_v3_대치동노하우결합.pdf
"""
from __future__ import annotations

import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "통합비전_v3_대치동노하우결합.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)


HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>통합 비전 v3 — 대치동 노하우 결합</title>
<style>
  @page { size: A4; margin: 14mm 14mm 14mm 14mm; }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, "Apple SD Gothic Neo", "Pretendard", "Noto Sans KR", sans-serif;
    color: #1a1a1a; line-height: 1.5; font-size: 11pt;
  }
  h1, h2, h3, h4 { color: #0d2a4d; margin: 0; }
  h1 { font-size: 28pt; font-weight: 800; letter-spacing: -.02em; }
  h2 { font-size: 18pt; font-weight: 700; margin-top: 12mm; padding-bottom: 3mm; border-bottom: 3px solid #ff6b35; }
  h3 { font-size: 13pt; font-weight: 700; margin-top: 6mm; margin-bottom: 2mm; color: #ff6b35; }
  h4 { font-size: 11pt; font-weight: 700; margin-top: 4mm; margin-bottom: 1mm; color: #444; }
  p, li { font-size: 10.5pt; }
  ul, ol { padding-left: 5mm; margin: 1mm 0 3mm; }
  li { margin-bottom: 0.5mm; }
  table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; font-size: 9.5pt; }
  th { background: #0d2a4d; color: white; padding: 2mm 3mm; text-align: left; font-weight: 600; }
  td { padding: 2mm 3mm; border-bottom: 1px solid #e0e0e0; vertical-align: top; }
  tr:nth-child(even) td { background: #f7f8fa; }
  .cover {
    page-break-after: always;
    height: 268mm; display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; padding: 20mm;
  }
  .cover-kicker {
    color: #ff6b35; font-weight: 700; font-size: 12pt; letter-spacing: .15em;
    margin-bottom: 6mm;
  }
  .cover-title { font-size: 38pt; line-height: 1.15; font-weight: 800; color: #0d2a4d; }
  .cover-subtitle { font-size: 14pt; color: #555; margin-top: 8mm; font-weight: 500; }
  .cover-meta { margin-top: 30mm; color: #888; font-size: 10pt; }
  .cover-badge {
    display: inline-block; background: #0d2a4d; color: white;
    padding: 3mm 6mm; border-radius: 30mm; font-size: 10pt; font-weight: 600;
    margin-top: 4mm;
  }
  .page-break { page-break-before: always; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3mm; }
  .card {
    background: #f7f8fa; border-left: 4px solid #ff6b35; padding: 3mm 4mm;
    border-radius: 0 2mm 2mm 0; margin-bottom: 2mm;
  }
  .card.blue { border-left-color: #0d2a4d; }
  .card.green { border-left-color: #2e7d32; }
  .card.red { border-left-color: #c62828; }
  .card-title { font-weight: 700; font-size: 10.5pt; margin-bottom: 1mm; color: #0d2a4d; }
  .card-body { font-size: 9.5pt; color: #444; }
  .badge {
    display: inline-block; padding: 0.5mm 2mm; border-radius: 2mm; font-size: 8.5pt;
    font-weight: 600; margin-right: 1mm;
  }
  .badge-a { background: #2e7d32; color: white; }
  .badge-b { background: #f9a825; color: white; }
  .badge-c { background: #c62828; color: white; }
  .badge-new { background: #ff6b35; color: white; }
  .quote {
    border-left: 4px solid #0d2a4d; padding: 2mm 4mm;
    background: #eef2f7; margin: 3mm 0; font-style: italic; color: #333;
  }
  .summary-box {
    border: 2px solid #ff6b35; padding: 4mm 5mm; border-radius: 2mm;
    background: #fff8f3; margin: 3mm 0;
  }
  .summary-box .title { color: #ff6b35; font-weight: 700; margin-bottom: 2mm; }
  .check { color: #2e7d32; font-weight: 700; }
  .warn { color: #c62828; font-weight: 700; }
  .small { font-size: 9pt; color: #666; }
  pre.flow {
    background: #1a1a1a; color: #d4ff60; padding: 4mm; font-size: 8.5pt;
    border-radius: 2mm; line-height: 1.4; overflow-x: auto;
    font-family: "SF Mono", Menlo, Monaco, monospace;
  }
  .roadmap-row {
    display: grid; grid-template-columns: 28mm 1fr; gap: 4mm;
    padding: 3mm 0; border-bottom: 1px solid #eee;
  }
  .roadmap-row .phase {
    background: #0d2a4d; color: white; padding: 2mm 3mm;
    font-weight: 700; font-size: 10pt; text-align: center;
    border-radius: 2mm; align-self: start;
  }
  .roadmap-row .phase.now { background: #ff6b35; }
  footer-note { font-size: 8.5pt; color: #888; text-align: center; }
</style>
</head>
<body>

<!-- ===================== COVER ===================== -->
<div class="cover">
  <div class="cover-kicker">EUM ACADEMY · 통합 운영 비전 v3</div>
  <div class="cover-title">
    내신 성적 운영자<br>
    <span style="color:#ff6b35;">시스템 청사진</span>
  </div>
  <div class="cover-subtitle">
    수업 · 클리닉 · 학생 카드 · 카톡 자동화 통합 설계
  </div>
  <div class="cover-badge">대치동 7대 노하우 + 5에이전트 교차검증 + /근본 자문</div>
  <div class="cover-meta">
    이영우 강사 / __DATE__<br>
    철산·광명 라인 · MathDB 기반
  </div>
</div>

<!-- ===================== 1. 한 화면 요약 ===================== -->
<h2>1. 한 화면 요약 — 시스템 전체 구조</h2>

<div class="summary-box">
  <div class="title">핵심 명제</div>
  사용자 비전은 <b>콘텐츠</b>(문제·시험지·교재)에서 출발했고, 대치동 7대 노하우는 <b>학생 단위 운영</b>이 본질이다.
  이 둘이 결합되는 지점이 <b>학생 개인 카드</b>이며, 모든 자동화(클리닉·카톡·진도표·교차연습)는 이 단일 허브를 통과한다.
</div>

<pre class="flow">
[정체성] "내신 성적 운영자(매니저)"
       ↓
[2층 구조]  쇼잉(증거)  +  점수 엔진(인출·분산·전이·교차·메타인지)
       ↓
[4트랙]
  ① 강사 자동화 — 학교별 내신 프로토콜, 주간 SLA, 상담 스크립트
  ② 수학 클리닉 — Q-M Chart + 오류코드 + 인출 3 + D+3/7/14/30
  ③ 수업 운영   — 3+1 블록 × 4, 워밍업 인출, 누적 + 교차 셔플
  ④ 소통 자동화 — AI+강사 하이브리드 카톡 주간 보고
       ↓
[허브] 학생 개인 카드 (Single Source of Truth)
       ↓ join
[MathDB 자산] questions · solutions · clinic_entries · flagged_problems
       ↓
[발송 채널] 솔라피 알림톡 + PDF 묶음 + Streamlit 학부모 공유 URL
</pre>

<!-- ===================== 2. 5에이전트 교차검증 결과 ===================== -->
<h2>2. 5에이전트 교차검증 결과</h2>

<table>
  <thead>
    <tr><th style="width:7mm">#</th><th style="width:30mm">관점</th><th style="width:15mm">등급</th><th>핵심 결론 / 가장 시급한 보강</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>학습과학 5원리</td>
      <td><span class="badge badge-b">B+</span></td>
      <td>인출·분산·메타인지는 우수. <b>교차연습(Interleaving)</b>·<b>확장분산(D+30)</b>·<b>메타인지 예측</b> 누락 — 현 blocked 구조는 단기 유창성↑ but 내신 변별문항 대응력↓</td>
    </tr>
    <tr>
      <td>2</td>
      <td>대치동 노하우 매핑</td>
      <td><span class="badge badge-b">B</span></td>
      <td>콘텐츠 자동화는 A급, 학생 운영 레이어 비어있음. <b>학생 카드 = Q-M Chart + 진도표 + 관리대장의 공통 허브</b>로 설계 시 3개 노하우 동시 흡수</td>
    </tr>
    <tr>
      <td>3</td>
      <td>기술 구현·MathDB 자산</td>
      <td>—</td>
      <td>학생 카드: <b>자체 DB(students 확장) + Streamlit `student_card.py`</b> / 카톡: <b>솔라피 알림톡</b> / AI: <b>Claude Haiku 4.5</b> (월 ~$1)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>학부모 신뢰·결제유지</td>
      <td>조건부</td>
      <td>AI 카톡 자동화는 강력하지만 <b>AI 티 나는 순간 신뢰 0</b>. <span class="warn">개인정보 동의서 + 알림톡 사업자 등록 + AI+강사 1문장 하이브리드</span> 강제</td>
    </tr>
    <tr>
      <td>5</td>
      <td>확장성·SaaS</td>
      <td>시나리오 B</td>
      <td>5년 후 <b>철산·광명 3~5개 학원 라이센싱 + 자기 학원 운영 (연 1~3억)</b>. 지금 행동: <b>학생 카드 스키마를 멀티 테넌트 전제로 설계</b></td>
    </tr>
  </tbody>
</table>

<!-- ===================== 3. 대치동 노하우 매핑 ===================== -->
<h2>3. 대치동 7대 노하우 × 사용자 시스템 매핑</h2>

<table>
  <thead>
    <tr>
      <th style="width:50mm">대치동 노하우 (학관노 2017)</th>
      <th style="width:50mm">사용자 시스템 현재</th>
      <th style="width:20mm">상태</th>
      <th>개선 행동</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>① Q-M Chart 오답 코드<br><span class="small">Q1-Q3(개념) / M1-M3(실수). 학생 자기기록 → 강사 검수 → 2~4주 그래프</span></td>
      <td>클리닉 오류코드 5분류 (개념누락·조건해석·전략선택·계산실수·시간관리)</td>
      <td><span class="badge badge-b">부분</span></td>
      <td>학생 자기기록 워크플로우 추가 + 2~4주 단위 그래프 자동 생성</td>
    </tr>
    <tr>
      <td>② 과제정밀평가<br><span class="small">정량(매일 A/B/C/D) + 정성(월 2회 4항목)</span></td>
      <td>주간 SLA (개념만 정의, 실제 평가표 없음)</td>
      <td><span class="badge badge-b">부분</span></td>
      <td>4항목 평가표(풀이노트/서술형/교재표시/2차풀이) 표준화 + 학생 카드 자동 기록</td>
    </tr>
    <tr>
      <td>③ Walk-Run-Fly 3단계<br><span class="small">학생 수준별 자기학습 → 교내경시 → 외부경시</span></td>
      <td>미니테스트 프리셋 (난이도 고정)</td>
      <td><span class="badge badge-c">미흡수</span></td>
      <td>학생별 트랙(W/R/F) 필드 추가, 시험지 생성 시 트랙별 풀(pool) 분리</td>
    </tr>
    <tr>
      <td>④ 스터디 플래너 시각화<br><span class="small">학생 일과 시간 색깔 분류</span></td>
      <td>없음</td>
      <td><span class="badge badge-c">미흡수</span></td>
      <td>학생 카드 1섹션으로 통합 (시간표·색상 코드)</td>
    </tr>
    <tr>
      <td>⑤ 개별 진도표<br><span class="small">단원·유형별 1차/2차/3차 처리 체크</span></td>
      <td>questions DB는 있으나 학생별 풀이 이력 join 없음</td>
      <td><span class="badge badge-c">미흡수</span></td>
      <td>student_progress 테이블 신설 + 1·2·3차 체크박스 자동 PDF</td>
    </tr>
    <tr>
      <td>⑥ 클래스 관리대장<br><span class="small">학생별 일자별 누적 운영 기록</span></td>
      <td>없음</td>
      <td><span class="badge badge-c">미흡수</span></td>
      <td>학생 카드의 본체로 — student_log 테이블(JSON, append-only)</td>
    </tr>
    <tr>
      <td>⑦ 표준화 9양식<br><span class="small">수업자료/모의고사/플래너/주간업무보고서 등</span></td>
      <td>시험지·교재 PDF 2종</td>
      <td><span class="badge badge-b">부분</span></td>
      <td>주간 보고서·진도표·정밀평가표·관리대장 PDF 템플릿 5종 추가</td>
    </tr>
  </tbody>
</table>

<div class="summary-box">
  <div class="title">매핑의 결론</div>
  사용자에게 빠진 공통 결손은 <b>"학생 단위 종단 트래킹"</b>이며, 진도표·관리대장·플래너가 모두 같은 빈자리를 가리킨다.
  → <b>학생 카드 하나가 3개 노하우 동시 흡수 가능</b>한 레버 포인트.
</div>

<!-- ===================== 4. 최적 수업방식 ===================== -->
<h2>4. 최적 수업방식 (v3) — 3+1 블록 + 교차 셔플</h2>

<h3>4-1. 골격 (주 2회 × 4시간 × 8주 = 16회 / 64시간)</h3>

<table>
  <thead>
    <tr><th>블록</th><th>주차</th><th>수업</th><th>신규 유형</th><th>총복습 누적 비율</th></tr>
  </thead>
  <tbody>
    <tr><td>A 기초</td><td>1-2</td><td>1~4</td><td>12</td><td>A 80% + 기초개념 20%</td></tr>
    <tr><td>B 중간</td><td>3-4</td><td>5~8</td><td>13</td><td>B 70% + A 30%</td></tr>
    <tr><td>C 심화</td><td>5-6</td><td>9~12</td><td>13</td><td>C 60% + B 25% + A 15%</td></tr>
    <tr><td>D 마무리 + 실전</td><td>7-8</td><td>13~16</td><td>12</td><td>D 30% + C 25% + B 25% + A 20%</td></tr>
  </tbody>
</table>

<h3>4-2. 4시간 수업 구성 (신규)</h3>
<div class="grid-2">
  <div class="card blue">
    <div class="card-title">0~15분 · 워밍업 인출 퀴즈</div>
    <div class="card-body">
      전시간 2문제 + 오래된 블록 1문제 + <b>다른 단원 1문제(NEW)</b>.
      마지막 항목이 교차연습(Interleaving) 핵심.
    </div>
  </div>
  <div class="card">
    <div class="card-title">15~205분 · 유형 4개 × 45분</div>
    <div class="card-body">
      개념(8분) → 해설(10분) → 학생 풀이 15~18분 → 피드백.
      강사는 1:1 코칭, 막힌 포인트 즉시 식별.
    </div>
  </div>
  <div class="card green">
    <div class="card-title">205~230분 · 오늘 유형 인출 테스트</div>
    <div class="card-body">
      당일 4유형 각 1문제 + <b>학생 자기예측 정답률 입력(NEW)</b>.
      실제 vs 예측 격차가 메타인지 시각화.
    </div>
  </div>
  <div class="card">
    <div class="card-title">230~240분 · 마무리</div>
    <div class="card-body">
      숙제 공지 + 오답노트 회수 + Q-M 코드 부여 (학생 자기기록).
    </div>
  </div>
</div>

<h3>4-3. v3 추가된 학습과학 보강 3가지</h3>
<ol>
  <li><b>교차연습</b> — 워밍업에 다른 단원 1문제 셔플 (Rohrer & Taylor 2007: 변별 ↑20%)</li>
  <li><b>확장분산</b> — 클리닉 재도전을 D+3/7/14 → <b>D+3/7/14/30/시험2주전</b>로 확장 (장기 보존)</li>
  <li><b>메타인지 예측</b> — 매 수업 끝 "자가예측 정답률" 입력 → 학생 카드 누적 → 격차 그래프</li>
</ol>

<!-- ===================== 5. 최적 클리닉 방식 ===================== -->
<h2>5. 최적 클리닉(관리)방식 (v3) — Q-M Chart 통합</h2>

<h3>5-1. 점수 엔진 4대 구성 (대치동 매핑 반영)</h3>
<table>
  <thead><tr><th>구성</th><th>사용자 v2</th><th>v3 보강 (대치동 결합)</th></tr></thead>
  <tbody>
    <tr><td>① 오류코드</td><td>5분류 (개념/조건/전략/계산/시간)</td><td>Q1-Q3 / M1-M3 매핑 추가 + <b>학생 자기기록 강제</b> → 강사 검수 워크플로우</td></tr>
    <tr><td>② 즉시 인출 3문항</td><td>유사 2 + 변형 1</td><td>+ <b>1문항은 다른 단원에서 교차 추출</b></td></tr>
    <tr><td>③ 분산복습 스케줄</td><td>D+3 / D+7 / D+14</td><td>+ <b>D+30 + 시험 2주 전</b> 자동 재출제 (확장분산)</td></tr>
    <tr><td>④ 주간 리포트</td><td>오류코드 분포 그래프</td><td>+ <b>Q-M 6숫자 자동 집계 + 자가예측 격차</b> 시각화. 학부모 카톡 자동 첨부</td></tr>
  </tbody>
</table>

<h3>5-2. 과제정밀평가 v3 (월 2회)</h3>
<div class="grid-2">
  <div class="card">
    <div class="card-title">정량평가 (매일)</div>
    <div class="card-body">과제 완성도 A/B/C/D · 클리닉 처방전 자동 갱신</div>
  </div>
  <div class="card">
    <div class="card-title">정성평가 (월 2회)</div>
    <div class="card-body">4항목: 풀이노트 완성도 / 서술형 완성도 / 교재 표시 습관 / 2차 풀이 후 틀린 이유 작성</div>
  </div>
</div>

<!-- ===================== 6. 학생 개인 카드 — 시스템 허브 ===================== -->
<h2>6. 학생 개인 카드 — 시스템 허브 (NEW)</h2>

<div class="summary-box">
  <div class="title">설계 원칙: Single Source of Truth + 멀티테넌트 전제</div>
  모든 자동화(클리닉·카톡·진도표·교차연습)는 학생 카드를 통과한다. school_id/tenant_id 컬럼을 처음부터 포함하여
  6개월 후 SaaS 전환 시 재작업 없도록 한다.
</div>

<h3>6-1. 카드 구조 (1 학생 = 1 페이지)</h3>
<div class="grid-3">
  <div class="card blue"><div class="card-title">기본 정보</div><div class="card-body">학교/학년/반/보호자 연락처/등록일/W·R·F 트랙</div></div>
  <div class="card blue"><div class="card-title">학습 진도</div><div class="card-body">단원·유형별 1차/2차/3차 체크 (questions join)</div></div>
  <div class="card"><div class="card-title">Q-M Chart</div><div class="card-body">2~4주 단위 오류 분포 그래프 (clinic_entries 집계)</div></div>
  <div class="card"><div class="card-title">자가예측 격차</div><div class="card-body">예측 정답률 vs 실제 (메타인지 시각화)</div></div>
  <div class="card green"><div class="card-title">과제 정밀평가</div><div class="card-body">정량 일별 + 정성 월 2회 4항목</div></div>
  <div class="card green"><div class="card-title">스터디 플래너</div><div class="card-body">학생 일과 시간 색칠 (학원/식사/자기학습)</div></div>
  <div class="card red"><div class="card-title">보호자 연락 로그</div><div class="card-body">카톡 발송 이력 + 응답 + 상담 기록</div></div>
  <div class="card red"><div class="card-title">관리 메모</div><div class="card-body">강사 일자별 누적 코멘트 (append-only)</div></div>
  <div class="card"><div class="card-title">출결</div><div class="card-body">자동 체크 + 결석 시 카톡 트리거</div></div>
</div>

<h3>6-2. 기술 구현 (5에이전트 권장)</h3>
<table>
  <thead><tr><th>레이어</th><th>선택</th><th>이유</th></tr></thead>
  <tbody>
    <tr><td>데이터</td><td>SQLite / Postgres students 확장 + <code>student_progress</code> / <code>student_log</code> 신규 테이블</td><td>기존 DB 추상화 재활용, 멀티 테넌트는 tenant_id 컬럼만 추가</td></tr>
    <tr><td>UI</td><td>Streamlit <code>app/pages/2_📋_학생카드.py</code></td><td>auth_ui.require_auth 재활용, MathDB와 단일 앱</td></tr>
    <tr><td>학부모 공유</td><td>서명 토큰 URL (학생별)</td><td>로그인 없이 안전 공유 (auth-free, expire 30일)</td></tr>
    <tr><td>내부 강사 메모</td><td>(선택) 노션 연동</td><td>강사간 협업 시. 학부모용은 절대 노션 노출 금지</td></tr>
  </tbody>
</table>

<!-- ===================== 7. AI 카톡 자동화 ===================== -->
<h2>7. AI 카톡 자동화 — 운영 룰 (NEW)</h2>

<h3>7-1. 기술 스택 (즉시 도입)</h3>
<table>
  <thead><tr><th>층</th><th>선택</th><th>비용</th><th>비고</th></tr></thead>
  <tbody>
    <tr><td>발송 API</td><td><b>솔라피 알림톡</b></td><td>9원/건</td><td>사업자등록 필요. 게이트웨이가 카카오 템플릿 심사 대행, 1~3일 시작 가능</td></tr>
    <tr><td>AI 메시지</td><td><b>Claude Haiku 4.5</b></td><td>월 ~$1 (50명×4주)</td><td>정형 보고에 충분. Sonnet은 12배</td></tr>
    <tr><td>스케줄러</td><td>GitHub Actions cron (금요일 17시)</td><td>무료</td><td>Streamlit Cloud에는 cron 없음. GH Actions 우회</td></tr>
    <tr><td>승인 큐</td><td>Streamlit 페이지 <code>3_📨_카톡_승인.py</code></td><td>—</td><td>AI 생성 → 강사 1문장 추가 → 발송 (자동 발송 금지)</td></tr>
  </tbody>
</table>

<h3>7-2. <span class="warn">필수 사전 조치 (에이전트 4 검증)</span></h3>
<ol>
  <li><b>개인정보 처리 동의서 서면 수령</b> — 학생 학습데이터 가공·발송 목적 명시. 미성년자는 법정대리인 동의 (개인정보보호법 22조)</li>
  <li><b>카카오 알림톡 사업자 등록</b> — 정보성 알림톡 템플릿 사전 승인 필요 (친구톡·마케팅톡 아님)</li>
  <li><b>AI 사용 사실 고지</b> — "학습 데이터는 AI로 요약 후 강사가 검수" 학부모에게 사전 안내 → 사후 발각 리스크 차단</li>
</ol>

<h3>7-3. 운영 룰 3가지 (신뢰 폭탄 방지)</h3>
<div class="grid-3">
  <div class="card red">
    <div class="card-title">① 하이브리드 강제</div>
    <div class="card-body">
      AI가 데이터·표 생성 → 강사가 학생별 <b>1문장 직접 추가</b> → 발송.
      강사 코멘트 미입력 시 발송 차단 (코드 레벨).
    </div>
  </div>
  <div class="card red">
    <div class="card-title">② 누락 방지 이중화</div>
    <div class="card-body">
      발송 후 강사 본인 카톡에 자동 사본. 금요일 22시까지 미수신 학생 자동 알림 → 강사 수동 재발송.
    </div>
  </div>
  <div class="card red">
    <div class="card-title">③ 월 1회 오프라인 백업</div>
    <div class="card-body">
      4주 중 1주는 종이 처방전 + 대면 1분 브리핑으로 교체. 자동화 의존 신호 희석.
    </div>
  </div>
</div>

<h3>7-4. 카톡 메시지 템플릿 (예시)</h3>
<div class="quote">
[EUM] OO 학부모님께 안녕하세요. 5월 4주차 학습 보고드립니다.<br>
· 이번 주 학습량: 신규 4유형 + 누적 복습 12문항<br>
· Q-M Chart: 계산실수 ↓20%, 개념누락 ↓50% (지난주 대비)<br>
· 자가예측 격차: 5%p (적정)<br>
· 다음 주 과제: 인수분해 복합형 6문항 (D+7 재도전 포함)<br>
&nbsp;&nbsp;<br>
<i>[강사 1문장]</i> OO이 이번 주 인수정리 적용에서 큰 진전 보였습니다. 다음 주 변형 문제로 깊이 다지겠습니다.<br>
&nbsp;&nbsp;<br>
[처방전·진도표 보기 → URL]<br>
<span class="small">※ 학습 데이터는 AI로 요약 후 담당 강사가 검수·발송합니다.</span>
</div>

<!-- ===================== 8. 12개월 로드맵 ===================== -->
<h2>8. 12개월 실행 로드맵</h2>

<div class="roadmap-row">
  <div class="phase now">즉시<br>(0~2주)</div>
  <div>
    <b>P1 · 학생 카드 v1</b><br>
    students 테이블 확장(tenant_id 추가) + student_progress / student_log 신규 + Streamlit <code>2_학생카드.py</code> 페이지<br>
    <b>P2 · 클리닉 v3</b> — D+30·시험2주전 확장분산 추가, 자가예측 격차 필드<br>
    <b>P3 · Q-M Chart 시각화</b> — clinic_entries 집계 그래프 자동 생성
  </div>
</div>
<div class="roadmap-row">
  <div class="phase">1~2개월</div>
  <div>
    <b>P4 · 카톡 자동화 v1</b><br>
    솔라피 사업자등록 + 친구톡 시작 → 알림톡 템플릿 승인 → 승인 큐 페이지 → GitHub Actions cron<br>
    <b>P5 · 과제정밀평가표</b> 정량·정성 4항목 PDF 자동 생성<br>
    <b>P6 · 교차연습</b> 워밍업 알고리즘에 다른 단원 1문제 셔플 추가
  </div>
</div>
<div class="roadmap-row">
  <div class="phase">3~6개월</div>
  <div>
    <b>P7 · Walk-Run-Fly 트랙</b> 학생별 트랙 분기 + 시험지 풀(pool) 분리<br>
    <b>P8 · 학교별 내신 지도</b> 광명북중·철산중·광명중 라인 빈출·실수 패턴 1장 PDF<br>
    <b>P9 · 학부모 공유 URL</b> 서명 토큰 기반 학생 카드 외부 공개 (auth-free)<br>
    <b>P10 · 영어 어휘/구문 모듈</b> 클리닉 점수 엔진 재활용 시범
  </div>
</div>
<div class="roadmap-row">
  <div class="phase">6~12개월</div>
  <div>
    <b>P11 · 멀티 테넌트 분리</b> tenant_id 활용해 학원 단위 격리<br>
    <b>P12 · SaaS 베타</b> 옆 학원 강사 1~2명 시범 라이선스<br>
    <b>P13 · 인수분해 라벨링</b> Claude Haiku로 sub-유형 자동 분류 + 임베딩 보완<br>
    <b>P14 · 적중분석 자동화</b> 시험 끝나면 학교별 적중률 자동 리포트
  </div>
</div>

<!-- ===================== 9. /근본 자문 요약 ===================== -->
<h2>9. /근본 3단계 자문 (요약)</h2>
<table>
  <thead><tr><th style="width:25mm">자문</th><th>판정 / 내용</th></tr></thead>
  <tbody>
    <tr><td><b>1차</b> 패치 vs 근본</td><td>모든 보강이 <b>근본 수정</b>. 단순 기능 추가가 아니라 "운영자 매니저" 정체성을 데이터로 증명하는 구조 전환</td></tr>
    <tr><td><b>2차</b> 왜 발생?</td><td>MathDB가 "문제" 중심 스키마라 "학생" 중심 종단 데이터 결손. 클리닉 MVP도 처방전 1건 단위라 종단 트래킹 부재</td></tr>
    <tr><td><b>3차</b> 재발 방지</td><td>① 학생 카드 = 단일 진실원본<br>② 멀티 테넌트 전제 설계<br>③ 카톡 AI+강사 1문장 미입력 시 발송 차단 로직<br>④ 교차·확장분산은 학생 카드 데이터를 input으로 → 카드가 곧 학습과학 엔진</td></tr>
  </tbody>
</table>

<!-- ===================== 10. 핵심 결론 ===================== -->
<h2>10. 핵심 결론</h2>

<div class="summary-box">
  <div class="title">한 문장 요약</div>
  사용자의 <b>"내신 성적 운영자" 포지셔닝</b>은 학습과학(인출·분산·전이·교차·메타인지)과 대치동 7대 노하우(Q-M Chart·과제정밀평가·진도표·관리대장·플래너·표준화 양식·3단계 진도)가 <b>학생 개인 카드 하나를 허브로</b> 결합될 때 완성되며,
  AI 카톡 자동화는 <b>"AI+강사 1문장 하이브리드"와 "멀티 테넌트 스키마"</b> 두 가지를 처음부터 강제할 때만 5년 후 시나리오 B (철산·광명 3~5개 학원 라이센싱)로 진화할 수 있다.
</div>

<h3>지금 시작할 단 하나의 행동</h3>
<div class="card blue">
  <div class="card-title">학생 카드 v1 빌드 (1~2주)</div>
  <div class="card-body">
    <code>students</code> 테이블에 <code>tenant_id</code> 컬럼 추가, <code>student_progress</code> / <code>student_log</code> 신규 테이블 생성, <code>app/pages/2_📋_학생카드.py</code> 페이지 신설.
    이 한 가지만 끝나면 클리닉·카톡·교차연습·확장분산이 모두 그 위에 자연 조립된다.
  </div>
</div>

<p style="margin-top:8mm; text-align:center; color:#888; font-size:9pt;">
  EUM ACADEMY · 통합 운영 비전 v3 · __DATE__<br>
  대치동 7대 노하우 (학관노 2017 · 김성태 대표) + 5에이전트 교차검증 + /근본 자문 통합
</p>

</body>
</html>"""


def main() -> Path:
    today = datetime.date.today().strftime("%Y-%m-%d")
    html = HTML.replace("__DATE__", today)

    tmp_html = ROOT / "output" / "_tmp_vision_report.html"
    tmp_html.write_text(html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(tmp_html.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(OUTPUT),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    tmp_html.unlink(missing_ok=True)
    return OUTPUT


if __name__ == "__main__":
    path = main()
    size_kb = path.stat().st_size // 1024
    print(f"[OK] PDF 생성 완료 → {path} ({size_kb} KB)")
