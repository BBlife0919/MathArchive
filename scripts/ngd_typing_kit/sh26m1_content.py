# -*- coding: utf-8 -*-
"""소하고등학교 2학년 2026 1학기 중간 대수(지수로그~삼각함수의 그래프) 19문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.2, layout='3+2',
    text='$ log_{2}3=a$이고, $ log_{2}5=b$일 때, $ log_{2}45$를 $a$와 $b$로 나타낸 것은?',
    choices=['$2ab$', '$a^{2}b$', '$a+b$', '$2a+b$', '$a+b+2$'],
    ans='④',
    sol=[
        '$45=3^{2} times5$이므로 $ log_{2}45= log_{2}3^{2}+ log_{2}5=2 log_{2}3+ log_{2}5$',
        '$therefore$ 구하는 값은',
        '$=2a+b$',
    ],
    ch='로그의 성질', lv='하')

add(id='q02', kind='mc', no=2, score=4.2, layout='3+2',
    text='$ sqrt[4]{ sqrt[3]{24}}- sqrt[6]{ sqrt{24}}$를 계산한 값은?',
    choices=['$0$', '$ sqrt[6]{2}$', '$ sqrt[6]{6}$', '$2 sqrt[6]{2}$', '$2 sqrt[6]{6}$'],
    ans='①',
    sol=[
        '$ sqrt[4]{ sqrt[3]{24}}=24^{{1} over{3} times{1} over{4}}=24^{{1} over{12}}$',
        '$ sqrt[6]{ sqrt{24}}=24^{{1} over{2} times{1} over{6}}=24^{{1} over{12}}$',
        '두 값이 서로 같으므로 차는',
        '$=0$',
    ],
    ch='거듭제곱근', lv='하')

add(id='q03', kind='mc', no=3, score=4.3, layout='1x5',
    text='반지름의 길이가 $8$이고, 넓이가 $8 pi$인 부채꼴의 중심각의 크기는?',
    choices=['${ pi} over{4}$', '${ pi} over{3}$', '${ pi} over{2}$', '$ pi$', '$2 pi$'],
    ans='①',
    sol=[
        '넓이 $={1} over{2}r^{2} theta$이므로 $8 pi={1} over{2} times64 times theta=32 theta$',
        '$therefore~ theta$',
        '$={ pi} over{4}$',
    ],
    ch='호도법과 부채꼴', lv='하')

add(id='q04', kind='mc', no=4, score=4.4, layout='3+2',
    text='$ sin{13} over{6} pi- cos LEFT(it-{ pi} over{3} RIGHT)$의 값은?',
    choices=['$it- sqrt{3}$', '$it-1$', '$0$', '$1$', '$ sqrt{3}$'],
    ans='③',
    sol=[
        '$ sin{13} over{6} pi= sin LEFT(2 pi+{ pi} over{6} RIGHT)= sin{ pi} over{6}={1} over{2}$',
        '$ cos LEFT(it-{ pi} over{3} RIGHT)= cos{ pi} over{3}={1} over{2}$',
        '$therefore$ 구하는 값은 ${1} over{2}-{1} over{2}$',
        '$=0$',
    ],
    ch='삼각함수의 값', lv='하')

add(id='q05', kind='mc', no=5, score=4.5, layout='1x5', emptybox={'paras': [
        '다음 그림은 상용로그표의 일부이다. (수 2.1, 열 8의 교차값: $0.3385$)',
    ]},
    text='위 상용로그표를 이용하여 $ log2180$의 값을 구하면?',
    choices=['$0.3385$', '$3.3385$', '$30.3385$', '$338.5$', '$3385$'],
    ans='②',
    sol=[
        '$2180=2.18 times10^{3}$이므로 $ log2180= log2.18+3$',
        '상용로그표에서 $ log2.18=0.3385$',
        '$therefore$ 구하는 값은 $0.3385+3$',
        '$=3.3385$',
    ],
    ch='상용로그표의 활용', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2',
    text='어느 금융상품에 $A$만원을 투자할 때, $t$년 후에 원금과 이익금의 합은 $A LEFT(1+LEFT({5} over{4} RIGHT)^{{t} over{2}} RIGHT)$만원이 된다고 한다. 처음 투자 금액이 $80$만원이고 $t$년 후에 원금과 이익금의 합이 $205$만원일 때, $t$의 값은?',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='②',
    sol=[
        '$80LEFT(1+LEFT({5} over{4} RIGHT)^{{t} over{2}} RIGHT)=205$에서 $1+LEFT({5} over{4} RIGHT)^{{t} over{2}}={205} over{80}=2.5625$',
        '$LEFT({5} over{4} RIGHT)^{{t} over{2}}=1.5625={25} over{16}=LEFT({5} over{4} RIGHT)^{2}$',
        '${t} over{2}=2$에서 $t=4$',
        '$therefore~t$',
        '$=4$',
    ],
    ch='지수함수의 활용', lv='중')

add(id='q07', kind='mc', no=7, score=4.8, layout='3+2',
    text='함수 $f(x)=2^{x+a}-3$의 역함수를 $g(x)$라 하자. 함수 $y=g(x)$의 그래프가 점 $(1,~3)$을 지나고, 점근선이 직선 $x=b$일 때, $ab$의 값은? (단, $a,~b$는 상수이다.)',
    choices=['$it-3$', '$it-1$', '$1$', '$3$', '$5$'],
    ans='④',
    sol=[
        '$g(1)=3$이므로 $f(3)=1$: $2^{3+a}-3=1$에서 $2^{3+a}=4=2^{2}$, $a=it-1$',
        '$f(x)=2^{x-1}-3$의 점근선은 $y=it-3$이고, 역함수 $g(x)$의 점근선은 이를 $y=x$에 대칭이동한 $x=it-3$이므로 $b=it-3$',
        '$therefore~ab=(it-1)(it-3)$',
        '$=3$',
    ],
    ch='역함수와 점근선', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2',
    text='실수 $a$에 대하여 ${3^{a}-3^{it-a}} over{3^{a}+3^{it-a}}={1} over{4}$일 때, $9^{a}+9^{it-a}$의 값은?',
    choices=['${26} over{15}$', '${28} over{15}$', '$2$', '${32} over{15}$', '${34} over{15}$'],
    ans='⑤',
    sol=[
        '$u=3^{a}$, $v=3^{it-a}$라 하면 $uv=1$이고 ${u-v} over{u+v}={1} over{4}$',
        '$(u-v)^{2}=u^{2}+v^{2}-2uv=S-2$, $(u+v)^{2}=S+2$ ($S=u^{2}+v^{2}=9^{a}+9^{it-a}$)',
        '${(u-v)^{2}} over{(u+v)^{2}}={1} over{16}$에서 ${S-2} over{S+2}={1} over{16}$',
        '$16(S-2)=S+2$에서 $16S-32=S+2$, $15S=34$',
        '$therefore~S$',
        '$={34} over{15}$',
    ],
    ch='지수의 변형', lv='중')

add(id='q09', kind='mc', no=9, score=5.0, layout='1x5',
    text='$x$에 대한 방정식 $9^{x}-(2a+1)3^{x}+a^{2}+a-6=0$이 실근을 갖지 않도록 하는 실수 $a$의 값의 범위는?',
    choices=['$a<2$', '$a LEQ 2$', '$a LEQ it-3$', '$a>it-3$', '$it-3 LEQ a LEQ 2$'],
    ans='③',
    sol=[
        '$t=3^{x}>0$이라 하면 $t^{2}-(2a+1)t+(a^{2}+a-6)=0$',
        '좌변을 인수분해하면 $LEFT{t-(a+3) RIGHT}LEFT{t-(a-2) RIGHT}=0$이므로 $t=a+3$ 또는 $t=a-2$',
        '원래 방정식이 실근을 갖지 않으려면 두 근 모두 $t>0$을 만족하지 않아야(즉 둘 다 $0$ 이하) 한다.',
        '$a+3 LEQ 0$에서 $a LEQ it-3$. 이때 $a-2 LEQ it-5<0$도 자동으로 성립한다.',
        '$therefore$ 구하는 범위는',
        '$=a LEQ it-3$',
    ],
    ch='지수방정식이 실근을 갖지 않을 조건', lv='중')

add(id='q10', kind='mc', no=10, score=5.1, layout='1x5',
    text='제$2$사분면의 각 $ theta$에 대하여 $LEFT | sin LEFT({ pi} over{2}- theta RIGHT) RIGHT |+ sqrt{(cos^{2} theta-cos theta+sin^{2} theta)^{2}}=2$일 때, $ tan LEFT({ pi} over{2}+ theta RIGHT)$의 값은?',
    choices=['$ sqrt{3}$', '${ sqrt{3}} over{3}$', '$1$', '$it-{ sqrt{3}} over{3}$', '$it- sqrt{3}$'],
    ans='②',
    sol=[
        '$ cos^{2} theta-cos theta+sin^{2} theta=( cos^{2} theta+sin^{2} theta)- cos theta=1- cos theta$이므로 $ sqrt{(1- cos theta)^{2}}=LEFT | 1- cos theta RIGHT |$',
        '$ sin LEFT({ pi} over{2}- theta RIGHT)= cos theta$이므로 식은 $LEFT | cos theta RIGHT |+LEFT | 1- cos theta RIGHT |=2$',
        '제$2$사분면이므로 $ cos theta<0$: $LEFT | cos theta RIGHT |=it- cos theta$, $1- cos theta>0$이므로 $LEFT | 1- cos theta RIGHT |=1- cos theta$',
        '$it- cos theta+1- cos theta=2$에서 $1-2 cos theta=2$, $ cos theta=it-{1} over{2}$',
        '제$2$사분면이므로 $ sin theta= sqrt{1-{1} over{4}}={ sqrt{3}} over{2}$',
        '$ tan theta={ sin theta} over{ cos theta}=it- sqrt{3}$',
        '$ tan LEFT({ pi} over{2}+ theta RIGHT)=it- cot theta=it-{1} over{ tan theta}=it-{1} over{it- sqrt{3}}={1} over{ sqrt{3}}$',
        '$therefore$ 구하는 값은',
        '$={ sqrt{3}} over{3}$',
    ],
    ch='삼각함수 사이의 관계', lv='상')

add(id='q11', kind='mc', no=11, score=5.2, layout='3+2',
    text='${2} over{3} pi< theta< pi$이고 각 $ theta$를 나타내는 동경과 각 $9 theta$를 나타내는 동경이 원점에 대하여 대칭일 때, 각 $ theta$의 크기를 ${a} over{b} pi$라 하자. 이때, $a+b$의 값은? (단, $a,~b$는 서로소인 자연수이다.)',
    choices=['$7$', '$12$', '$15$', '$30$', '$33$'],
    ans='③',
    sol=[
        '두 동경이 원점에 대해 대칭이므로 $9 theta= theta+(2k+1) pi$ (정수 $k$)에서 $8 theta=(2k+1) pi$, $ theta={(2k+1)} over{8} pi$',
        '${2} over{3} pi< theta< pi$에서 ${2} over{3}<{2k+1} over{8}<1$, $5.33<2k+1<8$을 만족하는 홀수는 $2k+1=7$',
        '$ theta={7} over{8} pi$. $a=7,~b=8$은 서로소',
        '$therefore~a+b=7+8$',
        '$=15$',
    ],
    ch='동경의 대칭', lv='상')

add(id='q12', kind='mc', no=12, score=5.3, layout='1x5',
    text='방정식 $2 log(x+2)+ log(x-3)^{2}= log36$의 모든 근의 합은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='⑤',
    sol=[
        '$2 log(x+2)= log(x+2)^{2}$이므로 $ log LEFT[(x+2)^{2}(x-3)^{2} RIGHT]= log36$',
        '$LEFT[(x+2)(x-3) RIGHT]^{2}=36$에서 $(x+2)(x-3)=pm6$',
        '$+6$: $x^{2}-x-12=0$, $(x-4)(x+3)=0$에서 $x=4$ 또는 $x=it-3$. 진수 조건 $x>it-2$에서 $x=4$만 유효',
        '$it-6$: $x^{2}-x=0$, $x(x-1)=0$에서 $x=0$ 또는 $x=1$. 둘 다 조건을 만족',
        '$therefore$ 모든 근의 합은 $4+0+1$',
        '$=5$',
    ],
    ch='로그방정식의 근', lv='중')

add(id='q13', kind='mc', no=13, score=5.3, layout='1x5',
    text='부등식 $(x^{2}+1)^{ log_{3}{1} over{5}} LEQ 5^{ log_{{1} over{3}}(2x+4)}$의 해가 $ alpha<x LEQ beta$ 또는 $x GEQ gamma$일 때, $ alpha+ beta+ gamma$의 값은? (단, $ alpha, beta, gamma$는 상수이다.)',
    choices=['$it-1$', '$it-{2} over{3}$', '$it-{1} over{3}$', '$0$', '${1} over{3}$'],
    ans='④',
    sol=[
        '$ log_{3}{1} over{5}=it- log_{3}5$, $ log_{{1} over{3}}(2x+4)=it- log_{3}(2x+4)$',
        '양변이 양수이므로 밑 $3$인 로그를 취하면 $it- log_{3}5 times log_{3}(x^{2}+1) LEQ it- log_{3}(2x+4) times log_{3}5$',
        '$ log_{3}5>0$으로 나누면 $it- log_{3}(x^{2}+1) LEQ it- log_{3}(2x+4)$, 즉 $ log_{3}(x^{2}+1) GEQ log_{3}(2x+4)$',
        '$x^{2}+1 GEQ 2x+4$에서 $x^{2}-2x-3 GEQ 0$, $(x-3)(x+1) GEQ 0$에서 $x LEQ it-1$ 또는 $x GEQ 3$',
        '진수 조건 $2x+4>0$에서 $x>it-2$. 이를 결합하면 $it-2<x LEQ it-1$ 또는 $x GEQ 3$',
        '$ alpha=it-2$, $ beta=it-1$, $ gamma=3$',
        '$therefore~ alpha+ beta+ gamma=it-2+(it-1)+3$',
        '$=0$',
    ],
    ch='지수·로그 부등식', lv='상')

add(id='q14', kind='mc', no=14, score=5.5, layout='1x5',
    text='두 자연수 $m,~n$에 대하여 $0 LEQ x LEQ 4n$에서 정의된 함수 $y=m cos LEFT({ pi} over{4}x RIGHT)$의 그래프가 직선 $y=0$과 만나는 점의 개수가 $17$개이고, 직선 $y=5$와 만나는 점의 개수가 $9$개일 때, $m+n$의 값은?',
    choices=['$14$', '$21$', '$22$', '$23$', '$26$'],
    ans='③',
    sol=[
        '주기는 $8$이다. $y=0$: $ cos LEFT({ pi} over{4}x RIGHT)=0$에서 $x=2+4k$ ($k=0,~1,~ cdots,~n-1$)로 $n$개 — 이 패턴은 $x=0,~4n$과 절대 겹치지 않으므로 항상 정확히 $n$개이다.',
        '$n=17$',
        '$y=5$: $m cos LEFT({ pi} over{4}x RIGHT)=5$가 해를 가지려면 $m GEQ 5$이고, $m=5$(경계)이면 $ cos LEFT({ pi} over{4}x RIGHT)=1$에서 $x=8k$',
        '$n=17$(홀수)이므로 $x=8k LEQ 4(17)=68$에서 $k=0,~1,~ cdots,~8$로 $9$개 — 조건과 일치',
        '$therefore~m=5$, $n=17$이므로 $m+n$',
        '$=22$',
    ],
    ch='삼각함수의 그래프와 직선의 교점 개수', lv='상')

add(id='q15', kind='mc', no=15, score=5.6, layout='1x5',
    text='실수 $x$에 대하여 $x$의 세제곱근 중에서 실수인 것의 개수를 $f(x)$, $x$의 네제곱근 중에서 실수인 것의 개수를 $g(x)$라 하자. $2LEFT | a RIGHT |+LEFT | b RIGHT | LEQ 4$를 만족시키는 두 정수 $a,~b$에 대하여 $1 LEQ f(a)+g(b)<3$을 만족시키는 모든 순서쌍 $(a,~b)$의 개수는?',
    choices=['$5$', '$8$', '$11$', '$13$', '$26$'],
    ans='④',
    sol=[
        '$f(a)$는 임의의 실수 $a$에 대해 세제곱근이 항상 $1$개이므로 $f(a)=1$ (항상)',
        '$1 LEQ 1+g(b)<3$에서 $0 LEQ g(b)<2$, 즉 $g(b)=0$ 또는 $1$',
        '$g(b)=0$은 $b<0$, $g(b)=1$은 $b=0$일 때이므로 조건은 $b LEQ 0$',
        '$b=0$: $2LEFT | a RIGHT | LEQ 4$에서 $LEFT | a RIGHT | LEQ 2$로 $a in{it-2,it-1,0,1,2}$ ($5$개)',
        '$b=it-1$: $LEFT | a RIGHT | LEQ 1.5$로 $a in{it-1,0,1}$ ($3$개). $b=it-2$: $LEFT | a RIGHT | LEQ 1$로 $3$개',
        '$b=it-3$: $LEFT | a RIGHT | LEQ 0.5$로 $a=0$ ($1$개). $b=it-4$: $LEFT | a RIGHT | LEQ 0$로 $a=0$ ($1$개)',
        '$therefore$ 구하는 순서쌍의 개수는 $5+3+3+1+1$',
        '$=13$',
    ],
    ch='거듭제곱근의 개수', lv='중')

add(id='q16', kind='mc', no=16, score=5.7, layout='1x5', emptybox={'paras': [
        '$f(x)=cases{{ log_{2}(it-x+7)}~~(x<5)#{ log_{2}(x-3)+k}~~(x GEQ 5)}$',
    ]},
    text='위 함수 $f(x)$에 대하여 $y=f(x)$의 그래프와 직선 $y=t$의 교점의 개수가 $1$이 되도록 하는 정수 $t$의 개수를 $h(k)$라 하자. 정수 전체의 집합에서 정의된 두 함수 $h(k)$와 $g(k)=a LEFT | k+b RIGHT |$에 대하여 정의역의 각 원소 $k$가 $h(k)=g(k)$를 만족할 때, $ab$의 값은? (단, $k$는 정수이고, $a,~b$는 실수이다.)',
    choices=['$it-2$', '$it-1$', '$0$', '$1$', '$2$'],
    ans='②',
    sol=[
        '$x<5$ 조각: $it-x+7$은 $x$가 커질수록 작아지므로 $f$는 감소, 치역 $(1,~ infty)$ (상한 제외, $x` ->`5-$에서 $1$에 수렴)',
        '$x GEQ 5$ 조각: $ log_{2}(x-3)+k$는 증가, $x=5$에서 값 $1+k$부터 $ infty$까지',
        '실수 $t$에 대해 교점의 개수 $N(t)=LEFT[t>1 RIGHT]+LEFT[t GEQ 1+k RIGHT]$ (왼쪽 조각에서 $1$개 생기면 $+1$, 오른쪽 조각에서 $1$개 생기면 $+1$)',
        '$N(t)=1$이려면 두 조건 중 정확히 하나만 성립해야 한다. $k>0$이면 $1<t<1+k$ 구간에서, $k LEQ 0$이면 $1+k LEQ t LEQ 1$ 구간에서 성립한다.',
        '$h(k)$는 이 구간에 속하는 정수 $t$의 개수이다. $k>0$(정수)이면 구간 $(1,~1+k)$ 안의 정수는 $2,~3,~ cdots,~k$로 $k-1$개',
        '$k LEQ 0$(정수)이면 구간 $[1+k,~1]$ 안의 정수는 $1+k,~ cdots,~1$로 $1-k$개',
        '두 식을 합치면 $h(k)=LEFT | k-1 RIGHT |$ ($k GEQ 1$일 때 $k-1=LEFT | k-1 RIGHT |$, $k LEQ 0$일 때 $1-k=LEFT | k-1 RIGHT |$로 일치)',
        '$g(k)=a LEFT | k+b RIGHT |$와 비교하면 $a=1$, $b=it-1$',
        '$therefore~ab=1 times(it-1)$',
        '$=it-1$',
    ],
    ch='로그함수의 그래프와 절댓값함수', lv='상')

add(id='q17', kind='mc', no=17, score=5.7, layout='1x5', jogeon=True,
    text='정의역이 $LEFT{x LEFT|~0 LEQ x LEQ 5 RIGHT. RIGHT}$이고 최고차항의 계수가 $1$인 이차함수 $f(x)$에 대하여 $g(x)=LEFT({1} over{2} RIGHT)^{f(x)}$라 할 때, 함수 $g(x)$가 다음 조건을 만족시킨다.',
    jogeon_items=[
        '함수 $g(x)$는 일대일함수가 아니다.',
        '함수 $g(x)$의 최댓값은 $8$, 최솟값은 ${1} over{64}$이다.',
    ],
    text2=['$g(4)<1$일 때, $g(1)$의 값은? [5.7점]'],
    choices=['$4$', '$2$', '$1$', '${1} over{2}$', '${1} over{4}$'],
    ans='①',
    sol=[
        '$g$가 최대일 때 $f$는 최소, $g$가 최소일 때 $f$는 최대(밑이 ${1} over{2}<1$이라 감소함수)이다.',
        '$8=LEFT({1} over{2} RIGHT)^{f_{min}}$에서 $f_{min}=it-3$. ${1} over{64}=LEFT({1} over{2} RIGHT)^{f_{max}}$에서 $f_{max}=6$',
        '$f$가 일대일이 아니므로 꼭짓점이 $(0,~5)$ 내부에 있다. $f(x)=(x-h)^{2}-3$',
        '최댓값 $6$은 꼭짓점에서 더 먼 끝점에서 나온다. $f(0)=h^{2}-3=6$이면 $h=3$, $f(5)=(5-h)^{2}-3=6$이면 $h=2$ (둘 다 $(0,5)$ 내부, 후보)',
        '$h=3$: $f(4)=(4-3)^{2}-3=it-2$. $g(4)=LEFT({1} over{2} RIGHT)^{it-2}=4$로 $g(4)<1$에 모순되어 제외',
        '$h=2$: $f(4)=(4-2)^{2}-3=1$. $g(4)=LEFT({1} over{2} RIGHT)^{1}={1} over{2}<1$로 조건 만족',
        '$f(x)=(x-2)^{2}-3$. $f(1)=(1-2)^{2}-3=it-2$',
        '$therefore~g(1)=LEFT({1} over{2} RIGHT)^{it-2}$',
        '$=4$',
    ],
    ch='이차함수와 지수함수의 합성', lv='상')

add(id='q18', kind='mc', no=18, score=5.8, layout='1x5',
    text='$0 LEQ x LEQ{2} over{3} pi$일 때, 방정식 $ sin LEFT(3x-{2} over{3} pi RIGHT)= cos LEFT({2} over{3} pi-2x RIGHT)$의 모든 해의 합은?',
    choices=['${11} over{30} pi$', '${ pi} over{2}$', '${3} over{5} pi$', '${7} over{10} pi$', '${13} over{15} pi$'],
    ans='⑤',
    sol=[
        '$ cos LEFT({2} over{3} pi-2x RIGHT)= sin LEFT({ pi} over{2}-LEFT({2} over{3} pi-2x RIGHT) RIGHT)= sin LEFT(2x-{ pi} over{6} RIGHT)$',
        '$ sin LEFT(3x-{2} over{3} pi RIGHT)= sin LEFT(2x-{ pi} over{6} RIGHT)$에서 두 경우가 생긴다.',
        '(ⅰ) $3x-{2} over{3} pi=2x-{ pi} over{6}+2k pi$에서 $x={ pi} over{2}+2k pi$. 범위 내 $k=0$: $x={ pi} over{2}$',
        '(ⅱ) $3x-{2} over{3} pi= pi-LEFT(2x-{ pi} over{6} RIGHT)+2k pi$에서 $5x={11} over{6} pi+2k pi$, $x={11} over{30} pi+{2k pi} over{5}$. 범위 내 $k=0$: $x={11} over{30} pi$ (다른 $k$는 범위 밖)',
        '$therefore$ 모든 해의 합은 ${ pi} over{2}+{11} over{30} pi={15} over{30} pi+{11} over{30} pi$',
        '$={13} over{15} pi$',
    ],
    ch='삼각방정식', lv='상')

add(id='q19', kind='sub', no=1, score=10.0,
    text='최고차항의 계수가 음수인 일차식 $f(x)$와 최고차항의 계수가 $1$인 이차식 $g(x)$가 있다. 함수 $h(x)$를 $ log_{LEFT | f(x) RIGHT |}g(x)$라 하고, 함수 $h(x)$의 정의역을 집합 $A$라 할 때, 함수 $h(x)$가 다음 조건을 만족시킨다. 다음 물음에 답하시오.',
    jogeon=True,
    jogeon_items=[
        '집합 $B=LEFT{x LEFT|~x in A^{C},~x는 실수 RIGHT. RIGHT}$의 원소의 개수는 $3$이고, 모든 원소의 합과 곱은 각각 $1$, $it-{1} over{9}$이다.',
        '이차방정식 $g(x)=0$의 실근이 존재한다.',
        '$h LEFT({5} over{3} RIGHT)=2$',
    ],
    text2=[
        '(1) 집합 $B$를 원소나열법으로 제시하고 그 과정을 서술하시오. 이를 바탕으로 조건을 만족시키는 다항식 $f(x)$를 쓰고 그 과정을 서술하시오. [4점]',
        '(2) 조건을 만족시키는 $g(x)$와 $h(it-1)$의 값을 구하고 그 과정을 서술하시오. [6점]',
    ],
    ans_mix='$f(x)=it-{3} over{2}x+{1} over{2}$, $g(x)=LEFT(x+{1} over{3} RIGHT)^{2}$, $h(it-1)=2-2 log_{2}3$',
    sol=[
        '(1) $h$의 정의역에서 빠지는 점은 $f(x)=0$, $LEFT | f(x) RIGHT |=1$(즉 $f(x)=pm1$), 또는 $g(x) LEQ 0$인 $x$이다.',
        '$f$는 일차식이므로 $f(x)=0,~1,~{it-1}$은 각각 정확히 한 개의 근을 주어 최대 $3$개의 서로 다른 점이 나온다.',
        '$B$가 정확히 $3$개이고 조건(나)에서 $g=0$이 실근을 가지므로(곧 보일 것처럼 중근이어야 구간이 아닌 한 점만 추가되어 개수가 유지됨), $g(x) LEQ 0$인 부분이 새 점을 추가하지 않으려면 $g$가 중근을 가져 $g(x) LEQ 0$인 점이 단 하나(그 중근)뿐이고, 그 점이 이미 $f$ 관련 세 점 중 하나와 같아야 한다.',
        '$f(x)=mx+c~(m<0)$라 하면 세 근 $x_{0}=it-{c} over{m}$ ($f=0$), $x_{1}={1-c} over{m}$ ($f=1$), $x_{2}={it-1-c} over{m}$ ($f=it-1$)의 합은 ${it-3c} over{m}=1$에서 $c=it-{m} over{3}$',
        '세 근의 곱은 ${c(1-c^{2})} over{m^{3}}=it-{1} over{9}$에 $c=it-{m} over{3}$ 대입: $it-{1} over{3m^{2}}+{1} over{27}=it-{1} over{9}$에서 $m^{2}={9} over{4}$, $m<0$이므로 $m=it-{3} over{2}$',
        '$c=it-{m} over{3}={1} over{2}$. $f(x)=it-{3} over{2}x+{1} over{2}$',
        '$therefore$ (가) 과정을 정리하면 세 근은 $f=0$: $x={1} over{3}$, $f=1$: $x=it-{1} over{3}$, $f=it-1$: $x=1$',
        '$B=LEFT{{it-{1} over{3}},~{1} over{3},~1 RIGHT}$ (합 $1$, 곱 $it-{1} over{9}$ 검산 완료)',
        '(2) $g(x)=(x-s)^{2}$ (중근 $s$)이고 $s$는 $B$의 세 값 중 하나와 같아야 한다.',
        '$f({5} over{3})=it-{3} over{2} times{5} over{3}+{1} over{2}=it-{5} over{2}+{1} over{2}=it-2$이므로 $LEFT | f({5} over{3}) RIGHT |=2$',
        '$h LEFT({5} over{3} RIGHT)= log_{2}g LEFT({5} over{3} RIGHT)=2$에서 $g LEFT({5} over{3} RIGHT)=4$',
        '$LEFT({5} over{3}-s RIGHT)^{2}=4$에서 $s={5} over{3}-2=it-{1} over{3}$ 또는 $s={5} over{3}+2={11} over{3}$',
        '$s$는 $B$의 원소여야 하므로 $s=it-{1} over{3}$ ($B$에 속함). $s={11} over{3}$은 $B$에 없어 제외',
        '$g(x)=LEFT(x+{1} over{3} RIGHT)^{2}$',
        '$f(it-1)=it-{3} over{2}(it-1)+{1} over{2}={3} over{2}+{1} over{2}=2$이므로 $LEFT | f(it-1) RIGHT |=2$',
        '$g(it-1)=LEFT(it-1+{1} over{3} RIGHT)^{2}=LEFT(it-{2} over{3} RIGHT)^{2}={4} over{9}$',
        '$therefore~h(it-1)= log_{2}{4} over{9}= log_{2}4- log_{2}9$',
        '$=2-2 log_{2}3$',
    ],
    ch='로그의 밑과 진수 조건, 함수의 정의역', lv='상')
