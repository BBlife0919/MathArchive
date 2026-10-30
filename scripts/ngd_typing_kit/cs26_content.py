# -*- coding: utf-8 -*-
"""철산중 3학년 기말대비 수학프린트(V. 원의 성질) 내용. 마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
원본: ~/Downloads/철산중 기말프린트.pdf (스캔, 학생 손글씨 있음). 프린트물이라 [중단원]/[난이도] 라벨·배점·해설 없음(사용자 지시 2026-10-19).
규칙: 숫자·변수·각도는 전부 수식. 정답은 손글씨가 아니라 직접 재계산한 값.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ============================================================ 1쪽 (1) 원과 현
add(id='c101', kind='short', no=1, fig='cs26_c1_01',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $6$, (2) $6$', sol=[])

add(id='c102', kind='short', no=2, fig='cs26_c1_02',
    text='어느 고고학자가 유물 발굴 과정에서 찾아낸 원 모양의 깨진 접시를 복원하려고 한다. 오른쪽 그림과 같이 현 $bar {rm AB}$의 중점을 $rm M$이라 하고, 현의 수직이등분선이 접시의 둘레와 만나는 점을 $rm C$라고 할 때, $bar {rm AM}=6`rm cm$, $bar {rm CM}=2`rm cm$이다. 이 접시의 반지름의 길이를 구하시오.',
    ans_eq='10`rm cm', sol=[])

add(id='c103', kind='short', no=3, fig='cs26_c1_03',
    text='다음은 한 원에서 원의 중심으로부터 같은 거리에 있는 두 현의 길이가 같음을 설명하는 과정이다. □ 안에 알맞은 것을 쓰시오.',
    emptybox=dict(
        paras=['다음 그림과 같이 원의 중심 $rm O$에서 같은 거리에 있는 두 현 $bar {rm AB}$, $bar {rm CD}$에 내린 수선의 발을 각각 $rm M$, $rm N$이라고 하자.',
               '$triangle rm OAM$과 $triangle rm ODN$에서',
               '$∠ {rm OMA}=∠ {rm OND}$$=$□, $bar {rm OA}=$□(반지름)',
               '$bar {rm OM}=bar {rm ON}$이므로 $triangle rm OAM equiv triangle rm ODN$이다.',
               '따라서 $bar {rm AM}=$□이다.',
               '그런데 $bar {rm AB}=2 bar {rm AM}$, $bar {rm CD}=$□이므로 $bar {rm AB}=bar {rm CD}$이다.',
               '즉, 한 원에서 원의 중심으로부터 같은 거리에 있는 두 현의 길이는 같다.']),
    ans_mix='$90 DEG$, $bar {rm OD}$, $bar {rm DN}$, $2 bar {rm DN}$', sol=[])

add(id='c104', kind='short', no=4, fig='cs26_c1_04',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $4$, (2) $5$', sol=[])

add(id='c105', kind='short', no=5, fig='cs26_c1_05',
    text='그림과 같이 중심이 같은 두 원으로 둘러싸인 꽃밭이 있다. 꽃밭의 작은 원의 접선이 큰 원과 만나는 점을 각각 $rm A$, $rm B$라고 하자. $bar {rm AB}=8`rm m$일 때, 꽃밭의 넓이를 구하시오.',
    ans_eq='16 pi `rm m ^{2}', sol=[])

add(id='c106', kind='short', no=6, fig='cs26_c1_06',
    text='그림에서 $bar {rm OM}=bar {rm ON}$이고 $∠ {rm B}=65 DEG$일 때, $∠ {rm BAC}$의 크기를 구하시오.',
    ans_eq='50 DEG', sol=[])

add(id='c107', kind='short', no=7, fig='cs26_c1_07',
    text='오른쪽 그림과 같이 원 $rm O$의 중심에서 두 현 $rm AB$, $rm CD$에 내린 수선의 발을 각각 $rm M$, $rm N$이라고 하자. $bar {rm AB}=bar {rm CD}$, $bar {rm OM}=4`rm cm$, $bar {rm CN}=5`rm cm$일 때, $x$, $y$의 값을 각각 구하시오.',
    ans_mix='$x=4$, $y= sqrt {41}$', sol=[])
