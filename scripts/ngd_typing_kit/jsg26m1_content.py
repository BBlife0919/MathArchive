# -*- coding: utf-8 -*-
"""진성고등학교 2학년 2026 1학기 중간 대수(지수,로그~삼각함수의 그래프) 25문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=3.5, layout='3+2',
    text='$LEFT(2^{2- sqrt{3}} RIGHT)^{2+ sqrt{3}} times sqrt[3]{27}$의 값은?',
    choices=['$6$', '$12$', '$24$', '$48$', '$96$'],
    ans='①',
    sol=[
        '$LEFT(2^{2- sqrt{3}} RIGHT)^{2+ sqrt{3}}=2^{(2- sqrt{3})(2+ sqrt{3})}=2^{4-3}=2^{1}=2$',
        '$ sqrt[3]{27}=3$',
        '$therefore$ 구하는 값은 $2 times3$',
        '$=6$',
    ],
    ch='지수법칙의 계산', lv='하')

add(id='q02', kind='mc', no=2, score=3.5, layout='3+2',
    text='$ log_{16}6- log_{16}{3} over{2}$의 값은?',
    choices=['$ log_{4}5$', '$2$', '$ log_{2}3$', '$1$', '${1} over{2}$'],
    ans='⑤',
    sol=[
        '$ log_{16}6- log_{16}{3} over{2}= log_{16}LEFT(6 div{3} over{2} RIGHT)= log_{16}4$',
        '$4=16^{{1} over{2}}$이므로 $ log_{16}4={1} over{2}$',
        '$therefore$ 구하는 값은',
        '$={1} over{2}$',
    ],
    ch='로그의 성질', lv='하')

add(id='q03', kind='mc', no=3, score=3.6, layout='3+2',
    text='두 상수 $a,~b$에 대하여 $300^{ circ}=a pi$, $420^{ circ}=b pi$일 때, $a+b$의 값은?',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='②',
    sol=[
        '$300^{ circ}=300 times{ pi} over{180}={5} over{3} pi$이므로 $a={5} over{3}$',
        '$420^{ circ}=420 times{ pi} over{180}={7} over{3} pi$이므로 $b={7} over{3}$',
        '$therefore~a+b={5} over{3}+{7} over{3}={12} over{3}$',
        '$=4$',
    ],
    ch='호도법', lv='하')

add(id='q04', kind='mc', no=4, score=3.6, layout='3+2',
    text='$ cos^{2}10^{ circ}+ cos^{2}20^{ circ}+ cos^{2}30^{ circ}+ cdots+ cos^{2}90^{ circ}$의 값은?',
    choices=['$4$', '$5$', '$6$', '$7$', '$8$'],
    ans='①',
    sol=[
        '$ cos^{2} theta+ cos^{2}(90^{ circ}- theta)= cos^{2} theta+ sin^{2} theta=1$임을 이용한다.',
        '$ cos^{2}10^{ circ}+ cos^{2}80^{ circ}=1$, $ cos^{2}20^{ circ}+ cos^{2}70^{ circ}=1$, $ cos^{2}30^{ circ}+ cos^{2}60^{ circ}=1$, $ cos^{2}40^{ circ}+ cos^{2}50^{ circ}=1$',
        '이 네 쌍의 합이 $4$이고, 남은 항 $ cos^{2}90^{ circ}=0$',
        '$therefore$ 구하는 값은 $4+0$',
        '$=4$',
    ],
    ch='삼각함수의 값의 성질', lv='중')

add(id='q05', kind='mc', no=5, score=3.6, layout='1x5',
    text='부등식 $ log_{2}(x-2)+ log_{2}(3x-1) LEQ 3$을 만족시키는 정수 $x$의 개수는?',
    choices=['$0$', '$1$', '$2$', '$3$', '$4$'],
    ans='②',
    sol=[
        '진수조건: $x-2>0$이고 $3x-1>0$에서 $x>2$',
        '$ log_{2}(x-2)+ log_{2}(3x-1)= log_{2}LEFT{(x-2)(3x-1) RIGHT} LEQ 3$에서 $(x-2)(3x-1) LEQ 8$',
        '$3x^{2}-7x+2 LEQ 8$에서 $3x^{2}-7x-6 LEQ 0$, $(3x+2)(x-3) LEQ 0$에서 $it-{2} over{3} LEQ x LEQ 3$',
        '$x>2$와의 교집합은 $2<x LEQ 3$이고, 이를 만족시키는 정수는 $x=3$뿐이다.',
        '$therefore$ 정수 $x$의 개수는',
        '$=1$',
    ],
    ch='로그부등식', lv='중')

add(id='q06', kind='mc', no=6, score=3.7, layout='1x5',
    text='$0< theta<{ pi} over{2}$이고 $ sin theta- cos theta={1} over{5}$일 때, $ sin^{4} theta- cos^{4} theta$의 값은?',
    choices=['${7} over{25}$', '${7} over{5}$', '${12} over{25}$', '$it-{7} over{5}$', '$it-{7} over{25}$'],
    ans='①',
    sol=[
        '$( sin theta- cos theta)^{2}=1-2 sin theta cos theta={1} over{25}$에서 $ sin theta cos theta={12} over{25}$',
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta=1+{24} over{25}={49} over{25}$이고 $0< theta<{ pi} over{2}$이므로 $ sin theta+ cos theta={7} over{5}$',
        '$ sin^{4} theta- cos^{4} theta=( sin^{2} theta- cos^{2} theta)( sin^{2} theta+ cos^{2} theta)=( sin theta- cos theta)( sin theta+ cos theta)$',
        '$={1} over{5} times{7} over{5}$',
        '$={7} over{25}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q07', kind='mc', no=7, score=3.7, layout='1x5',
    text=[
        '$1$보다 큰 자연수 $n$에 대하여',
        '$ log_{n}LEFT( log_{n}( log_{n}a) RIGHT)=0$',
        '을 만족시키는 양수 $a$의 값을 $f(n)$이라 할 때, $f(3)+f(4)$의 값은?',
    ],
    choices=['$279$', '$280$', '$281$', '$282$', '$283$'],
    ans='⑤',
    sol=[
        '$ log_{n}LEFT( log_{n}( log_{n}a) RIGHT)=0$에서 $ log_{n}( log_{n}a)=n^{0}=1$',
        '$ log_{n}( log_{n}a)=1$에서 $ log_{n}a=n^{1}=n$',
        '$ log_{n}a=n$에서 $a=n^{n}$이므로 $f(n)=n^{n}$',
        '$f(3)=3^{3}=27$, $f(4)=4^{4}=256$',
        '$therefore~f(3)+f(4)=27+256$',
        '$=283$',
    ],
    ch='로그의 활용', lv='중')

add(id='q08', kind='mc', no=8, score=3.7, layout='1x5',
    text='어느 악취 물질의 농도가 $x$ppm일 때, 악취의 세기를 $I$라 하면 $I={3} over{2} log x+{5} over{2}$인 관계가 성립한다고 한다. 이 물질의 농도가 $2$ppm일 때 악취의 세기는 농도가 $30$ppm일 때 악취의 세기의 몇 배인가? (단, $ log2=0.3$, $ log3=0.4$로 계산한다.)',
    choices=['${14} over{23}$', '${57} over{92}$', '${29} over{46}$', '${59} over{92}$', '${59} over{102}$'],
    ans='④',
    sol=[
        '농도 $2$ppm일 때: $I_{2}={3} over{2} log2+{5} over{2}={3} over{2}(0.3)+2.5=0.45+2.5=2.95$',
        '농도 $30$ppm일 때: $ log30= log3+ log10=0.4+1=1.4$',
        '$I_{30}={3} over{2}(1.4)+2.5=2.1+2.5=4.6$',
        '$therefore~{I_{2}} over{I_{30}}={2.95} over{4.6}={295} over{460}$',
        '$={59} over{92}$',
    ],
    ch='로그의 활용', lv='중')

add(id='q09', kind='mc', no=9, score=3.7, layout='1x5',
    text=[
        '세 양수 $a,~b,~c$에 대하여',
        '${1} over{4b}+{1} over{2a}={2} over{c}$, $5^{a}=7^{b}=k^{c}$',
        '이 성립할 때, $k^{8}$의 값은? (단, $k$는 양수이다.)',
    ],
    choices=['$35$', '$70$', '$175$', '$245$', '$1225$'],
    ans='③',
    sol=[
        '$5^{a}=7^{b}=k^{c}=t$ ($t>0$)로 놓으면 $a= log_{5}t$, $b= log_{7}t$, $c= log_{k}t$',
        '${1} over{a}= log_{t}5$, ${1} over{b}= log_{t}7$, ${1} over{c}= log_{t}k$',
        '주어진 식 ${1} over{4b}+{1} over{2a}={2} over{c}$의 양변에 $4$를 곱하면 ${1} over{b}+{2} over{a}={8} over{c}$',
        '$ log_{t}7+2 log_{t}5=8 log_{t}k$에서 $ log_{t}(7 times5^{2})= log_{t}k^{8}$',
        '$therefore~k^{8}=7 times25$',
        '$=175$',
    ],
    ch='지수와 로그의 관계', lv='중')

add(id='q10', kind='mc', no=10, score=3.8, layout='1x5',
    text='좌표평면 위의 두 점 $A(2,~ log_{4}a)$, $B(4,~ log_{8}b)$를 지나는 직선이 점 $C(it-2,~0)$을 지날 때, $ log_{b}a$의 값은? (단, $b>0$, $b NEQ 1$, $a>0$)',
    choices=['${9} over{4}$', '${3} over{2}$', '$1$', '${2} over{3}$', '${4} over{9}$'],
    ans='⑤',
    sol=[
        '세 점 $A,~B,~C$가 한 직선 위에 있으므로 직선 $CA$와 직선 $CB$의 기울기가 같다.',
        '${ log_{4}a-0} over{2-(it-2)}={ log_{8}b-0} over{4-(it-2)}$에서 ${ log_{4}a} over{4}={ log_{8}b} over{6}$',
        '${ log_{4}a} over{ log_{8}b}={4} over{6}={2} over{3}$',
        '$ log_{4}a={ ln a} over{ ln4}$, $ log_{8}b={ ln b} over{ ln8}$이므로 ${ ln a} over{ ln b} times{ ln8} over{ ln4}={2} over{3}$',
        '${ ln8} over{ ln4}= log_{4}8={3} over{2}$이므로 ${ ln a} over{ ln b} times{3} over{2}={2} over{3}$에서 ${ ln a} over{ ln b}={4} over{9}$',
        '$therefore~ log_{b}a$',
        '$={4} over{9}$',
    ],
    ch='로그함수의 그래프', lv='상')

add(id='q11', kind='mc', no=11, score=3.8, layout='1x5', emptybox={'paras': [
        '(가) $a^{2}$은 $b^{4}$의 세제곱근 중 하나이다.',
        '(나) $b^{{1} over{2}}$은 $c^{4}$의 네제곱근 중 하나이다.',
    ]},
    text='$1$이 아닌 세 양수 $a,~b,~c$가 다음 조건을 만족시킨다.',
    text2=['$a^{3}=b^{m}=c^{n}$일 때, $m times n$의 값은? (단, $m,~n$은 상수이다.)'],
    choices=['$2$', '$4$', '$6$', '$8$', '$10$'],
    ans='④',
    sol=[
        '(가)에서 $a^{2}$이 $b^{4}$의 세제곱근 중 하나이므로 $(a^{2})^{3}=b^{4}$, 즉 $a^{6}=b^{4}$',
        '양변에 로그를 취하면 $6 ln a=4 ln b$에서 ${ ln a} over{ ln b}={2} over{3}$',
        '(나)에서 $b^{{1} over{2}}$이 $c^{4}$의 네제곱근 중 하나이므로 $LEFT(b^{{1} over{2}} RIGHT)^{4}=c^{4}$, 즉 $b^{2}=c^{4}$',
        '양변에 로그를 취하면 $2 ln b=4 ln c$에서 ${ ln b} over{ ln c}=2$',
        '$a^{3}=b^{m}$에서 $3 ln a=m ln b$이므로 $m=3 times{ ln a} over{ ln b}=3 times{2} over{3}=2$',
        '$b^{m}=c^{n}$에서 $m ln b=n ln c$이므로 $n=m times{ ln b} over{ ln c}=2 times2=4$',
        '$therefore~m times n=2 times4$',
        '$=8$',
    ],
    ch='거듭제곱근의 활용', lv='상')

add(id='q12', kind='mc', no=12, score=3.8, layout='1x5',
    text=[
        '$1$이 아닌 두 양수 $a$와 $b$($0<a<b<1$)에 대하여',
        '${3a} over{2 log_{a}b}={b} over{5 log_{b}a}={3a+b} over{11}$',
        '가 성립할 때, $ log_{a}b$의 값은?',
    ],
    choices=['$3$', '${1} over{2}$', '$4$', '${3} over{2}$', '$5$'],
    ans='②',
    sol=[
        '$ log_{a}b=x$라 하면 $ log_{b}a={1} over{x}$',
        '$0<a<b<1$이고 밑 $a<1$이므로 $ log_{a}$는 감소함수이다. $b>a$이므로 $ log_{a}b< log_{a}a=1$이고, $b<1$이므로 $ log_{a}b> log_{a}1=0$',
        '즉 $0<x<1$이 성립해야 하므로, 선택지 중 이 범위에 있는 것은 ${1} over{2}$뿐이다.',
        '(검산) $x={1} over{2}$이면 $ log_{a}b={1} over{2}$에서 $b=a^{{1} over{2}}$',
        '주어진 식에서 $a={1} over{900}$, $b=a^{{1} over{2}}={1} over{30}$으로 두면 세 비가 모두 ${1} over{2}$로 같음을 확인할 수 있다.',
        '$therefore~ log_{a}b$',
        '$={1} over{2}$',
    ],
    ch='로그의 성질과 범위', lv='상')

add(id='q13', kind='mc', no=13, score=3.9, layout='1x5',
    text='자연수 $n$에 대하여 이차함수 $y=x^{2}-x-1$의 그래프와 직선 $y=2n(x-1)$이 만나는 서로 다른 두 점의 $x$좌표를 $ alpha_{n},~ beta_{n}$이라 하자. $f(n)={1} over{ alpha_{n}}+{1} over{ beta_{n}}$이라 할 때, ${ log f(1)+ log f(2)+ log f(3)+ cdots+ log f(12)} over{ log f(1)+ log f(2)}$의 값은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='②',
    sol=[
        '$x^{2}-x-1=2n(x-1)$에서 $x^{2}-(1+2n)x+(2n-1)=0$',
        '근과 계수의 관계에 의해 $ alpha_{n}+ beta_{n}=1+2n$, $ alpha_{n} beta_{n}=2n-1$',
        '$f(n)={ alpha_{n}+ beta_{n}} over{ alpha_{n} beta_{n}}={2n+1} over{2n-1}$',
        '$f(1)={3} over{1}$, $f(2)={5} over{3}$, $f(3)={7} over{5}$, $cdots$, $f(12)={25} over{23}$이므로, 곱이 망원(telescoping)된다.',
        '$f(1) times f(2) times cdots times f(12)={25} over{1}=25$이므로 $ log f(1)+ cdots+ log f(12)= log25$',
        '$f(1) times f(2)={3} over{1} times{5} over{3}=5$이므로 $ log f(1)+ log f(2)= log5$',
        '$therefore$ 구하는 값은 ${ log25} over{ log5}={2 log5} over{ log5}$',
        '$=2$',
    ],
    ch='이차함수와 직선의 교점·로그의 계산', lv='상')

add(id='q14', kind='mc', no=14, score=4.0, layout='1x5', fig='jsg26m1_q14',
    text='그림과 같이 $0 LEQ x<4$에서 함수 $y= cos pi x$의 그래프와 직선 $y=k$가 만나는 점의 $x$좌표를 각각 $ alpha,~ beta,~ gamma,~ delta$($ alpha< beta< gamma< delta$)라 하자. $ alpha delta={39} over{16}$일 때, $ beta gamma$의 값은? (단, $it-1<k<0$이다.)',
    choices=['${3} over{2}$', '${5} over{4}$', '${11} over{4}$', '${11} over{16}$', '${55} over{16}$'],
    ans='⑤',
    sol=[
        '$y= cos pi x$는 $x=1$에 대하여 대칭이므로 $ alpha=1-s$, $ beta=1+s$ ($0<s<1$)로 둘 수 있다.',
        '같은 함수모양이 $x=3$에서 반복되므로 $ gamma=3-s$, $ delta=3+s$',
        '$ alpha delta=(1-s)(3+s)=3-2s-s^{2}={39} over{16}$에서 $16s^{2}+32s-9=0$',
        '$s={it-32 pm sqrt{32^{2}+4 times16 times9}} over{32}={it-32 pm40} over{32}$이고 $0<s<1$이므로 $s={1} over{4}$',
        '$ beta gamma=(1+s)(3-s)=3+2s-s^{2}=3+{1} over{2}-{1} over{16}={48+8-1} over{16}$',
        '$={55} over{16}$',
    ],
    ch='삼각함수의 그래프와 직선의 교점', lv='상')

add(id='q15', kind='mc', no=15, score=4.0, layout='1x5',
    text='직선 $x-ny-1=0$과 함수 $y= sin{ pi} over{2}x$의 그래프가 제$1$사분면에서 만나는 점의 개수가 $5$가 되도록 하는 모든 자연수 $n$의 값의 합은?',
    choices=['$30$', '$32$', '$34$', '$36$', '$38$'],
    ans='①',
    sol=[
        '직선은 $y={x-1} over{n}$이고 항상 점 $(1,~0)$을 지난다. $x<1$이면 $y<0$이므로 제$1$사분면과 무관하다.',
        '$y= sin{ pi} over{2}x$는 $x=4k$에서 $4k+2$ ($k=0,~1,~2, cdots$)까지 양의 값의 산(hump)을 이룬다.',
        '첫 산($0<x<2$)에서는 $x=1$에서 $ sin=1>$직선$=0$이고 $x=2$에서 $ sin=0<$직선$={1} over{n}$이므로 항상 정확히 $1$개의 교점이 생긴다.',
        '$k$번째 산($4k<x<4k+2$, $k GEQ 1$)의 꼭짓점 $x=4k+1$에서 직선값은 ${4k} over{n}$이다. $1>{4k} over{n}$ 즉 $n>4k$이면 그 산에서 $2$개의 교점이, $n<4k$이면 $0$개, $n=4k$이면 접하여 $1$개가 생긴다.',
        '전체 교점이 $5$개가 되려면 $k=1,~2$에서는 $n>4k$(각 $2$개, 합 $4$개)이고 $k=3$에서는 $n LEQ 12$이면서 접하지 않아야 한다.',
        '즉 $n>8$이고 $n<12$(또는 $n=12$면 접하여 총 $6$개가 되므로 제외)이어야 하므로 $n=9,~10,~11,~12$ 중 $n=12$만 제외한다.',
        '$n=9$: 교점 $1+2+2+0=5$ ✓, $n=10,~11$도 동일하게 $5$ ✓, $n=12$는 $k=3$에서 접하여 $1+2+2+1=6$이 되어 제외.',
        '따라서 가능한 $n$은 $9,~10,~11$이다.',
        '$therefore$ 모든 $n$의 값의 합은 $9+10+11$',
        '$=30$',
    ],
    ch='삼각함수의 그래프와 직선의 교점 개수', lv='상')

add(id='q16', kind='mc', no=16, score=4.1, layout='1x5', emptybox={'paras': [
        '(가) 함수 $y=f(x)$의 그래프와 $x$축 및 $y$축으로 둘러싸인',
        '도형과 그 내부에 있는 점 중 $x$좌표와 $y$좌표가 모두',
        '자연수인 점의 개수는 $22$개다.',
        '(나) $f^{it-1}(b) times f^{it-1}(b+1)=8$',
    ]},
    text='두 자연수 $a,~b$에 대하여, 함수 $y= log_{3}x$의 그래프를 $y$축에 대하여 대칭이동한 후, $x$축의 방향으로 $a$만큼, $y$축의 방향으로 $b$만큼 평행이동한 그래프를 나타내는 식을 $y=f(x)$라 하자. 함수 $f(x)$가 다음 [조건]을 만족시킬 때, $a+b$의 값은? (단, $f^{it-1}$는 $f$의 역함수이다.)',
    choices=['$8$', '$9$', '$10$', '$11$', '$12$'],
    ans='③',
    sol=[
        '$y= log_{3}x$를 $y$축대칭: $y= log_{3}(it-x)$, $x$방향 $a$, $y$방향 $b$ 평행이동: $f(x)= log_{3}(a-x)+b$ ($x<a$)',
        '$f(x)$의 역함수: $y= log_{3}(a-x)+b$에서 $x=a-3^{y-b}$이므로 $f^{it-1}(y)=a-3^{y-b}$',
        '(나): $f^{it-1}(b)=a-3^{0}=a-1$, $f^{it-1}(b+1)=a-3^{1}=a-3$이므로 $(a-1)(a-3)=8$',
        '$a^{2}-4a-5=0$에서 $(a-5)(a+1)=0$이고 $a$는 자연수이므로 $a=5$',
        '$f(x)= log_{3}(5-x)+b$ ($x<5$). $x$좌표가 자연수인 $x=1,~2,~3,~4$에서 $y$좌표가 자연수(즉 $1$ 이상)인 개수를 센다.',
        '$f(1)= log_{3}4+b$ ($1<1.27$이므로 몫 $b+1$), $f(2)=1+b$(몫 $b+1$), $f(3)= log_{3}2+b$(몫 $b$), $f(4)=b$(몫 $b$)',
        '점의 개수 합: $(b+1)+(b+1)+b+b=4b+2=22$에서 $b=5$',
        '$therefore~a+b=5+5$',
        '$=10$',
    ],
    ch='로그함수의 평행이동과 격자점의 개수', lv='상')

add(id='q17', kind='mc', no=17, score=4.2, layout='1x5',
    text=[
        '실수 $k$에 대하여 함수',
        '$f(x)= cos^{2}LEFT(x-{3} over{4} pi RIGHT)- cos LEFT(x-{1} over{4} pi RIGHT)+k$',
        '의 최댓값은 $3$, 최솟값은 $m$이다. $k-m$의 값은?',
    ],
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='①',
    sol=[
        '$u=x-{1} over{4} pi$로 치환하면 $x-{3} over{4} pi=u-{ pi} over{2}$이므로 $ cos LEFT(u-{ pi} over{2} RIGHT)= sin u$',
        '$f= sin^{2}u- cos u+k=(1- cos^{2}u)- cos u+k$',
        '$t= cos u$ ($it-1 LEQ t LEQ 1$)로 놓으면 $f=it-t^{2}-t+1+k=it LEFT(t+{1} over{2} RIGHT)^{2}+{5} over{4}+k$',
        '최댓값은 $t=it-{1} over{2}$에서 ${5} over{4}+k=3$이므로 $k={7} over{4}$',
        '최솟값은 양 끝 $t=it-1$ 또는 $t=1$ 중 작은 값: $f(it-1)=it-1+1+1+k=1+k={11} over{4}$, $f(1)=it-1-1+1+k=it-1+k={3} over{4}$',
        '더 작은 값은 ${3} over{4}$이므로 $m={3} over{4}$',
        '$therefore~k-m={7} over{4}-{3} over{4}={4} over{4}$',
        '$=1$',
    ],
    ch='삼각함수의 최댓값과 최솟값', lv='상')

add(id='q18', kind='mc', no=18, score=4.2, layout='1x5',
    text='${1} over{2}< log a<{11} over{2}$인 양수 $a$에 대하여 ${1} over{3}+ log sqrt{a}$의 값이 자연수가 되도록 하는 모든 $a$의 값의 곱은?',
    choices=['$10^{9}$', '$10^{10}$', '$10^{11}$', '$10^{12}$', '$10^{13}$'],
    ans='②',
    sol=[
        '$ log a=L$이라 하면 ${1} over{2}<L<{11} over{2}$. ${1} over{3}+{L} over{2}=n$(자연수)이라 하면 $L=2n-{2} over{3}$',
        '${1} over{2}<2n-{2} over{3}<{11} over{2}$에서 $n$에 대해 풀면 ${7} over{12}<n<{37} over{12}$, 즉 $0.583<n<3.083$',
        '정수 $n$은 $1,~2,~3$',
        '$n=1$: $L={4} over{3}$, $a=10^{{4} over{3}}$. $n=2$: $L={10} over{3}$, $a=10^{{10} over{3}}$. $n=3$: $L={16} over{3}$, $a=10^{{16} over{3}}$',
        '$therefore$ 모든 $a$의 곱은 $10^{{4} over{3}+{10} over{3}+{16} over{3}}=10^{{30} over{3}}$',
        '$=10^{10}$',
    ],
    ch='로그의 성질과 자연수 조건', lv='상')

add(id='q19', kind='mc', no=19, score=4.2, layout='1x5',
    text='실수 $x$에 대하여 $x$의 세제곱근 중에서 실수인 것의 개수를 $f(x)$, $x^{2}-3 LEFT | x RIGHT |$의 네제곱근 중에서 실수인 것의 개수를 $g(x)$라 하자. $LEFT | a RIGHT | LEQ 1$과 $LEFT | b RIGHT | LEQ 5$를 만족시키는 두 정수 $a$와 $b$에 대하여 부등식 $f(a)g(b)+g(b+2)<3$을 만족시키는 순서쌍 $(a,~b)$의 개수는?',
    choices=['$12$', '$15$', '$18$', '$21$', '$24$'],
    ans='④',
    sol=[
        '임의의 실수 $x$에 대하여 세제곱근은 항상 실수인 것이 정확히 $1$개이므로 $f(x)=1$ (상수함수).',
        '$h(x)=x^{2}-3 LEFT | x RIGHT | = LEFT | x RIGHT | LEFT( LEFT | x RIGHT |-3 RIGHT)$. 네제곱근(짝수제곱근)은 $h>0$이면 $2$개, $h=0$이면 $1$개, $h<0$이면 $0$개이다.',
        '$h(x)>0 LEFT RIGHT. LEFT | x RIGHT |>3$, $h(x)=0 LEFT RIGHT. LEFT | x RIGHT |=0,~3$, $h(x)<0 LEFT RIGHT.0< LEFT | x RIGHT |<3$',
        '정수 $x$에서 $g$의 값: $g(0)=1$, $g( pm1)=g( pm2)=0$, $g( pm3)=1$, $LEFT | x RIGHT | GEQ 4$이면 $g(x)=2$',
        '$f(a)=1$이므로 부등식은 $g(b)+g(b+2)<3$으로 간단해진다. $b=it-5, cdots,5$ 각각에 대해 $g(b)+g(b+2)$를 계산하면 $b={it-4},~{it-3},~{it-2},~{it-1},~0,~1,~2$일 때만 $3$ 미만(각각 $2,~1,~1,~0,~1,~1,~2$)이고, $b={it-5},~3,~4,~5$는 $3$ 이상이다.',
        '조건을 만족시키는 $b$는 $7$개이고, $a$는 $it-1,~0,~1$의 $3$개 중 어느 것이어도 성립한다.',
        '$therefore$ 순서쌍 $(a,~b)$의 개수는 $3 times7$',
        '$=21$',
    ],
    ch='거듭제곱근의 개수', lv='상')

add(id='q20', kind='mc', no=20, score=4.2, layout='1x5',
    text=[
        '$it-{ pi} over{2}<x<{ pi} over{2}$일 때, 부등식',
        '$( sqrt{3}-1) cos^{2}x-( sqrt{3}+1) sin x cos x+1 LEQ 0$',
        '의 해가 $ alpha LEQ x LEQ beta$이다. $ alpha+ beta$의 값은? (단, $ alpha,~ beta$는 상수이다.)',
    ],
    choices=['${ pi} over{3}$', '${ pi} over{12}$', '${7} over{12} pi$', '${5} over{12} pi$', '${ pi} over{36}$'],
    ans='③',
    sol=[
        '$ cos^{2}x={1+ cos2x} over{2}$, $ sin x cos x={ sin2x} over{2}$를 대입하면',
        '$( sqrt{3}+1)+( sqrt{3}-1) cos2x-( sqrt{3}+1) sin2x LEQ 0$',
        '$( sqrt{3}-1) cos2x-( sqrt{3}+1) sin2x=R cos(2x+ phi)$ 꼴로 합성하면 $R= sqrt{( sqrt{3}-1)^{2}+( sqrt{3}+1)^{2}}= sqrt{8}=2 sqrt{2}$',
        '$ tan phi={ sqrt{3}+1} over{ sqrt{3}-1}=2+ sqrt{3}= tan75^{ circ}$이므로 $ phi={5} over{12} pi$',
        '부등식은 $( sqrt{3}+1)+2 sqrt{2} cos LEFT(2x+{5} over{12} pi RIGHT) LEQ 0$에서 $ cos LEFT(2x+{5} over{12} pi RIGHT) LEQit-{ sqrt{3}+1} over{2 sqrt{2}}=it- cos15^{ circ}$',
        '$ cos theta LEQit- cos15^{ circ}$의 해는 $ theta$가 $165^{ circ}={11} over{12} pi$에서 $195^{ circ}={13} over{12} pi$ 사이이다.',
        '$2x+{5} over{12} pi$가 이 범위에 있으려면 $2x$는 ${ pi} over{2}$에서 ${2} over{3} pi$ 사이, 즉 $x$는 ${ pi} over{4}$에서 ${ pi} over{3}$ 사이',
        '$ alpha={ pi} over{4}$, $ beta={ pi} over{3}$이므로 $ alpha+ beta={ pi} over{4}+{ pi} over{3}={3 pi} over{12}+{4 pi} over{12}$',
        '$={7} over{12} pi$',
    ],
    ch='삼각함수의 합성과 부등식', lv='상')

add(id='q21', kind='mc', no=21, score=4.3, layout='1x5', fig='jsg26m1_q21',
    text='최고차항의 계수가 정수인 두 이차함수 $y=f(x)$, $y=g(x)$의 그래프가 아래 그림과 같다. 부등식 $ log_{3}f(x)< log_{3}g(x)$를 만족시키는 정수 $x$가 $1$개뿐이고 함수 $f(x)$의 최고차항의 계수가 $1$일 때, $g(2)$의 최댓값을 $M$, 최솟값을 $m$이라 하자. $M+m$의 값은? (단, $M$과 $m$은 상수이고 $f(it-4)=f(2)=g(0)=g(6)=0$이다.)',
    choices=['$12$', '$16$', '$20$', '$24$', '$32$'],
    ans='④',
    sol=[
        '$f$는 최고차항 계수가 $1$(양수)이므로 아래로 볼록, 뿌리가 $it-4,~2$: $f(x)=(x+4)(x-2)$',
        '$g$는 그림에서 위로 볼록이므로 최고차항 계수는 음의 정수. 뿌리가 $0,~6$이므로 $g(x)=k x(x-6)$ ($k$는 음의 정수)이다. $k=it-p$ ($p$는 자연수)로 두면 $g(x)=p x(6-x)$',
        '진수조건 $f(x)>0$: $x<it-4$ 또는 $x>2$. $g(x)>0$: $0<x<6$. 교집합은 $2<x<6$',
        '이 범위의 정수 $x=3,~4,~5$에 대해 $f(3)=7$, $f(4)=16$, $f(5)=27$이고 $g(3)=9p$, $g(4)=8p$, $g(5)=5p$',
        '$f(x)<g(x)$ 조건: $x=3$은 $7<9p$에서 $p GEQ 1$이면 항상 성립, $x=4$는 $16<8p$에서 $p GEQ 3$, $x=5$는 $27<5p$에서 $p GEQ 6$',
        '정수 $x$가 정확히 $1$개(=$x=3$만)이려면 $p<3$이고 $p<6$, 즉 $p=1$ 또는 $p=2$',
        '$g(2)=p times2 times(6-2)=8p$이므로 $p=1$이면 $g(2)=8$, $p=2$이면 $g(2)=16$',
        '$M=16$, $m=8$이므로 $therefore~M+m=16+8$',
        '$=24$',
    ],
    ch='로그부등식과 이차함수의 그래프', lv='상')

add(id='q22', kind='mc', no=22, score=4.4, layout='1x5', fig='jsg26m1_q22',
    text=[
        '직선 $y=2x+k$가 두 함수',
        '$y=LEFT({2} over{3} RIGHT)^{x+3}+1$, $y=LEFT({2} over{3} RIGHT)^{x+1}+{8} over{3}$',
        '의 그래프와 만나는 점을 각각 $P,~Q$라 하자. $bar{PQ}= sqrt{5}$일 때, 상수 $k$의 값은?',
    ],
    choices=['${5} over{3}$', '${11} over{3}$', '${17} over{3}$', '${23} over{3}$', '${29} over{3}$'],
    ans='③',
    sol=[
        '직선의 기울기가 $2$이므로 두 교점의 $x$좌표의 차를 $d$라 하면 $bar{PQ}= sqrt{d^{2}+(2d)^{2}}= sqrt{5}d$',
        '$bar{PQ}= sqrt{5}$이므로 $d=1$, 즉 두 교점의 $x$좌표는 $1$만큼 차이난다.',
        '$P$의 $x$좌표를 $p$, $Q$의 $x$좌표를 $p+1$로 놓고 $g_{1}(x)=LEFT({2} over{3} RIGHT)^{x+3}+1$(점 $P$), $g_{2}(x)=LEFT({2} over{3} RIGHT)^{x+1}+{8} over{3}$(점 $Q$)라 하자.',
        '같은 직선 위의 두 점이므로 $g_{2}(p+1)-g_{1}(p)=2$',
        '$LEFT({2} over{3} RIGHT)^{p+2}-LEFT({2} over{3} RIGHT)^{p+3}+{8} over{3}-1=2$에서 ${1} over{3}LEFT({2} over{3} RIGHT)^{p+2}+{5} over{3}=2$',
        '${1} over{3}LEFT({2} over{3} RIGHT)^{p+2}={1} over{3}$에서 $LEFT({2} over{3} RIGHT)^{p+2}=1$이므로 $p=it-2$',
        '$P$: $g_{1}(it-2)=LEFT({2} over{3} RIGHT)^{1}+1={5} over{3}$. $Q$: $g_{2}(it-1)=LEFT({2} over{3} RIGHT)^{0}+{8} over{3}=1+{8} over{3}={11} over{3}$',
        '$P=(it-2,~{5} over{3})$이 직선 위에 있으므로 ${5} over{3}=2(it-2)+k$에서 $k={5} over{3}+4$',
        '$={17} over{3}$',
    ],
    ch='지수함수의 그래프와 직선', lv='상')

add(id='q23', kind='mc', no=23, score=4.7, layout='1x5', fig='jsg26m1_q23',
    text='함수 $f(x)=a sin bx+c$가 있다. $y= LEFT | f(x) RIGHT |$의 그래프가 그림과 같이 $ LEFT | f(0) RIGHT |=2$, $ LEFT | f LEFT({ pi} over{8} RIGHT) RIGHT |=5$, $ LEFT | f LEFT({7} over{8} pi RIGHT) RIGHT |=1$이 되도록 하는 세 실수 $a,~b,~c$에 대하여 $a+b+10c$의 최댓값과 최솟값을 각각 $M,~m$이라 하자. $M-m$의 값은? (단, $M$과 $m$은 상수이다.)',
    choices=['$44$', '$46$', '$48$', '$50$', '$52$'],
    ans='③',
    sol=[
        '$f(0)=a sin0+c=c$이므로 $ LEFT | c RIGHT |=2$, 즉 $c=2$ 또는 $c=it-2$',
        '그래프는 큰 산(높이 $5$)과 작은 산(높이 $1$)이 번갈아 나오므로 $f$의 최댓값과 최솟값의 절댓값이 각각 $5,~1$이다.',
        '$c=2$일 때 $ LEFT | a+2 RIGHT |$와 $ LEFT | a-2 RIGHT |$가 $5,~1$이 되려면 $a=3$ 또는 $a=it-3$',
        '$c=it-2$일 때도 마찬가지로 $a=3$ 또는 $a=it-3$',
        '산의 꼭짓점이 $x={ pi} over{8}$에서 처음 나타나는 조건으로 $b$를 정하면, 각 $(a,~c)$ 조합에 대해 $b= pm4$가 정해진다.',
        '네 경우를 직접 확인하면 $(a,~b,~c)=(3,~4,~2)$, $({it-3},~{it-4},~2)$, $({it-3},~4,~{it-2})$, $(3,~{it-4},~{it-2})$가 모두 주어진 세 점의 함숫값 조건을 만족시킨다.',
        '각각에 대해 $a+b+10c$: $3+4+20=27$, $it-3-4+20=13$, $it-3+4-20=it-19$, $3-4-20=it-21$',
        '$M=27$(최댓값), $m=it-21$(최솟값)',
        '$therefore~M-m=27-(it-21)$',
        '$=48$',
    ],
    ch='삼각함수 a sin bx+c의 그래프', lv='상')

add(id='q24', kind='mc', no=24, score=4.8, layout='1x5',
    text=[
        '자연수 $k$에 대하여 두 함수',
        '$f(x)= log_{3}x$, $g(x)={1} over{2} log_{3}(x-3^{it-k})-{1} over{2}$',
        '이 있다. 실수 $t$에 대하여 직선 $y=t$가 두 곡선 $y=f(x)$, $y=g(x)$와 만나는 점을 각각 $A,~B$라 하자. 두 점 $A,~B$ 사이의 거리가 ${1} over{12}$가 되도록 하는 실수 $t$의 개수가 $2$이고 이 두 실수의 합을 $a$라 할 때, $LEFT({1} over{3} RIGHT)^{a}-k$의 값은?',
    ],
    choices=['$105$', '$106$', '$107$', '$108$', '$109$'],
    ans='②',
    sol=[
        '$A=(3^{t},~t)$. $g(x_{B})=t$에서 $x_{B}-3^{it-k}=3^{2t+1}$이므로 $x_{B}=3^{2t+1}+3^{it-k}$',
        '$A,~B$는 같은 $y$좌표 $t$를 가지므로 $bar{AB}= LEFT | x_{B}-x_{A} RIGHT |= LEFT | 3^{2t+1}+3^{it-k}-3^{t} RIGHT |$',
        '$u=3^{t}$ ($u>0$)로 놓으면 $3^{2t+1}=3u^{2}$이므로 $ LEFT | 3u^{2}-u+3^{it-k} RIGHT |={1} over{12}$',
        '$ phi(u)=3u^{2}-u+3^{it-k}$는 $u={1} over{6}$에서 최솟값 $3^{it-k}-{1} over{12}$를 가지며, 이는 항상 $it-{1} over{12}$보다 크므로 $ phi(u)=it-{1} over{12}$는 해가 없다.',
        '따라서 $ phi(u)={1} over{12}$가 서로 다른 두 양의 실근을 가져야 하고, 이는 ${1} over{12}<3^{it-k}<{1} over{6}$일 때 성립한다.',
        '$k=1$: $3^{it-1}={1} over{3}$(범위밖), $k=2$: $3^{it-2}={1} over{9} approx0.111$(범위안 ✓), $k=3$: $3^{it-3}={1} over{27}$(범위밖). $therefore~k=2$',
        '$C=3^{it-2}-{1} over{12}={1} over{9}-{1} over{12}={1} over{36}$이고, 방정식은 $3u^{2}-u+{1} over{36}=0$',
        '두 근의 곱은 ${C} over{3}={1} over{108}$이므로, 두 $t$값의 합 $a= log_{3}u_{1}+ log_{3}u_{2}= log_{3}(u_{1}u_{2})= log_{3}{1} over{108}$',
        '$LEFT({1} over{3} RIGHT)^{a}=3^{it-a}=3^{it- log_{3}{1 over108}}={1} over{{1 over108}}=108$',
        '$therefore~LEFT({1} over{3} RIGHT)^{a}-k=108-2$',
        '$=106$',
    ],
    ch='로그함수의 평행이동과 두 점 사이의 거리', lv='최상')

add(id='q25', kind='mc', no=25, score=5.0, layout='1x5', box=True,
    text=[
        '$ LEFT | m RIGHT | LEQ 5$인 정수 $m$에 대하여 함수 $f(x)$가',
        '$f(x)= LEFT | 2^{it-x}-2^{m} RIGHT |-4^{m+2}$',
        '일 때, 방정식 $ LEFT{f(x)+2^{m+1} RIGHT} times LEFT{2^{f(x)}-1 RIGHT}=0$의 서로 다른 실근의 개수를 $g(m)$이라 하자. 다음 [보기] 중 옳은 것을 모두 고른 것은?',
    ],
    box_items=[
        '$g(0)=2$',
        '$g(m)=3$인 어떤 정수 $m$이 존재한다.',
        '$g(it-4)+g(0)+g(4)=6$',
    ],
    choices=['ㄱ', 'ㄴ', 'ㄱ,~ㄴ', 'ㄴ,~ㄷ', 'ㄱ,~ㄴ,~ㄷ'],
    ans='①',
    sol=[
        '$ LEFT{f(x)+2^{m+1} RIGHT} times LEFT{2^{f(x)}-1 RIGHT}=0$은 $f(x)=it-2^{m+1}$ 또는 $f(x)=0$($2^{y}=1$이면 $y=0$)과 같다.',
        '$v=2^{it-x}>0$로 치환하면 $f$는 $v=2^{m}$에서 최솟값 $it-4^{m+2}$를 갖는 V자형 함수이다.',
        '[경우1] $f=0$: $ LEFT | v-2^{m} RIGHT |=4^{m+2}$에서 $v=2^{m}+4^{m+2}$(항상 양)이거나 $v=2^{m}-4^{m+2}$(양수조건: $m<it-4$, 즉 $m=it-5$일 때만)',
        '[경우2] $f=it-2^{m+1}$: $ LEFT | v-2^{m} RIGHT |=4^{m+2}-2^{m+1}=2^{m+1}(2^{m+3}-1)$. $m GEQit-2$이면 양의 두 근 후보 중 작은쪽은 항상 음수가 되어 $1$개, $m=it-3$이면 $0$(접점) $1$개, $m LEQit-4$이면 음수(해 없음)',
        '종합하면 $g(it-5)=2$, $g(it-4)=1$, $g(m)=2$ ($it-3 LEQ m LEQ 5$)',
        'ㄱ. $g(0)=2$ (참)',
        'ㄴ. $g(m)$의 값은 $1$ 또는 $2$뿐이므로 $g(m)=3$인 정수 $m$은 존재하지 않는다. (거짓)',
        'ㄷ. $g(it-4)+g(0)+g(4)=1+2+2=5 NEQ 6$ (거짓)',
        '$therefore$ 옳은 것은',
        '$=ㄱ$',
    ],
    ch='지수방정식의 실근의 개수', lv='최상')
