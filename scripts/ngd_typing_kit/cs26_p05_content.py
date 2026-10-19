# -*- coding: utf-8 -*-
"""철산중 기말대비 프린트 5쪽 2. 원주각 (1) 원주각. 개념 정리 박스는 제외. 라벨·배점·해설 없음."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p05q01', kind='short', no=1, fig='cs26_p05_q01',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $120$, (2) $200$', sol=[])

add(id='p05q02', kind='short', no=2, fig='cs26_p05_q02',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $50$, (2) $25$', sol=[])

add(id='p05q03', kind='short', no=3, fig='cs26_p05_q03',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $25$, (2) $4$', sol=[])

add(id='p05q04', kind='short', no=4, fig='cs26_p05_q04',
    text='오른쪽 그림에서 $angle {rm AQB}=38 DEG$일 때, $angle x$, $angle y$의 크기를 각각 구하시오.',
    ans_mix='$angle x=38 DEG$, $angle y=76 DEG$', sol=[])

add(id='p05q05', kind='short', no=5, fig='cs26_p05_q05',
    text='다음은 한 원 $rm O$에서 원주각의 크기가 같으면 호의 길이가 같음을 설명하는 과정이다. □ 안에 알맞은 것을 쓰시오.',
    emptybox=dict(
        paras=['오른쪽 그림의 원 $rm O$에서',
               '$angle {rm APB}=angle {rm CQD}$라고 하면',
               '$angle {rm AOB}=2$□,',
               '$angle {rm COD}=2$□이므로',
               '$angle {rm AOB}=$□이다.',
               '그런데 중심각의 크기가 같으면',
               '호의 길이도 같으므로 $rm arch AB=$□이다.']),
    ans_mix='$angle {rm APB}$, $angle {rm CQD}$, $angle {rm COD}$, $rm arch CD$', sol=[])

add(id='p05q06', kind='short', no=6, fig='cs26_p05_q06',
    text='오른쪽 그림에서 $bar {rm BD}$는 원 $rm O$의 지름이다. $angle {rm DAC}=35 DEG$일 때, $angle {rm ABD}$의 크기를 구하시오.',
    ans_eq='55 DEG', sol=[])

add(id='p05q07', kind='short', no=7, fig='cs26_p05_q07',
    text='오른쪽 그림에서 호 $rm BC$의 길이는 호 $rm AB$의 길이의 $2$배이다. $angle {rm AEB}=25 DEG$일 때, $angle x$, $angle y$의 크기를 각각 구하시오.',
    ans_mix='$angle x=50 DEG$, $angle y=50 DEG$', sol=[])

add(id='p05q08', kind='short', no=8, fig='cs26_p05_q08',
    text='오른쪽 그림에서 $bar {rm PA}$, $bar {rm PB}$는 원 $rm O$의 접선이고, 두 점 $rm A$, $rm B$는 접점이다. $angle {rm APB}=66 DEG$일 때, $angle x$의 크기를 구하시오.',
    ans_eq='57 DEG', sol=[])
