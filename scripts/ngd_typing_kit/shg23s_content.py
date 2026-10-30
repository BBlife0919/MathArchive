# -*- coding: utf-8 -*-
"""소하고등학교 2학년 2023 1학기 중간 수학1 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ---------------------------------------------------------------- 객관식
add(id='q01', kind='mc', no=1, score=4, layout='1x5',
    text='$root{3} of{4} times sqrt{root{3} of{4}}$의 값은?',
    choices=['$2$', '$2 root{3} of{2}$', '$3 root{3} of{2}$', '$4$', '$4 root{3} of{2}$'],
    ans='①',
    sol=[
        '$root{3} of{4}=4^{{1} over{3}}$, $sqrt{root{3} of{4}}=4^{{1} over{6}}$',
        '$4^{{1} over{3}} times4^{{1} over{6}}=4^{{1} over{2}}$',
        '$=2$',
    ],
    ch='지수', lv='하')

add(id='q02', kind='mc', no=2, score=4, layout='3+2',
    text='$log_{3}54+log_{3} root{4} of{2}-{5} over {4}log_{3}2$의 값은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='③',
    sol=[
        '$log_{3}54+log_{3}2^{{1} over{4}}-{5} over{4}log_{3}2$',
        '$=log_{3}54+{1} over{4}log_{3}2-{5} over{4}log_{3}2$',
        '$=log_{3}54-log_{3}2$',
        '$=log_{3}{54} over{2}$',
        '$=log_{3}27$',
        '$=3$',
    ],
    ch='로그', lv='하')

add(id='q03', kind='mc', no=3, score=4, layout='3+2',
    text='$cosLEFT(it- {11} over {6}pi RIGHT)$의 값은?',
    choices=['$it- {sqrt{3}} over {2}$', '$it- {1} over {2}$', '${1} over {2}$', '${sqrt{2}} over {2}$', '${sqrt{3}} over {2}$'],
    ans='⑤',
    sol=[
        '$cosLEFT(it- {11} over{6}pi RIGHT)=cosLEFT({11} over{6}pi RIGHT)$',
        '$=cosLEFT(2 pi-{pi} over{6} RIGHT)$',
        '$=cosLEFT({pi} over{6} RIGHT)$',
        '$={sqrt{3}} over{2}$',
    ],
    ch='일반각과 호도법', lv='하')

add(id='q04', kind='mc', no=4, score=4, layout='3+2',
    text='좌표평면에서 지수함수 $y=a^{x}$의 그래프를 $x$축에 대하여 대칭이동시킨 후 $x$축의 방향으로 $1$만큼, $y$축의 방향으로 $2$만큼 평행이동시킨 그래프가 점 $(2,~{it-4})$를 지난다. 양수 $a$의 값은?',
    choices=['${1} over {4}$', '${1} over {2}$', '$2$', '$4$', '$6$'],
    ans='⑤',
    sol=[
        '$y=a^{x}$를 $x$축에 대하여 대칭이동하면 $y=it-a^{x}$',
        '이를 $x$축으로 $1$, $y$축으로 $2$만큼 평행이동하면 $y=it-a^{x-1}+2$',
        '점 $(2,~{it-4})$를 지나므로',
        '$it-4=it-a^{2-1}+2$',
        '$it-a=it-6$',
        '$therefore~a=6$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q05', kind='mc', no=5, score=4, layout='3+2', fig='shg23s_q5',
    text='그림과 같이 함수 $y=log_{2}(x-a)+b$의 그래프의 점근선의 방정식은 $x=it-4$이다. 이때 두 실수 $a$, $b$의 합 $a+b$의 값은?',
    choices=['$it-3$', '$it-1$', '$1$', '$3$', '$5$'],
    ans='①',
    sol=[
        '점근선이 $x=it-4$이므로 $x-a=0$의 해가 $x=it-4$',
        '$therefore~a=it-4$',
        '그래프가 점 $(0,~3)$을 지나므로',
        '$3=log_{2}(0-a)+b=log_{2}4+b=2+b$',
        '$therefore~b=1$',
        '$therefore~a+b=it-4+1=it-3$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q06', kind='mc', no=6, score=5, layout='3+2',
    text='두 양수 $a$, $b$에 대하여 $a^{it- {1} over {2}}+b^{it- {1} over {2}}=3$, $a^{it-1}+b^{it-1}=5$일 때, $a^{2}b+ab^{2}$의 값은?',
    choices=['${1} over {4}$', '${5} over {16}$', '${3} over {8}$', '${7} over {16}$', '${1} over {2}$'],
    ans='②',
    sol=[
        '$u=a^{it- {1} over {2}}$, $v=b^{it- {1} over {2}}$라 하면',
        '$u+v=3$, $u^{2}+v^{2}=5$',
        '$(u+v)^{2}=u^{2}+2uv+v^{2}=9$이므로 $2uv=4$, $uv=2$',
        '$uv={1} over { sqrt{ab}}=2$이므로 $ sqrt{ab}={1} over{2}$, $ab={1} over{4}$',
        '$a+b={1} over{u^{2}}+{1} over{v^{2}}={u^{2}+v^{2}} over{(uv)^{2}}={5} over{4}$',
        '$therefore~a^{2}b+ab^{2}=ab(a+b)={1} over{4} times{5} over{4}$',
        '$={5} over{16}$',
    ],
    ch='지수', lv='중')

add(id='q07', kind='mc', no=7, score=5, layout='3+2',
    text='자연수 $n$이 $3 LEQ n LEQ 10$일 때, $n^{2}-14n+45$의 $n$제곱근 중에서 음의 실수가 존재하도록 하는 모든 $n$의 값의 합은?',
    choices=['$18$', '$19$', '$20$', '$21$', '$22$'],
    ans='④',
    sol=[
        '$X=n^{2}-14n+45=(n-5)(n-9)$라 하자.',
        '$X$의 $n$제곱근 중 음의 실수가 존재하는 경우는',
        '$n$이 홀수이고 $X<0$이거나, $n$이 짝수이고 $X>0$일 때이다.',
        '$n=3$: $X=12>0$ (홀수, 부적합)',
        '$n=4$: $X=5>0$ (짝수, 적합)',
        '$n=5$: $X=0$ (부적합)',
        '$n=6$: $X=it-3<0$ (짝수, 부적합)',
        '$n=7$: $X=it-4<0$ (홀수, 적합)',
        '$n=8$: $X=it-3<0$ (짝수, 부적합)',
        '$n=9$: $X=0$ (부적합)',
        '$n=10$: $X=5>0$ (짝수, 적합)',
        '적합한 $n$은 $4,~7,~10$이므로 합은',
        '$4+7+10=21$',
    ],
    ch='지수', lv='상')

add(id='q08', kind='mc', no=8, score=5, layout='3+2',
    text='어느 멸종 위기 동물의 개체 수는 매년 $5 %$씩 감소하여 올해 개체 수가 $800$이라고 한다. 이와 같은 개체 수 감소 추세가 계속된다고 가정할 때, 이 동물의 개체 수가 처음으로 $400$이하가 되는 것은 $n$년 후일 때, 자연수 $n$의 값은? (단, $log2=0.3010$, $log9.5=0.9777$이다.)',
    choices=['$11$', '$12$', '$13$', '$14$', '$15$'],
    ans='④',
    sol=[
        '$n$년 후의 개체 수는 $800 times0.95^{n}$이므로',
        '$800 times0.95^{n} LEQ 400$',
        '$0.95^{n} LEQ {1} over{2}$',
        '양변에 상용로그를 취하면 $nlog0.95 LEQ it-log2$',
        '$log0.95=log9.5-1=it-0.0223$',
        '$n times(it-0.0223) LEQ it-0.3010$',
        '$n GEQ {0.3010} over{0.0223}$',
        '$n GEQ 13.49 cdots$',
        '$n$은 자연수이므로 $n=14$',
    ],
    ch='지수함수와 로그함수의 활용', lv='중')

add(id='q09', kind='mc', no=9, score=5, layout='3+2',
    text='$0 LEQ x LEQ 1$일 때, $10^{x}$을 $3$으로 나눈 몫이 자연수이고 나머지가 $2$인 모든 $x$의 값의 합은?',
    choices=['$1+log2$', '$2+log2$', '$1+2log2$', '$1+3log2$', '$2+2log2$'],
    ans='③',
    sol=[
        '$10^{x}=3k+2$ ($k$는 자연수) 꼴이어야 하고, $0 LEQ x LEQ 1$에서 $1 LEQ 10^{x} LEQ 10$',
        '$3k+2 LEQ 10$인 자연수 $k$는 $k=1,~2$이므로 $10^{x}=5$ 또는 $10^{x}=8$',
        '$10^{x}=5$에서 $x=log5=1-log2$',
        '$10^{x}=8$에서 $x=log8=3log2$',
        '두 값 모두 $0 LEQ x LEQ 1$을 만족한다.',
        '$therefore$ 합 $=(1-log2)+3log2$',
        '$=1+2log2$',
    ],
    ch='지수함수와 로그함수의 활용', lv='중')

add(id='q10', kind='mc', no=10, score=5, layout='3+2',
    text='$1$이 아닌 두 양수 $a$, $b$에 대하여 이차방정식 $x^{2}-LEFT(log_{a}2a^{2} RIGHT)x-2=0$의 서로 다른 두 근이 $log_{a}2$, $log_{2}b$일 때, $a+b$의 값은?',
    choices=['$4$', '${9} over {2}$', '$5$', '${11} over {2}$', '$6$'],
    ans='②',
    sol=[
        '근과 계수의 관계에서 두 근의 곱은 $it-2$',
        '$log_{a}2 times log_{2}b=it-2$',
        '두 근의 합은 $log_{a}2a^{2}=log_{a}2+log_{a}a^{2}=log_{a}2+2$',
        '$log_{a}2+log_{2}b=log_{a}2+2$이므로 $log_{2}b=2$',
        '$therefore~b=4$',
        '$log_{a}2 times log_{2}4=log_{a}2 times2=it-2$이므로 $log_{a}2=it-1$',
        '$a^{it-1}=2$에서 $a={1} over {2}$',
        '$therefore~a+b={1} over {2}+4={9} over {2}$',
    ],
    ch='로그', lv='상')

add(id='q11', kind='mc', no=11, score=5, layout='3+2',
    text='$x$에 대한 부등식 $x^{2}-xlog_{2}4n+log_{2}n^{2} LEQ 0$을 만족시키는 정수 $x$의 개수가 $4$가 되도록 하는 자연수 $n$의 개수는?',
    choices=['$16$', '$32$', '$33$', '$64$', '$65$'],
    ans='②',
    sol=[
        '$t=log_{2}n$이라 하면 $log_{2}4n=2+t$, $log_{2}n^{2}=2t$',
        '부등식은 $x^{2}-(2+t)x+2t LEQ 0$, 즉 $(x-2)(x-t) LEQ 0$',
        '$n GEQ 1$이므로 $t GEQ 0$',
        '$t GEQ 2$이면 해는 $2 LEQ x LEQ t$이고, 정수 $x$의 개수는 $LEFT[t RIGHT]-1$',
        '$LEFT[t RIGHT]-1=4$에서 $LEFT[t RIGHT]=5$, 즉 $5 LEQ t<6$',
        '$t<2$이면 해는 $t LEQ x LEQ 2$이고, $0 LEQ t<2$에서 정수 $x$의 개수는 최대 $3$개뿐이라 $4$가 될 수 없다.',
        '$therefore~5 LEQ log_{2}n<6$',
        '$32 LEQ n<64$',
        '이를 만족시키는 자연수 $n$은 $32,~33,~ cdots,~63$의 $32$개',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q12', kind='mc', no=12, score=5, layout='3+2',
    text='부등식 $cosx LEQ cosLEFT({4} over {5}pi RIGHT)$를 만족시키는 $x$에서 $sinLEFT({5} over {6}x RIGHT)$의 최댓값을 $M$, 최솟값은 $m$이라 할 때, $M^{2}+m^{2}$의 값은? (단, $0 LEQ x LEQ 2 pi$)',
    choices=['${1} over {2}$', '${3} over {4}$', '${5} over {4}$', '${3} over {2}$', '$1$'],
    ans='②',
    sol=[
        '$cosx$는 $LEFT[0,~pi RIGHT]$에서 감소, $LEFT[pi,~2 pi RIGHT]$에서 증가하므로',
        '$cosx LEQ cosLEFT({4} over{5}pi RIGHT)$를 만족시키는 $x$의 범위는 ${4} over{5}pi LEQ x LEQ {6} over{5}pi$',
        '$u={5} over{6}x$라 하면 $x={4} over{5}pi$일 때 $u={2} over{3}pi$, $x={6} over{5}pi$일 때 $u=pi$',
        '$u in LEFT[{2} over{3}pi,~pi RIGHT]$에서 $sinu$는 감소하므로',
        '$M=sinLEFT({2} over{3}pi RIGHT)={sqrt{3}} over{2}$, $m=sinpi=0$',
        '$therefore~M^{2}+m^{2}={3} over{4}+0={3} over{4}$',
    ],
    ch='삼각함수와 그래프', lv='중')

add(id='q13', kind='mc', no=13, score=5, layout='3+2', fig='shg23s_q13',
    text='그림과 같이 지름의 길이가 $2$인 반원의 원주 위에 점 $rm P$가 있다. $widehat{rm BP}={pi} over {3}$일 때, 선분 $rm AP$와 선분 $rm AB$, 호 $rm BP$로 둘러싸인 부분의 넓이는?',
    choices=['$ sqrt{3}+{pi} over {3}$', '${ sqrt{3}} over {2}+{pi} over {3}$', '${ sqrt{3}} over {4}+{pi} over {3}$', '${ sqrt{3}} over {2}+{pi} over {6}$', '${ sqrt{3}} over {4}+{pi} over {6}$'],
    ans='⑤',
    sol=[
        '반지름이 $1$이므로 호 $rm BP$의 중심각은 $widehat{rm BP}=1 times theta={pi} over{3}$에서 $theta={pi} over{3}$',
        '원의 중심을 $rm O$라 하면 삼각형 $rm AOP$에서',
        '$∠{rm AOP}=pi-{pi} over{3}={2} over{3}pi$',
        '넓이 $={1} over{2} times1 times1 times sinLEFT({2} over{3}pi RIGHT)={1} over{2} times{ sqrt{3}} over{2}={ sqrt{3}} over{4}$',
        '부채꼴 $rm OBP$의 넓이 $={1} over{2} times1^{2} times{pi} over{3}={pi} over{6}$',
        '구하는 넓이는 삼각형 $rm AOP$의 넓이와 부채꼴 $rm OBP$의 넓이의 합이므로',
        '${ sqrt{3}} over{4}+{pi} over{6}$',
    ],
    ch='일반각과 호도법', lv='상')

add(id='q14', kind='mc', no=14, score=5, layout='3+2',
    text='자연수 $n$에 대하여 $2log_{8}LEFT({1} over {6n+16} RIGHT)$의 값이 정수가 되도록 하는 $1000$이하의 모든 $n$의 값의 합은?',
    choices=['$682$', '$684$', '$686$', '$688$', '$690$'],
    ans='④',
    sol=[
        '$2log_{8}{1} over {6n+16}=it-2log_{8}(6n+16)=it- {2} over {3}log_{2}(6n+16)$',
        '이 값이 정수가 되려면 $log_{2}(6n+16)$이 $3$의 배수인 정수이어야 하므로',
        '$6n+16=8^{q}$ ($q$는 $0$ 이상의 정수)의 꼴이어야 한다.',
        '$6n+16 GEQ 22$이므로 $q GEQ 2$',
        '$8^{q} equiv 2^{q}LEFT(mod~6 RIGHT)$ 꼴을 살펴보면 $q$가 짝수일 때만 $8^{q}-16$이 $6$으로 나누어떨어진다.',
        '$q=2$: $6n+16=64$, $n={48} over{6}=8$',
        '$q=4$: $6n+16=4096$, $n={4080} over{6}=680$',
        '$q=6$: $6n+16=262144$, $n={262128} over{6}=43688$ ($1000$ 초과)',
        '$1000$ 이하인 $n$은 $8$, $680$이므로 합은',
        '$8+680=688$',
    ],
    ch='로그', lv='상')

add(id='q15', kind='mc', no=15, score=6, layout='3+2', fig='shg23s_q15',
    text='함수 $y=atan(bx+c)+d$의 그래프가 그림과 같을 때, $a times b times c times d$의 값은? (단, $a>0$, $0<c<{pi} over {2}$이고 $b$, $d$는 실수이다.)',
    choices=['$it- {2 sqrt{3}pi} over {3}$', '$it- {sqrt{3}pi} over {3}$', '${sqrt{3}pi} over {3}$', '${2 sqrt{3}pi} over {3}$', '$2 sqrt{3}pi$'],
    ans='①',
    sol=[
        '두 점근선 $x=it- {pi} over{12}$, $x={5} over{12}pi$ 사이의 거리가 주기이므로',
        '주기 $={5} over{12}pi-LEFT(it- {pi} over{12} RIGHT)={pi} over{2}$',
        '${pi} over {LEFT | b RIGHT |}={pi} over{2}$이므로 $LEFT | b RIGHT |=2$',
        '그래프가 감소하는 모양이고 $a>0$이므로 $b<0$, 즉 $b=it-2$',
        '점근선 조건 $bx+c={pi} over{2}+kpi$에 $x=it- {pi} over{12}$를 대입하면',
        '${pi} over{6}+c={pi} over{2}+kpi$에서 $c={pi} over{3}+kpi$',
        '$0<c<{pi} over{2}$이므로 $k=0$, $c={pi} over{3}$',
        '$x=0$일 때 $y=4$이므로 $atanLEFT({pi} over{3} RIGHT)+d=4$, 즉 $a sqrt{3}+d=4$',
        '$x={pi} over{4}$일 때 $y=0$이므로',
        '$atanLEFT(it- {pi} over{2}+{pi} over{3} RIGHT)+d=0$, 즉 $atanLEFT(it- {pi} over{6} RIGHT)+d=0$',
        '$it- {a} over { sqrt{3}}+d=0$에서 $d={a} over { sqrt{3}}$',
        '$a sqrt{3}+{a} over { sqrt{3}}=4$에서 $a times LEFT( sqrt{3}+{1} over { sqrt{3}} RIGHT)=4$',
        '$a times{4} over { sqrt{3}}=4$이므로 $a= sqrt{3}$',
        '$d={ sqrt{3}} over { sqrt{3}}=1$',
        '$therefore~a times b times c times d= sqrt{3} times(it-2) times{pi} over{3} times1$',
        '$=it- {2 sqrt{3}pi} over{3}$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q16', kind='mc', no=16, score=6, layout='3+2', fig='shg23s_q16',
    text='양수 $a$에 대하여 직선 $y=4x$가 두 함수 $f(x)=LEFT({1} over {2} RIGHT)^{x-2}+a$, $g(x)=it-2^{x+2}-a$의 그래프와 만나는 점을 각각 $rm A$, $rm B$라 하자. 함수 $f(x)$의 역함수를 $h(x)$라 할 때, 직선 $y={1} over {4}x$가 함수 $y=h(x)$의 그래프와 만나는 점을 $rm C$라 하자. $bar{rm BC}=5 sqrt{2}$일 때, $f(a)+g(it-2a)+h(3a)$의 값은?',
    choices=['${3} over {4}$', '$1$', '${5} over {4}$', '${3} over {2}$', '${7} over {4}$'],
    ans='①',
    sol=[
        '$g(x)=it-2^{x+2}-a=it-LEFT(2^{x+2}+a RIGHT)=it-f(it-x)$',
        '$rm A$의 $x$좌표를 $p$라 하면 $f(p)=4p$',
        '$rm B$는 $g(x)=4x$의 해이므로 $it-f(it-x)=4x$, $f(it-x)=it-4x$이고',
        '$u=it-x$로 치환하면 $f(u)=4u$로 같은 방정식이 되어 $u=p$, 즉 $x=it-p$',
        '$therefore~rm A=(p,~4p)$, $rm B=(it-p,~{it-4p})$',
        '$h=f^{it-1}$이므로 $rm C$는 $rm A$를 직선 $y=x$에 대칭이동한 점과 같은 방식으로 구할 수 있다.',
        '직선 $y={1} over{4}x$ 위의 점이 $h$ 위에 있다는 것은, 이를 $y=x$에 대칭이동한 직선 $y=4x$ 위의 점이 $f$ 위에 있다는 것과 같으므로',
        '$rm C$를 $y=x$에 대칭이동하면 $rm A$와 같은 조건이 되어 $rm C=(4p,~p)$',
        '$bar{rm BC}^{2}=(4p-(it-p))^{2}+(p-(it-4p))^{2}=(5p)^{2}+(5p)^{2}=50p^{2}$',
        '$bar{rm BC}=5 sqrt{2}$이므로 $50p^{2}=50$, $p^{2}=1$',
        '그래프에서 $rm A$는 제$1$사분면에 있으므로 $p=1$',
        '$f(1)=4 times1=4$이고 $f(1)=LEFT({1} over{2} RIGHT)^{1-2}+a=2+a=4$이므로 $a=2$',
        '$f(2)=LEFT({1} over{2} RIGHT)^{0}+2=3$',
        '$g(it-4)=it-2^{it-4+2}-2=it- {1} over{4}-2=it- {9} over{4}$',
        '$h(6)$은 $f(x)=6$의 해이므로 $LEFT({1} over{2} RIGHT)^{x-2}+2=6$, $2^{2-x}=4$, $x=0$',
        '$therefore~f(a)+g(it-2a)+h(3a)=3+LEFT(it- {9} over{4} RIGHT)+0$',
        '$={3} over{4}$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q17', kind='mc', no=17, score=6, layout='1x5',
    text='함수 $f(x)= {cases{3^{x}~~&(x<2)#LEFT({1} over {4} RIGHT)^{x+a}-LEFT({1} over {4} RIGHT)^{2+a}+9~~&(x GEQ 2)}}$에 대하여 곡선 $y=f(x)$위의 점 중에서 $y$좌표가 정수인 점의 개수가 $24$인 정수 $a$에 대하여 $f(3)+a$의 값은?',
    choices=['$it-9$', '$it-8$', '$it-7$', '$it-6$', '$it-5$'],
    ans='③',
    sol=[
        '$x<2$에서 $y=3^{x}$는 $0<y<9$에서 연속이고 증가하므로',
        '정수 $y$값은 $1,~2,~ cdots,~8$의 $8$개',
        '$x GEQ 2$에서 $y=LEFT({1} over{4} RIGHT)^{x+a}-LEFT({1} over{4} RIGHT)^{2+a}+9$는',
        '$x=2$일 때 $y=9$이고, $x$가 증가함에 따라 $LEFT({1} over{4} RIGHT)^{x+a}$가 $0$으로 감소하므로',
        '$y$는 $9$에서 $L=9-LEFT({1} over{4} RIGHT)^{2+a}$로 (도달하지 않고) 감소한다.',
        '이 구간의 정수 $y$값의 개수가 $24-8=16$이어야 하므로',
        '$L$이 $it-7 LEQ L<it-6$을 만족시켜야 ($9,~8,~ cdots,~{it-6}$의 $16$개)',
        '$it-7 LEQ 9-LEFT({1} over{4} RIGHT)^{2+a}<it-6$',
        '$15<LEFT({1} over{4} RIGHT)^{2+a} LEQ 16$',
        '$a$가 정수이므로 $LEFT({1} over{4} RIGHT)^{2+a}$는 $4$의 거듭제곱이고, 이 범위의 값은 $16$뿐이므로',
        '$LEFT({1} over{4} RIGHT)^{2+a}=16=4^{2}$에서 $2+a=it-2$',
        '$therefore~a=it-4$',
        '$f(3)=LEFT({1} over{4} RIGHT)^{3-4}-LEFT({1} over{4} RIGHT)^{2-4}+9=4-16+9=it-3$',
        '$therefore~f(3)+a=it-3+(it-4)=it-7$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q18', kind='mc', no=18, score=6, layout='1x5',
    text='함수 $y=6sinLEFT({1} over {4}(x-pi) RIGHT)$ $(0 LEQ x LEQ 11 pi)$의 그래프와 직선 $y=3 sqrt{3}$이 만나는 점들 중 서로 다른 두 점 $rm A$, $rm B$의 함수 $y=6sinLEFT({1} over {4}(x-pi) RIGHT)$ $(0 LEQ x LEQ 11 pi)$의 그래프의 위의 점 $rm P$에 대하여 삼각형 $rm PAB$의 넓이의 최댓값이 $(p+q sqrt{3})pi$이다. 이때, $p+q$의 값은? (단, 점 $rm P$는 직선 $y=3 sqrt{3}$ 위의 점이 아니고 $p$, $q$는 유리수이다.)',
    choices=['$34$', '$35$', '$36$', '$37$', '$38$'],
    ans='③',
    sol=[
        '$theta={1} over {4}(x-pi)$라 하면 $6sintheta=3 sqrt{3}$에서 $sintheta={ sqrt{3}} over{2}$',
        '$theta={pi} over{3}+2kpi$ 또는 $theta={2} over{3}pi+2kpi$',
        '$0 LEQ x LEQ 11 pi$에서 $theta={x-pi} over{4} in LEFT[it- {pi} over{4},~{5} over{2}pi RIGHT]$이므로',
        '이를 만족시키는 $theta$는 ${pi} over{3}$, ${2} over{3}pi$, ${7} over{3}pi$의 세 개이고,',
        '$x=4 theta+pi$에서 대응하는 $x$는 ${7} over{3}pi$, ${11} over{3}pi$, ${31} over{3}pi$이다.',
        {'fig': 'shg23s_q18_sol'},
        '교점 중 가장 멀리 떨어진 두 점을 $rm A$, $rm B$로 잡으면 넓이가 최대가 되므로',
        '$rm A LEFT({7} over{3}pi,~3 sqrt{3} RIGHT)$, $rm B LEFT({31} over{3}pi,~3 sqrt{3} RIGHT)$',
        '$bar{rm AB}={31} over{3}pi-{7} over{3}pi=8 pi$',
        '점 $rm P$는 곡선의 최솟값인 $y=it-6$에서 넓이가 최대가 되므로',
        '높이 $=LEFT | it-6-3 sqrt{3} RIGHT |=6+3 sqrt{3}$',
        '넓이의 최댓값 $={1} over{2} times8 pi times LEFT(6+3 sqrt{3} RIGHT)$',
        '$=4piLEFT(6+3 sqrt{3} RIGHT)$',
        '$=24 pi+12 sqrt{3}pi$',
        '$therefore~p=24$, $q=12$이므로 $p+q=36$',
    ],
    ch='삼각함수와 그래프', lv='상')

# ---------------------------------------------------------------- 서술형
add(id='q19', kind='sub', no=1, score=10,
    text='$sintheta+costheta={1} over {2}$일 때, $sin^{5}theta+cos^{5}theta$의 값을 구하시오.',
    ans_eq='{79} over {128}',
    sol=[
        '$s=sintheta+costheta={1} over {2}$, $p=sinthetacostheta$라 하면',
        '$s^{2}=1+2p$에서 ${1} over{4}=1+2p$이므로 $p=it- {3} over{8}$',
        '$S_{n}=sin^{n}theta+cos^{n}theta$라 하면 $S_{n}=s times S_{n-1}-p times S_{n-2}$ ($S_{0}=2$, $S_{1}=s$)',
        '$S_{2}=s times S_{1}-p times S_{0}={1} over{2} times{1} over{2}-LEFT(it- {3} over{8} RIGHT) times2={1} over{4}+{3} over{4}=1$',
        '$S_{3}=s times S_{2}-p times S_{1}={1} over{2} times1-LEFT(it- {3} over{8} RIGHT) times{1} over{2}={1} over{2}+{3} over{16}={11} over{16}$',
        '$S_{4}=s times S_{3}-p times S_{2}={1} over{2} times{11} over{16}-LEFT(it- {3} over{8} RIGHT) times1={11} over{32}+{3} over{8}={23} over{32}$',
        '$S_{5}=s times S_{4}-p times S_{3}={1} over{2} times{23} over{32}-LEFT(it- {3} over{8} RIGHT) times{11} over{16}={23} over{64}+{33} over{128}$',
        '$={46} over{128}+{33} over{128}$',
        '$therefore~sin^{5}theta+cos^{5}theta={79} over {128}$',
    ],
    ch='일반각과 호도법', lv='중')

add(id='q20', kind='sub', no=2, score=10,
    text='함수 $y=log_{4}LEFT | 3x RIGHT |$의 그래프와 함수 $y=log_{4}(x+4)$의 그래프가 만나는 서로 다른 두 점을 각각 $rm A$, $rm B$라 하자. 점 $rm A$를 지나고 직선 $rm AB$와 수직인 직선이 $y$축과 만나는 점을 $rm C$라 할 때, 삼각형 $rm ABC$의 넓이를 구하시오. (단, 점 $rm A$의 $x$좌표는 점 $rm B$의 $x$좌표보다 작다.)',
    ans_eq='{37} over {4}',
    sol=[
        '$log_{4}LEFT | 3x RIGHT |=log_{4}(x+4)$에서 $LEFT | 3x RIGHT |=x+4$ (단, $x+4>0$)',
        '$x>0$이면 $3x=x+4$에서 $x=2$ ($x+4=6>0$, 성립)',
        '$x<0$이면 $it-3x=x+4$에서 $x=it-1$ ($x+4=3>0$, 성립)',
        '점 $rm A$의 $x$좌표가 더 작으므로 $rm A=LEFT(it-1,~log_{4}3 RIGHT)$, $rm B=LEFT(2,~log_{4}6 RIGHT)$',
        '직선 $rm AB$의 기울기 $={log_{4}6-log_{4}3} over {2-(it-1)}={log_{4}2} over {3}={ {1} over {2}} over {3}={1} over {6}$',
        '점 $rm A$를 지나고 직선 $rm AB$에 수직인 직선의 기울기는 $it-6$',
        '이 직선의 방정식: $y-log_{4}3=it-6(x+1)$',
        '$x=0$을 대입하면 $y=log_{4}3-6$이므로 $rm C=(0,~log_{4}3-6)$',
        '직선 $rm AC$의 기울기가 $it-6$으로 직선 $rm AB$(기울기 ${1} over {6}$)와 수직이므로',
        '삼각형 $rm ABC$는 $rm A$에서 직각인 직각삼각형이다.',
        '$bar{rm AC}= sqrt{(0-(it-1))^{2}+LEFT(log_{4}3-6-log_{4}3 RIGHT)^{2}}= sqrt{1+36}= sqrt{37}$',
        '$bar{rm AB}= sqrt{(2-(it-1))^{2}+LEFT(log_{4}6-log_{4}3 RIGHT)^{2}}= sqrt{9+{1} over {4}}={ sqrt{37}} over {2}$',
        '삼각형 $rm ABC$의 넓이 $={1} over {2} times bar{rm AB} times bar{rm AC}={1} over {2} times{ sqrt{37}} over {2} times sqrt{37}$',
        '$={37} over {4}$',
    ],
    ch='지수함수와 로그함수', lv='상')
