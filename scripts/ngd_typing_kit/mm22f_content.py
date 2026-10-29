# -*- coding: utf-8 -*-
"""명문고등학교 2학년 2022 1학기 기말 수학(대수) 20문항 내용 (19MC+1서술형). 단원: 일반각과 호도법 ~ 수학적 귀납법.

Q15는 원본 PDF에 배점·범위 표기는 있으나 "N일째에는 M그루만 심으면 된다"는 문장이
"그 날짜까지 남은 총 필요량이 M"이라는 뜻으로 해석해야(해당 날 하루치가 아니라) x=2,
총개수=91로 깔끔하게 떨어짐 — 단순히 "그 날의 하루 심는 양=M"으로 읽으면 두 조건의 x가
서로 달라져(1과 -7/5) 모순되므로, 전자(누적 잔여량) 해석으로 복원함(완성 보고 시 고지).
원본에 배점 표기가 없어 난이도에 따라 임의로 배점을 매겼음."""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=3.0, layout='1x5',
    text='자연수 $n$에 대하여 수열 ${it-3n+7}$의 제$5$항은?',
    choices=['$it-8$', '$it-4$', '$0$', '$4$', '$8$'],
    ans='①',
    sol=[
        '제$5$항: $it-3 times5+7=it-15+7=it-8$',
        '$therefore~it-8$',
    ],
    ch='등차수열', lv='하')

add(id='q02', kind='mc', no=2, score=3.0, layout='1x5',
    text='반지름의 길이가 $4$이고 부채꼴의 넓이가 $2 pi$인 부채꼴의 호의 길이는?',
    choices=['$pi$', '${3} over{2} pi$', '$2 pi$', '${5} over{2} pi$', '$3 pi$'],
    ans='①',
    sol=[
        '넓이 $= {1} over{2}r^{2} theta$에서 $2 pi= {1} over{2}(16) theta=8 theta$',
        '$theta= {pi} over{4}$',
        '호의 길이 $=r theta=4 times {pi} over{4}=pi$',
        '$therefore~pi$',
    ],
    ch='일반각과 호도법', lv='하')

add(id='q03', kind='mc', no=3, score=3.2, layout='1x5',
    text='$sum^{8}_{k=1}a_{k}=5,~sum^{8}_{n=1}b_{n}=20$일 때, $sum^{8}_{k=1}(2a_{k}+b_{k})$의 값은?',
    choices=['$22$', '$25$', '$30$', '$40$', '$45$'],
    ans='③',
    sol=[
        '$sum(2a_{k}+b_{k})=2 sum a_{k}+ sum b_{k}=2(5)+20=30$',
        '$therefore~30$',
    ],
    ch='수열의 합', lv='하')

add(id='q04', kind='mc', no=4, score=3.2, layout='1x5',
    text='$sin {7} over{6} pi+cos {5} over{3} pi+tan {7} over{4} pi$의 값은?',
    choices=['$it-2$', '$it-1$', '$0$', '$1$', '$2$'],
    ans='②',
    sol=[
        '$sin {7} over{6} pi=sin LEFT( pi+ {pi} over{6} RIGHT)=it-sin {pi} over{6}=it- {1} over{2}$',
        '$cos {5} over{3} pi=cos LEFT(2 pi- {pi} over{3} RIGHT)=cos {pi} over{3}= {1} over{2}$',
        '$tan {7} over{4} pi=tan LEFT(2 pi- {pi} over{4} RIGHT)=it-tan {pi} over{4}=it-1$',
        '$therefore~it- {1} over{2}+ {1} over{2}+(it-1)=it-1$',
    ],
    ch='삼각함수와 그래프', lv='하')

add(id='q05', kind='mc', no=5, score=3.4, layout='1x5',
    text='$sum^{10}_{l=1} LEFT( sum^{l}_{k=1}2 RIGHT)$의 값은?',
    choices=['$70$', '$80$', '$90$', '$100$', '$110$'],
    ans='⑤',
    sol=[
        '$sum^{l}_{k=1}2=2l$이므로 $sum^{10}_{l=1}2l=2 sum^{10}_{l=1}l=2 times55=110$',
        '$therefore~110$',
    ],
    ch='수열의 합', lv='중')

