# -*- coding: utf-8 -*-
"""운산고등학교 2학년 2026 1학기 기말 대수(삼각함수의 그래프~수열의 귀납적정의) 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='sub', no=1, score=5.0, layout='1x5',
    text='$0<x LEQ 2 pi$일 때, 방정식 $ cos^{2}x- sin^{2}x=it- cos x$의 모든 해를 구하고 그 과정을 자세히 서술하시오.',
    ans_mix='$x={ pi} over{3},~ pi,~{5} over{3} pi$',
    sol=[
        '$ cos^{2}x- sin^{2}x= cos^{2}x-(1- cos^{2}x)=2 cos^{2}x-1$이므로 방정식은 $2 cos^{2}x-1=it- cos x$',
        '$t= cos x$라 하면 $2t^{2}+t-1=0$에서 $(2t-1)(t+1)=0$이므로 $t={1} over{2}$ 또는 $t=it-1$',
        '$ cos x={1} over{2}$이고 $0<x LEQ 2 pi$이므로 $x={ pi} over{3}$ 또는 $x={5} over{3} pi$',
        '$ cos x=it-1$이고 $0<x LEQ 2 pi$이므로 $x= pi$',
        '$therefore$ 모든 해는',
        '$=x={ pi} over{3},~ pi,~{5} over{3} pi$',
    ],
    ch='삼각방정식', lv='중')

add(id='q02', kind='sub', no=2, score=7.0, layout='1x5', fig='us26f_q02',
    text=[
        '그림과 같이 삼각형 $ABC$에서 선분 $BC$ 위의 점 $D$는 $∠BAD=∠DAC$를 만족시킨다.',
        '$bar{AB}=6$, $bar{AD}=4$, $ cos(∠BAD)=7/12$일 때, 다음 물음에 답하시오. (단 $bar{AB}<bar{AC}$)',
    ],
    text2=['(1) 선분 $BD$의 길이를 구하고, 그 과정을 자세히 서술하시오. [3.0점]',
           '(2) 선분 $AC$의 길이를 구하고 그 과정을 자세히 서술하시오. [4.0점]'],
    ans_mix='(1) $bar{BD}=2 sqrt{6}$ (2) $bar{AC}=8$',
    sol=[
        '(1) 삼각형 $ABD$에서 코사인법칙: $bar{BD}^{2}=bar{AB}^{2}+bar{AD}^{2}-2 times bar{AB} times bar{AD} times cos(∠BAD)$',
        '$=36+16-2 times6 times4 times{7} over{12}=52-28=24$',
        '$therefore~bar{BD}= sqrt{24}$',
        '$=2 sqrt{6}$',
        '(2) $AD$는 $∠A$의 이등분선이므로 각의 이등분선 길이 공식 $bar{AD}={2 times bar{AB} times bar{AC} times cos(∠BAD)} over{bar{AB}+bar{AC}}$를 이용한다.',
        '$bar{AC}=b$라 하면 $4={2 times6 times b times{7} over{12}} over{6+b}={7b} over{6+b}$',
        '$4(6+b)=7b$에서 $24+4b=7b$, $24=3b$',
        '$therefore~bar{AC}$',
        '$=8$',
    ],
    ch='코사인법칙과 각의 이등분선', lv='상')

add(id='q03', kind='sub', no=3, score=8.0, layout='1x5',
    text='수열 ${a_{n}}$의 첫째항부터 제$n$항까지의 합을 $S_{n}$이라 할 때, $S_{n}=2n^{2}+n+1$을 만족한다. 다음 물음에 답하시오.',
    text2=['3-1) 수열 ${a_{n}}$의 일반항을 구하고, 그 과정을 자세히 서술하시오. [3.0점]',
           '3-2) $ sum^{15}_{n=1}{4} over{a_{n}a_{n+1}}$의 값을 구하고, 그 과정을 자세히 서술하시오. [5.0점]'],
    ans_mix='3-1) $a_{1}=4$, $a_{n}=4n-1$($n GEQ 2$) 3-2) ${17} over{63}$',
    sol=[
        '3-1) $a_{1}=S_{1}=2+1+1=4$',
        '$n GEQ 2$일 때 $a_{n}=S_{n}-S_{n-1}=(2n^{2}+n+1)-LEFT{2(n-1)^{2}+(n-1)+1 RIGHT}=(2n^{2}+n+1)-(2n^{2}-3n+2)=4n-1$',
        '$a_{1}=4$는 이 식에 $n=1$을 대입한 $3$과 다르므로 $n=1$은 따로 구분한다.',
        '$therefore~a_{n}$',
        '$=a_{1}=4,~a_{n}=4n-1 (n GEQ 2)$',
        '3-2) $n=1$: $a_{1}=4$, $a_{2}=4(2)-1=7$이므로 ${4} over{a_{1}a_{2}}={4} over{28}={1} over{7}$',
        '$n GEQ 2$: ${4} over{a_{n}a_{n+1}}={4} over{(4n-1)(4n+3)}={1} over{4n-1}-{1} over{4n+3}$ (부분분수)',
        '$ sum^{15}_{n=2}LEFT({1} over{4n-1}-{1} over{4n+3} RIGHT)$는 망원급수로 ${1} over{7}-{1} over{63}$',
        '$therefore$ 구하는 값은 ${1} over{7}+LEFT({1} over{7}-{1} over{63} RIGHT)={2} over{7}-{1} over{63}={18} over{63}-{1} over{63}$',
        '$={17} over{63}$',
    ],
    ch='수열의 합과 일반항, 부분분수', lv='상')

add(id='q04', kind='mc', no=4, score=4.0, layout='3+2',
    text='$a_{2}=3/2$, $a_{3}=3$인 등비수열 ${a_{n}}$의 공비는?',
    choices=['${1} over{4}$', '${1} over{2}$', '$1$', '$2$', '$4$'],
    ans='④',
    sol=[
        '$r={a_{3}} over{a_{2}}=3 div{3} over{2}=3 times{2} over{3}$',
        '$therefore~r$',
        '$=2$',
    ],
    ch='등비수열의 공비', lv='하')

add(id='q05', kind='mc', no=5, score=4.0, layout='3+2',
    text='수열 ${a_{n}}$은 $a_{1}=1$이고, 모든 자연수 $n$에 대하여 $a_{n+1}=a_{n}+2$를 만족시킨다. $a_{4}$의 값은?',
    choices=['$5$', '$6$', '$7$', '$8$', '$9$'],
    ans='③',
    sol=[
        '$a_{n}$은 첫째항 $1$, 공차 $2$인 등차수열이므로 $a_{n}=1+(n-1) times2=2n-1$',
        '$therefore~a_{4}=2(4)-1$',
        '$=7$',
    ],
    ch='수열의 귀납적 정의', lv='하')

add(id='q06', kind='mc', no=6, score=4.1, layout='3+2',
    text='$ tan LEFT( pi/2+ pi/6 RIGHT) sin LEFT( pi/2- pi/3 RIGHT)$의 값은?',
    choices=['$it-{ sqrt{3}} over{2}$', '$it-{ sqrt{3}} over{6}$', '${1} over{2}$', '${ sqrt{3}} over{6}$', '${ sqrt{3}} over{2}$'],
    ans='①',
    sol=[
        '$ tan LEFT({ pi} over{2}+{ pi} over{6} RIGHT)=it- cot LEFT({ pi} over{6} RIGHT)=it- sqrt{3}$',
        '$ sin LEFT({ pi} over{2}-{ pi} over{3} RIGHT)= cos LEFT({ pi} over{3} RIGHT)={1} over{2}$',
        '$therefore$ 구하는 값은 $(it- sqrt{3}) times{1} over{2}$',
        '$=it-{ sqrt{3}} over{2}$',
    ],
    ch='삼각함수의 성질', lv='하')

add(id='q07', kind='mc', no=7, score=4.2, layout='3+2',
    text='네 수 $a,~4,~b,~20$이 이 순서대로 등차수열을 이룰 때, $it-a+b$의 값은?',
    choices=['$15$', '$16$', '$17$', '$18$', '$19$'],
    ans='②',
    sol=[
        '공차를 $d$라 하면 $4=a+d$, $b=4+d=a+2d$, $20=a+3d$',
        '$20-4=2d$에서 $d=8$',
        '$a=4-d=4-8=it-4$, $b=4+d=12$',
        '$therefore~it-a+b=4+12$',
        '$=16$',
    ],
    ch='등차수열', lv='하')

add(id='q08', kind='mc', no=8, score=4.3, layout='1x5',
    text='두 수열 ${a_{n}},~{b_{n}}$에 대하여 $ sum^{10}_{n=1}a_{n}=10$, $ sum^{10}_{n=1}b_{n}=5$일 때, $ sum^{10}_{n=1}(a_{n}+2b_{n}+1)$의 값은?',
    choices=['$18$', '$21$', '$24$', '$27$', '$30$'],
    ans='⑤',
    sol=[
        '$ sum^{10}_{n=1}(a_{n}+2b_{n}+1)= sum^{10}_{n=1}a_{n}+2 sum^{10}_{n=1}b_{n}+10 times1=10+2(5)+10$',
        '$therefore$ 구하는 값은',
        '$=30$',
    ],
    ch='수열의 합의 성질', lv='하')

add(id='q09', kind='mc', no=9, score=4.4, layout='1x5',
    text='$ cos( pi- theta)=1/5$이고 $ tan theta<0$일 때, $ sin theta$의 값은?',
    choices=['$it-{2 sqrt{6}} over{5}$', '$it-{4} over{5}$', '${ sqrt{6}} over{5}$', '${4} over{5}$', '${2 sqrt{6}} over{5}$'],
    ans='⑤',
    sol=[
        '$ cos( pi- theta)=it- cos theta={1} over{5}$에서 $ cos theta=it-{1} over{5}$',
        '$ cos theta<0$이고 $ tan theta<0$이므로 $ sin theta>0$ (제$2$사분면)',
        '$ sin theta= sqrt{1- cos^{2} theta}= sqrt{1-{1} over{25}}= sqrt{{24} over{25}}$',
        '$therefore~ sin theta$',
        '$={2 sqrt{6}} over{5}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q10', kind='mc', no=10, score=4.5, layout='1x5', fig='us26f_q10',
    text='그림과 같이 $bar{AB}=8 sqrt{2}$이고 $∠B=60^{ circ}$, $∠C=45^{ circ}$인 삼각형 $ABC$에서 선분 $AC$의 길이는?',
    choices=['$6 sqrt{3}$', '$7 sqrt{3}$', '$8 sqrt{3}$', '$9 sqrt{3}$', '$10 sqrt{3}$'],
    ans='③',
    sol=[
        '사인법칙: ${bar{AC}} over{ sin B}={bar{AB}} over{ sin C}$이므로 $bar{AC}=bar{AB} times{ sin B} over{ sin C}=8 sqrt{2} times{ sin60^{ circ}} over{ sin45^{ circ}}$',
        '$=8 sqrt{2} times{{ sqrt{3}} over{2}} over{{ sqrt{2}} over{2}}=8 sqrt{2} times{ sqrt{3}} over{ sqrt{2}}$',
        '$therefore~bar{AC}$',
        '$=8 sqrt{3}$',
    ],
    ch='사인법칙', lv='중')

add(id='q11', kind='mc', no=11, score=4.6, layout='1x5',
    text='$0<x LEQ pi$에서 부등식 $ tan x- sqrt{3} LEQ 0$의 해가 $0<x LEQ alpha$ 또는 $ beta<x LEQ pi$일 때, $ alpha+ beta$의 값은?',
    choices=['${7} over{12} pi$', '${2} over{3} pi$', '${3} over{4} pi$', '${5} over{6} pi$', '${11} over{12} pi$'],
    ans='④',
    sol=[
        '$ tan x LEQ sqrt{3}$. $0<x<{ pi} over{2}$에서 $ tan x$는 $0$에서 $+ infty$로 증가하므로 $ tan x LEQ sqrt{3}$은 $0<x LEQ{ pi} over{3}$에서 성립($ tan{ pi} over{3}= sqrt{3}$)',
        '$x={ pi} over{2}$에서는 정의되지 않으므로 제외.',
        '${ pi} over{2}<x LEQ pi$에서 $ tan x$는 음수이므로 항상 $ sqrt{3}$보다 작아 부등식이 항상 성립.',
        '따라서 해는 $0<x LEQ{ pi} over{3}$ 또는 ${ pi} over{2}<x LEQ pi$이므로 $ alpha={ pi} over{3}$, $ beta={ pi} over{2}$',
        '$therefore~ alpha+ beta={ pi} over{3}+{ pi} over{2}={2 pi} over{6}+{3 pi} over{6}$',
        '$={5} over{6} pi$',
    ],
    ch='삼각부등식', lv='중')

add(id='q12', kind='mc', no=12, score=4.7, layout='1x5',
    text=[
        '인플레이션은 재화와 서비스의 전반적인 가격 수준이 지속적으로 상승하여 화폐 가치가 하락하는 현상을 말한다. 어느 국가의 물가가 매년 $2$%씩 일정하게 상승한다고 하자. 현재 가격이 $5000$원인 어떤 제품의 가격이 인플레이션으로 인해 처음으로 $6000$원을 초과하는 시점을 아래의 표를 이용하여 구한 것은?',
    ],
    box=True,
    box_items=[
        '$n=7$일 때 $(1.02)^{n}=1.149$',
        '$n=8$일 때 $(1.02)^{n}=1.172$',
        '$n=9$일 때 $(1.02)^{n}=1.195$',
        '$n=10$일 때 $(1.02)^{n}=1.219$',
        '$n=11$일 때 $(1.02)^{n}=1.243$',
    ],
    choices=['$7$년후', '$8$년후', '$9$년후', '$10$년후', '$11$년후'],
    ans='④',
    sol=[
        '$n$년 후 가격은 $5000(1.02)^{n}$이므로 $5000(1.02)^{n}>6000$에서 $(1.02)^{n}>1.2$',
        '표에서 $n=9$: $1.195<1.2$, $n=10$: $1.219>1.2$',
        '따라서 처음으로 초과하는 시점은',
        '$=10$년후',
    ],
    ch='등비수열의 활용', lv='중')

add(id='q13', kind='mc', no=13, score=4.8, layout='1x5', fig='us26f_q13',
    text=[
        '다음은 어느 지역에서 하루 동안 관측한 시간에 따른 해수면의 높이를 그래프로 나타낸 것이다.',
        '시간을 $t$축, 해수면의 높이를 $y$축으로 하여 위 그래프가 나타내는 함수의 식을 $y=a sin LEFT( pi/b(t-6) RIGHT)+120+a$ ($a,~b$는 자연수)라 할 때, $a/(10b)$의 값은?',
    ],
    choices=['$2$', '$4$', '$6$', '$8$', '$10$'],
    ans='②',
    sol=[
        '그래프에서 최댓값 $600$은 $t=9,~21$에서, 최솟값 $120$은 $t=3,~15$에서 나타나므로 주기는 $12$이다.',
        '주기 $={2 pi} over{{ pi} over{b}}=2b=12$에서 $b=6$',
        '최댓값 $=a+120+a=2a+120=600$에서 $a=240$',
        '$therefore~{a} over{10b}={240} over{60}$',
        '$=4$',
    ],
    ch='삼각함수의 그래프의 활용', lv='중')

add(id='q14', kind='mc', no=14, score=4.9, layout='1x5',
    text='첫째항이 양수인 등차수열 ${a_{n}}$에 대하여 $S_{6}=S_{7}$이 성립한다. $a_{8}=it-3$일 때, 수열 ${a_{n}}$의 첫째항부터 제$10$항까지의 합은?',
    choices=['$33$', '$45$', '$54$', '$60$', '$63$'],
    ans='②',
    sol=[
        '$S_{6}=S_{7}$에서 $a_{7}=S_{7}-S_{6}=0$',
        '$a_{8}-a_{7}=d$이므로 $d=it-3-0=it-3$',
        '$a_{7}=a_{1}+6d=0$에서 $a_{1}=it-6d=it-6(it-3)=18$',
        '$S_{10}={10} over{2}LEFT{2a_{1}+9d RIGHT}=5LEFT{36+9(it-3) RIGHT}=5(36-27)$',
        '$therefore~S_{10}$',
        '$=45$',
    ],
    ch='등차수열의 합', lv='중')

add(id='q15', kind='mc', no=15, score=5.0, layout='1x5',
    text='두 함수 $f(x)= log_{3}x$와 $g(x)=3^{x^{2}-2x}$에 대하여 수열 ${a_{n}}$의 일반항을 두 함수의 합성함수인 $a_{n}=(f~ circ~g)(n)$으로 정의할 때, $ sum^{10}_{k=1}a_{k}$의 값은?',
    choices=['$275$', '$330$', '$385$', '$440$', '$495$'],
    ans='①',
    sol=[
        '$a_{n}=f(g(n))= log_{3}LEFT(3^{n^{2}-2n} RIGHT)=n^{2}-2n$',
        '$ sum^{10}_{k=1}a_{k}= sum^{10}_{k=1}(k^{2}-2k)= sum^{10}_{k=1}k^{2}-2 sum^{10}_{k=1}k={10 times11 times21} over{6}-2(55)=385-110$',
        '$therefore$ 구하는 값은',
        '$=275$',
    ],
    ch='합성함수와 수열의 합', lv='중')

add(id='q16', kind='mc', no=16, score=5.1, layout='1x5',
    text='반지름의 길이가 $16$인 원에 내접하는 삼각형 $ABC$가 있다. 삼각형 $ABC$의 세 변의 길이 $a,~b,~c$에 대하여 $a+2b-2c=0$, $4a-4b+c=0$이 성립할 때, 삼각형 $ABC$의 넓이는? (단, $bar{BC}=a$, $bar{CA}=b$, $bar{AB}=c$)',
    choices=['$25 sqrt{15}$', '$30 sqrt{15}$', '$35 sqrt{15}$', '$40 sqrt{15}$', '$45 sqrt{15}$'],
    ans='⑤',
    sol=[
        '$a=2c-2b$를 $4a-4b+c=0$에 대입: $4(2c-2b)-4b+c=0$에서 $9c-12b=0$, $c={4} over{3}b$',
        '$a=2c-2b=2LEFT({4} over{3}b RIGHT)-2b={8} over{3}b-{6} over{3}b={2} over{3}b$',
        '$a:b:c={2} over{3}:1:{4} over{3}=2:3:4$이므로 $a=2k,~b=3k,~c=4k$로 둔다.',
        '$c$(가장 긴 변)의 대각 $C$에 대해 $ cos C={a^{2}+b^{2}-c^{2}} over{2ab}={4k^{2}+9k^{2}-16k^{2}} over{12k^{2}}=it-{1} over{4}$',
        '$ sin C= sqrt{1-{1} over{16}}={ sqrt{15}} over{4}$',
        '사인법칙: ${c} over{ sin C}=2R=32$에서 $4k={ sqrt{15}} over{4} times32=8 sqrt{15}$이므로 $k=2 sqrt{15}$, $k^{2}=60$',
        '삼각형의 넓이 $={1} over{2}ab sin C={1} over{2}(2k)(3k) times{ sqrt{15}} over{4}={3k^{2} sqrt{15}} over{4}={3(60) sqrt{15}} over{4}$',
        '$therefore$ 넓이는',
        '$=45 sqrt{15}$',
    ],
    ch='사인법칙과 코사인법칙의 활용', lv='상')

add(id='q17', kind='mc', no=17, score=5.2, layout='1x5',
    text='첫째항이 양수이고 모든 항이 실수인 등비수열 ${a_{n}}$의 첫째항부터 제$n$항까지의 합을 $S_{n}$이라 하자. $a_{2}=it-30$, $4S_{2}+3S_{3}+S_{4}=0$일 때, $S_{n} GEQ 165$를 만족하는 $20$이하의 자연수 $n$의 개수는?',
    choices=['$8$', '$9$', '$10$', '$11$', '$12$'],
    ans='①',
    sol=[
        '$S_{2}=a_{1}(1+r)$, $S_{3}=a_{1}(1+r+r^{2})$, $S_{4}=a_{1}(1+r+r^{2}+r^{3})$',
        '$4S_{2}+3S_{3}+S_{4}=0$에서 $a_{1} NEQ 0$이므로 $4(1+r)+3(1+r+r^{2})+(1+r+r^{2}+r^{3})=0$',
        '정리하면 $r^{3}+4r^{2}+8r+8=0$이고, $(r+2)(r^{2}+2r+4)=0$',
        '$r^{2}+2r+4=0$의 판별식 $=4-16<0$이므로 실근은 $r=it-2$뿐',
        '$a_{1}r=it-30$에서 $a_{1}=15$',
        '$S_{n}={a_{1}(1-r^{n})} over{1-r}={15(1-(it-2)^{n})} over{3}=5-5(it-2)^{n}$',
        '$S_{n} GEQ 165$에서 $it-5(it-2)^{n} GEQ 160$, $(it-2)^{n} LEQit-32$',
        '$n$이 짝수면 $(it-2)^{n}>0$이라 성립 불가. $n$이 홀수면 $(it-2)^{n}=it-2^{n}$이므로 $it-2^{n} LEQit-32$에서 $2^{n} GEQ 32$, $n GEQ 5$',
        '$20$이하의 홀수 중 $n GEQ 5$인 것: $n=5,~7,~9,~11,~13,~15,~17,~19$',
        '$therefore$ 개수는',
        '$=8$',
    ],
    ch='등비수열과 수열의 합', lv='상')

add(id='q18', kind='mc', no=18, score=5.3, layout='1x5', fig='us26f_q18',
    text='양수 $a,~b$에 대하여 집합 ${x LEFT | 0 LEQ x LEQ 2/b RIGHT.}$에서 정의된 함수 $f(x)=a cos b pi x$가 있다. 그림과 같이 직선 $y=it- sqrt{3}$과 함수 $y=f(x)$의 그래프가 점 $A$에서 만나고, 직선 $y= sqrt{3}/2$와 함수 $y=f(x)$의 그래프가 점 $B$와 점 $C$에서 만난다. 삼각형 $ABC$가 정삼각형일 때, $3a^{2}b$의 값은?',
    choices=['$3$', '$2 sqrt{3}$', '$4$', '$3 sqrt{2}$', '$5$'],
    ans='③',
    sol=[
        '$f(x)=a cos(b pi x)$는 $x=0$에서 $a$(최댓값), $x={1} over{b}$에서 $it-a$(최솟값, 점 $A$)를 갖고 $x={2} over{b}$에서 다시 $a$가 된다.',
        '최솟값이 $it- sqrt{3}$이므로 $a= sqrt{3}$',
        '$f(x)={ sqrt{3}} over{2}$인 점: $ cos(b pi x)={1} over{2}$에서 $b pi x={ pi} over{3}$ 또는 ${5} over{3} pi$ (구간 $[0,2 pi]$ 내에서)',
        '점 $B$: $x_{B}={1} over{3b}$, 점 $C$: $x_{C}={5} over{3b}$',
        '$bar{BC}=x_{C}-x_{B}={4} over{3b}$',
        '$A$의 $y$좌표에서 $B,C$의 $y$좌표까지의 수직거리(높이) $={ sqrt{3}} over{2}-(it- sqrt{3})={3 sqrt{3}} over{2}$',
        '정삼각형의 높이 $={ sqrt{3}} over{2} times(밑변)$이므로 ${3 sqrt{3}} over{2}={ sqrt{3}} over{2} times bar{BC}$에서 $bar{BC}=3$',
        '${4} over{3b}=3$에서 $b={4} over{9}$',
        '$therefore~3a^{2}b=3(3)LEFT({4} over{9} RIGHT)=9 times{4} over{9}$',
        '$=4$',
    ],
    ch='삼각함수의 그래프와 도형', lv='상')

add(id='q19', kind='mc', no=19, score=5.4, layout='1x5', fig='us26f_q19', jogeon=True,
    text='그림과 같이 반지름의 길이가 $r$인 원에 내접하는 삼각형 $ABC$가 있다. 점 $B$와 이 원의 중심을 지나는 직선이 원과 만나는 점 중 $B$가 아닌 점을 $D$라 하자. 이때, 다음 조건을 만족시키는 사각형 $ADBC$의 넓이는? (단, $bar{BC}=a$, $bar{CA}=b$, $bar{AB}=c$, $bar{BD}=2r$)',
    jogeon_items=[
        '$bar{AB}=2 sqrt{3}$',
        '삼각형 $ABC$에 대하여 $a sin A=b sin B$',
        '삼각형 $ABC$에 대하여 $ sin A={c^{2}-a^{2}-b^{2}} over{2 sqrt{3}br}$',
    ],
    choices=['$6-3 sqrt{3}$', '$6-2 sqrt{3}$', '$6- sqrt{3}$', '$6+ sqrt{3}$', '$6+3 sqrt{3}$'],
    ans='⑤',
    sol=[
        '사인법칙 $a=2r sin A$, $b=2r sin B$를 (나)에 대입: $2r sin^{2}A=2r sin^{2}B$에서 $ sin A= sin B$이므로 $A=B$ (즉 $a=b$)',
        '코사인법칙에서 $c^{2}-a^{2}-b^{2}=it-2ab cos C$이므로 (다)는 $ sin A=it-{2ab cos C} over{2 sqrt{3}br}=it-{a cos C} over{ sqrt{3}r}$',
        '$ sin A={a} over{2r}$(사인법칙)이므로 ${a} over{2r}=it-{a cos C} over{ sqrt{3}r}$에서 ${1} over{2}=it-{ cos C} over{ sqrt{3}}$, $ cos C=it-{ sqrt{3}} over{2}$, $C=150^{ circ}$',
        '$a=b$이므로 $A=B={180^{ circ}-150^{ circ}} over{2}=15^{ circ}$',
        '코사인법칙: $c^{2}=2a^{2}-2a^{2} cos150^{ circ}=2a^{2}LEFT(1+{ sqrt{3}} over{2} RIGHT)$',
        '$c=2 sqrt{3}$이므로 $12=2a^{2}LEFT({2+ sqrt{3}} over{2} RIGHT)=a^{2}(2+ sqrt{3})$에서 $a^{2}={12} over{2+ sqrt{3}}=12(2- sqrt{3})=24-12 sqrt{3}$',
        '삼각형 $ABC$의 넓이 $={1} over{2}ab sin C={1} over{2}a^{2} sin150^{ circ}={1} over{4}a^{2}={1} over{4}(24-12 sqrt{3})=6-3 sqrt{3}$',
        '사인법칙으로 $r$을 구하면 ${c} over{ sin C}=2r$에서 $2 sqrt{3} div{1} over{2}=4 sqrt{3}=2r$이므로 $r=2 sqrt{3}$, $bar{BD}=2r=4 sqrt{3}$',
        '$∠BAD=90^{ circ}$($BD$가 지름)이므로 직각삼각형 $ABD$에서 $bar{AD}^{2}=bar{BD}^{2}-bar{AB}^{2}=48-12=36$, $bar{AD}=6$',
        '삼각형 $ABD$의 넓이 $={1} over{2} times bar{AB} times bar{AD}={1} over{2}(2 sqrt{3})(6)=6 sqrt{3}$',
        '$therefore$ 사각형 $ADBC$의 넓이 $=$삼각형$ABD$+삼각형$ABC$ $=6 sqrt{3}+(6-3 sqrt{3})$',
        '$=6+3 sqrt{3}$',
    ],
    ch='원에 내접하는 사각형의 넓이', lv='최상')

add(id='q20', kind='mc', no=20, score=5.5, layout='1x5', jogeon=True,
    text='좌표평면 위의 점 $P_{n}(x_{n},~y_{n})$이 모든 자연수 $n$에 대하여 다음 조건을 만족시킨다. 점 $P_{n}$의 $x$좌표 $x_{n}$에 대하여 $x_{n+1}=tx_{n}+s$가 성립할 때, $ sum^{3}_{k=2}(tx_{k}-1)+ sum^{4}_{k=1}sy_{k}$의 값은? (단, $t,~s$는 상수이다.)',
    jogeon_items=[
        '점 $P_{1}$의 좌표는 $(8,~8)$이다.',
        '점 $A_{n}$은 점 $P_{n}$을 $x$축의 방향으로 $4$만큼 평행이동한 점이다.',
        '점 $P_{n+1}$은 원점 $O$와 점 $A_{n}$을 연결한 선분 $OA_{n}$의 중점이다.',
    ],
    choices=['$32$', '${65} over{2}$', '$33$', '${67} over{2}$', '$34$'],
    ans='④',
    sol=[
        '$A_{n}=(x_{n}+4,~y_{n})$이고 $P_{n+1}$은 $O(0,0)$와 $A_{n}$의 중점이므로 $x_{n+1}={x_{n}+4} over{2}={1} over{2}x_{n}+2$, $y_{n+1}={1} over{2}y_{n}$',
        '따라서 $t={1} over{2}$, $s=2$',
        '$y_{n}$은 첫째항 $8$, 공비 ${1} over{2}$인 등비수열: $y_{1}=8,~y_{2}=4,~y_{3}=2,~y_{4}=1$',
        '$x_{n}-4$는 첫째항 $x_{1}-4=4$, 공비 ${1} over{2}$인 등비수열: $x_{n}=4+4LEFT({1} over{2} RIGHT)^{n-1}$이므로 $x_{2}=6$, $x_{3}=5$',
        '$ sum^{3}_{k=2}(tx_{k}-1)=LEFT({1} over{2}x_{2}-1 RIGHT)+LEFT({1} over{2}x_{3}-1 RIGHT)={1} over{2}(x_{2}+x_{3})-2={1} over{2}(11)-2={11} over{2}-2={7} over{2}$',
        '$ sum^{4}_{k=1}sy_{k}=2(y_{1}+y_{2}+y_{3}+y_{4})=2(8+4+2+1)=2(15)=30$',
        '$therefore$ 구하는 값은 ${7} over{2}+30$',
        '$={67} over{2}$',
    ],
    ch='수열의 귀납적 정의와 도형', lv='상')
