# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 6쪽: V. 원의 성질 2. 원주각 (1) 원주각 정리. 형식은 cs26_content.py 와 동일.
원본 PDF 6쪽. 정답은 손글씨가 아니라 직접 재계산한 값."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p06q01', kind='short', no=1,
    text=['다음 □ 안에 알맞은 것을 써넣으시오.',
          '(1) 한 호에 대한 원주각의 크기는 그 호에 대한 중심각의 크기의 □과 같다.',
          '(2) 한 □에 대한 원주각의 크기는 모두 같다.',
          '(3) 한 원에서 같은 길이의 □에 대한 원주각의 크기는 서로 같다.',
          '(4) 한 원에서 같은 크기의 원주각에 대한 □의 길이는 서로 같다.'],
    ans_mix='(1) $ {1} over {2}$, (2) 호, (3) 호, (4) 호', sol=[])

add(id='p06q02', kind='short', no=2, fig='cs26_p06_q02',
    text=['오른쪽 그림을 보고, 다음을 기호로 나타내시오.',
          '(1) 호 $rm AB$에 대한 원주각',
          '(2) 원주각 $angle {rm CAD}$에 대한 호'],
    ans_mix='(1) $angle {rm ACB}$, $angle {rm ADB}$, $angle {rm AEB}$ 중 하나, (2) $rm arch CD$', sol=[])

add(id='p06q03', kind='short', no=3, fig='cs26_p06_q03',
    text='다음 그림에서 $angle x$의 크기를 구하시오.',
    ans_mix='(1) $40 DEG$, (2) $110 DEG$, (3) $60 DEG$', sol=[])

add(id='p06q04', kind='short', no=4, fig='cs26_p06_q04',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $50$, (2) $6$', sol=[])

add(id='p06q05', kind='short', no=5, fig='cs26_p06_q05',
    text='오른쪽 그림의 원 $rm O$에서 두 현 $rm AB$, $rm CD$가 평행할 때, $rm arch AC=rm arch BD$임을 설명하시오.',
    ans_mix='$angle {rm BAD}=angle {rm ADC}$ (엇각)이므로 $rm arch BD=rm arch AC$',
    sol=['두 현 $rm AB$, $rm CD$가 평행하므로 $angle {rm BAD}=angle {rm ADC}$ (엇각)이다.',
         '한 원에서 크기가 같은 원주각에 대한 호의 길이는 같으므로 $rm arch BD=rm arch AC$이다.'])

add(id='p06q06', kind='short', no=6, fig='cs26_p06_q06',
    text='오른쪽 그림의 원에서 $rm arch AB : rm arch BC : rm arch CA=3 : 4 : 5$이다. $angle {rm BAC}=a DEG$, $angle {rm ABC}=b DEG$, $angle {rm BCA}=c DEG$라고 할 때, $a+b-c$의 값을 구하시오.',
    ans_eq='90', sol=[])

add(id='p06q07', kind='short', no=7, fig='cs26_p06_q07',
    text='오른쪽 그림과 같은 원 $rm O$에서 $angle x$의 크기를 구하시오.',
    ans_eq='37 DEG', sol=[])

add(id='p06q08', kind='short', no=8, fig='cs26_p06_q08',
    text='오른쪽 그림과 같은 원 $rm O$에서 $rm arch AB=3`rm cm$, $rm arch BC=9`rm cm$이고, $angle {rm BOC}=120 DEG$일 때, $angle x$의 크기를 구하시오.',
    ans_eq='80 DEG', sol=[])

add(id='p06q09', kind='short', no=9, fig='cs26_p06_q09',
    text='오른쪽 그림에서 $bar {rm AB}$는 원 $rm O$의 지름이고, $angle {rm COD}=56 DEG$일 때, $angle {rm DPC}$의 크기를 구하시오.',
    ans_eq='62 DEG', sol=[])

add(id='p06q10', kind='short', no=10, fig='cs26_p06_q10',
    text='오른쪽 그림의 원 $rm O$에서 $rm arch AB=rm arch BC$, $angle {rm ABD}=55 DEG$, $angle {rm BDC}=43 DEG$일 때, $angle {rm CAD}$의 크기를 구하시오.',
    ans_eq='39 DEG', sol=[])

add(id='p06q11', kind='short', no=11, fig='cs26_p06_q11',
    text='오른쪽 그림의 원 $rm O$에서 $rm arch BQP$의 중심각의 크기가 $170 DEG$일 때, $angle {rm D}$의 크기를 구하시오.',
    ans_eq='95 DEG', sol=[])

add(id='p06q12', kind='short', no=12, fig='cs26_p06_q12',
    text='오른쪽 그림과 같이 원 $rm O$에 내접하는 오각형 $rm ABCDE$에서 $angle {rm B}=110 DEG$, $angle {rm COD}=60 DEG$일 때, $angle {rm AED}$의 크기를 구하시오.',
    ans_eq='100 DEG', sol=[])

add(id='p06q13', kind='short', no=13, fig='cs26_p06_q13',
    text='어떤 박물관에는 오른쪽 그림과 같이 벽에 걸린 그림을 $90 DEG$로 비추는 조명을 바닥에 설치하였다. 이 조명의 위치를 바꾸어 가면서 $90 DEG$로 그림을 비추려고 한다. 이때 조명을 설치할 수 있는 곳을 찾아보시오.',
    ans_mix='그림의 양 끝점을 지름의 양 끝점으로 하는 원과 바닥이 만나는 점',
    sol=['그림의 양 끝점을 $rm A$, $rm B$, 조명의 위치를 $rm P$라고 하면 $angle {rm APB}=90 DEG$이어야 한다.',
         '$angle {rm APB}=90 DEG$이면 점 $rm P$는 $bar {rm AB}$를 지름으로 하는 원 위에 있다.',
         '따라서 조명은 그림의 양 끝점을 지름의 양 끝점으로 하는 원과 바닥이 만나는 점에 설치할 수 있다.'])
