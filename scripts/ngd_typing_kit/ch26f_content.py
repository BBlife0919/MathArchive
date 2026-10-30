# -*- coding: utf-8 -*-
"""충현고등학교 2학년 2026 1학기 기말 대수(삼각함수의 그래프~수학적귀납법) 19문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.5, layout='3+2',
    text='수열 $LEFT{2n-1 RIGHT}$의 제$6$항은?',
    choices=['$3$', '$5$', '$7$', '$9$', '$11$'],
    ans='⑤',
    sol=[
        '$a_{n}=2n-1$에서 $a_{6}=2 times6-1$',
        '$therefore~a_{6}$',
        '$=11$',
    ],
    ch='수열의 일반항', lv='하')

add(id='q02', kind='mc', no=2, score=4.6, layout='3+2',
    text='$ sum^{10}_{k=1}a_{k}=15$이고, $ sum^{10}_{k=1}b_{k}=10$일 때, $ sum^{10}_{k=1}(a_{k}+3b_{k})$의 값은?',
    choices=['$25$', '$30$', '$35$', '$40$', '$45$'],
    ans='⑤',
    sol=[
        '$ sum^{10}_{k=1}(a_{k}+3b_{k})= sum^{10}_{k=1}a_{k}+3 sum^{10}_{k=1}b_{k}$',
        '$=15+3 times10$',
        '$therefore$ 구하는 값은',
        '$45$',
    ],
    ch='시그마의 성질', lv='하')

add(id='q03', kind='mc', no=3, score=4.7, layout='3+2',
    text='삼각형 $ABC$에서 $bar{BC}=1$, $A=30 ^{ circ}$일 때, 삼각형 $ABC$의 외접원의 지름의 길이는?',
    choices=['${1} over{8}$', '${1} over{4}$', '${1} over{2}$', '$1$', '$2$'],
    ans='⑤',
    sol=[
        '사인법칙에 의하여 ${bar{BC}} over{ sin A}=2R$',
        '$2R={1} over{ sin30 ^{ circ}}={1} over{{1} over{2}}$',
        '$therefore$ 외접원의 지름은',
        '$2$',
    ],
    ch='사인법칙', lv='하')

add(id='q04', kind='mc', no=4, score=4.8, layout='3+2',
    text='삼각형 $ABC$에서 $bar{AB}=10$, $bar{AC}=12$, $A=45 ^{ circ}$일 때, 삼각형 $ABC$의 넓이는?',
    choices=['$30$', '$30 sqrt{2}$', '$30 sqrt{3}$', '$60$', '$120$'],
    ans='②',
    sol=[
        '삼각형의 넓이는 $S={1} over{2} times bar{AB} times bar{AC} times sin A$',
        '$={1} over{2} times10 times12 times sin45 ^{ circ}$',
        '$=60 times{ sqrt{2}} over{2}$',
        '$therefore~S$',
        '$=30 sqrt{2}$',
    ],
    ch='삼각형의 넓이', lv='하')

add(id='q05', kind='mc', no=5, score=4.8, layout='1x5',
    text='삼각형 $ABC$에서 $∠A$, $∠B$, $∠C$의 대변의 길이를 각각 $a,~b,~c$라 할 때, 항상 성립하는 식은?',
    choices=['$a^{2}=b^{2}+c^{2}-2bc cos A$', '$b^{2}=c^{2}+a^{2}+2ca cos B$', '$c^{2}=a^{2}-b^{2}-2ab cos C$',
             '$ cos B={b^{2}+c^{2}-a^{2}} over{2bc}$', '$ sin C={a^{2}+b^{2}-c^{2}} over{2ab}$'],
    ans='①',
    sol=[
        '코사인법칙의 올바른 형태는 $a^{2}=b^{2}+c^{2}-2bc cos A$이다.',
        '②는 부호가 틀렸고(마지막 항이 $-2ca cos B$이어야 함), ③도 부호가 틀렸다.',
        '④의 우변은 $ cos A$에 대한 식이지 $ cos B$에 대한 식이 아니며, ⑤와 같은 $ sin C$ 공식은 존재하지 않는다.',
        '$therefore$ 항상 성립하는 식은',
        '①',
    ],
    ch='코사인법칙', lv='하')

add(id='q06', kind='mc', no=6, score=4.9, layout='3+2',
    text='함수 $y= tan x$에 대한 설명으로 옳은 것만을 [보기]에서 있는 대로 고른 것은?',
    box=True,
    box_items=[
        '치역은 실수 전체의 집합이다.',
        '$y= tan x$의 그래프는 원점에 대하여 대칭이다.',
        '주기가 $2 pi$이다.',
        '$y= tan x$의 그래프의 점근선은 직선 $x=n pi+ pi/2$ ($n$은 정수)이다.',
    ],
    choices=['$ㄱ,~ㄴ$', '$ㄴ,~ㄷ$', '$ㄱ,~ㄴ,~ㄹ$', '$ㄱ,~ㄷ,~ㄹ$', '$ㄴ,~ㄷ,~ㄹ$'],
    ans='③',
    sol=[
        'ㄱ. $ tan x$는 모든 실수값을 가지므로 치역은 실수 전체의 집합이다. (참)',
        'ㄴ. $ tan(it-x)=it- tan x$이므로 기함수이고, 그래프는 원점 대칭이다. (참)',
        'ㄷ. $y= tan x$의 주기는 $ pi$이다 ($2 pi$가 아님). (거짓)',
        'ㄹ. $ tan x$는 $x=n pi+ pi/2$에서 정의되지 않으므로 이 직선들이 점근선이다. (참)',
        '$therefore$ 옳은 것은',
        'ㄱ,~ㄴ,~ㄹ',
    ],
    ch='탄젠트함수의 그래프', lv='중')

add(id='q07', kind='mc', no=7, score=4.9, layout='3+2',
    text='연이율이 $4$%이고 $1$년마다 복리로 매년 초에 $10$만원씩 $5$년 동안 적립할 때, $5$년 말까지 적립금의 원리합계는? (단, $1.04^{5}=1.2$로 계산한다.)',
    choices=['$52$만원', '$53$만원', '$54$만원', '$55$만원', '$56$만원'],
    ans='①',
    sol=[
        '매년 초에 적립하므로, 첫 번째 납입금은 $5$년간, 마지막 납입금은 $1$년간 복리로 불어난다.',
        '원리합계는 $10(1.04+1.04^{2}+ cdots+1.04^{5})$ (만원)',
        '$=10 times1.04 times{1.04^{5}-1} over{1.04-1}$',
        '$=10 times1.04 times{0.2} over{0.04}$',
        '$=10 times1.04 times5$',
        '$therefore$ 원리합계는',
        '$52$만원',
    ],
    ch='등비수열의 활용(연금의 원리합계)', lv='중')

add(id='q08', kind='mc', no=8, score=5.0, layout='1x5',
    text='다음은 모든 자연수 $n$에 대하여 등식',
    emptybox={'paras': [
        '$1^{2}+2^{2}+3^{2}+ cdots+n^{2}={n(n+1)(2n+1)} over{6}$ $ cdots cdots$①',
        '이 성립함을 수학적 귀납법으로 증명한 것이다.',
        'ⅰ) $n=1$일 때,',
        '(좌변)$=1^{2}=1$, (우변)$={1 times2 times3} over{6}=1$',
        '따라서, $n=1$일 때, ①이 성립한다.',
        'ⅱ) $n=k$일 때, ①이 성립한다고 가정하면',
        '$1^{2}+2^{2}+3^{2}+ cdots+k^{2}={k(k+1)(2k+1)} over{6}$',
        '$n=(가)$일 때,',
        '$1^{2}+2^{2}+3^{2}+ cdots+k^{2}+(k+1)^{2}$',
        '$={k(k+1)(2k+1)} over{6}+(k+1)^{2}$',
        '$={k+1} over{6}LEFT{k(2k+1)+6(k+1) RIGHT}$',
        '$={(k+1)(k+2)(나)} over{6}$',
        '따라서, $n=k+1$일 때도 ①이 성립한다.',
        'ⅰ)과 ⅱ)에 의하여 모든 자연수 $n$에 대하여 ①이 성립한다.',
    ]},
    text2='위의 $(가)$, $(나)$에 알맞은 식을 각각 $f(k)$, $g(k)$라 할 때, $f(1)+g(2)$의 값은?',
    choices=['$7$', '$8$', '$9$', '$10$', '$11$'],
    ans='③',
    sol=[
        '$k(2k+1)+6(k+1)=2k^{2}+k+6k+6=2k^{2}+7k+6=(k+2)(2k+3)$',
        '따라서 $(가)$는 $k+1$ (즉 $f(k)=k+1$), $(나)$는 $2k+3$ (즉 $g(k)=2k+3$)이다.',
        '$f(1)=1+1=2$, $g(2)=2 times2+3=7$',
        '$therefore~f(1)+g(2)=2+7$',
        '$=9$',
    ],
    ch='수학적 귀납법', lv='중')

add(id='q09', kind='mc', no=9, score=5.0, layout='3+2',
    text='$0 LEQ theta<2 pi$인 상수 $ theta$에 대하여 이차방정식 $x^{2}-2x tan theta+3=0$이 실근을 가지도록 하는 $ theta$의 값으로 될 수 있는 것은?',
    choices=['${1} over{4} pi$', '${1} over{2} pi$', '${5} over{6} pi$', '$ pi$', '${4} over{3} pi$'],
    ans='⑤',
    sol=[
        '이차방정식이 실근을 가지려면 판별식 $D GEQ 0$이어야 한다.',
        '$D/4=( tan theta)^{2}-3 GEQ 0$에서 $ tan^{2} theta GEQ 3$',
        '즉 $ tan theta GEQ sqrt{3}$ 또는 $ tan theta LEQ it- sqrt{3}$',
        '①${1} over{4} pi$: $ tan{ pi} over{4}=1$ (조건 미만족)',
        '③${5} over{6} pi$: $ tan{5} over{6} pi=it-{1} over{ sqrt{3}}$ (조건 미만족)',
        '④$ pi$: $ tan pi=0$ (조건 미만족)',
        '⑤${4} over{3} pi$: $ tan{4} over{3} pi= tan{1} over{3} pi= sqrt{3}$ (조건 만족, $ sqrt{3} GEQ sqrt{3}$)',
        '$therefore~ theta$의 값으로 될 수 있는 것은',
        '${4} over{3} pi$',
    ],
    ch='삼각방정식과 판별식', lv='상')

add(id='q10', kind='mc', no=10, score=5.0, layout='3+2',
    text='공차가 양수인 등차수열 ${a_{n}}$에 대하여 $a_{1}+a_{2}+a_{3}=24$이고, $a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=210$일 때, $a_{10}$의 값은?',
    choices=['$29$', '$32$', '$35$', '$38$', '$41$'],
    ans='②',
    sol=[
        '$a_{1}+a_{2}+a_{3}=3a_{2}=24$에서 $a_{2}=8$',
        '$a_{1}=8-d$, $a_{3}=8+d$ ($d$는 공차)라 하면',
        '$a_{1}^{2}+a_{2}^{2}+a_{3}^{2}=(8-d)^{2}+8^{2}+(8+d)^{2}=192+2d^{2}=210$',
        '$2d^{2}=18$에서 $d^{2}=9$',
        '공차가 양수이므로 $d=3$',
        '$a_{10}=a_{2}+8d=8+24$',
        '$therefore~a_{10}$',
        '$=32$',
    ],
    ch='등차수열과 제곱의 합', lv='중')

add(id='q11', kind='mc', no=11, score=5.1, layout='3+2',
    text='$1/(3^{2}-1)+1/(5^{2}-1)+1/(7^{2}-1)+ cdots+1/(25^{2}-1)=p/q$를 만족시키는 서로소인 자연수 $p,~q$에 대하여 $p+q$의 값은?',
    choices=['$10$', '$12$', '$14$', '$16$', '$18$'],
    ans='④',
    sol=[
        '${1} over{n^{2}-1}={1} over{(n-1)(n+1)}={1} over{2}LEFT({1} over{n-1}-{1} over{n+1} RIGHT)$',
        '$n=3,~5,~7,~ cdots,~25$ ($12$개 항)에 대하여 합을 구하면',
        '${1} over{2}LEFT[LEFT({1} over{2}-{1} over{4} RIGHT)+LEFT({1} over{4}-{1} over{6} RIGHT)+ cdots+LEFT({1} over{24}-{1} over{26} RIGHT) RIGHT]$',
        '$={1} over{2}LEFT({1} over{2}-{1} over{26} RIGHT)={1} over{2} times{6} over{13}$',
        '$={3} over{13}$',
        '$p=3$, $q=13$이고 서로소이므로',
        '$therefore~p+q=3+13$',
        '$=16$',
    ],
    ch='부분분수를 이용한 망원급수', lv='상')

add(id='q12', kind='mc', no=12, score=5.1, layout='3+2',
    text='함수 $y=a LEFT| cos bx RIGHT|$의 주기가 $2 pi$이고 최솟값이 $it-4$일 때, $a/b^{2}$의 값은? (단, $a,~b$는 $ab NEQ 0$인 상수이다.)',
    choices=['$it-16$', '$it-{1} over{16}$', '${1} over{16}$', '$8$', '$16$'],
    ans='①',
    sol=[
        '$ LEFT| cos bx RIGHT|$의 주기는 ${ pi} over{ LEFT|b RIGHT|}$이므로 ${ pi} over{ LEFT|b RIGHT|}=2 pi$에서 $ LEFT|b RIGHT|={1} over{2}$',
        '$b^{2}=LEFT({1} over{2} RIGHT)^{2}={1} over{4}$',
        '$ LEFT| cos bx RIGHT|$의 치역은 $LEFT[0,~1 RIGHT]$이므로 $y=a LEFT| cos bx RIGHT|$의 최솟값이 $it-4$이려면 $a<0$이고 최솟값$=a times1=a$',
        '$a=it-4$',
        '$therefore~{a} over{b^{2}}={it-4} over{{1} over{4}}$',
        '$=it-16$',
    ],
    ch='삼각함수의 그래프와 주기', lv='중')

add(id='q13', kind='mc', no=13, score=5.2, layout='3+2',
    text='$a_{1}=4$, $a_{6}=128$인 수열 ${a_{n}}$이 있다. 이차방정식 $a_{n}x^{2}-2a_{n+1}x+a_{n+2}=0$이 중근을 가질 때, $ sum^{m}_{k=1} log_{2}a_{k}=170$을 만족하는 자연수 $m$의 값은?',
    choices=['$13$', '$15$', '$17$', '$19$', '$20$'],
    ans='③',
    sol=[
        '이차방정식이 모든 $n$에 대하여 중근을 가지므로 판별식 $4a_{n+1}^{2}-4a_{n}a_{n+2}=0$에서 $a_{n+1}^{2}=a_{n}a_{n+2}$',
        '이는 ${a_{n}}$이 등비수열임을 뜻한다. 공비를 $r$이라 하면 $a_{6}=a_{1}r^{5}$에서 $128=4r^{5}$, $r^{5}=32$이므로 $r=2$',
        '$a_{n}=4 times2^{n-1}=2^{n+1}$',
        '$ log_{2}a_{k}= log_{2}2^{k+1}=k+1$',
        '$ sum^{m}_{k=1}(k+1)={m(m+1)} over{2}+m={m(m+3)} over{2}=170$',
        '$m(m+3)=340$에서 $m^{2}+3m-340=0$',
        '$(m-17)(m+20)=0$이고 $m$은 자연수이므로',
        '$therefore~m$',
        '$=17$',
    ],
    ch='등비수열과 수학적 귀납법적 추론', lv='상')

add(id='q14', kind='mc', no=14, score=5.2, layout='3+2',
    text='서로 다른 두 실수 $a,~b$에 대하여 세 수 $2a^{2}$, $it-b$, $it-4$가 이 순서대로 등차수열을 이루고, 세 수 $1$, $it-b$, $2-a$는 이 순서대로 등비수열을 이룰 때, $a+b$의 값은?',
    choices=['$-4$', '$-1$', '$0$', '$1$', '$2$'],
    ans='④',
    sol=[
        '등차수열 조건: $2(it-b)=2a^{2}+(it-4)$에서 $it-2b=2a^{2}-4$, 즉 $b=2-a^{2}$ ㉠',
        '등비수열 조건: $(it-b)^{2}=1 times(2-a)$, 즉 $b^{2}=2-a$ ㉡',
        '㉠을 ㉡에 대입: $(2-a^{2})^{2}=2-a$에서 $4-4a^{2}+a^{4}=2-a$',
        '$a^{4}-4a^{2}+a+2=0$',
        '$a=1$을 대입하면 $1-4+1+2=0$이므로 $(a-1)$이 인수',
        '조립제법으로 나누면 $a^{4}-4a^{2}+a+2=(a-1)(a^{3}+a^{2}-3a-2)$',
        '$a=it-2$를 대입하면 $it-8+4+6-2=0$이므로 $(a+2)$도 인수',
        '$a^{3}+a^{2}-3a-2=(a+2)(a^{2}-a-1)$',
        '따라서 $(a-1)(a+2)(a^{2}-a-1)=0$',
        '$a=1$이면 $b=2-1=1=a$ (서로 다른 두 실수 조건에 위배되어 제외)',
        '$a=it-2$이면 $b=2-4=it-2=a$ (마찬가지로 제외)',
        '$a^{2}-a-1=0$인 경우: $a^{2}=a+1$이므로 ㉠에서 $b=2-a^{2}=2-(a+1)=1-a$',
        '즉 $a+b=a+(1-a)$',
        '$=1$',
    ],
    ch='등차수열·등비수열의 혼합 추론', lv='상')

add(id='q15', kind='mc', no=15, score=5.3, layout='3+2',
    text='자연수 $n$에 대하여 좌표평면 위에 $4$개의 점 $(n^{2},~n)$, $(n^{2},~2n)$, $(2n^{2},~2n)$, $(2n^{2},~n)$이 있다. 이 $4$개의 점을 꼭짓점으로 하는 직사각형을 $A_{n}$이라 하고, 직사각형 $A_{n}$과 함수 $y=LEFT(1/m RIGHT)x$의 그래프가 만나도록 하는 자연수 $m$의 개수를 $a_{n}$이라 하자. 이때, 옳은 것만을 [보기]에서 있는 대로 고른 것은?',
    fig='ch26f_q15',
    box=True,
    box_items=[
        '$a_{4}=7$',
        '$a_{n+1}-a_{n}=2$',
        '$ sum^{20}_{k=1}a_{k}=330$',
    ],
    choices=['$ㄱ$', '$ㄱ,~ㄴ$', '$ㄱ,~ㄷ$', '$ㄴ,~ㄷ$', '$ㄱ,~ㄴ,~ㄷ$'],
    ans='③',
    sol=[
        '직사각형 $A_{n}$은 $n^{2} LEQ x LEQ 2n^{2}$, $n LEQ y LEQ 2n$ 범위이다.',
        '직선 $y={x} over{m}$이 이 직사각형과 만나려면, $x$가 $LEFT[n^{2},~2n^{2} RIGHT]$를 지날 때 $y={x} over{m}$의 값이 $LEFT[n,~2n RIGHT]$과 겹쳐야 한다.',
        '이는 구간 $LEFT[mn,~2mn RIGHT]$과 $LEFT[n^{2},~2n^{2} RIGHT]$이 겹치는 것과 같고, 정리하면 ${n} over{2} LEQ m LEQ 2n$',
        '$a_{n}$은 이 범위의 자연수 $m$의 개수이다.',
        '$n=4$일 때 $2 LEQ m LEQ 8$이므로 $a_{4}=7$ (ㄱ 참)',
        '$n$이 짝수($n=2j$)일 때 $a_{n}=3j+1$, $n$이 홀수($n=2j+1$)일 때 $a_{n}=3j+2$ (직접 계산으로 확인됨)',
        '$a_{1}=2,~a_{2}=4,~a_{3}=5,~a_{4}=7,~a_{5}=8,~a_{6}=10, cdots$ 이므로 차이는 $2,1,2,1,2, cdots$로 번갈아 나타나며 항상 $2$는 아니다 (ㄴ 거짓)',
        '$a_{1}$부터 $a_{20}$까지 직접 나열하여 더하면 $2+4+5+7+8+10+11+13+14+16+17+19+20+22+23+25+26+28+29+31=330$ (ㄷ 참)',
        '$therefore$ 옳은 것은',
        'ㄱ,~ㄷ',
    ],
    ch='수열의 귀납적 정의와 그래프', lv='최상')

add(id='q16', kind='mc', no=16, score=5.4, layout='1x5',
    text='$bar{DA}=2 bar{AB}$, $∠DAB= pi/3$이고 반지름의 길이가 $1$인 원에 내접하는 사각형 $ABCD$가 있다. 두 삼각형 $ACB$와 $ACD$의 넓이를 각각 $S_{1},~S_{2}$라 할 때, $S_{1}:S_{2}=1:4$이다. 사각형 $ABCD$의 넓이가 $LEFT(q/p RIGHT) sqrt{3}$일 때, $p+q$의 값은? (단, $p$와 $q$는 서로소인 자연수이다.)',
    fig='ch26f_q16',
    choices=['$11$', '$12$', '$13$', '$14$', '$15$'],
    ans='②',
    sol=[
        '원의 반지름 $R=1$이고, 대각선 $BD$는 $∠DAB$에 대한 원주각이 만드는 현이므로 사인법칙에 의하여 $bar{BD}=2R sin(∠DAB)=2 sin60 ^{ circ}$',
        '$= sqrt{3}$',
        '$bar{AB}=x$라 하면 $bar{AD}=2x$. 삼각형 $ABD$에서 코사인법칙: $bar{BD}^{2}=bar{AB}^{2}+bar{AD}^{2}-2 times bar{AB} times bar{AD} times cos60 ^{ circ}$',
        '$3=x^{2}+4x^{2}-2x(2x)LEFT({1} over{2} RIGHT)=5x^{2}-2x^{2}$',
        '$3=3x^{2}$에서 $x=1$이므로 $bar{AB}=1$, $bar{AD}=2$',
        '$∠BAC= beta$, $∠DAC= alpha$라 하면 $ alpha+ beta={ pi} over{3}$이고',
        '$S_{1}:S_{2}=LEFT({1} over{2} bar{AB} times bar{AC} sin beta RIGHT):LEFT({1} over{2} bar{AD} times bar{AC} sin alpha RIGHT)=( sin beta):(2 sin alpha)=1:4$',
        '$ sin beta={1} over{2} sin alpha$이고 $ beta={ pi} over{3}- alpha$이므로 $ sinLEFT({ pi} over{3}- alpha RIGHT)={1} over{2} sin alpha$',
        '전개: ${ sqrt{3}} over{2} cos alpha-{1} over{2} sin alpha={1} over{2} sin alpha$에서 ${ sqrt{3}} over{2} cos alpha= sin alpha$, 즉 $ tan alpha={ sqrt{3}} over{2}$',
        '직각삼각형비로 $ sin alpha={ sqrt{3}} over{ sqrt{7}}$, $ cos alpha={2} over{ sqrt{7}}$',
        '삼각형 $ACD$, $ACB$ 모두 같은 원(반지름 $1$) 위의 세 점으로 이루어지므로 사인법칙의 $2R=2$가 각각에 그대로 적용된다.',
        '$bar{AD}/ sin(∠ACD)=2$에서 $ sin(∠ACD)=bar{AD}/2=1$이므로 $∠ACD=90 ^{ circ}$',
        '삼각형 $ACD$에서 $∠ADC=90 ^{ circ}- alpha$이고, $bar{AC}=2 sin(∠ADC)=2 cos alpha=2 times{2} over{ sqrt{7}}$',
        '$={4} over{ sqrt{7}}$',
        '$S_{1}={1} over{2} times bar{AB} times bar{AC} times sin beta={1} over{2} times1 times{4} over{ sqrt{7}} times{ sqrt{3}} over{2 sqrt{7}}$',
        '$={ sqrt{3}} over{7}$',
        '$S_{2}={1} over{2} times bar{AD} times bar{AC} times sin alpha={1} over{2} times2 times{4} over{ sqrt{7}} times{ sqrt{3}} over{ sqrt{7}}$',
        '$={4 sqrt{3}} over{7}$',
        '사각형 $ABCD$의 넓이$=S_{1}+S_{2}={ sqrt{3}} over{7}+{4 sqrt{3}} over{7}={5 sqrt{3}} over{7}$',
        '즉 ${q} over{p}={5} over{7}$이고 $p,~q$가 서로소이므로 $p=7$, $q=5$',
        '$therefore~p+q=7+5$',
        '$=12$',
    ],
    ch='원에 내접하는 사각형과 넓이의 비', lv='최상')

add(id='q17', kind='mc', no=17, score=5.5, layout='3+2',
    text='양의 실수에서 정의된 함수 $f(x)$를 $f(x)= cases{2 sin pi x~~(0<x<k)#2^{x-k}-1~~(x GEQ k)}$라 하자. 방정식 $f(x)=1$의 모든 실근의 합이 $300$일 때, 자연수 $k$의 값은?',
    choices=['$19$', '$20$', '$21$', '$23$', '$24$'],
    ans='④',
    sol=[
        '$0<x<k$ 구간: $2 sin pi x=1$에서 $ sin pi x={1} over{2}$이므로 $x=2n+{1} over{6}$ 또는 $x=2n+{5} over{6}$ ($n=0,1,2, cdots$)',
        '$x GEQ k$ 구간: $2^{x-k}-1=1$에서 $2^{x-k}=2$이므로 $x-k=1$, 즉 $x=k+1$ (유일한 근)',
        '$k$가 홀수, $k=2M+1$ ($M$은 $0$ 이상의 정수)인 경우로 확인한다. $0<x<k$에서 두 근 $2n+{1} over{6}$, $2n+{5} over{6}$이 함께 포함되는 범위는 $n=0,1, cdots,M$ (총 $M+1$쌍)이다.',
        '첫째 구간 근들의 합은 $ sum^{M}_{n=0}LEFT[(2n+{1} over{6})+(2n+{5} over{6}) RIGHT]= sum^{M}_{n=0}(4n+1)=2M(M+1)+(M+1)=(M+1)(2M+1)$',
        '전체 근의 합$=(M+1)(2M+1)+(k+1)=(M+1)(2M+1)+(2M+2)=(M+1)(2M+3)$',
        '$(M+1)(2M+3)=300$을 만족하는 자연수 $M$을 찾으면 $M=11$일 때 $12 times25=300$',
        '$therefore~k=2M+1=2 times11+1$',
        '$=23$',
    ],
    ch='삼각방정식과 지수방정식의 실근의 합', lv='최상')

add(id='q18', kind='sub', no=1, score=7.0, layout='1x5',
    text='함수 $y=2 cos pi x$의 그래프와 직선 $y=1$의 교점을 이용하여 방정식 $2 cos pi x=1$의 해를 구하려고 한다. 물음에 답하시오.',
    text2=[
        '(1) 함수 $y=2 cos pi x$의 치역과 주기를 구하시오. [2.0점]',
        '(2) $0 LEQ x<3$일 때, 방정식 $2 cos pi x=1$의 해를 구하고, 그 과정을 서술하시오. [5.0점]',
    ],
    ans_mix='(1) 치역: $LEFT[it-2,~2 RIGHT]$, 주기: $2$ (2) $x={1} over{3},~{5} over{3},~{7} over{3}$',
    sol=[
        '(1) $ cos pi x$의 치역은 $LEFT[it-1,~1 RIGHT]$이므로 $y=2 cos pi x$의 치역은 $2 times LEFT[it-1,~1 RIGHT]=LEFT[it-2,~2 RIGHT]$이다.',
        '주기는 ${2 pi} over{ pi}$',
        '$=2$',
        '(2) $2 cos pi x=1$에서 $ cos pi x={1} over{2}$',
        '일반해: $ pi x=2n pi pm{ pi} over{3}$ ($n$은 정수), 즉 $x=2n pm{1} over{3}$',
        '$0 LEQ x<3$에서 $n=0$: $x={1} over{3}$ (음의 해 $it-{1} over{3}$는 범위 밖)',
        '$n=1$: $x=2+{1} over{3}={7} over{3}$, 또는 $x=2-{1} over{3}={5} over{3}$',
        '$n=2$: $x=4 pm{1} over{3}$은 모두 $3$ 이상이므로 제외',
        '$therefore$ 방정식의 해는',
        '$x={1} over{3},~{5} over{3},~{7} over{3}$',
    ],
    ch='삼각함수의 그래프와 삼각방정식', lv='중')

add(id='q19', kind='sub', no=2, score=8.0, layout='1x5',
    text='수열 ${a_{n}}$에서 제$1$항부터 제$n$항까지의 합 $S_{n}$에 대하여 $S_{n}=2n^{2}+3$인 수열의 일반항을 구하고, 이를 이용하여 $ sum^{10}_{k=1}ka_{2k}$의 값을 구하려고 한다. 물음에 답하시오.',
    text2=[
        '(1) 수열 ${a_{n}}$의 제$1$항 $a_{1}$의 값을 구하시오. [1.0점]',
        '(2) $n GEQ 2$일 때, 수열 ${a_{n}}$의 일반항을 구하고, 그 과정을 서술하시오. [2.0점]',
        '(3) $ sum$의 성질과 자연수의 거듭제곱의 합을 이용하여 $ sum^{10}_{k=1}ka_{2k}$의 값을 구하고, 그 과정을 서술하시오. [5.0점]',
    ],
    ans_mix='(1) $a_{1}=5$ (2) $a_{n}=4n-2$ ($n GEQ 2$) (3) $ sum^{10}_{k=1}ka_{2k}=2970$',
    sol=[
        '(1) $a_{1}=S_{1}=2(1)^{2}+3=2+3$',
        '$=5$',
        '(2) $n GEQ 2$일 때 $a_{n}=S_{n}-S_{n-1}=(2n^{2}+3)-(2(n-1)^{2}+3)=2LEFT{n^{2}-(n-1)^{2} RIGHT}$',
        '$=2(2n-1)$',
        '$therefore~a_{n}$',
        '$=4n-2$',
        '(3) $2k GEQ 2$이므로 모든 $k=1, cdots,10$에 대하여 $a_{2k}=4(2k)-2=8k-2$를 사용할 수 있다.',
        '$ sum^{10}_{k=1}ka_{2k}= sum^{10}_{k=1}k(8k-2)= sum^{10}_{k=1}(8k^{2}-2k)=8 sum^{10}_{k=1}k^{2}-2 sum^{10}_{k=1}k$',
        '$ sum^{10}_{k=1}k^{2}={10 times11 times21} over{6}=385$, $ sum^{10}_{k=1}k={10 times11} over{2}=55$',
        '$=8 times385-2 times55$',
        '$=3080-110$',
        '$therefore sum^{10}_{k=1}ka_{2k}$',
        '$=2970$',
    ],
    ch='수열의 합과 일반항, 시그마 계산', lv='상')
