# -*- coding: utf-8 -*-
"""명문고등학교 2학년 2026 1학기 중간 대수(지수로그~삼각함수의 기본성질) 21문항 내용 (전부 선택형).
출처: 명문고등학교_2학년_2026_1학기중간_대수_선택,공통_문제.pdf (정답 없음 → 전 문항 재계산).
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.3, layout='3+2',
    text='$ log sqrt[4]{10}$의 값은?',
    choices=['$it-{1} over{4}$', '$it-{1} over{5}$', '${1} over{6}$', '${1} over{5}$', '${1} over{4}$'],
    ans='⑤',
    sol=[
        '$ sqrt[4]{10}=10^{{1} over{4}}$이므로',
        '$ log sqrt[4]{10}= log10^{{1} over{4}}$',
        '$={1} over{4} log10$',
        '$={1} over{4}$',
    ],
    ch='로그의 성질', lv='중')

add(id='q02', kind='mc', no=2, score=4.3, layout='3+2',
    text='$(2^{ sqrt{3}+1})^{ sqrt{3}-1}$의 값은?',
    choices=['$1$', '$ sqrt{2}$', '$ sqrt{3}$', '$2$', '$4$'],
    ans='⑤',
    sol=[
        '$(2^{ sqrt{3}+1})^{ sqrt{3}-1}=2^{( sqrt{3}+1)( sqrt{3}-1)}$',
        '$=2^{3-1}$',
        '$=2^{2}$',
        '$=4$',
    ],
    ch='거듭제곱의 성질', lv='중')

add(id='q03', kind='mc', no=3, score=4.4, layout='3+2',
    text='반지름의 길이가 $3$, 중심각의 크기가 $2/3 pi$인 부채꼴의 호의 길이를 $l$, 넓이를 $S$라 할 때, $l/S$의 값은?',
    choices=['${1} over{3}$', '${2} over{3}$', '$1$', '${4} over{3}$', '${5} over{3}$'],
    ans='②',
    sol=[
        '$l=r theta=3 times{2} over{3} pi$',
        '$=2 pi$',
        '$S={1} over{2}r^{2} theta={1} over{2} times9 times{2} over{3} pi$',
        '$=3 pi$',
        '$therefore~{l} over{S}={2 pi} over{3 pi}$',
        '$={2} over{3}$',
    ],
    ch='호도법과 부채꼴', lv='중')

add(id='q04', kind='mc', no=4, score=4.6, layout='3+2',
    text='$x= log_{2}9 times log_{9}5 times log_{5} sqrt{2}$일 때, $5^{x}$의 값은?',
    choices=['${1} over{5}$', '$ sqrt{5}$', '$5$', '$5 sqrt{5}$', '$25$'],
    ans='②',
    sol=[
        '밑의 변환을 연쇄적으로 적용하면',
        '$x= log_{2}9 times log_{9}5 times log_{5} sqrt{2}= log_{2} sqrt{2}$',
        '$= log_{2}2^{{1} over{2}}$',
        '$={1} over{2}$',
        '$therefore~5^{x}=5^{{1} over{2}}$',
        '$= sqrt{5}$',
    ],
    ch='로그의 성질(밑의 변환)', lv='상')

add(id='q05', kind='mc', no=5, score=4.4, layout='3+2',
    text='$ theta$가 제$2$사분면의 각이고 $ sin theta+ cos theta= sqrt{3}/3$일 때, $ sin theta cos theta$의 값은?',
    choices=['$it-{1} over{2}$', '$it-{1} over{3}$', '$it-{1} over{4}$', '$it-{1} over{5}$', '$it-{1} over{6}$'],
    ans='②',
    sol=[
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta$',
        '$ LEFT({ sqrt{3}} over{3} RIGHT)^{2}={3} over{9}$',
        '$={1} over{3}$',
        '$1+2 sin theta cos theta={1} over{3}$에서',
        '$2 sin theta cos theta={1} over{3}-1$',
        '$=it-{2} over{3}$',
        '$therefore~ sin theta cos theta=it-{1} over{3}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2',
    text='부등식 $ log_{1/2}(2x-5) GEQ log_{1/2}(7-x)$를 만족하는 $x$값의 범위는?',
    choices=['$x LEQ 4$', '$x GEQ 4$', '${5} over{2}<x LEQ 4$', '${5} over{2}<x<7$', '$4 LEQ x<7$'],
    ans='③',
    sol=[
        '진수조건: $2x-5>0$에서 $x>{5} over{2}$, $7-x>0$에서 $x<7$',
        '밑 ${1} over{2}<1$이므로 부등호 방향이 바뀌어',
        '$2x-5 LEQ 7-x$',
        '$3x LEQ 12$',
        '$x LEQ 4$',
        '진수조건과 종합하면',
        '$therefore~{5} over{2}<x LEQ 4$',
    ],
    ch='로그부등식', lv='상')

add(id='q07', kind='mc', no=7, score=4.6, layout='3+2',
    text='$ sqrt[3]{a} sqrt{a}= sqrt[p]{a^{q}}$일 때, $p-q$의 값은? (단, $a>0$, $p,~q$는 서로소인 자연수이다.)',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='①',
    sol=[
        '$ sqrt[3]{a} sqrt{a}=a^{{1} over{3}} times a^{{1} over{2}}$',
        '$=a^{{5} over{6}}$',
        '$=a^{{5} over{6}}= sqrt[6]{a^{5}}$이므로 $p=6$, $q=5$',
        '$therefore~p-q=6-5$',
        '$=1$',
    ],
    ch='거듭제곱근의 성질', lv='상')

add(id='q08', kind='mc', no=8, score=4.7, layout='3+2',
    text='집합 $A= LEFT{ log_{2}3,~1/2 log_{2}6,~1/2 log_{2}24 RIGHT}$의 원소 중 최댓값을 $M$, 최솟값을 $m$이라고 할 때, $M-m$의 값은?',
    choices=['${1} over{2}$', '$1$', '${3} over{2}$', '$2$', '${5} over{2}$'],
    ans='②',
    sol=[
        '밑을 $4$로 바꾸면 $ log_{2}3= log_{4}9$, ${1} over{2} log_{2}6= log_{4}6$, ${1} over{2} log_{2}24= log_{4}24$',
        '$9<24$이고 $6<9$이므로 $ log_{4}6< log_{4}9< log_{4}24$',
        '$M= log_{4}24$, $m= log_{4}6$',
        '$M-m= log_{4}{24} over{6}= log_{4}4$',
        '$=1$',
    ],
    ch='로그의 대소비교', lv='상')

add(id='q09', kind='mc', no=9, score=4.7, layout='3+2',
    text='$n$이 $2$ 이상의 정수일 때, $ sqrt[n]{64}$가 어떤 자연수의 세제곱근이 되도록 하는 $n$의 최댓값은?',
    choices=['$6$', '$10$', '$12$', '$18$', '$24$'],
    ans='④',
    sol=[
        '$64=2^{6}$이므로 $ sqrt[n]{64}=2^{{6} over{n}}$',
        '이 값이 어떤 자연수의 세제곱근, 즉 $2^{{18} over{n}}$이 자연수가 되려면',
        '${18} over{n}$이 음이 아닌 정수여야 하므로 $n$은 $18$의 양의 약수',
        '$18$의 약수 중 $2$ 이상인 가장 큰 값은',
        '$n=18$',
    ],
    ch='거듭제곱근의 성질', lv='상')

add(id='q10', kind='mc', no=10, score=4.7, layout='1x5', box=True,
    text=[
        '$ theta$가 제$1$사분면의 각일 때, $ theta/3$의 동경이 놓일 수 있는 사분면만을 <보기>에서 있는 대로 고른 것은?',
    ],
    box_items=[
        '제$1$사분면', '제$2$사분면', '제$3$사분면', '제$4$사분면',
    ],
    choices=['ㄱ,~ㄴ', 'ㄷ,~ㄹ', 'ㄱ,~ㄴ,~ㄷ', 'ㄱ,~ㄷ,~ㄹ', 'ㄱ,~ㄴ,~ㄷ,~ㄹ'],
    ans='③',
    sol=[
        '$ theta$가 제$1$사분면의 각이므로 $360^{ circ}n<`` theta<``360^{ circ}n+90^{ circ}$',
        '$3$으로 나누면 $120^{ circ}n<`` { theta} over{3}<``120^{ circ}n+30^{ circ}$',
        '$n=0$: $0^{ circ}<`` { theta} over{3}<``30^{ circ}$ → 제$1$사분면',
        '$n=1$: $120^{ circ}<`` { theta} over{3}<``150^{ circ}$ → 제$2$사분면',
        '$n=2$: $240^{ circ}<`` { theta} over{3}<``270^{ circ}$ → 제$3$사분면',
        '$therefore$ ${ theta} over{3}$의 동경은 제$1$,~제$2$,~제$3$사분면에만 놓일 수 있다.',
    ],
    ch='일반각과 동경', lv='상')

add(id='q11', kind='mc', no=11, score=4.7, layout='3+2',
    text='$ log x=2.7952$, $ log y=it-0.8539$를 만족시키는 양수 $x,~y$에 대하여 $x+y$의 값은? (단, $ log6.24=0.7952$, $ log1.4=0.1461$로 계산한다.)',
    choices=['$7.64$', '$62.54$', '$624.14$', '$625.4$', '$638$'],
    ans='③',
    sol=[
        '$ log x=2.7952=2+0.7952$',
        '$= log100+ log6.24$',
        '$= log624$이므로 $x=624$',
        '$ log y=it-0.8539=it-1+0.1461$',
        '$= log10^{it-1}+ log1.4$',
        '$= log0.14$이므로 $y=0.14$',
        '$therefore~x+y=624+0.14$',
        '$=624.14$',
    ],
    ch='상용로그', lv='상')

add(id='q12', kind='mc', no=12, score=4.8, layout='3+2',
    text='두 양수 $a,~b$와 $xyz NEQ 0$인 세 실수 $x,~y,~z$에 대하여 $k=a^{x}=b^{y}=7^{z}$, $xy-2yz-3xz=0$일 때, $a^{2}b^{3}$의 값은?',
    choices=['$4$', '$5$', '$6$', '$7$', '$8$'],
    ans='④',
    sol=[
        '$k=a^{x}=b^{y}=7^{z}$에서 ${1} over{x}= log_{k}a$, ${1} over{y}= log_{k}b$, ${1} over{z}= log_{k}7$',
        '$xy-2yz-3xz=0$의 양변을 $xyz$로 나누면 ${1} over{z}-{2} over{x}-{3} over{y}=0$',
        '$therefore~ log_{k}7=2 log_{k}a+3 log_{k}b$',
        '$= log_{k}(a^{2}b^{3})$',
        '$7=a^{2}b^{3}$이므로',
        '$a^{2}b^{3}=7$',
    ],
    ch='로그의 성질(밑의 변환)', lv='상')

add(id='q13', kind='mc', no=13, score=4.8, layout='3+2',
    text=[
        '신호를 입력받아 그 신호를 증폭하여 출력하는 전송 기기가 있다. 이 전송 기기가 입력받는 신호를 $S_{1}$, 그때의 잡음을 $N_{1}$이라 하고, 출력하는 신호를 $S_{2}$, 그때의 잡음을 $N_{2}$라 하면 잡음 지수 $F$dB(데시벨)은',
        '$F=10 log LEFT({S_{1} times N_{2}} over{S_{2} times N_{1}} RIGHT)$',
        '인 관계가 있다고 한다. 잡음 지수 $F$가 $4.1$dB이고 출력 시의 잡음 $N_{2}$가 입력 시의 잡음 $N_{1}$의 $1/2$일 때, $S_{1}/S_{2}$의 값은? (단, 로그의 값은 다음 상용로그표를 참고하여 계산한다.)',
    ],
    emptybox={'paras': [
        '다음 그림은 상용로그표의 일부이다. (수 $5.1$, 열 $4$의 교차값: $0.7110$)',
    ]},
    choices=['$5$', '$5.04$', '$5.14$', '$5.2$', '$5.24$'],
    ans='③',
    sol=[
        '$4.1=10 log LEFT({S_{1}} over{S_{2}} times{1} over{2} RIGHT)$에서',
        '$0.41= log{S_{1}} over{S_{2}}- log2$',
        '$ log{S_{1}} over{S_{2}}=0.41+0.3010$',
        '$=0.7110$',
        '상용로그표에서 $ log5.14=0.7110$이므로',
        '$therefore~{S_{1}} over{S_{2}}=5.14$',
    ],
    ch='상용로그의 활용', lv='상')

add(id='q14', kind='mc', no=14, score=4.8, layout='3+2',
    text='$ theta$가 제$3$사분면의 각이고 $ sin theta- cos theta=1/2$일 때, $ sin^{3} theta+ cos^{3} theta$의 값은?',
    choices=['$it-{5 sqrt{7}} over{16}$', '$it-{3 sqrt{7}} over{16}$', '$it-{ sqrt{7}} over{16}$', '${ sqrt{7}} over{16}$', '${3 sqrt{7}} over{16}$'],
    ans='①',
    sol=[
        '$( sin theta- cos theta)^{2}=1-2 sin theta cos theta={1} over{4}$에서',
        '$ sin theta cos theta={3} over{8}$',
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta={7} over{4}$',
        '$ theta$가 제$3$사분면의 각이므로 $ sin theta+ cos theta<0$',
        '$therefore~ sin theta+ cos theta=it-{ sqrt{7}} over{2}$',
        '$ sin^{3} theta+ cos^{3} theta=( sin theta+ cos theta)(1- sin theta cos theta)$',
        '$= LEFT(it-{ sqrt{7}} over{2} RIGHT) LEFT(1-{3} over{8} RIGHT)$',
        '$=it-{ sqrt{7}} over{2} times{5} over{8}$',
        '$=it-{5 sqrt{7}} over{16}$',
    ],
    ch='삼각함수 사이의 관계', lv='상')

add(id='q15', kind='mc', no=15, score=4.9, layout='1x5', img_choices=True, fig='mm26m1_q15',
    text='좌표평면 위에서 점 $(2,~0)$을 지나는 지수함수 $y=a^{x-2}+b$의 그래프가 아래 그림과 같을 때, 로그함수 $y=it- log_{a}(bx)$의 그래프 개형으로 알맞은 것은? (단, $a,~b$는 상수이고 $a>0$, $a NEQ 1$이다.)',
    ans='①',
    sol=[
        '그래프가 점근선 $y=it-1$을 가지는 감소함수이므로 $0<a<1$이고 $b=it-1$',
        '점 $(2,~0)$을 지나므로 $0=a^{0}+b$',
        '$=1+b$에서 $b=it-1$ (점근선과 일치, 확인됨)',
        '$y=it- log_{a}(bx)=it- log_{a}(it-x)$이고 정의역은 $it-x>0$, 즉 $x<0$',
        '$0<a<1$이므로 $it- log_{a}t= log_{{1} over{a}}t$ ($t=it-x>0$)와 같고, 이는 $t$에 대한 증가함수',
        '$t=it-x$는 $x$가 증가할수록 감소하므로 합성하면 $x<0$에서 $x$에 대한 감소함수',
        '$x=it-1$일 때 $t=1$, $y= log_{{1} over{a}}1=0$을 지나고, $xarrow0^{it-}$일 때 $yarrowit- infty$',
        '$therefore$ 정의역 $x<0$에서 감소하며 $x=it-1$을 지나고 $x=0$에서 점근선을 갖는 ①.',
    ],
    ch='지수함수와 로그함수의 그래프', lv='최상')

add(id='q16', kind='mc', no=16, score=4.9, layout='3+2',
    text='함수 $y= log_{3}k(x+2)$의 그래프를 $x$축의 방향으로 $it-1$만큼 평행이동한 그래프가 제$2$사분면을 지나지 않도록 하는 양의 실수 $k$의 최댓값은?',
    choices=['${1} over{3}$', '${1} over{2}$', '$1$', '$2$', '$3$'],
    ans='①',
    sol=[
        '평행이동한 그래프는 $y= log_{3}k(x+1+2)$',
        '$= log_{3}k(x+3)$',
        '밑 $3>1$이므로 증가함수이고, 점근선은 $x=it-3$',
        '제$2$사분면($x<0,~y>0$)을 지나지 않으려면 $x=0$에서의 함숫값이 $0$ 이하이어야 한다.',
        '$ log_{3}k(0+3) LEQ 0$',
        '$3k LEQ 1$',
        '$therefore~k LEQ{1} over{3}$이므로 최댓값은',
        '${1} over{3}$',
    ],
    ch='로그함수의 그래프', lv='최상')

add(id='q17', kind='mc', no=17, score=5.0, layout='3+2',
    text='방정식 $9^{x}+9=k times3^{x}$의 서로 다른 두 근을 $ alpha,~ beta$라 하자. $ alpha- beta=1$일 때, 상수 $k$의 값은?',
    choices=['$ sqrt{3}$', '$2 sqrt{3}$', '$3 sqrt{3}$', '$4 sqrt{3}$', '$5 sqrt{3}$'],
    ans='④',
    sol=[
        '$t=3^{x}>0$으로 치환하면 $t^{2}-kt+9=0$',
        '두 근은 $t_{1}=3^{ alpha}$, $t_{2}=3^{ beta}$ ($ alpha> beta$)이고, 근과 계수의 관계에서 $t_{1}t_{2}=9$',
        '$ alpha- beta=1$에서 ${t_{1}} over{t_{2}}=3^{ alpha- beta}=3$',
        '$t_{1}=3t_{2}$를 $t_{1}t_{2}=9$에 대입하면 $3t_{2}^{2}=9$',
        '$t_{2}^{2}=3$에서 $t_{2}= sqrt{3}$, $t_{1}=3 sqrt{3}$',
        '$therefore~k=t_{1}+t_{2}=3 sqrt{3}+ sqrt{3}$',
        '$=4 sqrt{3}$',
    ],
    ch='지수방정식', lv='최상')

add(id='q18', kind='mc', no=18, score=5.0, layout='3+2',
    text='두 함수 $f(x)=1/2 x^{2}-3x+3/2$, $g(x)= log_{a}x$에 대하여 $1 LEQ x LEQ 4$에서 합성함수 $(g^{it-1} circ f)(x)$의 최솟값이 $2$일 때, 최댓값은? (단, $a>0$, $a NEQ 1$이다.)',
    choices=['$4$', '$5$', '$6$', '$7$', '$8$'],
    ans='⑤',
    sol=[
        '$f(x)={1} over{2}(x-3)^{2}-3$이고, $1 LEQ x LEQ 4$에서 $f(1)=it-1$, $f(3)=it-3$, $f(4)=it-{5} over{2}$',
        '따라서 $f(x)$의 치역은 $it-3 LEQ f(x) LEQ it-1$',
        '$g^{it-1}(y)=a^{y}$이므로 $(g^{it-1} circ f)(x)=a^{f(x)}$',
        '$a>1$이면 $a^{f(x)}$은 $f(x)$에 대해 증가하여 최솟값은 $f(x)=it-3$에서 $a^{it-3}=2$',
        '이때 $a=2^{it-{1} over{3}}<1$이 되어 $a>1$에 모순',
        '$0<a<1$이면 $a^{f(x)}$은 $f(x)$에 대해 감소하여 최솟값은 $f(x)=it-1$에서 $a^{it-1}=2$',
        '$therefore~a={1} over{2}$이고, 최댓값은 $f(x)=it-3$에서 $a^{it-3}= LEFT({1} over{2} RIGHT)^{it-3}$',
        '$=8$',
    ],
    ch='로그함수의 합성함수', lv='최상')

add(id='q19', kind='mc', no=19, score=5.1, layout='3+2',
    text=[
        '삼각형 $ABC$의 세 변의 길이 $a,~b,~c$에 대하여',
        '$ log_{a}(c+b)+ log_{a}(c-b)=2$, $ log_{12}a+ log_{12}b=1$',
        '이 성립한다고 할 때, 삼각형 $ABC$의 내접원의 넓이는? (단, $1<a<b<c$이고 $a,~b,~c$는 자연수이다.)',
    ],
    choices=['${ pi} over{2}$', '$ pi$', '${3} over{2} pi$', '$2 pi$', '${5} over{2} pi$'],
    ans='②',
    sol=[
        '$ log_{a} LEFT{(c+b)(c-b) RIGHT}=2$에서 $c^{2}-b^{2}=a^{2}$',
        '$therefore~a^{2}+b^{2}=c^{2}$ (빗변이 $c$인 직각삼각형)',
        '$ log_{12}(ab)=1$에서 $ab=12$',
        '$ab=12$이고 $a^{2}+b^{2}=c^{2}$을 만족하는 자연수 $1<a<b<c$는 $a=3$, $b=4$, $c=5$',
        '직각삼각형의 내접원의 반지름은 $r={a+b-c} over{2}={3+4-5} over{2}$',
        '$=1$',
        '$therefore$ 내접원의 넓이는 $ pi r^{2}= pi times1^{2}$',
        '$= pi$',
    ],
    ch='로그의 성질의 활용', lv='최상')

add(id='q20', kind='mc', no=20, score=5.2, layout='3+2', fig='mm26m1_q20',
    text=[
        '두 함수 $y=2^{x}+1$, $y=2^{x-b}+1$의 그래프가 직선 $x=a$와 만나는 점을 각각 $A,~B$라 하고, $y$축과 만나는 점을 각각 $C,~D$라 하면 선분 $BC$는 $x$축과 평행이다. 삼각형 $ABC$의 넓이가 삼각형 $BCD$의 넓이의 $13/4$배일 때, $2^{a+b}$의 값은? (단, $a,~b$는 상수이고 $a>0$이다.)',
    ],
    choices=['${9} over{4}$', '${13} over{4}$', '${27} over{8}$', '${81} over{16}$', '${169} over{16}$'],
    ans='⑤',
    sol=[
        '$C=(0,~2)$이고 $BC$가 $x$축과 평행하므로 $B$의 $y$좌표도 $2$',
        '$2^{a-b}+1=2$에서 $a-b=0$',
        '$therefore~a=b$',
        '$A=(a,~2^{a}+1)$, $B=(a,~2)$이므로 $ overline{AB}=2^{a}-2^{a-b}=2^{a}-1$, $ overline{BC}=a$',
        '$D=(0,~2^{it-b}+1)$이므로 $ overline{CD}=2-(2^{it-b}+1)=1-2^{it-b}$',
        '삼각형 넓이의 비 조건에서 ${{1} over{2}(2^{a}-1)a} over{{1} over{2}(1-2^{it-b})a}={13} over{4}$',
        '$a=b$를 대입하면 $2^{a}-1={13} over{4}(1-2^{it-a})$',
        '$T=2^{a}$로 치환($T>1$)하면 $T-1={13} over{4} times{T-1} over{T}$',
        '$T-1 NEQ 0$이므로 양변을 나누면 $T={13} over{4}$',
        '$therefore~2^{a+b}=2^{2a}=T^{2}= LEFT({13} over{4} RIGHT)^{2}$',
        '$={169} over{16}$',
    ],
    ch='지수함수의 그래프와 도형', lv='최상')

add(id='q21', kind='mc', no=21, score=5.3, layout='3+2',
    text=[
        '두 집합',
        '$A= LEFT{x | (x^{2}+2x+1)^{ log_{4}3}=3^{ log_{2} LEFT | a RIGHT |} RIGHT}$,',
        '$B= LEFT{x | LEFT({1} over{27} RIGHT)^{x} GEQ 3^{4-x^{2}} RIGHT}$',
        '에 대하여 $n(A cap B)=1$을 만족하는 정수 $a$의 개수는?',
    ],
    choices=['$5$', '$6$', '$7$', '$8$', '$9$'],
    ans='④',
    sol=[
        '$2 log_{4}3= log_{2}3$이므로 $(x+1)^{2 log_{4}3}=(x+1)^{ log_{2}3}=3^{ log_{2} LEFT | x+1 RIGHT |}$',
        '$3^{ log_{2} LEFT | x+1 RIGHT |}=3^{ log_{2} LEFT | a RIGHT |}$에서 $ LEFT | x+1 RIGHT |= LEFT | a RIGHT |$',
        '$therefore~x= LEFT | a RIGHT |-1$ 또는 $x=it- LEFT | a RIGHT |-1$ ($a NEQ 0$)',
        '$B$: $3^{it-3x} GEQ 3^{4-x^{2}}$에서 $it-3x GEQ 4-x^{2}$',
        '$x^{2}-3x-4 GEQ 0$',
        '$(x-4)(x+1) GEQ 0$이므로 $B$: $x LEQ it-1$ 또는 $x GEQ 4$',
        '$p= LEFT | a RIGHT | GEQ 1$이라 하면 $x=it-p-1 LEQ it-2$는 항상 $B$에 속한다.',
        '$n(A cap B)=1$이 되려면 나머지 한 원소 $x=p-1$은 $B$에 속하지 않아야 하므로',
        '$it-1<p-1<4$',
        '$0<p<5$이므로 $p=1,~2,~3,~4$',
        '$a=` pm p$이므로 정수 $a$는 $ pm1,~ pm2,~ pm3,~ pm4$',
        '$therefore$ 정수 $a$의 개수는',
        '$8$',
    ],
    ch='로그방정식과 지수부등식', lv='최상')
