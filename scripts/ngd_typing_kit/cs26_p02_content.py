# -*- coding: utf-8 -*-
"""철산중3 기말대비 프린트 PDF 2쪽 ((1) 원과 현 정리) 12문항. 마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
원본: ~/Downloads/철산중 기말프린트.pdf 2쪽. [중단원]/[난이도]·배점·해설 없음(사용자 지시). 정답은 손글씨가 아니라 직접 재계산.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='p02q01', kind='short', no=1,
    text=['다음 □ 안에 알맞은 것을 써넣으시오.',
          '(1) 원의 중심에서 현에 내린 □은 그 현을 이등분한다.',
          '(2) 현의 수직이등분선은 그 원의 □을 지난다.',
          '(3) 한 원에서 중심으로부터 같은 거리에 있는 두 현의 길이는 □.',
          '(4) 한 원에서 길이가 같은 두 현은 원의 □으로부터 같은 거리에 있다.'],
    ans_mix='(1) 수선, (2) 중심, (3) 같다, (4) 중심', sol=[])

add(id='p02q02', kind='short', no=2, fig='cs26_p02_q02',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $13$, (2) $9$', sol=[])

add(id='p02q03', kind='short', no=3, fig='cs26_p02_q03',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $4$, (2) $6 sqrt {3}$', sol=[])

add(id='p02q04', kind='short', no=4, fig='cs26_p02_q04',
    text='오른쪽 그림에서 원 $rm O$가 $triangle rm ABC$의 외접원이고 $bar {rm OL}=bar {rm OM}$$=bar {rm ON}$일 때, $angle {rm BAC}$의 크기를 구하시오.',
    ans_eq='60 DEG', sol=[])

add(id='p02q05', kind='short', no=5, fig='cs26_p02_q05',
    text='오른쪽 그림은 원 모양의 접시의 일부가 깨진 것이다. 이를 복원하기 위해 원의 중심을 찾고자 할 때, 어떻게 해야 할지 그 방법을 설명하시오.',
    ans_mix='접시의 둘레 위의 두 현의 수직이등분선의 교점이 원의 중심이다.',
    sol=['접시의 둘레 위에 서로 다른 세 점 $rm A$, $rm B$, $rm C$를 잡는다.',
         '두 현 $rm AB$, $rm BC$를 긋고 각각의 수직이등분선을 작도한다.',
         '현의 수직이등분선은 그 원의 중심을 지나므로',
         '두 수직이등분선의 교점이 원의 중심이다.'])

add(id='p02q06', kind='short', no=6, fig='cs26_p02_q06',
    text='오른쪽 그림의 원 $rm O$에서 현 $rm AB$는 반지름 $rm OC$의 수직이등분선이다. $bar {rm AB}=10`rm cm$일 때, 원 $rm O$의 반지름의 길이를 구하고, 그 풀이 과정을 쓰시오.',
    ans_eq='{10 sqrt {3}} over {3}`rm cm',
    sol=['원 $rm O$의 반지름의 길이를 $r`rm cm$라 하고',
         '$bar {rm AB}$와 $bar {rm OC}$의 교점을 $rm M$이라 하면',
         '$bar {rm OM}= {r} over {2}`rm cm$, $bar {rm AM}=5`rm cm$',
         '$triangle rm OAM$에서 $bar {rm OA} ^{2} = bar {rm OM} ^{2} + bar {rm AM} ^{2}$이므로',
         '$r ^{2} = left( {r} over {2} right) ^{2} + 5 ^{2}$',
         '$ {3} over {4} r ^{2} = 25$',
         '$r ^{2} = {100} over {3}$',
         '$r>0$이므로',
         '$r= {10 sqrt {3}} over {3}$'])

add(id='p02q07', kind='short', no=7, fig='cs26_p02_q07',
    text='다음 그림에서 $x$의 값을 구하시오.',
    ans_mix='(1) $6$, (2) $2 sqrt {13}$', sol=[])

add(id='p02q08', kind='short', no=8, fig='cs26_p02_q08',
    text='오른쪽 그림에서 원 $rm O$는 $triangle rm ABC$의 외접원이고 $bar {rm OM} bot bar {rm AB}$, $bar {rm ON} bot bar {rm AC}$, $bar {rm OM}=bar {rm ON}$이다. $angle {rm B}=50 DEG$일 때, $angle {rm A}$의 크기를 구하시오.',
    ans_eq='80 DEG', sol=[])

add(id='p02q09', kind='short', no=9, fig='cs26_p02_q09',
    text='다음 그림은 탱크로리에 탑재된 원기둥 모양의 탱크의 단면이다. 단면의 반지름의 길이가 $1`rm m$이고, 탱크에 들어 있는 액체의 높이가 $0.5`rm m$일 때 색칠된 부분의 넓이를 구하시오.',
    ans_eq='left( {pi} over {3} - {sqrt {3}} over {4} right) `rm m ^{2}', sol=[])

add(id='p02q10', kind='short', no=10, fig='cs26_p02_q10',
    text='오른쪽 그림에서 원 $rm O$는 $triangle rm ABC$의 외접원이고 $bar {rm OM} bot bar {rm AB}$, $bar {rm ON} bot bar {rm AC}$, $bar {rm OM}=bar {rm ON}$이다. $angle {rm B}=66 DEG$일 때, $angle {rm A}$의 크기를 구하시오.',
    ans_eq='48 DEG', sol=[])

add(id='p02q11', kind='short', no=11, fig='cs26_p02_q11',
    text='오른쪽 그림과 같이 원 $rm O$의 중심에서 두 현 $rm AB$, $rm CD$에 내린 수선의 발을 각각 $rm M$, $rm N$이라고 하자. $bar {rm OM}=bar {rm ON}$일 때, $x$의 값을 구하시오.',
    ans_eq='6', sol=[])

add(id='p02q12', kind='short', no=12, fig='cs26_p02_q12',
    text='오른쪽 그림의 원 $rm O$에서 $bar {rm AB} bot bar {rm OC}$이고, $bar {rm BD}=6`rm cm$, $bar {rm CD}=4`rm cm$일 때, 원 $rm O$의 반지름의 길이를 구하시오.',
    ans_eq='{13} over {2}`rm cm', sol=[])