add(id='q06', kind='mc', no=6, score=3.6, layout='1x5',
    text='이차방정식 $4x^{2}-3x-k=0$의 두 근이 $sin theta,~cos theta$일 때, 상수 $k$의 값은?',
    choices=['${1} over{8}$', '${3} over{8}$', '${5} over{8}$', '${7} over{8}$', '${9} over{8}$'],
    ans='④',
    sol=[
        '근과 계수의 관계: $sin theta+cos theta= {3} over{4}$, $sin theta cos theta=it- {k} over{4}$',
        '$(sin theta+cos theta)^{2}=1+2 sin theta cos theta= {9} over{16}$에서 $2 sin theta cos theta= {9} over{16}-1=it- {7} over{16}$',
        '$sin theta cos theta=it- {7} over{32}$이므로 $it- {k} over{4}=it- {7} over{32}$',
        '$therefore~k= {7} over{8}$',
    ],
    ch='삼각함수와 그래프', lv='중')

add(id='q07', kind='mc', no=7, score=3.8, layout='1x5', fig='mm22f_q07',
    text='다음 그림은 함수 $y=a sin(bx-c)+d$의 그래프이다. 이때, 상수 $a,~b,~c,~d$에 대하여 $abcd$의 값은? (단, $a>0,~b>0,~0<c<pi$)',
    choices=['$2 pi$', '$3 pi$', '$4 pi$', '$5 pi$', '$6 pi$'],
    ans='⑤',
    sol=[
        '그래프의 최댓값 $4$, 최솟값 $0$이므로 $a= {4-0} over{2}=2,~d= {4+0} over{2}=2$',
        '두 봉우리 사이 간격(주기) $= {pi} over{3}-LEFT(it- {pi} over{3} RIGHT)= {2 pi} over{3}$이므로 $b= {2 pi} over{2 pi/3}=3$',
        '$x=it- {pi} over{3}$에서 최댓값이므로 $3 LEFT(it- {pi} over{3} RIGHT)-c= {pi} over{2}+2n pi$',
        '$it- pi-c= {pi} over{2}+2n pi$에서 $c=it- {3} over{2} pi-2n pi$, $n=it-1$일 때 $c= {pi} over{2}$ ($0<c<pi$ 만족)',
        '$a=2,~b=3,~c= {pi} over{2},~d=2$이므로 $therefore~abcd=2 times3 times {pi} over{2} times2=6 pi$',
    ],
    ch='삼각함수와 그래프', lv='중')

add(id='q08', kind='mc', no=8, score=3.8, layout='1x5',
    text='$11$과 $59$ 사이에 $n$개의 수를 넣어 $11,~a_{1},~a_{2},~cdots,~a_{n},~59$가 순서대로 공차가 $d$인 등차수열을 이루고 모든 항의 합이 $595$일 때, $n+d$의 값은?',
    choices=['$14$', '$15$', '$16$', '$17$', '$18$'],
    ans='⑤',
    sol=[
        '전체 항의 개수는 $n+2$개, 첫째항 $11$, 끝항 $59$',
        '합 $= {(n+2)(11+59)} over{2}=35(n+2)=595$에서 $n+2=17$, $n=15$',
        '끝항 $=11+(n+1)d=11+16d=59$에서 $16d=48$, $d=3$',
        '$therefore~n+d=15+3=18$',
    ],
    ch='등차수열', lv='중')

add(id='q09', kind='mc', no=9, score=3.0, layout='1x5',
    text='$a_{1}=2$인 수열 $LEFT{a_{n} RIGHT}$이 모든 자연수 $n$에 대하여 $a_{n+1}=a_{n}+n+2$을 만족시킬 때, $a_{5}$의 값은?',
    choices=['$14$', '$20$', '$26$', '$32$', '$38$'],
    ans='②',
    sol=[
        '$a_{5}=a_{1}+ sum^{4}_{n=1}(n+2)=2+LEFT[(1+2)+(2+2)+(3+2)+(4+2) RIGHT]=2+18=20$',
        '$therefore~20$',
    ],
    ch='수학적 귀납법', lv='하')

