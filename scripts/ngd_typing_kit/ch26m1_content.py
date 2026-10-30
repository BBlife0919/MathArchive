# -*- coding: utf-8 -*-
"""충현고등학교 2학년 2026 1학기 중간 대수(지수로그~삼각함수의 기본성질) 19문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.5, layout='3+2',
    text='$a>0$, $a NEQ 1$이고 $a^{k} times sqrt[5]{ sqrt{a}}=a$일 때, 상수 $k$의 값은?',
    choices=['${1} over{10}$', '${1} over{5}$', '${4} over{5}$', '${6} over{7}$', '${9} over{10}$'],
    ans='⑤',
    sol=[
        '$ sqrt[5]{ sqrt{a}}= sqrt[5]{a^{{1} over{2}}}=a^{{1} over{10}}$',
        '$a^{k} times a^{{1} over{10}}=a^{k+{1} over{10}}=a^{1}$이므로 $k+{1} over{10}=1$',
        '$therefore~k=1-{1} over{10}$',
        '$={9} over{10}$',
    ],
    ch='거듭제곱근의 변형', lv='하')

add(id='q02', kind='mc', no=2, score=4.6, layout='3+2',
    text='$ sqrt[4]{9^{2}}+ sqrt[3]{(it-4)^{3}}+LEFT( sqrt[3]{2} RIGHT)^{6}- sqrt[4]{(it-3)^{4}}$의 값은?',
    choices=['$0$', '$2$', '$4$', '$6$', '$8$'],
    ans='①',
    sol=[
        '$ sqrt[4]{9^{2}}=9^{{2} over{4}}=9^{{1} over{2}}=3$',
        '$ sqrt[3]{(it-4)^{3}}=it-4$ (세제곱근은 홀수제곱근이므로 그대로)',
        '$LEFT( sqrt[3]{2} RIGHT)^{6}=2^{{6} over{3}}=2^{2}=4$',
        '$ sqrt[4]{(it-3)^{4}}= sqrt[4]{81}=81^{{1} over{4}}=3$',
        '$therefore$ 구하는 값은 $3+(it-4)+4-3$',
        '$=0$',
    ],
    ch='거듭제곱근의 계산', lv='하')

add(id='q03', kind='mc', no=3, score=4.7, layout='3+2',
    text='중심각의 크기가 ${2} over{3} pi$이고 넓이가 $12 pi$인 부채꼴의 반지름의 길이는?',
    choices=['$ sqrt{6}$', '$3 sqrt{2}$', '$6$', '$18$', '$36$'],
    ans='③',
    sol=[
        '부채꼴의 넓이 $S={1} over{2}r^{2} theta$이므로 ${1} over{2}r^{2}LEFT({2} over{3} pi RIGHT)=12 pi$',
        '${1} over{3} pi r^{2}=12 pi$에서 $r^{2}=36$',
        '$therefore~r$',
        '$=6$',
    ],
    ch='호도법과 부채꼴의 넓이', lv='하')

add(id='q04', kind='mc', no=4, score=4.8, layout='3+2',
    text='$ sin390^{ circ}+ cos(it-120^{ circ})+ tan135^{ circ}+ cos0^{ circ}$의 값은?',
    choices=['$0$', '${1} over{2}$', '${ sqrt{2}} over{2}$', '${ sqrt{3}} over{2}$', '$1$'],
    ans='①',
    sol=[
        '$ sin390^{ circ}= sin(360^{ circ}+30^{ circ})= sin30^{ circ}={1} over{2}$',
        '$ cos(it-120^{ circ})= cos120^{ circ}=it-{1} over{2}$',
        '$ tan135^{ circ}=it- tan45^{ circ}=it-1$',
        '$ cos0^{ circ}=1$',
        '$therefore$ 구하는 값은 ${1} over{2}+LEFT(it-{1} over{2} RIGHT)+(it-1)+1$',
        '$=0$',
    ],
    ch='삼각함수의 값', lv='하')

add(id='q05', kind='mc', no=5, score=4.8, layout='1x5',
    text='부등식 $LEFT({1} over{3} RIGHT)^{x}>LEFT({1} over{3} RIGHT)^{it-2x+18}$를 만족시키는 모든 자연수 $x$의 개수는?',
    choices=['$2$', '$3$', '$4$', '$5$', '$6$'],
    ans='④',
    sol=[
        '밑 ${1} over{3}$이 $1$보다 작으므로 지수함수는 감소함수이다. 따라서 부등호의 방향이 바뀐다.',
        '$x<it-2x+18$에서 $3x<18$',
        '$x<6$이므로 자연수 $x$는 $1,~2,~3,~4,~5$',
        '$therefore$ 자연수 $x$의 개수는',
        '$=5$',
    ],
    ch='지수부등식', lv='하')

add(id='q06', kind='mc', no=6, score=4.9, layout='3+2',
    text='함수 $y=2^{x+a}+b$의 그래프가 원점을 지나고, 점근선이 $y=it-4$이다. 이때, $a+b$의 값은? (단, $a,~b$는 상수이다.)',
    choices=['$it-6$', '$it-4$', '$it-2$', '$0$', '$2$'],
    ans='③',
    sol=[
        '점근선이 $y=it-4$이므로 $b=it-4$',
        '원점을 지나므로 $0=2^{0+a}+b=2^{a}-4$에서 $2^{a}=4$',
        '$a=2$',
        '$therefore~a+b=2+(it-4)$',
        '$=it-2$',
    ],
    ch='지수함수의 그래프와 점근선', lv='중')

add(id='q07', kind='mc', no=7, score=4.9, layout='1x5',
    text='어느 산유국의 올해 산유량은 $A$이고, 매년 $5$%씩 산유량을 감축하려고 한다. $n$년 후의 산유량이 올해 산유량의 ${1} over{4}$배가 된다고 할 때, 상수 $n$의 값은? (단, $ log2=0.30$, $ log0.95=it-0.02$로 계산한다.)',
    choices=['$15$', '$20$', '$25$', '$30$', '$35$'],
    ans='④',
    sol=[
        '$n$년 후 산유량은 $A(0.95)^{n}$이므로 $A(0.95)^{n}={1} over{4}A$에서 $(0.95)^{n}={1} over{4}$',
        '양변에 로그를 취하면 $n log0.95=it- log4=it-2 log2$',
        '$n(it-0.02)=it-2(0.30)=it-0.6$',
        '$therefore~n={it-0.6} over{it-0.02}$',
        '$=30$',
    ],
    ch='지수함수의 활용', lv='중')

add(id='q08', kind='mc', no=8, score=5.0, layout='1x5',
    text='이차방정식 $x^{2}+x+1=0$의 두 근을 $ alpha,~ beta$라고 할 때, $3^{{1} over{ alpha}} times3^{{1} over{ beta}}$의 값은?',
    choices=['${1} over{9}$', '${1} over{3}$', '$1$', '$3$', '$9$'],
    ans='②',
    sol=[
        '근과 계수의 관계에 의해 $ alpha+ beta=it-1$, $ alpha beta=1$',
        '$3^{{1} over{ alpha}} times3^{{1} over{ beta}}=3^{{1} over{ alpha}+{1} over{ beta}}=3^{{ alpha+ beta} over{ alpha beta}}=3^{{it-1} over{1}}$',
        '$therefore$ 구하는 값은',
        '$={1} over{3}$',
    ],
    ch='이차방정식의 근과 거듭제곱근의 활용', lv='중')

add(id='q09', kind='mc', no=9, score=5.0, layout='1x5',
    text='$ log_{3}LEFT(1+{1} over{2} RIGHT)+ log_{3}LEFT(1+{1} over{3} RIGHT)+ log_{3}LEFT(1+{1} over{4} RIGHT)+ cdots+ log_{3}LEFT(1+{1} over{n+1} RIGHT)=2$를 만족시키는 자연수 $n$의 값은?',
    choices=['$10$', '$12$', '$14$', '$16$', '$18$'],
    ans='④',
    sol=[
        '각 항은 $ log_{3}LEFT({k+1} over{k} RIGHT)$ ($k=2,~3, cdots,~n+1$) 꼴이므로, 전체 합은 $ log_{3}LEFT({3} over{2} times{4} over{3} times{5} over{4} times cdots times{n+2} over{n+1} RIGHT)$',
        '분모·분자가 연쇄적으로 약분(망원)되어 $={n+2} over{2}$',
        '$ log_{3}LEFT({n+2} over{2} RIGHT)=2$에서 ${n+2} over{2}=3^{2}=9$',
        '$n+2=18$',
        '$therefore~n$',
        '$=16$',
    ],
    ch='로그의 성질과 텔레스코핑', lv='중')

add(id='q10', kind='mc', no=10, score=5.0, layout='1x5',
    text='이차방정식 $3x^{2}-x+k=0$의 두 근이 $ sin theta,~ cos theta$일 때, 상수 $k$의 값은?',
    choices=['$it-{4} over{3}$', '$it-{1} over{3}$', '${1} over{3}$', '${4} over{3}$', '${8} over{3}$'],
    ans='①',
    sol=[
        '근과 계수의 관계에 의해 $ sin theta+ cos theta={1} over{3}$, $ sin theta cos theta={k} over{3}$',
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta$이므로 LEFT({1} over{3} RIGHT)^{2}=1+2LEFT({k} over{3} RIGHT)',
        '${1} over{9}=1+{2k} over{3}$에서 ${2k} over{3}={1} over{9}-1=it-{8} over{9}$',
        '$therefore~k=it-{8} over{9} times{3} over{2}$',
        '$=it-{4} over{3}$',
    ],
    ch='이차방정식의 근과 삼각함수', lv='중')

add(id='q11', kind='mc', no=11, score=5.1, layout='1x5',
    text='$a=4+2 sqrt{2}$, $b=4-2 sqrt{2}$이고, $x=a^{{1} over{3}}+b^{{1} over{3}}$일 때, $x^{3}-6x$의 값은?',
    choices=['$4$', '$4 sqrt{2}$', '$6$', '$6 sqrt{2}$', '$8$'],
    ans='⑤',
    sol=[
        '$a+b=8$, $ab=(4+2 sqrt{2})(4-2 sqrt{2})=16-8=8$',
        '$x^{3}=(a^{{1} over{3}}+b^{{1} over{3}})^{3}=a+b+3(ab)^{{1} over{3}}LEFT(a^{{1} over{3}}+b^{{1} over{3}} RIGHT)=a+b+3(ab)^{{1} over{3}}x$',
        '$(ab)^{{1} over{3}}=8^{{1} over{3}}=2$이므로 $x^{3}=8+3(2)x=8+6x$',
        '$therefore~x^{3}-6x=8+6x-6x$',
        '$=8$',
    ],
    ch='거듭제곱근의 활용', lv='상')

add(id='q12', kind='mc', no=12, score=5.1, layout='1x5', jogeon=True,
    text='두 양의 실수 $x,~y$가 다음 조건을 만족시킬 때, $LEFT | x-y RIGHT |$의 값은?',
    jogeon_items=[
        '$ log_{2}x+ log_{2}y=1$',
        '$ log_{3}LEFT(1+{2} over{x} RIGHT)+ log_{3}LEFT(1+{2} over{y} RIGHT)=2$',
    ],
    choices=['$2$', '$4$', '$2 sqrt{7}$', '$6$', '$4 sqrt{7}$'],
    ans='③',
    sol=[
        '(가)에서 $ log_{2}(xy)=1$이므로 $xy=2$',
        '(나)에서 $ log_{3}LEFT{LEFT(1+{2} over{x} RIGHT)LEFT(1+{2} over{y} RIGHT) RIGHT}=2$이므로 $LEFT(1+{2} over{x} RIGHT)LEFT(1+{2} over{y} RIGHT)=9$',
        '전개하면 $1+{2} over{x}+{2} over{y}+{4} over{xy}=9$이고 $xy=2$이므로 ${4} over{xy}=2$',
        '$1+{2} over{x}+{2} over{y}+2=9$에서 ${2} over{x}+{2} over{y}=6$, 즉 ${1} over{x}+{1} over{y}=3$',
        '${x+y} over{xy}=3$에서 ${x+y} over{2}=3$이므로 $x+y=6$',
        '$(x-y)^{2}=(x+y)^{2}-4xy=36-8=28$',
        '$therefore~LEFT | x-y RIGHT |= sqrt{28}$',
        '$=2 sqrt{7}$',
    ],
    ch='로그방정식의 연립', lv='상')

add(id='q13', kind='mc', no=13, score=5.2, layout='1x5',
    text='부등식 ${1} over{2} log_{2}(4x+12)>{1} over{ log_{x}2}$를 만족시키는 모든 정수 $x$의 개수는?',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='②',
    sol=[
        '진수조건: $4x+12>0$에서 $x>it-3$. 밑조건: $x>0$, $x NEQ 1$ (${1} over{ log_{x}2}$가 정의되려면)',
        '${1} over{ log_{x}2}= log_{2}x$이므로 부등식은 ${1} over{2} log_{2}(4x+12)> log_{2}x$, 즉 $ log_{2} sqrt{4x+12}> log_{2}x$',
        '$x>0$이므로 $ sqrt{4x+12}>x$의 양변을 제곱하면 $4x+12>x^{2}$에서 $x^{2}-4x-12<0$',
        '$(x-6)(x+2)<0$에서 $it-2<x<6$',
        '$x>0$, $x NEQ 1$ 조건과의 교집합은 $0<x<6$, $x NEQ 1$',
        '이를 만족시키는 정수는 $2,~3,~4,~5$',
        '$therefore$ 정수 $x$의 개수는',
        '$=4$',
    ],
    ch='로그부등식', lv='상')

add(id='q14', kind='mc', no=14, score=5.2, layout='1x5',
    text='정의역이 ${x LEFT | {it-2} LEQ x LEQ 2 RIGHT.}$인 함수 $y=LEFT({1} over{4} RIGHT)^{x}-LEFT({1} over{2} RIGHT)^{x-2}+5$는 $x= alpha$일 때, 최댓값 $M$, $x= beta$일 때, 최솟값 $m$을 갖는다. 이때, $ alpha beta+M+m$의 값은? (단, $ alpha,~ beta,~M,~m$은 상수이다.)',
    choices=['$8$', '$10$', '$12$', '$14$', '$16$'],
    ans='①',
    sol=[
        '$t=LEFT({1} over{2} RIGHT)^{x}$로 치환하면 ${it-2} LEQ x LEQ 2$에서 $t$는 ${1} over{4} LEQ t LEQ 4$',
        '$LEFT({1} over{4} RIGHT)^{x}=t^{2}$, $LEFT({1} over{2} RIGHT)^{x-2}=LEFT({1} over{2} RIGHT)^{x} times4=4t$',
        '$y=t^{2}-4t+5=(t-2)^{2}+1$',
        '꼭짓점 $t=2$가 구간 안에 있으므로, 최솟값은 $t=2$일 때 $m=1$이고, 이때 $LEFT({1} over{2} RIGHT)^{x}=2$에서 $x=it-1$, 즉 $ beta=it-1$',
        '최댓값은 양 끝 $t={1} over{4}$ 또는 $t=4$ 중 더 큰 값. $t={1} over{4}$: $LEFT({1} over{4}-2 RIGHT)^{2}+1={49} over{16}+1={65} over{16}$. $t=4$: $(4-2)^{2}+1=5$',
        '${65} over{16}<5$이므로 최댓값은 $t=4$일 때 $M=5$, 이때 $LEFT({1} over{2} RIGHT)^{x}=4$에서 $x=it-2$, 즉 $ alpha=it-2$',
        '$therefore~ alpha beta+M+m=(it-2)(it-1)+5+1=2+6$',
        '$=8$',
    ],
    ch='지수함수의 최대·최소', lv='상')

add(id='q15', kind='mc', no=15, score=5.3, layout='1x5',
    text=[
        '정의역과 공역이 각각 실수 전체의 집합인 함수',
        '$f(x)= cases{2^{it-x-4}-4~~(x<k)#{it- log_{2}(x+4)}-4~~(x GEQ k)}$',
        '가 일대일대응이 되도록 하는 상수 $k$의 값이 포함되는 범위는?',
    ],
    choices=['$it-{79} over{16}<k<it-4$', '$it-4<k<it-{63} over{16}$', '$it-{63} over{16}<k<it-3$', '$it-3<k<it-{47} over{16}$', '$it-{47} over{16}<k<it-2$'],
    ans='③',
    sol=[
        '$x<k$에서 $f(x)=2^{it-x-4}-4$는 감소함수이며, $x to k^{it-}$일 때 극한값 $L=2^{it-k-4}-4$에 가까워지나 도달하지 않는다. 치역은 $(L,~ infty)$',
        '$x GEQ k$에서 $f(x)=it- log_{2}(x+4)-4$도 감소함수이며, $x=k$에서 최댓값 $g(k)=it- log_{2}(k+4)-4$를 갖고, 치역은 $(it- infty,~g(k)RIGHT]$',
        '전체가 일대일대응이 되려면 두 치역이 겹치지도, 틈이 생기지도 않아야 하므로 $g(k)=L$이어야 한다.',
        '$it- log_{2}(k+4)-4=2^{it-k-4}-4$에서 $it- log_{2}(k+4)=2^{it-k-4}$',
        '$u=k+4$로 치환($0<u<1$, $k>it-4$ 영역에서 탐색)하면 $it- log_{2}u=2^{it-u}$',
        '$u=0.64$ 부근에서 양변이 근사적으로 일치함을 수치적으로 확인할 수 있다 (좌변 $ approx0.644$, 우변 $ approx0.642$)',
        '이때 $k=u-4 approxit-3.36$',
        '$therefore~k$의 값이 포함되는 범위는',
        '$=it-{63} over{16}<k<it-3$',
    ],
    ch='지수함수와 로그함수의 일대일대응', lv='최상')

add(id='q16', kind='mc', no=16, score=5.4, layout='1x5',
    text='양수 $n$과 상수 $k$에 대하여 함수 $f(x)=2^{x-2}+n$의 역함수를 $g(x)$라 하고, 두 곡선 $y=f(x)$, $y=g(x)$가 직선 $y=it-x+k$와 만나는 점을 각각 $P,~Q$라 하자. 두 점 $P,~Q$ 사이의 거리는 $4 sqrt{2}$이고 삼각형 $OPQ$의 넓이는 $20$일 때, $n+k$의 값은? (단, $O$는 원점이다.)',
    choices=['$13$', '$15$', '$16$', '$17$', '$19$'],
    ans='②',
    sol=[
        '$f,~g$는 서로 역함수이므로 $y=x$에 대해 대칭이다. 직선 $y=it-x+k$는 기울기가 $it-1$이라 $y=x$와 수직이므로, $P,~Q$는 이 직선 위에서 $y=x$에 대해 서로 대칭이다.',
        '$P=(p,~q)$라 하면 $Q=(q,~p)$. $bar{PQ}= sqrt{2}LEFT | p-q RIGHT |=4 sqrt{2}$에서 $LEFT | p-q RIGHT |=4$',
        '원점 $O$에서 직선 $x+y-k=0$까지의 거리는 ${LEFT | k RIGHT |} over{ sqrt{2}}$이므로, 삼각형 $OPQ$의 넓이 $={1} over{2} times4 sqrt{2} times{LEFT | k RIGHT |} over{ sqrt{2}}=2LEFT | k RIGHT |=20$에서 $LEFT | k RIGHT |=10$',
        '$p-q=it-4$ (즉 $q=p+4$)로 두면 $p={k-4} over{2}$, $q={k+4} over{2}$이고 $q=f(p)=2^{p-2}+n$',
        '$k=10$일 때 $p=3$, $q=7$이므로 $7=2^{3-2}+n=2+n$에서 $n=5$ ($n>0$으로 조건 만족)',
        '($k=it-10$이나 $p-q=4$인 경우는 $n$이 음수가 되어 제외)',
        '검산: $f(3)=2^{1}+5=7=q$ ✓, 삼각형 넓이 $={1} over{2}LEFT | 3 times3-7 times7 RIGHT |=20$ ✓',
        '$therefore~n+k=5+10$',
        '$=15$',
    ],
    ch='지수함수와 로그함수(역함수)의 그래프와 직선', lv='최상')

add(id='q17', kind='mc', no=17, score=5.5, layout='1x5', jogeon=True,
    text='함수 $y= log x$의 그래프 위의 서로 다른 두 점 $A(a,~ log a)$, $B(b,~ log b)$와 $x$축 위의 점 $C(1,~0)$이 다음 조건을 만족시킬 때, $a+b$의 값은? (단, $1<a<b$이다.)',
    jogeon_items=[
        '직선 $AC$의 기울기는 직선 $AB$의 기울기의 $4$배이다.',
        '두 점 $A,~B$에서 $x$축에 내린 수선의 발을 각각 $D,~E$라 할 때, 사다리꼴 $ADEB$의 넓이는 삼각형 $ACD$의 넓이의 $12$배이다.',
    ],
    choices=['$12$', '$16$', '$18$', '$20$', '$30$'],
    ans='④',
    sol=[
        '$p=a-1$, $q=b-a$ ($p,~q>0$)로 놓자. 삼각형 $ACD$의 넓이 $={1} over{2}(a-1) log a={1} over{2}p log a$',
        '사다리꼴 $ADEB$의 넓이 $={1} over{2}( log a+ log b)(b-a)={1} over{2}( log a+ log b)q$',
        '조건(나): $( log a+ log b)q=12p log a$ $ cdots$ ㉠',
        '조건(가): ${ log a} over{a-1}=4 times{ log b- log a} over{b-a}$에서 $( log a)q=4p( log b- log a)$ $ cdots$ ㉡',
        '㉡에서 $ log b= log a+{( log a)q} over{4p}= log a LEFT(1+{q} over{4p} RIGHT)$',
        '이를 ㉠에 대입하고 $ log a$로 나누면 $LEFT{1+LEFT(1+{q} over{4p} RIGHT) RIGHT}q=12p$에서 $LEFT({8p+q} over{4p} RIGHT)q=12p$',
        '$(8p+q)q=48p^{2}$에서 $q^{2}+8pq-48p^{2}=0$, $(q-4p)(q+12p)=0$이고 $q>0$이므로 $q=4p$',
        '$q=4p$를 ㉡에 대입: $ log b= log a LEFT(1+{4p} over{4p} RIGHT)=2 log a$이므로 $b=a^{2}$',
        '$b-a=4p=4(a-1)$에서 $a^{2}-a=4a-4$, $a^{2}-5a+4=0$, $(a-1)(a-4)=0$이고 $a>1$이므로 $a=4$',
        '$b=a^{2}=16$',
        '$therefore~a+b=4+16$',
        '$=20$',
    ],
    ch='로그함수의 그래프와 도형의 넓이', lv='최상')

add(id='q18', kind='sub', no=1, score=7.0, layout='1x5',
    text='함수 $y= log_{a}(x^{2}-2x+5)$의 최댓값이 $it-2$일 때 상수 $a$의 값을 구하고, 그 풀이과정을 서술하시오. (단, $a>0$, $a NEQ 1$이다.)',
    ans_mix='$a={1} over{2}$',
    sol=[
        '$u=x^{2}-2x+5=(x-1)^{2}+4$라 하면 $u$의 최솟값은 $4$(최댓값은 없음)이다.',
        '$y= log_{a}u$가 최댓값을 가지려면, $a>1$일 때는 $u to infty$에서 $y to infty$가 되어 최댓값이 존재하지 않으므로 $0<a<1$이어야 한다.',
        '$0<a<1$이면 $ log_{a}$는 감소함수이므로, $u$가 최솟값 $4$일 때 $y$가 최댓값을 갖는다.',
        '$ log_{a}4=it-2$에서 $a^{it-2}=4$, 즉 ${1} over{a^{2}}=4$에서 $a^{2}={1} over{4}$',
        '$a>0$이므로',
        '$therefore~a$',
        '$={1} over{2}$',
    ],
    ch='로그함수의 최댓값', lv='상')

add(id='q19', kind='sub', no=2, score=8.0, layout='1x5',
    text='$2$이상 $26$이하의 자연수 $n$에 대하여 $n^{2}-16$의 $n$제곱근 중 양의 실수가 존재하고, $n-16$의 $n$제곱근 중 음의 실수가 존재하도록 하는 모든 $n$의 개수를 구하고, 그 풀이과정을 서술하시오.',
    ans_mix='$11$',
    sol=[
        '[조건1] $n^{2}-16$의 $n$제곱근 중 양의 실수가 존재하려면 $n^{2}-16>0$이어야 한다(어떤 양수든 $n$제곱근 중 양의 실수가 정확히 하나 존재).',
        '$n^{2}>16$에서 $n>4$ (양의 정수), 즉 $n GEQ 5$',
        '[조건2] $n-16$의 $n$제곱근 중 음의 실수가 존재하는 경우를 나누어 본다.',
        '($n$이 홀수)일 때: 홀수제곱근은 부호를 그대로 가지므로, $n-16<0$ (즉 $n<16$)이면 음의 실근이 존재한다.',
        '($n$이 짝수)일 때: 짝수제곱근은 $n-16>0$ (즉 $n>16$)이면 양·음 두 실근이 존재하여 음의 실근도 존재한다. $n-16 LEQ 0$이면 음의 실근은 존재하지 않는다.',
        '즉 조건2는 ($n$이 홀수이고 $n<16$) 또는 ($n$이 짝수이고 $n>16$)일 때 성립한다.',
        '조건1($n GEQ 5$)과 조건2를 모두 만족시키는 $n$을 $2 LEQ n LEQ 26$에서 찾으면:',
        '(ⅰ) $n$이 홀수, $5 LEQ n<16$: $n=5,~7,~9,~11,~13,~15$ ($6$개)',
        '(ⅱ) $n$이 짝수, $16<n LEQ 26$: $n=18,~20,~22,~24,~26$ ($5$개)',
        '$therefore$ 모든 $n$의 개수는 $6+5$',
        '$=11$',
    ],
    ch='거듭제곱근의 존재조건', lv='상')
