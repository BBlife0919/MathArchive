# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 PDF 8쪽(원주각의 활용 정리 #1~#10). 정답은 직접 재계산."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p08q01', kind='short', no=1,
    text='다음 □ 안에 알맞은 것을 써넣으시오.',
    emptybox=dict(paras=['원의 접선과 그 접점을 지나는 □이 이루는 각의 크기는 그 각의 내부에 있는 호에 대한 □의 크기와 같다.']),
    ans_mix='현, 원주각', sol=[])

add(id='p08q02', kind='short', no=2, fig='cs26_p08_q02',
    text='다음 그림에서 직선 $rm AT$는 원 $rm O$의 접선일 때, $∠ x$의 크기를 구하시오.',
    ans_mix='(1) $80 DEG$, (2) $70 DEG$', sol=[])

add(id='p08q03', kind='short', no=3, fig='cs26_p08_q03',
    text='다음 그림에서 네 점 $rm A$, $rm B$, $rm C$, $rm D$가 한 원 위에 있을 때, $∠ x$의 크기를 구하시오.',
    ans_mix='(1) $80 DEG$, (2) $30 DEG$', sol=[])

add(id='p08q04', kind='short', no=4, fig='cs26_p08_q04',
    text='다음 그림에서 $∠ x$와 $∠ y$의 크기를 각각 구하시오.',
    ans_mix='(1) $∠ x=95 DEG$, $∠ y=100 DEG$, (2) $∠ x=90 DEG$, $∠ y=105 DEG$', sol=[])

add(id='p08q05', kind='short', no=5, fig='cs26_p08_q05',
    text='오른쪽 그림에서 직선 $rm AT$는 원 $rm O$의 접선이고 $rm arch AB=rm arch BP$이다. $∠ {rm BAT}=65 DEG$일 때, $∠ {rm PAB}$의 크기를 구하시오.',
    ans_eq='65 DEG', sol=[])

add(id='p08q06', kind='short', no=6, fig='cs26_p08_q06',
    text='다음 그림에서 반직선 $rm PT$는 원 $rm O$의 접선이고, $bar {rm AB}$는 원 $rm O$의 지름이다. $∠ {rm ATP}=36 DEG$일 때, $∠ {rm BAT}$의 크기를 구하시오.',
    ans_eq='54 DEG', sol=[])

add(id='p08q07', kind='short', no=7, fig='cs26_p08_q07',
    text='오른쪽 그림에서 세 점 $rm D$, $rm E$, $rm F$는 직각삼각형 $rm ABC$의 내접원의 접점이고, $bar {rm BE}=6`rm cm$, $bar {rm CE}=4`rm cm$일 때, 원 $rm O$의 반지름의 길이를 구하시오.',
    ans_eq='2`rm cm', sol=[])

add(id='p08q08', kind='short', no=8, fig='cs26_p08_q08',
    text='다음 그림과 같이 $triangle rm ABC$의 내접원이 $triangle rm EDF$의 외접원이다. $∠ {rm A}=60 DEG$, $∠ {rm B}=50 DEG$일 때, $∠ {rm FEC}$의 크기를 구하시오.',
    ans_eq='55 DEG', sol=[])

add(id='p08q09', kind='short', no=9, fig='cs26_p08_q09',
    text='오른쪽 그림에서 $bar {rm PA}$와 $bar {rm PB}$는 원 $rm O$ 위의 두 점 $rm A$, $rm B$를 각각 지나는 접선이다. 원 위의 한 점 $rm C$에 대하여 $□ rm APBC$가 평행사변형일 때, $∠ {rm APB}$의 크기를 구하시오.',
    ans_eq='60 DEG', sol=[])

add(id='p08q10', kind='short', no=10, fig='cs26_p08_q10',
    text='오른쪽 그림은 강물에 떠 있는 원기둥 모양의 통나무의 단면을 나타낸 것이다. $bar {rm BD}=bar {rm CD}$, $bar {rm AD}$ $bot$ $bar {rm BC}$이고, $bar {rm AD}=20`rm cm$, $bar {rm BD}=40`rm cm$일 때, 이 통나무의 지름의 길이를 구하시오.',
    ans_eq='100`rm cm', sol=[])
