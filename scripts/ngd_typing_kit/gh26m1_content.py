# -*- coding: utf-8 -*-
"""광휘고등학교 2학년 2026 1학기 중간 대수(지수,로그~삼각함수의그래프) 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.5, layout='3+2',
    text='$ sqrt[3]{27}+ sqrt[5]{it-32}$의 값은?',
    choices=['$it-2$', '$it-1$', '$0$', '$1$', '$2$'],
    ans='④',
    sol=[
        '$ sqrt[3]{27}=3$, $ sqrt[5]{it-32}=it-2$',
        '$therefore$ 구하는 값은 $3+(it-2)$',
        '$=1$',
    ],
    ch='거듭제곱근', lv='하')

add(id='q02', kind='mc', no=2, score=4.5, layout='3+2',
    text='$ log_{3}9+ log_{5} sqrt{5}$의 값은?',
    choices=['${1} over{2}$', '$1$', '${3} over{2}$', '$2$', '${5} over{2}$'],
    ans='⑤',
    sol=[
        '$ log_{3}9=2$, $ log_{5} sqrt{5}={1} over{2}$',
        '$therefore$ 구하는 값은 $2+{1} over{2}$',
        '$={5} over{2}$',
    ],
    ch='로그의 성질', lv='하')

add(id='q03', kind='mc', no=3, score=4.5, layout='3+2',
    text='방정식 $4^{x}=2^{3-x}$의 해는?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='①',
    sol=[
        '$4^{x}=2^{2x}$이므로 $2x=3-x$에서 $3x=3$',
        '$therefore~x$',
        '$=1$',
    ],
    ch='지수방정식', lv='하')

add(id='q04', kind='mc', no=4, score=4.5, layout='3+2',
    text='부등식 $ log_{5}(x-1)> log_{5}(it-x+9)$를 만족시키는 모든 정수 $x$의 값의 합은?',
    choices=['$19$', '$21$', '$23$', '$25$', '$27$'],
    ans='②',
    sol=[
        '진수 조건: $x-1>0$, $it-x+9>0$에서 $1<x<9$',
        '밑이 $5>1$이므로 $x-1>it-x+9$에서 $2x>10$, $x>5$',
        '$5<x<9$를 만족하는 정수는 $6,~7,~8$',
        '$therefore$ 이 정수들의 합은 $6+7+8$',
        '$=21$',
    ],
    ch='로그부등식', lv='중')

add(id='q05', kind='mc', no=5, score=4.5, layout='3+2',
    text='반지름의 길이가 $6$이고 중심각의 크기가 ${ pi} over{3}$인 부채꼴의 호의 길이가 $a$이고 넓이가 $b$일 때, $a+b$의 값은?',
    choices=['$7 pi$', '$8 pi$', '$9 pi$', '$10 pi$', '$11 pi$'],
    ans='②',
    sol=[
        '$a=r theta=6 times{ pi} over{3}=2 pi$',
        '$b={1} over{2}r^{2} theta={1} over{2} times36 times{ pi} over{3}=6 pi$',
        '$therefore~a+b=2 pi+6 pi$',
        '$=8 pi$',
    ],
    ch='호도법과 부채꼴', lv='하')

add(id='q06', kind='mc', no=6, score=4.5, layout='1x5',
    text='$ sin LEFT(it-{7} over{6} pi RIGHT)+ cos LEFT(it-{ pi} over{3} RIGHT)+ tan LEFT(it-{ pi} over{4} RIGHT)$의 값은?',
    choices=['$it- sqrt{3}$', '$it-1$', '$0$', '$1$', '$ sqrt{3}$'],
    ans='③',
    sol=[
        '$ sin LEFT(it-{7} over{6} pi RIGHT)=it- sin LEFT({7} over{6} pi RIGHT)=it-LEFT(it- sin{ pi} over{6} RIGHT)={1} over{2}$',
        '$ cos LEFT(it-{ pi} over{3} RIGHT)= cos{ pi} over{3}={1} over{2}$',
        '$ tan LEFT(it-{ pi} over{4} RIGHT)=it- tan{ pi} over{4}=it-1$',
        '$therefore$ 구하는 값은 ${1} over{2}+{1} over{2}+(it-1)$',
        '$=0$',
    ],
    ch='삼각함수의 값', lv='하')

add(id='q07', kind='mc', no=7, score=4.7, layout='3+2', fig='gh26m1_q07',
    text='함수 $y=a cos(bx-c)$의 그래프가 그림과 같을 때, 세 상수 $a,~b,~c$에 대하여 $abc$의 최솟값은? (단, $a>0$, $b>0$, $c>0$)',
    choices=['${7} over{12} pi$', '${7} over{10} pi$', '${7} over{8} pi$', '${7} over{6} pi$', '${7} over{4} pi$'],
    ans='③',
    sol=[
        '그래프의 최댓값이 $7$, 최솟값이 $it-7$이므로 $a=7$',
        '한 주기가 $8 pi$(최댓값 $x=2 pi$에서 다음 최댓값 $x=10 pi$까지)이므로 $b={2 pi} over{8 pi}={1} over{4}$',
        '$x=2 pi$에서 최댓값을 가지므로 $bx-c=2 pi n$ (정수 $n$)에서 $c=b(2 pi)-2 pi n={ pi} over{2}-2 pi n$',
        '$c>0$이면서 최소가 되는 경우는 $n=0$일 때 $c={ pi} over{2}$',
        '$therefore~abc$의 최솟값은 $7 times{1} over{4} times{ pi} over{2}$',
        '$={7} over{8} pi$',
    ],
    ch='삼각함수의 그래프', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2', emptybox={'paras': [
        '어떤 용액의 수소이온 농도가 $[H⁺]~mol/L$일 때, 용액의 산성도를 나타내는 $pH$는',
        '$pH= log LEFT({1} over{[H⁺]} RIGHT)$이라 한다.',
    ]},
    text='$A$용액의 $pH$가 $6.5$이고, $B$용액의 수소이온 농도가 $A$용액의 수소이온 농도의 $30$배일 때, $B$용액의 $pH$의 값은? (단, $ log3=0.48$로 계산한다.)',
    choices=['$5$', '$5.02$', '$5.04$', '$5.06$', '$5.08$'],
    ans='②',
    sol=[
        '$pH_{A}=it- log [H⁺]_{A}=6.5$',
        '$[H⁺]_{B}=30[H⁺]_{A}$이므로 $pH_{B}=it- log(30[H⁺]_{A})=it- log 30+6.5$',
        '$ log 30= log3+ log10=0.48+1=1.48$',
        '$therefore~pH_{B}=6.5-1.48$',
        '$=5.02$',
    ],
    ch='로그의 활용', lv='중')

add(id='q09', kind='mc', no=9, score=4.9, layout='3+2',
    text='$a^{x}=243$, $17^{y}=9$인 두 실수 $x,~y$에 대하여 ${5} over{x}-{2} over{y}=2$일 때, 자연수 $a$의 값은?',
    choices=['$17$', '$51$', '$85$', '$119$', '$153$'],
    ans='⑤',
    sol=[
        '$a^{x}=243=3^{5}$이므로 $x=5 log_{a}3$, ${5} over{x}={1} over{ log_{a}3}= log_{3}a$',
        '$17^{y}=9=3^{2}$이므로 $y=2 log_{17}3$, ${2} over{y}={1} over{ log_{17}3}= log_{3}17$',
        '${5} over{x}-{2} over{y}= log_{3}a- log_{3}17= log_{3}LEFT({a} over{17} RIGHT)=2$',
        '${a} over{17}=3^{2}=9$',
        '$therefore~a$',
        '$=153$',
    ],
    ch='지수와 로그의 관계', lv='중')

add(id='q10', kind='mc', no=10, score=5.0, layout='3+2',
    text='이차방정식 $x^{2}-6x+2=0$의 두 근이 $ log_{2}a,~ log_{2}b$라 할 때, $ log_{a}b^{3}+ log_{b}a^{3}$의 값은?',
    choices=['$36$', '$39$', '$42$', '$45$', '$48$'],
    ans='⑤',
    sol=[
        '$p= log_{2}a$, $q= log_{2}b$라 하면 $p+q=6$, $pq=2$',
        '$ log_{a}b^{3}=3 log_{a}b={3q} over{p}$, $ log_{b}a^{3}={3p} over{q}$',
        '합$={3(p^{2}+q^{2})} over{pq}={3LEFT[(p+q)^{2}-2pq RIGHT]} over{pq}={3(36-4)} over{2}={3 times32} over{2}$',
        '$therefore$ 구하는 값은',
        '$=48$',
    ],
    ch='로그방정식의 근', lv='중')

add(id='q11', kind='mc', no=11, score=5.1, layout='3+2',
    text='두 상수 $a,~b$에 대하여 곡선 $y=2^{a-x}+b$와 직선 $y=it-3x$가 서로 다른 두 점 $A,~B$에서 만나고 $bar{OA}=bar{OB}= sqrt{10}$일 때, $b-a$의 값은? (단, $O$는 원점이다.)',
    choices=['$it-7$', '$it-6$', '$it-5$', '$it-4$', '$it-3$'],
    ans='①',
    sol=[
        '직선 위의 점 $(t,~{it-3t})$가 원점에서 거리 $ sqrt{10}$이려면 $t^{2}+9t^{2}=10$, $t^{2}=1$, $t=pm1$',
        '두 점은 $(1,~{it-3})$, $(it-1,~3)$이다.',
        '$(1,~{it-3})$: $it-3=2^{a-1}+b$. $(it-1,~3)$: $3=2^{a+1}+b$',
        '두 식을 빼면 $6=2^{a+1}-2^{a-1}=2^{a-1}(4-1)=3 times2^{a-1}$에서 $2^{a-1}=2$, $a=2$',
        '$it-3=2^{1}+b$에서 $b=it-5$',
        '$therefore~b-a=it-5-2$',
        '$=it-7$',
    ],
    ch='지수함수의 그래프', lv='상')

add(id='q12', kind='mc', no=12, score=5.2, layout='1x5',
    text='함수 $y= log_{4}x$의 그래프를 $y$축의 방향으로 $1$만큼 평행이동한 후 직선 $y=x$에 대하여 대칭이동한 그래프를 나타내는 식이 $y=f(x)$이다. 함수 $y=f(x)$의 그래프를 $y$축에 대하여 대칭이동한 후 $x$축의 방향으로 $1$만큼, $y$축의 방향으로 $it-2$만큼 평행이동한 그래프를 나타내는 식이 $y=g(x)$이다. $it-1 LEQ x LEQ 4$에서 함수 $f(x)g(x)$의 최댓값은?',
    choices=['${1} over{8}$', '${1} over{4}$', '${3} over{8}$', '${1} over{2}$', '${5} over{8}$'],
    ans='①',
    sol=[
        '$y= log_{4}x+1$을 $y=x$에 대해 대칭이동: $x= log_{4}y+1$에서 $y=4^{x-1}$이므로 $f(x)=4^{x-1}$',
        '$f(x)$를 $y$축 대칭: $4^{it-x-1}$. 이를 $x$축으로 $1$, $y$축으로 $it-2$ 평행이동: $g(x)=4^{it-(x-1)-1}-2=4^{it-x}-2$',
        '$f(x)g(x)=4^{x-1}(4^{it-x}-2)=4^{it-1}-2 times4^{x-1}={1} over{4}-2 times4^{x-1}$',
        '$4^{x-1}$은 증가함수이므로 $f(x)g(x)$는 감소함수이다. $it-1 LEQ x LEQ 4$에서 $x=it-1$일 때 최대이다.',
        '$x=it-1$: $4^{x-1}=4^{it-2}={1} over{16}$',
        '$f(it-1)g(it-1)={1} over{4}-2 times{1} over{16}={1} over{4}-{1} over{8}$',
        '$therefore$ 최댓값은',
        '$={1} over{8}$',
    ],
    ch='로그함수의 평행이동과 대칭이동', lv='상')

add(id='q13', kind='mc', no=13, score=5.3, layout='3+2',
    text='점 $rmP(a,~1)~(a NEQ 1)$을 $y=x$에 대하여 대칭이동한 점을 $rmQ$라 할 때, 두 동경 $rmOP,~rmOQ$가 나타내는 각을 각각 $ alpha, beta$라 하자. $ cos alpha+ sin beta={2} over{3}$일 때, $ tan^{2} alpha+ tan^{2} beta$의 값은? (단, $O$는 원점이고, 시초선은 $x$축의 양의 방향이다.)',
    choices=['${5} over{2}$', '${17} over{4}$', '${37} over{6}$', '${65} over{8}$', '${101} over{10}$'],
    ans='④',
    sol=[
        '$rmQ=(1,~a)$. $r= sqrt{a^{2}+1}$이라 하면 $ cos alpha={a} over{r}$, $ sin alpha={1} over{r}$, $ cos beta={1} over{r}$, $ sin beta={a} over{r}$',
        '($rmQ$가 $rmP$의 $y=x$ 대칭이므로 $ beta={ pi} over{2}- alpha$에 해당, $ sin beta= cos alpha$, $ cos beta= sin alpha$)',
        '$ cos alpha+ sin beta={a} over{r}+{a} over{r}={2a} over{r}={2} over{3}$에서 ${a} over{r}={1} over{3}$, 즉 $ cos alpha={1} over{3}$',
        '$r^{2}=a^{2}+1$에 $a={r} over{3}$을 대입: $r^{2}={r^{2}} over{9}+1$에서 $r^{2}={9} over{8}$',
        '$ sin alpha={1} over{r}$이므로 $ sin^{2} alpha={1} over{r^{2}}={8} over{9}$, $ tan^{2} alpha={ sin^{2} alpha} over{ cos^{2} alpha}={8/9} over{1/9}=8$',
        '$ beta={ pi} over{2}- alpha$이므로 $ tan beta= cot alpha={1} over{ tan alpha}$, $ tan^{2} beta={1} over{8}$',
        '$therefore~ tan^{2} alpha+ tan^{2} beta=8+{1} over{8}$',
        '$={65} over{8}$',
    ],
    ch='삼각함수의 정의', lv='상')

add(id='q14', kind='mc', no=14, score=5.4, layout='3+2',
    text='$2 LEQ n LEQ 10$인 자연수 $n$에 대하여 $4n^{2}-20n-11$의 $n$제곱근 중 실수인 것의 개수를 $f(n)$이라 하고, $4n^{2}-20n-11$의 $(n+1)$제곱근 중 실수인 것의 개수를 $g(n)$이라 할 때, $f(n)+g(n)=3$을 만족시키는 모든 자연수 $n$의 값의 합은?',
    choices=['$34$', '$40$', '$45$', '$49$', '$52$'],
    ans='②',
    sol=[
        '$M=4n^{2}-20n-11$이라 하자. $n,~n+1$ 중 하나는 짝수, 하나는 홀수이다.',
        '$M>0$이면: 지수가 홀수인 쪽은 실근 $1$개, 짝수인 쪽은 실근 $2$개이므로 항상 $f(n)+g(n)=1+2=3$이 성립한다.',
        '$M=0$이면 $f(n)=g(n)=1$로 합이 $2$, $M<0$이면 홀수 지수만 $1$개·짝수 지수는 $0$개로 합이 $1$이다. 둘 다 $3$이 아니다.',
        '따라서 조건은 $M>0$, 즉 $4n^{2}-20n-11>0$과 동치이다.',
        '$4n^{2}-20n-11=0$의 근은 $n={20pm sqrt{400+176}} over{8}={20pm24} over{8}$에서 $n=5.5$ 또는 $n=it-0.5$',
        '$4n^{2}-20n-11>0$이려면 $n>5.5$ (범위 내에서), 즉 $n=6,~7,~8,~9,~10$',
        '$therefore$ 이 값들의 합은 $6+7+8+9+10$',
        '$=40$',
    ],
    ch='거듭제곱근의 개수', lv='상')

add(id='q15', kind='mc', no=15, score=5.5, layout='1x5',
    text='함수 $f(x)=LEFT | a^{x+1}-3 RIGHT |$에 대하여 $y=f(x)$의 그래프와 직선 $y=2$가 서로 다른 두 점 $A,~B$에서 만난다. $bar{AB}=3$일 때, $a$의 값은? (단, $0<a<1$)',
    choices=['${1} over{ sqrt[3]{25}}$', '${1} over{ sqrt[3]{16}}$', '${1} over{ sqrt[3]{9}}$', '${1} over{ sqrt[3]{5}}$', '${1} over{ sqrt[3]{4}}$'],
    ans='④',
    sol=[
        '$LEFT | a^{x+1}-3 RIGHT |=2$에서 $a^{x+1}=5$ 또는 $a^{x+1}=1$',
        '$a^{x+1}=1$에서 $x+1=0$, $x=it-1$',
        '$a^{x+1}=5$에서 $x+1= log_{a}5$, $x= log_{a}5-1$',
        '$bar{AB}=LEFT | (it-1)-( log_{a}5-1) RIGHT |=LEFT | log_{a}5 RIGHT |=3$',
        '$0<a<1$이므로 $ log_{a}5<0$, 따라서 $ log_{a}5=it-3$에서 $a^{it-3}=5$, $a^{3}={1} over{5}$',
        '$therefore~a$',
        '$={1} over{ sqrt[3]{5}}$',
    ],
    ch='지수함수의 그래프와 절댓값', lv='상')

add(id='q16', kind='mc', no=16, score=5.6, layout='1x5',
    text='$0 LEQ x LEQ 2 pi$에서 정의된 두 함수 $f(x)= cosx$, $g(x)=it-k sinx~(0<k<1)$의 그래프가 만나는 서로 다른 두 점을 $A,~B$라 하자. 직선 $AB$의 기울기가 ${1} over{2 pi}$일 때, $k$의 값은?',
    choices=['${ sqrt{3}} over{3}$', '${ sqrt{2}} over{4}$', '${ sqrt{11}} over{11}$', '${ sqrt{3}} over{6}$', '${ sqrt{15}} over{15}$'],
    ans='⑤',
    sol=[
        '$ cosx=it-k sinx$에서 $ tanx=it-{1} over{k}$ (단, $ cosx NEQ 0$)',
        '$ tan$의 주기가 $ pi$이므로 두 해는 $x_{1}$, $x_{1}+ pi$이다. $A=(x_{1},~ cosx_{1})$, $B=(x_{1}+ pi,~{it- cosx_{1}})$',
        '기울기$={it-2 cosx_{1}} over{ pi}={1} over{2 pi}$에서 $ cosx_{1}=it-{1} over{4}$',
        '$0<k<1$이므로 $ tanx_{1}=it-{1} over{k}<0$이고 $ cosx_{1}<0$이므로 $x_{1}$은 제$2$사분면 각이다.',
        '$ sinx_{1}= sqrt{1-{1} over{16}}={ sqrt{15}} over{4}$ (양수)',
        '$ tanx_{1}={{ sqrt{15}} over{4}} over{it-{1} over{4}}=it- sqrt{15}=it-{1} over{k}$에서 $k={1} over{ sqrt{15}}$',
        '$therefore~k$',
        '$={ sqrt{15}} over{15}$',
    ],
    ch='삼각함수의 그래프의 교점', lv='상')

add(id='q17', kind='mc', no=17, score=5.7, layout='1x5',
    text='직선 $y=a$가 두 곡선 $y= log_{9}x$, $y= log_{3}x$ 및 $y$축과 만나는 점을 각각 $A,~B,~C$라 하자. 점 $A$를 지나고 $y$축에 평행한 직선이 곡선 $y= log_{3}x$와 만나는 점을 $D$, 점 $B$를 지나고 $y$축에 평행한 직선이 곡선 $y= log_{9}x$와 만나는 점을 $E$라 하고, 점 $D$에서 $y$축에 내린 수선의 발을 $F$라 하자. 사다리꼴 $BCFD$의 넓이가 사다리꼴 $AEBD$의 넓이의 $3$배일 때, $3^{a}$의 값은? (단, $a>0$)',
    choices=['${9} over{7}$', '${11} over{7}$', '${13} over{7}$', '${15} over{7}$', '${17} over{7}$'],
    ans='②',
    sol=[
        '$A=(9^{a},~a)$, $B=(3^{a},~a)$, $C=(0,~a)$',
        '$D$는 $x=9^{a}$ 위에서 $y= log_{3}x$와의 교점이므로 $D=(9^{a},~2a)$. $E$는 $x=3^{a}$ 위에서 $y= log_{9}x$와의 교점이므로 $E=(3^{a},~{a} over{2})$. $F=(0,~2a)$',
        '사다리꼴 $AEBD$(평행변 $bar{EB}={a} over{2}$, $bar{DA}=a$, 높이 $9^{a}-3^{a}$): 넓이$={1} over{2}LEFT({a} over{2}+a RIGHT)(9^{a}-3^{a})={3a} over{4}(9^{a}-3^{a})$',
        '사다리꼴 $BCFD$(평행변 $bar{BC}=3^{a}$, $bar{FD}=9^{a}$, 높이 $a$): 넓이$={1} over{2}(3^{a}+9^{a})a$',
        '${1} over{2}(3^{a}+9^{a})a=3 times{3a} over{4}(9^{a}-3^{a})$에서 $a$로 나누면 $2(3^{a}+9^{a})=9(9^{a}-3^{a})$',
        '$t=3^{a}$라 하면 $2t+2t^{2}=9t^{2}-9t$에서 $7t^{2}-11t=0$, $t(7t-11)=0$에서 $t={11} over{7}$ ($t NEQ 0$)',
        '$therefore~3^{a}$',
        '$={11} over{7}$',
    ],
    ch='로그함수의 그래프와 도형의 넓이', lv='상')

add(id='q18', kind='mc', no=18, score=5.8, layout='1x5',
    text='두 자연수 $m,~n$에 대하여 $0 LEQ x LEQ m pi$에서 정의된 함수 $f(x)=LEFT | n sin2x+{n} over{2} RIGHT |$의 그래프가 직선 $y=n-3$과 만나는 점의 개수가 $13$일 때, $m+n$의 값은?',
    choices=['$8$', '$9$', '$10$', '$11$', '$12$'],
    ans='③',
    sol=[
        '$f(x) GEQ 0$이므로 $n GEQ 3$ 필요. $h(x)=n sin2x+{n} over{2}$ (최댓값 ${3n} over{2}$, 최솟값 $it-{n} over{2}$)',
        '$f(x)=n-3$은 $h(x)=n-3$ 또는 $h(x)=3-n$과 같다.',
        '$n=6$인 경우를 확인: $h(x)=3$에서 $ sin2x=0$, $x={k pi} over{2}$ ($k=0,~1,~ cdots,~2m$)로 닫힌구간 $[0,~m pi]$에 $2m+1$개',
        '$h(x)=it-3$에서 $ sin2x=it-1$ (최솟값, $n=6$일 때 $it-{n} over{2}=it-3$과 일치), $x={3 pi} over{4}+k pi$ ($k=0,~1,~ cdots,~m-1$)로 $m$개',
        '총 개수 $=(2m+1)+m=3m+1=13$에서 $m=4$',
        '($n NEQ 6$인 다른 자연수들은 경계 보정이 없어 전체 개수가 항상 짝수(또는 $4$의 배수)가 되어 $13$을 만들 수 없음을 확인할 수 있다.)',
        '$therefore~m+n=4+6$',
        '$=10$',
    ],
    ch='삼각함수의 그래프와 직선의 교점 개수', lv='상')

add(id='q19', kind='sub', no=1, score=5.0,
    text='$ sin theta+ cos theta={1} over{3}$일 때, $ sin^{3} theta+ cos^{3} theta$의 값을 구하시오.',
    ans_mix='${13} over{27}$',
    sol=[
        '$ sin^{3} theta+ cos^{3} theta=( sin theta+ cos theta)(1- sin theta cos theta)$',
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta={1} over{9}$에서 $ sin theta cos theta=it-{4} over{9}$',
        '$ sin^{3} theta+ cos^{3} theta={1} over{3}LEFT(1+{4} over{9} RIGHT)={1} over{3} times{13} over{9}$',
        '$therefore$ 구하는 값은',
        '$={13} over{27}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q20', kind='sub', no=2, score=5.0,
    text='양의 실수 $x$에 대하여 부등식 $( log_{2}x)^{2}-(3^{a}-1) log_{2}x^{2}+2(3^{a}-1)>0$이 성립하도록 하는 실수 $a$의 값의 범위를 구하시오.',
    ans_mix='$0<a<1$',
    sol=[
        '$t= log_{2}x$ ($x>0$이므로 $t$는 모든 실수), $ log_{2}x^{2}=2t$',
        '부등식: $t^{2}-2(3^{a}-1)t+2(3^{a}-1)>0$. $k=3^{a}-1$로 치환',
        '모든 실수 $x$(즉 모든 실수 $t$)에 대해 성립하려면 $t$에 대한 이차식이 항상 양수여야 하므로 판별식 $<0$',
        '$4k^{2}-8k<0$에서 $4k(k-2)<0$, $0<k<2$',
        '$0<3^{a}-1<2$에서 $1<3^{a}<3$',
        '$therefore$ 구하는 범위는',
        '$=0<a<1$',
    ],
    ch='지수·로그 부등식', lv='상')