add(id='q10', kind='mc', no=10, score=4.5, layout='1x5',
    text=[
        '$0 LEQ x<2 pi$에서 $x$에 대한 부등식',
        '$a sin^{2}x-(3a+3)cosx-a-9>0$',
        '의 해가 존재하도록 하는 자연수 $a$의 최솟값은?',
    ],
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='②',
    sol=[
        '$t=cosx~(it-1 LEQ t LEQ 1)$로 치환: $sin^{2}x=1-t^{2}$',
        '$a(1-t^{2})-(3a+3)t-a-9>0$을 정리하면 $it-at^{2}-3t(a+1)-9>0$, 즉 $g(t)=at^{2}+3(a+1)t+9<0$',
        '$a GEQ 1$이면 $g$는 아래로 볼록, 꼭짓점 $t^{*}=it- {3(a+1)} over{2a}<it-1$ (항상 구간 왼쪽 밖)이므로 $g$는 $LEFT[it-1,1 RIGHT]$에서 증가',
        '구간에서의 최솟값은 $g(it-1)=a-3(a+1)+9=it-2a+6$',
        '해가 존재하려면 $g(it-1)<0$: $it-2a+6<0$에서 $a>3$',
        '자연수 $a$의 최솟값은 $therefore~4$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q11', kind='mc', no=11, score=3.8, layout='1x5',
    text='삼각형 $rm ABC$에서 $bar{rmAB}=6,~bar{rmAC}=8$이고 $sin(B+C)= {1} over{3}$일 때, 삼각형 $rm ABC$의 넓이는?',
    choices=['$2$', '$4$', '$6$', '$8$', '$10$'],
    ans='④',
    sol=[
        '$B+C=pi-A$이므로 $sin(B+C)=sin(pi-A)=sinA= {1} over{3}$',
        '넓이 $= {1} over{2} times bar{rmAB} times bar{rmAC} times sinA= {1} over{2} times6 times8 times {1} over{3}=8$',
        '$therefore~8$',
    ],
    ch='사인법칙과 코사인법칙', lv='중')

add(id='q12', kind='mc', no=12, score=4.7, layout='1x5',
    text='정의역이 양의 실수로 정의된 함수 $f(x)= {2} over{x^{7}}+ {2} over{x^{6}}+ cdots+ {2} over{x^{2}}+ {2} over{x}-5$일 때, 함수 $f(9)$의 값은?',
    choices=[
        '${1} over{4} {it-39-LEFT( {1} over{9} RIGHT)^{7}}$',
        '${1} over{4} {it-19-LEFT( {1} over{9} RIGHT)^{7}}$',
        '${1} over{4} {it-4-LEFT( {1} over{9} RIGHT)^{7}}$',
        '${1} over{8} {it-4-LEFT( {1} over{9} RIGHT)^{7}}$',
        '${1} over{8} {it-39-LEFT( {1} over{9} RIGHT)^{7}}$',
    ],
    ans='②',
    sol=[
        '$f(9)=2 sum^{7}_{k=1} LEFT( {1} over{9} RIGHT)^{k}-5$',
        '$sum^{7}_{k=1} LEFT( {1} over{9} RIGHT)^{k}= {{1} over{9}LEFT[1-LEFT( {1} over{9} RIGHT)^{7} RIGHT]} over{1- {1} over{9}}= {1} over{8}LEFT[1-LEFT( {1} over{9} RIGHT)^{7} RIGHT]$',
        '$f(9)=2 times {1} over{8}LEFT[1-LEFT( {1} over{9} RIGHT)^{7} RIGHT]-5= {1} over{4}-LEFT( {1} over{4} RIGHT)LEFT( {1} over{9} RIGHT)^{7}-5$',
        '$= {1} over{4} {1-LEFT( {1} over{9} RIGHT)^{7}}-5= {1} over{4} {it-19-LEFT( {1} over{9} RIGHT)^{7}}$',
        '$therefore~ {1} over{4} {it-19-LEFT( {1} over{9} RIGHT)^{7}}$',
    ],
    ch='수열의 합', lv='상')

add(id='q13', kind='mc', no=13, score=4.6, layout='1x5',
    text=[
        '그림과 같이 자연수를 나열할 때, $n$행에 나열되는 수들의 합을 $a_{n}$이라 하자.',
        '$1$행:$~1$',
        '$2$행:$~2,~4$',
        '$3$행:$~3,~6,~9$',
        '$4$행:$~4,~8,~12,~16$',
        '$5$행:$~5,~10,~15,~20,~25$',
        '$sum^{10}_{n=1} {n} over{a_{n}}$의 값은?',
    ],
    choices=['${5} over{11}$', '${10} over{11}$', '${15} over{11}$', '${20} over{11}$', '${25} over{11}$'],
    ans='④',
    sol=[
        '$n$행에는 $n,2n,cdots,n^{2}$의 $n$개 수가 있으므로 $a_{n}=n(1+2+cdots+n)=n times {n(n+1)} over{2}= {n^{2}(n+1)} over{2}$',
        '${n} over{a_{n}}= {n} over{{n^{2}(n+1)}/{2}}= {2} over{n(n+1)}=2 LEFT( {1} over{n}- {1} over{n+1} RIGHT)$',
        '$sum^{10}_{n=1} {n} over{a_{n}}=2 LEFT(1- {1} over{11} RIGHT)=2 times {10} over{11}= {20} over{11}$',
        '$therefore~ {20} over{11}$',
    ],
    ch='수열의 합', lv='상')

add(id='q14', kind='mc', no=14, score=3.9, layout='1x5',
    text='삼각형 $rm ABC$에 대하여 $sinA=cosA times tanB$가 성립할 때, 삼각형 $rm ABC$는 어떤 삼각형인가?',
    choices=[
        '$a$가 빗변인 직각삼각형',
        '$c$가 빗변인 직각삼각형',
        '$a=b$인 이등변삼각형',
        '$b=c$인 이등변삼각형',
        '$c=a$인 이등변삼각형',
    ],
    ans='③',
    sol=[
        '$sinA=cosA times tanB$에서 $tanB= {sinA} over{cosA}=tanA$ (단, $cosA NEQ 0$)',
        '$A,~B in(0,~ pi)$에서 $tanA=tanB$이면 $A=B$',
        '$A=B$이면 마주보는 변의 길이도 같으므로 $a=b$',
        '$therefore~a=b$인 이등변삼각형',
    ],
    ch='사인법칙과 코사인법칙', lv='중')

add(id='q15', kind='mc', no=15, score=5.0, layout='1x5',
    text=[
        '학교 정화 활동으로 목련 나무를 심기로 계획을 하는데 소요되는 일수를 계산해 보았다. 첫째 날에는 $3$그루, 다음 날은 그 전날보다 $x$그루씩 더 심으면 $9$일째에는 $11$그루만 심으면 되고, 첫째 날에는 $13$그루, 다음 날은 그 전날보다 $x$그루씩 더 심으면 $6$일째에는 $6$그루만 심으면 된다.',
        '이때 심으려는 목련나무의 총 개수는?',
    ],
    choices=['$84$', '$85$', '$87$', '$89$', '$91$'],
    ans='⑤',
    sol=[
        '목련나무의 총 필요 개수를 $T$라 하면, $9$일째까지 심은 뒤 남은 양이 $11$이므로 처음 $8$일간 심은 합 $S_{8}$에 대해 $T-S_{8}=11$',
        '$S_{8}= {8} over{2}LEFT[2(3)+7x RIGHT]=4(6+7x)=24+28x$이므로 $T=35+28x$ (ㄱ)',
        '마찬가지로 $6$일째까지 심은 뒤 남은 양이 $6$이므로 처음 $5$일간 심은 합 $S_{5}$에 대해 $T-S_{5}=6$',
        '$S_{5}= {5} over{2}LEFT[2(13)+4x RIGHT]=5(13+2x)=65+10x$이므로 $T=71+10x$ (ㄴ)',
        '(ㄱ)=(ㄴ): $35+28x=71+10x$에서 $18x=36$, $x=2$',
        '$therefore~T=35+28(2)=91$',
    ],
    ch='등차수열', lv='상')

add(id='q16', kind='mc', no=16, score=4.2, layout='1x5',
    text='수열 $LEFT{a_{n} RIGHT}$의 각 항은 $it-1,~0,~2$ 중의 어느 한 수이다. $sum^{10}_{k=1}a_{k}=8,~sum^{10}_{k=1}a_{k}^{3}=38$일 때, $sum^{10}_{k=1}a_{k}^{2}$의 값은?',
    choices=['$22$', '$24$', '$26$', '$28$', '$30$'],
    ans='①',
    sol=[
        '$it-1$이 $p$개, $0$이 $q$개, $2$가 $r$개라 하면 $p+q+r=10$',
        '합: $it-p+2r=8$. 세제곱의 합: $it-p+8r=38$',
        '두 식을 빼면 $6r=30$, $r=5$. 첫 식에 대입: $it-p+10=8$, $p=2$',
        '$sum a_{k}^{2}=p+4r=2+20=22$',
        '$therefore~22$',
    ],
    ch='수열의 합', lv='중')

add(id='q17', kind='mc', no=17, score=4.8, layout='1x5', fig='mm22f_q17',
    text='그림과 같이 $angle A=120 DEG,~bar{rmAB}=4,~bar{rmAC}=6$인 삼각형 $rm ABC$의 두 변 $rm AB,~AC$ 위에 삼각형 $rm ADE$의 넓이가 삼각형 $rm ABC$의 넓이의 ${1} over{3}$이 되도록 하는 두 점 $rm D,~E$를 각각 잡을 때, $bar{rmDE}$의 길이의 최솟값은?',
    choices=['$2 sqrt{3}$', '$3 sqrt{2}$', '$2 sqrt{6}$', '$sqrt{30}$', '$6$'],
    ans='③',
    sol=[
        '$bar{rmAD}=p,~bar{rmAE}=q$라 하면 넓이비 $= {p times q} over{bar{rmAB} times bar{rmAC}}= {pq} over{24}= {1} over{3}$에서 $pq=8$',
        '코사인법칙: $bar{rmDE}^{2}=p^{2}+q^{2}-2pq cos 120 DEG=p^{2}+q^{2}+pq$',
        '산술-기하평균: $p^{2}+q^{2} GEQ 2pq=16$ (등호는 $p=q=2 sqrt{2}$일 때, $2 sqrt{2} LEQ 4,~2 sqrt{2} LEQ 6$ 모두 만족)',
        '$bar{rmDE}^{2} GEQ 16+8=24$이므로 $bar{rmDE} GEQ 2 sqrt{6}$',
        '$therefore~2 sqrt{6}$',
    ],
    ch='사인법칙과 코사인법칙', lv='상')

add(id='q18', kind='mc', no=18, score=5.0, layout='1x5',
    text='연준이는 전 구간이 $20$km인 단축마라톤에 참가하였다. 처음 $6$km 구간까지는 시속 $12$km 속력으로 일정하게 달렸다. 이후 체력이 떨어져 $1$km를 달리는 데 걸린 시간은 바로 전 $1$km를 달리는 데 걸린 시간보다 $10$퍼센트씩 증가하였다. 문명이가 전 구간을 완주하는 데 걸린 시간은? (단, $1.1^{14}=4$로 계산한다.)',
    choices=['$3$시간 $15$분', '$3$시간 $30$분', '$3$시간 $45$분', '$4$시간', '$4$시간 $15$분'],
    ans='①',
    sol=[
        '처음 $6$km: 시간 $= {6} over{12}= {1} over{2}$시간',
        '마지막 $1$km(처음 $6$km 구간 안의 한 구간)의 시간은 $ {1} over{12}$시간. 그 다음 $1$km(전체 $7$번째)부터는 이전 구간보다 $10$퍼센트씩 증가',
        '$7$번째 구간 시간 $={1} over{12} times1.1$, 공비 $1.1$인 등비수열로 $20-6=14$개 구간(전체 $7$번째부터 $20$번째)',
        '이 $14$구간의 합 $= {{1} over{12}(1.1)(1.1^{14}-1)} over{1.1-1}= {{1} over{12}(1.1)(4-1)} over{0.1}= {1.1 times3} over{12 times0.1}= {3.3} over{1.2}= {33} over{12}$시간',
        '총 시간 $= {1} over{2}+ {33} over{12}= {6} over{12}+ {33} over{12}= {39} over{12}= {13} over{4}$시간$=3.25$시간',
        '$therefore~3$시간 $15$분',
    ],
    ch='등비수열', lv='상')

add(id='q19', kind='mc', no=19, score=4.9, layout='1x5',
    text='자연수 $n$에 대하여 $0 LEQ x LEQ 2^{n+1}$에서 함수 $y=3 cos LEFT( {pi} over{2^{n}}x RIGHT)$의 그래프가 직선 $y= {1} over{n}$과 만나는 모든 점의 $x$좌표의 합을 $x_{n}$이라 할 때, $sum^{6}_{n=1}x_{n}$의 값은?',
    choices=['$63$', '$126$', '$252$', '$504$', '$1008$'],
    ans='③',
    sol=[
        '주기: $T= {2 pi} over{ pi/2^{n}}=2^{n+1}$이므로 주어진 구간 $LEFT[0,~2^{n+1} RIGHT]$은 정확히 한 주기',
        '$theta= {pi} over{2^{n}}x$로 치환하면 $theta in LEFT[0,~2 pi RIGHT]$이고 $cos theta= {1} over{3n}$ ($0< {1} over{3n}<1$이므로 교점 $2$개)',
        {'fig': 'mm22f_q19_sol'},
        '두 해는 $theta= alpha$와 $theta=2 pi-alpha$ ($alpha$는 $cos theta= {1} over{3n}$을 만족하는 예각) 이고, 대응하는 $x$값의 합은 $x= {2^{n}} over{pi} theta$이므로',
        '$x_{n}= {2^{n}} over{pi}(alpha+(2 pi-alpha))= {2^{n}} over{pi} times2 pi=2^{n+1}$',
        '$sum^{6}_{n=1}x_{n}= sum^{6}_{n=1}2^{n+1}=2^{2}+2^{3}+2^{4}+2^{5}+2^{6}+2^{7}=4+8+16+32+64+128=252$',
        '$therefore~252$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q20', kind='sub', no=1, score=8.0, layout='1x5', fig='mm22f_q20',
    text=[
        '다음 그림과 같이 원에 내접하는 사각형 $rm ABCD$에서 $bar{rmAB}=4,~bar{rmBC}=6,~bar{rmCD}=3$이고, $sinD= {sqrt{5}} over{3}$일 때, 다음 물음에 답하시오. (단, $B$는 예각이다.)',
        '(1) 코사인 법칙을 활용하여 $bar{rmAC}$의 길이를 구하시오.',
        '(2) (1)을 활용하여 사각형 $rm ABCD$의 외접원의 넓이를 구하시오.',
    ],
    ans_mix='(1) $2 sqrt{5}$ (2) $9 pi$',
    sol=[
        '(1) 원에 내접하는 사각형이므로 $B+D=180 DEG$, $cosB=it-cosD$',
        '$sinD= {sqrt{5}} over{3}$이고 $B$가 예각이므로 $cosB>0$, 즉 $cosD<0$이어야 하므로 $cosD=it- {2} over{3}$ (피타고라스 정리: $cos^{2}D=1- {5} over{9}= {4} over{9}$)',
        '$cosB=it-cosD= {2} over{3}$',
        '삼각형 $rm ABC$에서 코사인법칙: $bar{rmAC}^{2}=bar{rmAB}^{2}+bar{rmBC}^{2}-2 times bar{rmAB} times bar{rmBC} times cosB=16+36-2(4)(6) LEFT( {2} over{3} RIGHT)=52-32=20$',
        '$therefore~bar{rmAC}=2 sqrt{5}$',
        '(2) $sinB=sqrt{1-cos^{2}B}=sqrt{1- {4} over{9}}= {sqrt{5}} over{3}$',
        '삼각형 $rm ABC$에 사인법칙 적용: $ {bar{rmAC}} over{sinB}=2R$에서 $2R= {2 sqrt{5}} over{{sqrt{5}}/{3}}=2 sqrt{5} times {3} over{sqrt{5}}=6$',
        '$R=3$이므로 외접원의 넓이 $=pi R^{2}=9 pi$',
        '$therefore~9 pi$',
    ],
    ch='사인법칙과 코사인법칙', lv='상')
