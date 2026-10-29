# -*- coding: utf-8 -*-
"""운산고등학교 2학년 2026 1학기 중간 대수(지수로그~삼각함수의 기본성질) 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.0, layout='3+2',
    text='$ log_{2}4+ log_{3}1$의 값은?',
    choices=['$2$', '$3$', '$4$', '$5$', '$6$'],
    ans='①',
    sol=[
        '$ log_{2}4=2$, $ log_{3}1=0$',
        '$therefore$ 구하는 값은 $2+0$',
        '$=2$',
    ],
    ch='로그의 성질', lv='하')

add(id='q02', kind='mc', no=2, score=4.0, layout='1x5',
    text='$ sqrt[3]{16} div2^{x}=2$일 때, $x$의 값은?',
    choices=['$0$', '${1} over{12}$', '${1} over{6}$', '${1} over{4}$', '${1} over{3}$'],
    ans='⑤',
    sol=[
        '$ sqrt[3]{16}=16^{{1} over{3}}=2^{{4} over{3}}$',
        '$2^{{4} over{3}} div2^{x}=2^{{4} over{3}-x}=2^{1}$에서 ${4} over{3}-x=1$',
        '$therefore~x={4} over{3}-1$',
        '$={1} over{3}$',
    ],
    ch='거듭제곱근의 변형', lv='하')

add(id='q03', kind='mc', no=3, score=4.1, layout='1x5',
    text='$ cos(it-300^{ circ})$의 값은?',
    choices=['${1} over{2}$', '${ sqrt{3}} over{3}$', '${ sqrt{2}} over{2}$', '${ sqrt{3}} over{2}$', '$1$'],
    ans='①',
    sol=[
        '$ cos(it-300^{ circ})= cos300^{ circ}= cos(360^{ circ}-60^{ circ})= cos60^{ circ}$',
        '$therefore$ 구하는 값은',
        '$={1} over{2}$',
    ],
    ch='일반각의 삼각함수', lv='하')

add(id='q04', kind='mc', no=4, score=4.2, layout='3+2',
    text='반지름의 길이가 $2$이고 호의 길이가 $3$인 부채꼴의 넓이는?',
    choices=['$1$', '${1} over{2}$', '$2$', '${5} over{2}$', '$3$'],
    ans='⑤',
    sol=[
        '넓이 $={1} over{2}rl={1} over{2} times2 times3$',
        '$therefore$ 구하는 값은',
        '$=3$',
    ],
    ch='호도법과 부채꼴', lv='하')

add(id='q05', kind='mc', no=5, score=4.3, layout='1x5', box=True,
    text='실수인 것의 개수가 $2$인 것만을 [보기]에서 고른 것은?',
    box_items=[
        '$it-8$의 세제곱근',
        '$5$의 네제곱근',
        '$0$의 다섯제곱근',
        '$ sqrt{(it-9)^{2}}$의 여섯제곱근',
    ],
    choices=['ㄱ,~ㄴ', 'ㄱ,~ㄷ', 'ㄴ,~ㄷ', 'ㄴ,~ㄹ', 'ㄷ,~ㄹ'],
    ans='④',
    sol=[
        'ㄱ. 세제곱근(홀수제곱근)은 실수에서 항상 $1$개(음수여도 마찬가지)이므로 $1$개',
        'ㄴ. 네제곱근(짝수제곱근, 양수 $5$)은 실수에서 $2$개',
        'ㄷ. $0$의 다섯제곱근은 $0$ 하나뿐이므로 $1$개',
        'ㄹ. $ sqrt{(it-9)^{2}}= sqrt{81}=9$(양수)의 여섯제곱근(짝수제곱근)은 $2$개',
        '$therefore$ 개수가 $2$인 것은',
        '$=ㄴ,~ㄹ$',
    ],
    ch='거듭제곱근의 개수', lv='하')

add(id='q06', kind='mc', no=6, score=4.4, layout='3+2',
    text='곡선 $y=2^{x}+3$의 점근선과 곡선 $y= log_{3}x+1$의 교점의 $x$좌표는?',
    choices=['$6$', '$9$', '$12$', '$18$', '$27$'],
    ans='②',
    sol=[
        '$y=2^{x}+3$의 점근선은 $y=3$ (수평점근선)',
        '$ log_{3}x+1=3$에서 $ log_{3}x=2$',
        '$therefore~x$',
        '$=9$',
    ],
    ch='지수함수와 로그함수의 점근선', lv='하')

add(id='q07', kind='mc', no=7, score=4.5, layout='1x5',
    text='$0<a<1$인 실수 $a$에 대하여 함수 $f(x)=a^{x}$은 $it-1 LEQ x LEQ 2$에서 최솟값 $m$, 최댓값 ${5} over{4}$를 갖는다. ${m} over{a}$의 값은?',
    choices=['${2} over{5}$', '${3} over{4}$', '${4} over{5}$', '$1$', '${5} over{4}$'],
    ans='③',
    sol=[
        '$0<a<1$이므로 $f(x)=a^{x}$은 감소함수이다. 최댓값은 $x=it-1$에서, 최솟값은 $x=2$에서 나온다.',
        '$a^{it-1}={1} over{a}={5} over{4}$에서 $a={4} over{5}$',
        '$m=a^{2}=LEFT({4} over{5} RIGHT)^{2}={16} over{25}$',
        '$therefore~{m} over{a}={16/25} over{4/5}={16} over{25} times{5} over{4}={4} over{5}$',
        '$={4} over{5}$',
    ],
    ch='지수함수의 최대·최소', lv='중')

add(id='q08', kind='mc', no=8, score=4.6, layout='1x5', fig='us26m1_q08',
    text='그림과 같이 원뿔 모양의 물컵이 있다. 물컵의 밑면의 반지름의 길이는 $3$이고, 부피가 $12 pi$이다. 물컵을 그림과 같이 펼쳤을 때, 부채꼴 $OAB$의 넓이는?',
    choices=['$6 pi$', '$12 pi$', '$15 pi$', '$24 pi$', '$30 pi$'],
    ans='③',
    sol=[
        '부피 $={1} over{3} pir^{2}h={1} over{3} pi(9)h=3 pih=12 pi$에서 $h=4$',
        '모선의 길이 $l= sqrt{r^{2}+h^{2}}= sqrt{9+16}= sqrt{25}=5$',
        '펼친 부채꼴의 반지름은 모선 $l=5$, 호의 길이는 밑면 둘레 $2 pir=6 pi$',
        '부채꼴의 넓이 $={1} over{2} times l times(호의 길이)={1} over{2} times5 times6 pi$',
        '$therefore$ 구하는 넓이는',
        '$=15 pi$',
    ],
    ch='부채꼴의 넓이(원뿔의 전개도)', lv='중')

add(id='q09', kind='mc', no=9, score=4.7, layout='1x5',
    text='$0$이 아닌 세 실수 $x,~y,~z$가 $2^{x}=3^{y}=12^{z}$을 만족시킬 때, ${2} over{x}+{1} over{y}-{1} over{z}$의 값은?',
    choices=['$it-1$', '$0$', '${1} over{2}$', '$1$', '$2$'],
    ans='②',
    sol=[
        '$2^{x}=3^{y}=12^{z}=K$ ($K>0,~K NEQ 1$)라 하면 $x= log_{2}K$, $y= log_{3}K$, $z= log_{12}K$',
        '${2} over{x}={2} over{ log_{2}K}=2 log_{K}2= log_{K}4$. ${1} over{y}= log_{K}3$. ${1} over{z}= log_{K}12$',
        '${2} over{x}+{1} over{y}-{1} over{z}= log_{K}4+ log_{K}3- log_{K}12= log_{K}LEFT({4 times3} over{12} RIGHT)= log_{K}1$',
        '$therefore$ 구하는 값은',
        '$=0$',
    ],
    ch='지수와 로그의 변형', lv='중')

add(id='q10', kind='mc', no=10, score=4.8, layout='1x5',
    text='$ theta$가 제$3$사분면의 각이고 $ cos theta=it-{4} over{5}$일 때, $ sin theta+ tan theta$의 값은?',
    choices=['${1} over{40}$', '${1} over{20}$', '${1} over{10}$', '${3} over{20}$', '${1} over{5}$'],
    ans='④',
    sol=[
        '제$3$사분면이므로 $ sin theta<0$. $ sin theta=it- sqrt{1-{16} over{25}}=it- sqrt{{9} over{25}}=it-{3} over{5}$',
        '$ tan theta={ sin theta} over{ cos theta}={it-3/5} over{it-4/5}={3} over{4}$',
        '$therefore~ sin theta+ tan theta=it-{3} over{5}+{3} over{4}=it-{12} over{20}+{15} over{20}$',
        '$={3} over{20}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q11', kind='mc', no=11, score=4.9, layout='3+2',
    text='상수 $a,~b$에 대하여 함수 $y=2^{x-a}+b$의 그래프와 함수 $y= log_{2}(x-b)+a$의 그래프가 만나는 두 점의 $x$좌표가 각각 $it-1,~{it-2}$일 때, $a times b$의 값은?',
    choices=['$2$', '$4$', '$6$', '$8$', '$10$'],
    ans='③',
    sol=[
        '두 함수는 서로 역함수 관계이므로, 교점은 직선 $y=x$ 위의 점(고정점)이거나 $(p,~q)$-$(q,~p)$ 형태의 짝으로 나타난다.',
        '두 교점의 $x$좌표가 서로 다른 $it-1,~{it-2}$이므로, 각각이 $y=x$ 위의 고정점(즉 $f(it-1)=it-1$, $f(it-2)=it-2$)인 경우로 해석된다.',
        '$2^{it-1-a}+b=it-1$ ... (ⅰ), $2^{it-2-a}+b=it-2$ ... (ⅱ)',
        '(ⅰ)$-$(ⅱ): $2^{it-1-a}-2^{it-2-a}=1$에서 $2^{it-2-a}(2-1)=1$, $2^{it-2-a}=1$, $it-2-a=0$, $a=it-2$',
        '(ⅱ)에 대입: $2^{it-2-(it-2)}+b=2^{0}+b=1+b=it-2$에서 $b=it-3$',
        '$therefore~a times b=(it-2) times(it-3)$',
        '$=6$',
    ],
    ch='역함수의 교점과 고정점', lv='상')

add(id='q12', kind='mc', no=12, score=5.0, layout='1x5', emptybox={'paras': [
        '$P=20 log255-10 logE$ ($E>0$)',
    ]},
    text='디지털 사진을 압축할 때, 원본 사진과 압축한 사진의 다른 정도를 나타내는 지표인 최대 신호 대 잡음비를 $P$, 원본 사진과 압축한 사진의 평균제곱오차를 $E$라 하면, 위와 같은 관계식이 성립한다고 한다. 두 원본 사진 $A,~B$를 압축했을 때 최대 신호 대 잡음비를 각각 $P_{A},~P_{B}$라 하고, 평균제곱오차를 각각 $E_{A},~E_{B}$라 하자. $P_{A}-P_{B}=26.59$일 때, ${E_{B}} over{E_{A}}$의 값을 다음 상용로그표의 일부를 이용하여 구한 것은? (단, $E_{A}>0,~E_{B}>0$) (상용로그표: 행 $4.5$, 열 $6$의 교차값 $0.6590$)',
    choices=['$445$', '$446$', '$455$', '$456$', '$457$'],
    ans='④',
    sol=[
        '$P_{A}-P_{B}=LEFT(20 log255-10 logE_{A} RIGHT)-LEFT(20 log255-10 logE_{B} RIGHT)=10LEFT( logE_{B}- logE_{A} RIGHT)=10 log LEFT({E_{B}} over{E_{A}} RIGHT)$',
        '$10 log LEFT({E_{B}} over{E_{A}} RIGHT)=26.59$에서 $ log LEFT({E_{B}} over{E_{A}} RIGHT)=2.659$',
        '$2.659=2+0.659$이고 상용로그표에서 $ log4.56=0.6590 fallapprox0.659$',
        '${E_{B}} over{E_{A}}=10^{2.659}=10^{2} times10^{0.659}=100 times4.56$',
        '$therefore$ 구하는 값은',
        '$=456$',
    ],
    ch='상용로그표의 활용', lv='중')

add(id='q13', kind='mc', no=13, score=5.1, layout='1x5', jogeon=True,
    text='두 양수 $x,~y$가 다음 두 조건을 만족시킬 때, $(x-y)^{2}$의 값은?',
    jogeon_items=[
        '$ log_{5}x+ log_{5}y=2$',
        '$ log_{2}(x+2)+ log_{2}(y+2)= log_{2}54$',
    ],
    choices=['${15} over{2}$', '${25} over{2}$', '${217} over{4}$', '${225} over{4}$', '${625} over{4}$'],
    ans='④',
    sol=[
        '(가): $ log_{5}(xy)=2$에서 $xy=25$',
        '(나): $ log_{2}LEFT[(x+2)(y+2) RIGHT]= log_{2}54$에서 $(x+2)(y+2)=54$',
        '전개하면 $xy+2(x+y)+4=54$, $xy=25$를 대입하면 $2(x+y)=25$, $x+y={25} over{2}$',
        '$(x-y)^{2}=(x+y)^{2}-4xy=LEFT({25} over{2} RIGHT)^{2}-4(25)={625} over{4}-100={625} over{4}-{400} over{4}$',
        '$therefore$ 구하는 값은',
        '$={225} over{4}$',
    ],
    ch='로그의 성질과 연립방정식', lv='중')

add(id='q14', kind='mc', no=14, score=5.2, layout='1x5', emptybox={'paras': [
        '(가) 점 $A$는 곡선 $y= log_{a}(x+2)+1$ 위의 점 중 제$4$사분면에 있는 점이고, 점 $B$는 점 $A$를',
        '지나고 $x$축과 평행한 직선이 곡선 $y= log_{a}(x+2)+1$의 점근선과 만나는 점이다.',
        '(나) 점 $C$는 점 $A$를 $x$축에 대해 대칭이동 시킨 점이다. 직선 $BC$가 점 $O$를 지나고,',
        '곡선 $y= log_{a}(x+2)+1$을 $y$축에 대해 대칭이동 시킨 곡선도 점 $O$를 지난다.',
    ]},
    text='상수 $a$에 대하여 곡선 $y= log_{a}(x+2)+1$이 다음 조건을 만족시킬 때, $a times bar{OA}$의 값은? (단, $0<a<1$이고, 점 $O$는 원점이다.)',
    choices=['${ sqrt{3}} over{2}$', '${ sqrt{5}} over{2}$', '${ sqrt{10}} over{2}$', '$ sqrt{5}$', '$2 sqrt{5}$'],
    ans='②',
    sol=[
        '점근선은 $x=it-2$이다. $A=(p,~y_{A})$라 하면 $B=(it-2,~y_{A})$, $C=(p,~{it-y_{A}})$',
        '$B,~C$를 잇는 직선이 원점을 지나는 조건에서 $x=0$일 때 $y=0$이 되는 매개변수 $t$를 구하면 $t={1} over{2}$가 되고, 이때 $x$좌표 $=it-2+{1} over{2}(p+2)=0$에서 $p=2$',
        '$y= log_{a}(x+2)+1$을 $y$축에 대칭이동한 곡선 $y= log_{a}(it-x+2)+1$이 원점을 지나므로 $0= log_{a}2+1$에서 $ log_{a}2=it-1$, $a={1} over{2}$',
        '$y_{A}= log_{{1} over{2}}(2+2)+1= log_{{1} over{2}}4+1=it-2+1=it-1$',
        '$A=(2,~{it-1})$. $bar{OA}= sqrt{2^{2}+(it-1)^{2}}= sqrt{4+1}= sqrt{5}$',
        '$therefore~a times bar{OA}={1} over{2} times sqrt{5}$',
        '$={ sqrt{5}} over{2}$',
    ],
    ch='로그함수의 그래프와 점근선', lv='상')

add(id='q15', kind='mc', no=15, score=5.3, layout='1x5', fig='us26m1_q15',
    text='그림과 같이 $ angle A=90^{ circ}$인 직각삼각형 $ABC$에 대하여 꼭짓점 $A$에서 변 $BC$ 위에 내린 수선의 발이 $H$이고, $bar{AH}=27$, $bar{BH}=x$, $bar{CH}=y$이다. 두 양수 $x,~y$에 대하여 $ log_{ sqrt{x}}3 times log_{3}y=4$일 때, 변 $BC$의 길이는? (단, $bar{BH} NEQ 1$, $bar{BH}<bar{CH}$)',
    choices=['$81$', '$84$', '$90$', '$108$', '$162$'],
    ans='③',
    sol=[
        '직각삼각형의 닮음 관계(수선의 성질)에 의해 $bar{AH}^{2}=bar{BH} times bar{CH}$, 즉 $27^{2}=xy=729$',
        '$ log_{ sqrt{x}}3={2} over{ log_{3}x}$ (밑변환)이므로 $ log_{ sqrt{x}}3 times log_{3}y={2 log_{3}y} over{ log_{3}x}=4$에서 $ log_{3}y=2 log_{3}x$, 즉 $y=x^{2}$',
        '$xy=x^{3}=729=3^{6}$에서 $x=3^{2}=9$, $y=81$',
        '$bar{BH}=9<bar{CH}=81$로 조건과 일치, $bar{BH}=9 NEQ 1$도 만족',
        '$therefore~bar{BC}=x+y=9+81$',
        '$=90$',
    ],
    ch='직각삼각형의 닮음과 로그', lv='상')

add(id='q16', kind='mc', no=16, score=5.4, layout='1x5', jogeon=True,
    text='양수 $k$에 대하여 곡선 $y= log_{ sqrt{2}}(x-k)$가 $x$축과 만나는 점을 $A$라 하자. 직선 $y=4$가 곡선 $y= log_{ sqrt{2}}(x-k)$와 만나는 점을 $B$, $y$축과 만나는 점을 $C$라 할 때, 다음 조건을 만족시킨다.',
    jogeon_items=[
        '$4 bar{AB}=3 bar{AC}$',
    ],
    text2=['삼각형 $ABC$의 넓이가 ${q} over{p}$일 때, $p+q$의 값은? (단, $p,~q$는 서로소인 자연수이다.) [5.4점]'],
    choices=['$35$', '$41$', '$43$', '$47$', '$53$'],
    ans='⑤',
    sol=[
        '$A$: $y=0$에서 $x-k=1$, $A=(k+1,~0)$. $B$: $y=4$에서 $x-k=( sqrt{2})^{4}=4$, $B=(k+4,~4)$. $C$: 직선 $y=4$와 $y$축의 교점이므로 $C=(0,~4)$',
        '$bar{AB}= sqrt{(k+4-(k+1))^{2}+4^{2}}= sqrt{9+16}= sqrt{25}=5$',
        '$4 bar{AB}=3 bar{AC}$에서 $ bar{AC}={20} over{3}$',
        '$bar{AC}= sqrt{(k+1)^{2}+16}={20} over{3}$에서 $(k+1)^{2}+16={400} over{9}$, $(k+1)^{2}={256} over{9}$, $k+1={16} over{3}$',
        '$B,~C$는 모두 $y=4$ 위에 있으므로 $bar{BC}$는 수평선분: $bar{BC}=LEFT | k+4-0 RIGHT |={16} over{3}+3={25} over{3}$',
        '$A$에서 직선 $BC(y=4)$까지의 거리 $=4$',
        '삼각형 넓이 $={1} over{2} times{25} over{3} times4={50} over{3}$',
        '$p=3,~q=50$ (서로소)이므로 $p+q=3+50$',
        '$=53$',
    ],
    ch='로그함수의 그래프와 삼각형의 넓이', lv='상')

add(id='q17', kind='mc', no=17, score=5.5, layout='1x5', fig='us26m1_q17',
    text='원점 $O$와 점 $P LEFT(it- sqrt{2},~ sqrt{6} RIGHT)$에 대하여 선분 $OP$와 단위원의 교점을 $P\'$이라고 하자. 단위원과 $x$축이 만나는 두 점을 각각 $A,~B$라 하고, 점 $P\'$에서 $x$축에 내린 수선의 발을 $H$라고 하자. 이때 삼각형 $P\'HO$의 넓이를 $a$, 선분 $AP\'$과 호 $AP\'$으로 둘러싸인 도형의 넓이를 $b$라고 할 때, $a+b$의 값은? (단, 점 $A$의 $x$좌표는 점 $B$의 $x$좌표의 값보다 크다.)',
    choices=['${ pi} over{3}-{ sqrt{3}} over{8}$', '${ pi} over{3}-{ sqrt{3}} over{4}$', '${2} over{3} pi-{ sqrt{3}} over{8}$', '${2} over{3} pi-{ sqrt{3}} over{4}$', '${ pi} over{3}+{ sqrt{3}} over{4}$'],
    ans='①',
    sol=[
        '$bar{OP}= sqrt{2+6}= sqrt{8}=2 sqrt{2}$이므로 $P\'=LEFT({it- sqrt{2}} over{2 sqrt{2}},~{ sqrt{6}} over{2 sqrt{2}} RIGHT)=LEFT(it-{1} over{2},~{ sqrt{3}} over{2} RIGHT)$ (각 $120^{ circ}$)',
        '$A=(1,~0)$ (더 큰 $x$좌표), $H=LEFT(it-{1} over{2},~0 RIGHT)$',
        '삼각형 $P\'HO$: 직각삼각형, 밑변 $bar{OH}={1} over{2}$, 높이 $bar{HP\'}={ sqrt{3}} over{2}$',
        '$a={1} over{2} times{1} over{2} times{ sqrt{3}} over{2}={ sqrt{3}} over{8}$',
        '호 $AP\'$의 중심각은 $120^{ circ}={2} over{3} pi$. 부채꼴 $OAP\'$의 넓이 $={1} over{2}(1)^{2}LEFT({2} over{3} pi RIGHT)={ pi} over{3}$',
        '삼각형 $OAP\'$의 넓이 $={1} over{2}LEFT | 1 times{ sqrt{3}} over{2}-LEFT(it-{1} over{2} RIGHT) times0 RIGHT |={ sqrt{3}} over{4}$',
        '$b=$(부채꼴 넓이)$-$(삼각형 넓이)$={ pi} over{3}-{ sqrt{3}} over{4}$',
        '$therefore~a+b={ sqrt{3}} over{8}+{ pi} over{3}-{ sqrt{3}} over{4}={ pi} over{3}-{ sqrt{3}} over{8}$',
        '$={ pi} over{3}-{ sqrt{3}} over{8}$',
    ],
    ch='단위원과 부채꼴의 넓이', lv='상')

add(id='q18', kind='sub', no=1, score=6.0,
    text='$k= log_{3}LEFT(1+{1} over{1} RIGHT)+ log_{3}LEFT(1+{1} over{2} RIGHT)+ log_{3}LEFT(1+{1} over{3} RIGHT)+ cdots+ log_{3}LEFT(1+{1} over{25} RIGHT)+ log_{3}LEFT(1+{1} over{26} RIGHT)$일 때, 다음 물음에 답하시오.',
    text2=[
        '1-1) $k$의 값을 구하고, 그 풀이과정을 논리적으로 서술하시오. [2.0점]',
        '1-2) $a^{2x}=k$일 때, ${a^{3x}+a^{it-3x}} over{a^{x}-a^{it-x}}$의 값을 ${q} over{p}$의 꼴로 나타내고, 그 풀이과정을 논리적으로 서술하시오. (단, $a>0$, $p,~q$는 서로소인 자연수이다.) [4.0점]',
    ],
    ans_mix='1-1) $k=3$. 1-2) ${14} over{3}$',
    sol=[
        '1-1) $1+{1} over{n}={n+1} over{n}$이므로 $k= log_{3}LEFT( prod_{n=1}^{26}{n+1} over{n} RIGHT)$',
        '$ prod_{n=1}^{26}{n+1} over{n}={2} over{1} times{3} over{2} times cdots times{27} over{26}=27$ (연속으로 약분되는 텔레스코핑)',
        '$k= log_{3}27= log_{3}3^{3}$',
        '$therefore~k$',
        '$=3$',
        '1-2) $u=a^{x}$라 하면 $a^{2x}=u^{2}=k=3$이므로 $u= sqrt{3}$ ($a>0$이므로 $u>0$)',
        '$s=u+{1} over{u}$: $s^{2}=u^{2}+2+{1} over{u^{2}}=3+2+{1} over{3}={16} over{3}$에서 $s={4} over{ sqrt{3}}={4 sqrt{3}} over{3}$',
        '$u^{2}+{1} over{u^{2}}=3+{1} over{3}={10} over{3}$이므로 $u^{3}+{1} over{u^{3}}=s LEFT(u^{2}-1+{1} over{u^{2}} RIGHT)={4 sqrt{3}} over{3} timesLEFT({10} over{3}-1 RIGHT)={4 sqrt{3}} over{3} times{7} over{3}={28 sqrt{3}} over{9}$',
        '$u-{1} over{u}= sqrt{3}-{1} over{ sqrt{3}}= sqrt{3}-{ sqrt{3}} over{3}={2 sqrt{3}} over{3}$',
        '${a^{3x}+a^{it-3x}} over{a^{x}-a^{it-x}}={u^{3}+{1} over{u^{3}}} over{u-{1} over{u}}={{28 sqrt{3}} over{9}} over{{2 sqrt{3}} over{3}}={28 sqrt{3}} over{9} times{3} over{2 sqrt{3}}={28 times3} over{9 times2}={84} over{18}$',
        '약분하면 $p=3,~q=14$ (서로소)이므로',
        '$therefore$ 구하는 값은',
        '$={14} over{3}$',
    ],
    ch='로그의 텔레스코핑과 지수의 변형', lv='상')

add(id='q19', kind='sub', no=2, score=7.0,
    text='부등식 $(x-1)(9^{x-2}-27)<0$과 $ log_{2}(x+3)+ log_{{1} over{2}}(x-2)-1 GEQ 0$을 모두 만족시키는 자연수 $x$의 값을 구하고, 그 풀이과정을 논리적으로 서술하시오.',
    ans_mix='$x=3$',
    sol=[
        '$9^{x-2}-27=0$에서 $3^{2x-4}=3^{3}$, $2x-4=3$, $x={7} over{2}$. $9^{x-2}-27$은 증가함수이므로 $x<{7} over{2}$에서 음수, $x>{7} over{2}$에서 양수',
        '$(x-1)(9^{x-2}-27)<0$은 두 인수의 부호가 반대여야 하므로 $x-1>0$이고 $9^{x-2}-27<0$: $1<x<{7} over{2}$',
        '(다른 경우 $x-1<0$이고 $9^{x-2}-27>0$은 $x<1$과 $x>{7} over{2}$를 동시에 만족할 수 없어 불가능)',
        '진수 조건: $x+3>0$, $x-2>0$에서 $x>2$',
        '$ log_{{1} over{2}}(x-2)=it- log_{2}(x-2)$이므로 부등식은 $ log_{2}(x+3)- log_{2}(x-2)-1 GEQ 0$, $ log_{2}LEFT({x+3} over{x-2} RIGHT) GEQ 1$',
        '${x+3} over{x-2} GEQ 2$이고 $x>2$이므로 양변에 $(x-2)$를 곱하면 $x+3 GEQ 2x-4$, $x LEQ 7$',
        '$x>2$와 결합하면 $2<x LEQ 7$',
        '두 부등식을 모두 만족하는 범위: $1<x<{7} over{2}$와 $2<x LEQ 7$의 교집합은 $2<x<{7} over{2}$',
        '이 범위의 자연수는',
        '$x=3$',
    ],
    ch='지수·로그 부등식의 연립', lv='상')

add(id='q20', kind='sub', no=3, score=7.0,
    text='$ pi< theta<{3} over{2} pi$인 $ theta$에 대하여 $ sin theta cos theta={2} over{5}$일 때, 다음 물음에 답하시오.',
    text2=[
        '3-1) $ tan theta+{1} over{ tan theta}$의 값을 구하고, 그 풀이과정을 논리적으로 서술하시오. [3.0점]',
        '3-2) ${ cos theta} over{1- sin^{2} theta}+{ sin theta} over{1- cos^{2} theta}$의 값을 구하고, 그 풀이과정을 논리적으로 서술하시오. [4.0점]',
    ],
    ans_mix='3-1) ${5} over{2}$. 3-2) $it-{3 sqrt{5}} over{2}$',
    sol=[
        '3-1) $ tan theta+{1} over{ tan theta}={ sin theta} over{ cos theta}+{ cos theta} over{ sin theta}={ sin^{2} theta+ cos^{2} theta} over{ sin theta cos theta}={1} over{ sin theta cos theta}={1} over{2/5}$',
        '$therefore$ 구하는 값은',
        '$={5} over{2}$',
        '3-2) $1- sin^{2} theta= cos^{2} theta$, $1- cos^{2} theta= sin^{2} theta$이므로 식은 ${ cos theta} over{ cos^{2} theta}+{ sin theta} over{ sin^{2} theta}={1} over{ cos theta}+{1} over{ sin theta}={ sin theta+ cos theta} over{ sin theta cos theta}$',
        '$( sin theta+ cos theta)^{2}=1+2 sin theta cos theta=1+{4} over{5}={9} over{5}$',
        '$ pi< theta<{3} over{2} pi$(제$3$사분면)이므로 $ sin theta<0$, $ cos theta<0$, 즉 $ sin theta+ cos theta<0$',
        '$ sin theta+ cos theta=it- sqrt{{9} over{5}}=it-{3} over{ sqrt{5}}=it-{3 sqrt{5}} over{5}$',
        '${ sin theta+ cos theta} over{ sin theta cos theta}={it-{3 sqrt{5}} over{5}} over{{2} over{5}}=it-{3 sqrt{5}} over{5} times{5} over{2}=it-{3 sqrt{5}} over{2}$',
        '$therefore$ 구하는 값은',
        '$=it-{3 sqrt{5}} over{2}$',
    ],
    ch='삼각함수 사이의 관계 종합', lv='상')
