# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 7쪽: V. 원의 성질 2. 원주각 (2) 원주각의 활용. 형식은 cs26_content.py 와 동일.
원본 PDF 7쪽(좌상단 개념 정리 박스는 문제가 아니므로 제외). 정답은 직접 재계산한 값."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p07q01', kind='short', no=1, fig='cs26_p07_q01',
    text='그림과 같이 원에 사각형 $rm ABCD$에서 $angle {rm A}+angle {rm C}=180 DEG$, $angle {rm B}+angle {rm D}=180 DEG$가 성립함을 보이시오.',
    ans_mix='$angle {rm A}+angle {rm C}=180 DEG$, $angle {rm B}+angle {rm D}=180 DEG$',
    sol=['$angle {rm A}$는 호 $rm BCD$에 대한 원주각이고, $angle {rm C}$는 호 $rm BAD$에 대한 원주각이다.',
         '호 $rm BCD$의 중심각의 크기를 $a$, 호 $rm BAD$의 중심각의 크기를 $b$라고 하면 $a+b=360 DEG$이다.',
         '$angle {rm A}= {1} over {2} a$, $angle {rm C}= {1} over {2} b$이므로',
         '$angle {rm A}+angle {rm C}= {1} over {2} left(a+b right)$$=180 DEG$',
         '같은 방법으로 $angle {rm B}+angle {rm D}=180 DEG$이다.'])

add(id='p07q02', kind='short', no=2, fig='cs26_p07_q02',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $85$, (2) $45$', sol=[])

add(id='p07q03', kind='short', no=3, fig='cs26_p07_q03',
    text='오른쪽 그림에서 직선 $rm AT$가 원 $rm O$의 접선일 때, $x$, $y$의 값을 각각 구하시오.',
    ans_mix='$x=40$, $y=25$', sol=[])

add(id='p07q04', kind='short', no=4, fig='cs26_p07_q04',
    text='다음 그림에서 $x$, $y$의 값을 각각 구하시오.',
    ans_mix='(1) $x=92$, $y=85$, (2) $x=110$, $y=105$', sol=[])

add(id='p07q05', kind='short', no=5, fig='cs26_p07_q05',
    text='오른쪽 그림에서 $□ rm ABCD$는 원 $rm O$에 내접한다. $angle {rm BCD}=120 DEG$이고, $rm arch AB=rm arch AD$, $bar {rm BD}=8`rm cm$일 때, $triangle rm ABD$의 넓이를 구하시오.',
    ans_eq='16 sqrt {3}`rm cm ^{2}', sol=[])

add(id='p07q06', kind='short', no=6, fig='cs26_p07_q06',
    text='다음 그림에서 직선 $rm AT$가 원 $rm O$의 접선일 때, $angle x$의 크기를 구하시오.',
    ans_mix='네 점 $rm A$, $rm B$, $rm C$, $rm D$가 한 원 위에 있는 것: (2), (4)', sol=[])

add(id='p07q07', kind='short', no=7, fig='cs26_p07_q07',
    text='다음 그림에서 직선 $rm AT$가 원 $rm O$의 접선일 때, $angle x$의 크기를 구하시오.',
    ans_mix='(1) $70 DEG$, (2) $60 DEG$', sol=[])

add(id='p07q08', kind='short', no=8, fig='cs26_p07_q08',
    text='오른쪽 그림에서 직선 $rm AT$는 원 $rm O$의 접선이고, $angle {rm ABC}=100 DEG$, $angle {rm ACT}=30 DEG$일 때, $angle {rm CTA}$의 크기를 구하시오.',
    ans_eq='50 DEG', sol=[])

add(id='p07q09', kind='short', no=9, fig='cs26_p07_q09',
    text='오른쪽 그림에서 직선 $rm CA$는 원 $rm O$의 접선이고, $bar {rm BC}$는 원 $rm O$의 중심을 지난다. $angle {rm BAT}=60 DEG$일 때, $angle {rm BCA}$의 크기를 구하시오.',
    ans_eq='30 DEG', sol=[])
