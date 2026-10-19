# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 PDF 3쪽 ((2) 원과 접선) 10문항. 좌상단 '1. 접선의 길이' 개념 박스는 타이핑하지 않음.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트. 배점·라벨·해설 없음(사용자 지시). 정답은 직접 재계산.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p03q01', kind='short', no=1, fig='cs26_p03_q01',
    text='다음 그림에서 두 점 $rm A$, $rm B$는 원 $rm O$의 외부의 한 점 $rm P$에서 원 $rm O$에 그은 두 접선의 접점일 때, $x$의 값을 구하시오.',
    ans_mix='(1) $7$, (2) $14$', sol=[])

add(id='p03q02', kind='short', no=2, fig='cs26_p03_q02',
    text='오른쪽 그림에서 두 점 $rm A$, $rm B$는 원 $rm O$의 외부의 한 점 $rm P$에서 원 $rm O$에 그은 두 접선의 접점이다. $bar {rm OA}=9`rm cm$, $bar {rm OP}=15`rm cm$일 때, $□ rm APBO$의 넓이를 구하시오.',
    ans_eq='108`rm cm ^{2}', sol=[])

add(id='p03q03', kind='short', no=3, fig='cs26_p03_q03',
    text='다음 그림에서 원 $rm O$는 $triangle rm ABC$의 내접원이고, 세 점 $rm D$, $rm E$, $rm F$에서 각각 $triangle rm ABC$의 세 변과 접할 때, $x$의 값을 구하시오.',
    ans_mix='(1) $3$, (2) $6$', sol=[])

add(id='p03q04', kind='short', no=4, fig='cs26_p03_q04',
    text='오른쪽 그림에서 원 $rm O$는 $triangle rm ABC$의 내접원이고, 세 점 $rm D$, $rm E$, $rm F$에서 각각 $triangle rm ABC$의 세 변과 접한다. $bar {rm AF}=3`rm cm$, $bar {rm BD}=8`rm cm$, $bar {rm CE}=4`rm cm$일 때, $triangle rm ABC$의 둘레의 길이를 구하시오.',
    ans_eq='30`rm cm', sol=[])

add(id='p03q05', kind='short', no=5, fig='cs26_p03_q05',
    text='오른쪽 그림에서 $□ rm ABCD$는 원 $rm O$에 외접하고, 네 점 $rm P$, $rm Q$, $rm R$, $rm S$는 그 접점일 때, $bar {rm AB}+bar {rm CD}=bar {rm AD}+bar {rm BC}$임을 설명하시오.',
    ans_mix='접선의 길이가 서로 같음을 이용하여 설명한다.',
    sol=['원 밖의 한 점에서 그 원에 그은 두 접선의 길이는 서로 같으므로',
         '$bar {rm AP}=bar {rm AS}$, $bar {rm BP}=bar {rm BQ}$, $bar {rm CR}=bar {rm CQ}$, $bar {rm DR}=bar {rm DS}$',
         '$bar {rm AB}+bar {rm CD}=bar {rm AP}+bar {rm BP}+bar {rm CR}+bar {rm DR}$',
         '$=bar {rm AS}+bar {rm BQ}+bar {rm CQ}+bar {rm DS}$',
         '$=left( bar {rm AS}+bar {rm DS} right) + left( bar {rm BQ}+bar {rm CQ} right)$',
         '$=bar {rm AD}+bar {rm BC}$'])

add(id='p03q06', kind='short', no=6, fig='cs26_p03_q06',
    text='오른쪽 그림에서 $□ rm ABCD$는 원 $rm O$에 외접한다. $bar {rm AB}=8`rm cm$, $bar {rm AD}=8`rm cm$, $bar {rm CD}=10`rm cm$일 때, $x$의 값을 구하시오.',
    ans_eq='10', sol=[])

add(id='p03q07', kind='short', no=7, fig='cs26_p03_q07',
    text='오른쪽 그림에서 두 점 $rm A$, $rm B$는 원 $rm O$의 외부의 한 점 $rm P$에서 원 $rm O$에 그은 두 접선의 접점이다. $angle {rm APB}=80 DEG$일 때, $angle {rm ABP}$의 크기를 구하시오.',
    ans_eq='50 DEG', sol=[])

add(id='p03q08', kind='short', no=8, fig='cs26_p03_q08',
    text='오른쪽 그림에서 $bar {rm PA}$, $bar {rm PB}$, $bar {rm CD}$는 원 $rm O$의 접선이고 점 $rm A$, $rm B$, $rm E$는 원 $rm O$의 접점이다. $bar {rm PA}=8`rm cm$, $bar {rm PC}=5`rm cm$, $bar {rm PD}=6`rm cm$일 때, $bar {rm CD}$의 길이를 구하시오.',
    ans_eq='5`rm cm', sol=[])

add(id='p03q09', kind='short', no=9, fig='cs26_p03_q09',
    text='오른쪽 그림에서 원 $rm O$는 $triangle rm ABC$의 내접원이고, 세 점 $rm D$, $rm E$, $rm F$에서 각각 $triangle rm ABC$의 세 변과 접한다. $bar {rm BD}=6`rm cm$, $bar {rm CE}=4`rm cm$이고, $triangle rm ABC$의 둘레의 길이가 $26`rm cm$일 때, $bar {rm AF}$의 길이를 구하시오.',
    ans_eq='3`rm cm', sol=[])

add(id='p03q10', kind='short', no=10, fig='cs26_p03_q10',
    text='오른쪽 그림에서 $□ rm ABCD$는 원 $rm O$에 외접하고, 네 점 $rm P$, $rm Q$, $rm R$, $rm S$는 그 접점이다. $bar {rm AD}=7`rm cm$, $bar {rm BC}=10`rm cm$, $bar {rm BQ}=5`rm cm$, $bar {rm CD}=9`rm cm$일 때, $bar {rm AP}$의 길이를 구하시오.',
    ans_eq='3`rm cm', sol=[])
