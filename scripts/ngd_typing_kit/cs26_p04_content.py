# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 4쪽 (2) 원과 접선 정리. 라벨·배점·해설 없음. 정답은 직접 재계산."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p04q01', kind='short', no=1,
    text=['다음 □ 안에 알맞은 것을 써넣으시오.',
          '(1) 원 밖의 한 점에서 그 원에 그을 수 있는 접선은 □개이다.',
          '(2) 원 밖의 한 점에서 그 원에 그은 두 접선의 길이는 서로 □.'],
    ans_mix='(1) $2$, (2) 같다', sol=[])

add(id='p04q02', kind='short', no=2, fig='cs26_p04_q02',
    text=['오른쪽 그림에서 두 점 $rm A$, $rm B$는 점 $rm P$에서 원 $rm O$에 그은 두 접선의 접점이다. $bar {rm PA}=6`rm cm$, $angle {rm APB}=50 DEG$일 때, 다음을 구하시오.',
          '(1) $bar {rm PB}$의 길이',
          '(2) $angle x$의 크기'],
    ans_mix='(1) $6`rm cm$, (2) $65 DEG$', sol=[])

add(id='p04q03', kind='short', no=3, fig='cs26_p04_q03',
    text='오른쪽 그림에서 $triangle rm ABC$가 원 $rm O$에 외접하고 세 점 $rm P$, $rm Q$, $rm R$는 각각 원 $rm O$의 접점이다. $bar {rm AP}=4`rm cm$, $bar {rm BQ}=8`rm cm$, $bar {rm CR}=5`rm cm$일 때, $triangle rm ABC$의 둘레의 길이를 구하시오.',
    ans_eq='34`rm cm', sol=[])

add(id='p04q04', kind='short', no=4, fig='cs26_p04_q04',
    text='오른쪽 그림과 같이 $□ rm ABCD$가 원 $rm O$에 외접하고, $bar {rm AB}=8`rm cm$, $bar {rm BC}=10`rm cm$, $bar {rm CD}=12`rm cm$이다. 이때 $bar {rm AD}$의 길이를 구하시오.',
    ans_eq='10`rm cm', sol=[])

add(id='p04q05', kind='short', no=5, fig='cs26_p04_q05',
    text='오른쪽 그림에서 $bar {rm PA}$, $bar {rm PB}$, $bar {rm CD}$는 원 $rm O$의 접선이고, 점 $rm A$, $rm B$, $rm E$는 접점이다. $bar {rm AC}=3`rm cm$, $bar {rm CD}=7`rm cm$, $bar {rm PC}=10`rm cm$일 때, $bar {rm PD}$의 길이를 구하시오.',
    ans_eq='9`rm cm', sol=[])

add(id='p04q06', kind='short', no=6, fig='cs26_p04_q06',
    text='오른쪽 그림에서 두 점 $rm A$, $rm B$는 점 $rm P$에서 원 $rm O$에 그은 두 접선의 접점이다. $angle {rm APB}=60 DEG$이고 $bar {rm AP}=2 sqrt {3}`rm cm$일 때, 색칠한 부분의 넓이를 구하시오.',
    ans_eq='{4} over {3} pi `rm cm ^{2}', sol=[])

add(id='p04q07', kind='short', no=7, fig='cs26_p04_q07',
    text='오른쪽 그림과 같이 중심이 같고, 반지름의 길이가 각각 $5`rm cm$와 $3`rm cm$인 두 원이 있다. 큰 원의 현 $rm AB$가 작은 원의 점 $rm H$를 지나는 접선일 때 $bar {rm AB}$의 길이를 구하시오.',
    ans_eq='8`rm cm', sol=[])

add(id='p04q08', kind='short', no=8, fig='cs26_p04_q08',
    text='오른쪽 그림과 같이 $bar {rm AD}$, $bar {rm BC}$, $bar {rm CD}$는 각각 세 점 $rm A$, $rm B$, $rm E$에서 반원 $rm O$에 접한다. $bar {rm AD}=4`rm cm$, $bar {rm BC}=9`rm cm$일 때, 반원 $rm O$의 반지름의 길이를 구하시오.',
    ans_eq='6`rm cm', sol=[])

add(id='p04q09', kind='short', no=9, fig='cs26_p04_q09',
    text='오른쪽 그림과 같이 중심이 같은 두 원에서 작은 원의 접선과 큰 원의 교점을 각각 $rm A$, $rm B$라고 하자. $bar {rm AB}=14`rm cm$일 때, 색칠한 부분의 넓이를 구하시오.',
    ans_eq='49 pi `rm cm ^{2}', sol=[])

add(id='p04q10', kind='short', no=10, fig='cs26_p04_q10',
    text='오른쪽 그림에서 $bar {rm AD}$, $bar {rm BC}$, $bar {rm CD}$는 반원 $rm O$의 접선일 때, $bar {rm CD}$의 길이를 구하시오.',
    ans_eq='15`rm cm', sol=[])

add(id='p04q11', kind='short', no=11, fig='cs26_p04_q11',
    text='오른쪽 그림과 같이 $angle {rm B}=90 DEG$인 직각삼각형 $rm ABC$가 원 $rm O$에 외접하고, 세 점 $rm D$, $rm E$, $rm F$는 각각 원 $rm O$의 접점이다. $bar {rm AF}=2`rm cm$, $bar {rm CF}=3`rm cm$일 때, 원 $rm O$의 둘레의 길이를 구하시오.',
    ans_eq='2 pi `rm cm', sol=[])

add(id='p04q12', kind='short', no=12, fig='cs26_p04_q12',
    text='오른쪽 그림에서 $triangle rm ABC$가 원 $rm O$에 외접하고, 세 점 $rm D$, $rm E$, $rm F$는 각각 원 $rm O$의 접점이다. $bar {rm PQ}$가 원 $rm O$의 접선이고 점 $rm R$는 원 $rm O$의 접점일 때, $triangle rm PBQ$의 둘레의 길이를 구하시오.',
    ans_eq='10`rm cm', sol=[])

add(id='p04q13', kind='short', no=13, fig='cs26_p04_q13',
    text='오른쪽 그림과 같이 가로의 길이가 $9`rm cm$, 세로의 길이가 $6`rm cm$인 직사각형의 $3$개의 변에 원 $rm O$가 내접하고, $bar {rm DE}$는 원 $rm O$의 접선일 때, $bar {rm DE}$의 길이를 구하시오.',
    ans_eq='{15} over {2}`rm cm', sol=[])
