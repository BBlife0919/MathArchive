# -*- coding: utf-8 -*-
"""소하고등학교 2학년 2026 1학기 중간 대수(지수로그~삼각함수의 그래프) 19문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ---------------------------------------------------------------- 객관식
add(id='q01', kind='mc', no=1, score=4.2, layout='3+2',
    text='$log_{2}3=a$이고, $log_{2}5=b$일 때, $log_{2}45$를 $a$와 $b$로 나타낸 것은?',
    choices=['$2ab$', '$a^{2}b$', '$a+b$', '$2a+b$', '$a+b+2$'],
    ans='④',
    sol=[
        '$log_{2}45=log_{2}(9 times5)=log_{2}9+log_{2}5$',
        '$=2log_{2}3+log_{2}5$',
        '$therefore~log_{2}45$',
        '$=2a+b$',
    ],
    ch='지수와 로그', lv='하')

add(id='q02', kind='mc', no=2, score=4.2, layout='1x5',
    text='$root{4} of{root{3} of{24}}-root{6} of{ sqrt{24}}$를 계산한 값은?',
    choices=['$0$', '$root{6} of{2}$', '$root{6} of{6}$', '$2 root{6} of{2}$', '$2 root{6} of{6}$'],
    ans='①',
    sol=[
        '$root{4} of{root{3} of{24}}=24^{{1} over{3} times{1} over{4}}=24^{{1} over{12}}$',
        '$root{6} of{ sqrt{24}}=24^{{1} over{2} times{1} over{6}}=24^{{1} over{12}}$',
        '두 값이 같으므로 $therefore$ 구하는 값은',
        '$0$이다.',
    ],
    ch='지수와 로그', lv='하')

add(id='q03', kind='mc', no=3, score=4.3, layout='3+2',
    text='반지름의 길이가 $8$이고, 넓이가 $8 pi$인 부채꼴의 중심각의 크기는?',
    choices=['${pi} over {4}$', '${pi} over {3}$', '${pi} over {2}$', '$pi$', '$2 pi$'],
    ans='①',
    sol=[
        '부채꼴의 넓이 $={1} over{2}r^{2} theta$',
        '$8 pi={1} over{2} times8^{2} times theta=32 theta$',
        '$therefore~theta$',
        '$={pi} over{4}$',
    ],
    ch='삼각함수', lv='하')

add(id='q04', kind='mc', no=4, score=4.4, layout='3+2',
    text='$sinLEFT({13} over {6}pi RIGHT)-cosLEFT(it- {pi} over {3} RIGHT)$의 값은?',
    choices=['$it- sqrt {3}$', '$it-1$', '$0$', '$1$', '$ sqrt {3}$'],
    ans='③',
    sol=[
        '$sinLEFT({13} over{6}pi RIGHT)=sinLEFT({13} over{6}pi-2 pi RIGHT)=sinLEFT({pi} over{6} RIGHT)={1} over{2}$',
        '$cosLEFT(it- {pi} over{3} RIGHT)=cos{pi} over{3}={1} over{2}$',
        '$therefore~sinLEFT({13} over{6}pi RIGHT)-cosLEFT(it- {pi} over{3} RIGHT)={1} over{2}- {1} over{2}$',
        '$=0$',
    ],
    ch='삼각함수', lv='중')

add(id='q05', kind='mc', no=5, score=4.5, layout='3+2', fig='shg26m_q05',
    text='다음 그림은 상용로그표의 일부이다. 그림을 이용하여 $log2180$의 값을 구하면?',
    choices=['$0.3385$', '$3.3385$', '$30.3385$', '$338.5$', '$3385$'],
    ans='②',
    sol=[
        '$log2180=logLEFT(2.18 times10^{3} RIGHT)=log2.18+3$',
        '표에서 $log2.18=0.3385$ (행 $2.1$, 열 $8$)',
        '$therefore~log2180=0.3385+3$',
        '$=3.3385$',
    ],
    ch='지수와 로그', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2',
    text='어느 금융상품에 $A$만원을 투자할 때, $t$년 후에 원금과 이익금의 합은 $ALEFT(1+LEFT({5} over {4} RIGHT)^{{t} over {2}} RIGHT)$만원이 된다고 한다. 처음 투자 금액이 $80$만원이고 $t$년 후에 원금과 이익금의 합이 $205$만원일 때, $t$의 값은?',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='②',
    sol=[
        '$80LEFT(1+LEFT({5} over{4} RIGHT)^{{t} over{2}} RIGHT)=205$',
        '$1+LEFT({5} over{4} RIGHT)^{{t} over{2}}={205} over{80}=2.5625={41} over{16}$',
        '$LEFT({5} over{4} RIGHT)^{{t} over{2}}={25} over{16}=LEFT({5} over{4} RIGHT)^{2}$',
        '${t} over{2}=2$에서 $therefore~t$',
        '$=4$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q07', kind='mc', no=7, score=4.8, layout='3+2',
    text='함수 $f(x)=2^{x+a}-3$의 역함수를 $g(x)$라 하자. 함수 $y=g(x)$의 그래프가 점 $(1,~3)$을 지나고, 점근선이 직선 $x=b$일 때, $ab$의 값은? (단, $a,~b$는 상수이다.)',
    choices=['$it-3$', '$it-1$', '$1$', '$3$', '$5$'],
    ans='④',
    sol=[
        '$g(1)=3$이므로 $f(3)=1$',
        '$f(3)=2^{3+a}-3=1$에서 $2^{3+a}=4=2^{2}$, $3+a=2$, $therefore~a=it-1$',
        '$f$의 점근선은 $y=it-3$이므로, 역함수 $g$의 점근선은 $x=it-3$. $therefore~b=it-3$',
        '$therefore~ab=(it-1)(it-3)$',
        '$=3$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2',
    text='실수 $a$에 대하여 ${3^{a}-3^{-a}} over {3^{a}+3^{-a}}={1} over {4}$일 때, $9^{a}+9^{-a}$의 값은?',
    choices=['$26/15$', '$28/15$', '$2$', '$32/15$', '$34/15$'],
    ans='⑤',
    sol=[
        '$x=3^{a}$, $y=3^{-a}$ ($xy=1$)라 하면 ${x-y} over{x+y}={1} over{4}$에서 $4(x-y)=x+y$, $3x=5y$',
        '$x:y=5:3$이므로 $x=5k$, $y=3k$ ($k>0$)라 하면 $xy=15k^{2}=1$에서 $k^{2}={1} over{15}$',
        '$9^{a}+9^{-a}=x^{2}+y^{2}=25k^{2}+9k^{2}=34k^{2}=34 times{1} over{15}$',
        '$therefore~9^{a}+9^{-a}$',
        '$=34/15$',
    ],
    ch='지수와 로그', lv='중')

add(id='q09', kind='mc', no=9, score=5.0, layout='1x5',
    text='$x$에 대한 방정식 $9^{x}-(2a+1)3^{x}+a^{2}+a-6=0$이 실근을 갖지 않도록 하는 실수 $a$의 값의 범위는?',
    choices=['$a<2$', '$a LEQ 2$', '$a LEQ it-3$', '$a>it-3$', '$it-3 LEQ a LEQ 2$'],
    ans='③',
    sol=[
        '$t=3^{x}>0$이라 하면 $t^{2}-(2a+1)t+LEFT(a^{2}+a-6 RIGHT)=0$',
        '좌변을 인수분해하면 $LEFT{t-(a+3) RIGHT}LEFT{t-(a-2) RIGHT}=0$ (∵ $(a+3)(a-2)=a^{2}+a-6$, 합 $(a+3)+(a-2)=2a+1$)',
        '$t=a+3$ 또는 $t=a-2$',
        '실근 $x$가 존재하지 않으려면 양의 실근 $t$가 존재하지 않아야 하므로 $a+3 LEQ 0$이고 $a-2 LEQ 0$',
        '$a LEQ it-3$이고 $a LEQ 2$이므로 $therefore~a$',
        '$LEQ it-3$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q10', kind='mc', no=10, score=5.1, layout='1x5',
    text='제 $2$사분면의 각 $theta$에 대하여 $LEFT | sinLEFT({pi} over {2}-theta RIGHT) RIGHT |+ sqrt{LEFT(cos^{2}theta-costheta+sin^{2}theta RIGHT)^{2}}=2$일 때, $tanLEFT({pi} over {2}+theta RIGHT)$의 값은?',
    choices=['$ sqrt {3}$', '$ sqrt {3}/3$', '$1$', '$it- sqrt {3}/3$', '$it- sqrt {3}$'],
    ans='②',
    sol=[
        '$sinLEFT({pi} over{2}-theta RIGHT)=costheta$이고, 제$2$사분면에서 $costheta<0$이므로 $LEFT | costheta RIGHT |=it-costheta$',
        '$cos^{2}theta-costheta+sin^{2}theta=1-costheta$이고, 제$2$사분면에서 $costheta<0$이므로 $1-costheta>0$, $sqrt{(1-costheta)^{2}}=1-costheta$',
        '$it-costheta+(1-costheta)=1-2costheta=2$에서 $costheta=it- {1} over{2}$',
        '제$2$사분면이므로 $theta={2} over{3}pi$, $sintheta={ sqrt{3}} over{2}$',
        '$tanLEFT({pi} over{2}+theta RIGHT)=it-cottheta=it- {costheta} over{sintheta}=it- { it- {1} over{2}} over{ {sqrt{3}} over{2}}={1} over{sqrt{3}}$',
        '$therefore~tanLEFT({pi} over{2}+theta RIGHT)$',
        '$= sqrt{3}/3$',
    ],
    ch='삼각함수', lv='상')

add(id='q11', kind='mc', no=11, score=5.2, layout='3+2',
    text='${2} over {3}pi<theta<pi$이고 각 $theta$를 나타내는 동경과 각 $9 theta$를 나타내는 동경이 원점에 대하여 대칭일 때, 각 $theta$의 크기를 ${a} over {b}pi$라 하자. 이때, $a+b$의 값은? (단, $a,~b$는 서로 소인 자연수이다.)',
    choices=['$7$', '$12$', '$15$', '$30$', '$33$'],
    ans='③',
    sol=[
        '두 동경이 원점에 대하여 대칭이므로 $9 theta=theta+pi+2k pi$ ($k$는 정수)',
        '$8 theta=pi+2k pi$에서 $theta={pi} over{8}+{k} over{4}pi$',
        '${2} over{3}pi<theta<pi$에 대입하여 정수 $k$를 찾으면 $k=3$일 때 $theta={pi} over{8}+{3} over{4}pi={7} over{8}pi$',
        '범위 확인: ${2} over{3}pi approx0.667 pi<{7} over{8}pi=0.875 pi<pi$ (성립)',
        '$theta={7} over{8}pi$이므로 $a=7$, $b=8$ (서로 소)',
        '$therefore~a+b=7+8$',
        '$=15$',
    ],
    ch='삼각함수', lv='상')

add(id='q12', kind='mc', no=12, score=5.3, layout='3+2',
    text='방정식 $2log(x+2)+logLEFT(x-3 RIGHT)^{2}=log36$의 모든 근의 합은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='⑤',
    sol=[
        '$2log(x+2)=logLEFT(x+2 RIGHT)^{2}$이므로 $logLEFT{(x+2)^{2}(x-3)^{2} RIGHT}=log36$',
        '$LEFT{(x+2)(x-3) RIGHT}^{2}=36$에서 $(x+2)(x-3)=pm6$',
        '$(x+2)(x-3)=6$: $x^{2}-x-12=0$, $(x-4)(x+3)=0$, $x=4$ 또는 $x=it-3$',
        '$(x+2)(x-3)=it-6$: $x^{2}-x=0$, $x(x-1)=0$, $x=0$ 또는 $x=1$',
        '정의역($x+2>0$, 즉 $x>it-2$)을 만족하는 근: $x=4,~0,~1$ ($x=it-3$은 제외)',
        '$therefore$ 모든 근의 합은 $4+0+1$',
        '$=5$',
    ],
    ch='지수와 로그', lv='상')

add(id='q13', kind='mc', no=13, score=5.3, layout='3+2',
    text='부등식 $LEFT(x^{2}+1 RIGHT)^{log_{3}{1} over {5}} LEQ 5^{log_{{1} over {3}}(2x+4)}$의 해가 $alpha<x LEQ beta$ 또는 $x GEQ gamma$일 때, $alpha+beta+gamma$의 값은? (단, $alpha,~beta,~gamma$는 상수이다.)',
    choices=['$it-1$', '$it-2/3$', '$it-1/3$', '$0$', '$1/3$'],
    ans='④',
    sol=[
        '$A^{log_{3}B}=B^{log_{3}A}$ 성질을 이용: 좌변 $=LEFT({1} over{5} RIGHT)^{log_{3}LEFT(x^{2}+1 RIGHT)}$',
        '$log_{{1} over{3}}(2x+4)={log_{3}(2x+4)} over{log_{3}{1} over{3}}=it-log_{3}(2x+4)$이므로 우변 $=5^{it-log_{3}(2x+4)}=LEFT({1} over{5} RIGHT)^{log_{3}(2x+4)}$',
        '부등식: $LEFT({1} over{5} RIGHT)^{log_{3}LEFT(x^{2}+1 RIGHT)} LEQ LEFT({1} over{5} RIGHT)^{log_{3}(2x+4)}$',
        '밑 ${1} over{5}<1$이므로 $log_{3}LEFT(x^{2}+1 RIGHT) GEQ log_{3}(2x+4)$, 즉 $x^{2}+1 GEQ 2x+4$',
        '$x^{2}-2x-3 GEQ 0$에서 $(x-3)(x+1) GEQ 0$, $x LEQ it-1$ 또는 $x GEQ 3$',
        '진수조건 $2x+4>0$에서 $x>it-2$',
        '$x>it-2$와 연립: $it-2<x LEQ it-1$ 또는 $x GEQ 3$',
        '$therefore~alpha=it-2,~beta=it-1,~gamma=3$',
        '$alpha+beta+gamma=it-2-1+3$',
        '$=0$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q14', kind='mc', no=14, score=5.5, layout='3+2',
    text='두 자연수 $m,~n$에 대하여 $0 LEQ x LEQ 4n$에서 정의된 함수 $y=mcosLEFT({pi} over {4}x RIGHT)$의 그래프가 직선 $y=0$과 만나는 점의 개수가 $17$개이고, 직선 $y=5$와 만나는 점의 개수가 $9$개일 때, $m+n$의 값은?',
    choices=['$14$', '$21$', '$22$', '$23$', '$26$'],
    ans='③',
    sol=[
        '$cosLEFT({pi} over{4}x RIGHT)=0$의 해는 $x=2+4k$ ($k$는 정수). $0 LEQ x LEQ 4n$에서 $k=0,~1, cdots,~n-1$로 $n$개',
        '$n$개 $=17$이므로 $therefore~n=17$',
        '$y=5$와 만나려면 $cosLEFT({pi} over{4}x RIGHT)={5} over{m}$이고 $LEFT | {5} over{m} RIGHT | LEQ 1$이어야 함',
        '만나는 점이 $9$개(비교적 적은 개수)이므로 극값(${5} over{m}=1$)에서 만나는 경우로 추정: $m=5$라 하면 $cosLEFT({pi} over{4}x RIGHT)=1$의 해는 $x=8k$',
        '$0 LEQ x LEQ 68$(=$4 times17$)에서 $k=0,~1, cdots,~8$로 $9$개 (조건과 일치)',
        {'fig': 'shg26m_q14_sol'},
        '$therefore~m=5$',
        '$therefore~m+n=5+17$',
        '$=22$',
    ],
    ch='삼각함수', lv='상')

add(id='q15', kind='mc', no=15, score=5.6, layout='3+2',
    text='실수 $x$에 대하여 $x$의 세제곱근 중에서 실수인 것의 개수를 $f(x)$, $x$의 네제곱근 중에서 실수인 것의 개수를 $g(x)$라 하자. $2LEFT | a RIGHT |+LEFT | b RIGHT | LEQ 4$를 만족시키는 두 정수 $a,~b$에 대하여 $1 LEQ f(a)+g(b)<3$을 만족시키는 모든 순서쌍 $(a,~b)$의 개수는?',
    choices=['$5$', '$8$', '$11$', '$13$', '$26$'],
    ans='④',
    sol=[
        '세제곱근(홀수차)은 항상 실수 전체에서 유일하게 $1$개 존재하므로 $f(a)=1$ (모든 실수 $a$)',
        '네제곱근(짝수차): $b>0$이면 $2$개, $b=0$이면 $1$개, $b<0$이면 $0$개',
        '$1 LEQ 1+g(b)<3$에서 $0 LEQ g(b)<2$, 즉 $g(b)=0$ 또는 $1$, 따라서 $b LEQ 0$',
        '$2 LEQ |a| LEQ 4$가 아니라 $2LEFT | a RIGHT |+LEFT | b RIGHT | LEQ 4$이고 $b LEQ 0$이므로, 각 정수 $a$ ($LEFT | a RIGHT | LEQ 2$)에 대해 $LEFT | b RIGHT | LEQ 4-2LEFT | a RIGHT |$이고 $b LEQ 0$인 정수 $b$의 개수는 $(4-2LEFT | a RIGHT |)+1$개',
        '$a=0$: $5$개, $a=pm1$: $3$개씩, $a=pm2$: $1$개씩',
        '$therefore$ 총 개수 $=5+3+3+1+1$',
        '$=13$개',
    ],
    ch='지수와 로그', lv='상')

add(id='q16', kind='mc', no=16, score=5.7, layout='3+2', emptybox={'paras': [
        '$f(x)= cases{log_{2}(it-x+7)~~(x<5)#log_{2}(x-3)+k~~(x GEQ 5)}$',
    ]},
    text='위 함수 $f(x)$에 대하여 $y=f(x)$의 그래프와 직선 $y=t$의 교점의 개수가 $1$개가 되는 정수 $t$의 개수를 $h(k)$라 하자. 정수 전체의 집합에서 정의된 두 함수 $h(k)$와 $g(k)=aLEFT | k+b RIGHT |$에 대하여 정의역이 각 원소 $k$가 $h(k)=g(k)$를 만족할 때, $ab$의 값은? (단, $k$는 정수이고, $a,~b$는 실수이다.)',
    choices=['$it-2$', '$it-1$', '$0$', '$1$', '$2$'],
    ans='②',
    sol=[
        '$x<5$에서 $f(x)=log_{2}(7-x)$는 감소함수로 치역 $(1,~ infty)$ (열림)',
        '$x GEQ 5$에서 $f(x)=log_{2}(x-3)+k$는 증가함수로 치역 $[1+k,~ infty)$ (닫힘, $x=5$일 때 $log_{2}2+k=1+k$)',
        '직선 $y=t$와 교점이 $1$개: 두 치역 중 정확히 하나에만 $t$가 속할 때',
        '$k>0$인 경우: $1<t<1+k$인 정수 $t$ (첫 번째 치역만 해당)의 개수 $=k-1$',
        '$k LEQ 0$인 경우: $1+k LEQ t LEQ 1$인 정수 $t$(두 번째 치역만 해당)의 개수 $=1-k$',
        '정리하면 $h(k)=LEFT | k-1 RIGHT |$ (모든 정수 $k$에서 성립, 검산: $k=0$이면 $h=1$, $k=1$이면 $h=0$)',
        '$h(k)=g(k)=aLEFT | k+b RIGHT |$가 모든 정수 $k$에서 성립하려면 $a=1$, $b=it-1$',
        '$therefore~ab=1 times(it-1)$',
        '$=it-1$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q17', kind='mc', no=17, score=5.7, layout='3+2', jogeon=True,
    jogeon_items=[
        '함수 $g(x)$는 일대일 함수가 아니다.',
        '함수 $g(x)$의 최댓값은 $8$, 최솟값은 $1/64$이다.',
    ],
    text='정의역이 $LEFT{x|0 LEQ x LEQ 5 RIGHT}$이고 최고차항의 계수가 $1$인 이차함수 $f(x)$에 대하여 $g(x)=LEFT({1} over {2} RIGHT)^{f(x)}$라 할 때, 함수 $g(x)$가 위 조건을 만족시킨다. $g(4)<1$일 때, $g(1)$의 값은?',
    choices=['$4$', '$2$', '$1$', '$1/2$', '$1/4$'],
    ans='①',
    sol=[
        '밑 ${1} over{2}<1$이므로 $g$는 $f$에 대해 감소함수: $g$ 최대일 때 $f$ 최소, $g$ 최소일 때 $f$ 최대',
        '조건 (가)에서 $g$가 일대일이 아니므로 $f$의 꼭짓점 $x=h$가 $(0,~5)$ 내부에 있다',
        '$f$는 최고차항 계수 $1$(아래로 볼록)이므로 최솟값은 $f(h)$, 최댓값은 $f(0)$, $f(5)$ 중 큰 값',
        '$g$ 최댓값 $8=2^{3}$에서 $LEFT({1} over{2} RIGHT)^{f(h)}=2^{3}$, $f(h)=it-3$',
        '$g$ 최솟값 ${1} over{64}=2^{it-6}$에서 $LEFT({1} over{2} RIGHT)^{max f}=2^{it-6}$, $max f=6$',
        '$f(x)=(x-h)^{2}-3$. $f(0)=h^{2}-3$, $f(5)=(5-h)^{2}-3$',
        '만약 $f(0)=6$이면 $h^{2}=9$, $h=3$ ($0<h<5$). 이때 $f(5)=4-3=1<6$ (일치), 그런데 $f(4)=1-3=it-2 LEQ 0$이므로 $g(4)=2^{2}=4 GEQ 1$ (조건 $g(4)<1$에 모순)',
        '따라서 $f(5)=6$인 경우: $(5-h)^{2}=9$, $h=2$ ($0<h<5$). $f(0)=4-3=1<6$ (일치)',
        '검산: $f(4)=(4-2)^{2}-3=1>0$이므로 $g(4)=LEFT({1} over{2} RIGHT)^{1}={1} over{2}<1$ (조건 성립)',
        '$therefore~f(x)=(x-2)^{2}-3$',
        '$f(1)=(1-2)^{2}-3=1-3=it-2$',
        '$g(1)=LEFT({1} over{2} RIGHT)^{it-2}=2^{2}$',
        '$=4$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q18', kind='mc', no=18, score=5.8, layout='1x5',
    text='$0 LEQ x LEQ {2} over {3}pi$일 때, 방정식 $sinLEFT(3x- {2} over {3}pi RIGHT)=cosLEFT({2} over {3}pi-2x RIGHT)$의 모든 해의 합은?',
    choices=['$11 pi/30$', '$pi/2$', '$3 pi/5$', '$7 pi/10$', '$13 pi/15$'],
    ans='⑤',
    sol=[
        '$cosLEFT({2} over{3}pi-2x RIGHT)=sinLEFT({pi} over{2}-LEFT({2} over{3}pi-2x RIGHT) RIGHT)=sinLEFT(2x- {pi} over{6} RIGHT)$',
        '$sinLEFT(3x- {2} over{3}pi RIGHT)=sinLEFT(2x- {pi} over{6} RIGHT)$',
        '경우(1): $3x- {2} over{3}pi=2x- {pi} over{6}+2k pi$에서 $x= {pi} over{2}+2k pi$. $0 LEQ x LEQ {2} over{3}pi$에서 $k=0$일 때 $x= {pi} over{2}$ (유효)',
        '경우(2): $3x- {2} over{3}pi=pi-LEFT(2x- {pi} over{6} RIGHT)+2k pi$에서 $5x= {11} over{6}pi+2k pi$, $x= {11} over{30}pi+ {2k} over{5}pi$',
        '$k=0$: $x={11} over{30}pi$ (범위 내, 유효). $k=1$: $x={23} over{30}pi>{2} over{3}pi={20} over{30}pi$ (범위 밖). $k=it-1$: 음수 (범위 밖)',
        '$therefore$ 모든 해: $x={pi} over{2},~ {11} over{30}pi$. 합 $={15} over{30}pi+ {11} over{30}pi={26} over{30}pi$',
        '$=13 pi/15$',
    ],
    ch='삼각함수', lv='상')

# ---------------------------------------------------------------- 서술형
add(id='q19', kind='sub', no=1, score=10.0, jogeon=True,
    jogeon_items=[
        '집합 $B=LEFT{x|x`in`A^{c} RIGHT}$ ($x$는 실수)의 원소의 개수는 $3$이고, 모든 원소의 합과 곱은 각각 $1,~{it-1/9}$이다.',
        '이차방정식 $g(x)=0$의 실근이 존재한다.',
        '$hLEFT({5} over {3} RIGHT)=2$',
    ],
    text='최고차항의 계수가 음수인 일차식 $f(x)$와 최고차항의 계수가 $1$인 이차식 $g(x)$가 있다. 함수 $h(x)$를 $h(x)=log_{LEFT | f(x) RIGHT |}g(x)$라 하고, 함수 $h(x)$의 정의역을 집합 $A$라 할 때, 함수 $h(x)$가 다음 조건을 만족시킨다. 다음 물음에 답하시오.',
    text2=['(1) 집합 $B$를 원소나열법으로 제시하고 그 과정을 서술하시오. 이를 바탕으로 조건을 만족시키는 다항식 $f(x)$를 쓰고 그 과정을 서술하시오. [$4$점]',
           '(2) 조건을 만족시키는 $g(x)$와 $h(it-1)$의 값을 구하고 그 과정을 서술하시오. [$6$점]'],
    ans_mix='풀이 참조',
    sol=[
        '(1) $h$가 정의되지 않는 점: $f(x)=0$인 점, $LEFT | f(x) RIGHT |=1$ 즉 $f(x)=pm1$인 점, $g(x) LEQ 0$인 점',
        '$f$는 일차식이므로 $f(x)=0,~1,~{it-1}$은 각각 정확히 한 점씩 준다(총 $3$개, 서로 다름)',
        '집합 $B$가 정확히 $3$개이려면 "$g(x) LEQ 0$"이 새 점을 추가하면 안 되므로, $g(x) GEQ 0$ 항상 성립(아래로 볼록)하면서 조건(2)에 의해 실근이 존재 — 즉 $g$는 중근을 가지며 그 중근이 위 세 점 중 하나와 겹친다',
        '$B=LEFT{x_{0},~x_{1},~x_{it-1} RIGHT}$ ($f(x_{0})=0$, $f(x_{1})=1$, $f(x_{it-1})=it-1$)라 하면, $f$가 일차식이므로 이 세 점은 공차 $1/m$인 등차수열을 이룬다 ($f(x)=mx+c$, $m<0$)',
        '합 $=3x_{0}=1$에서 $x_{0}=1/3$',
        '곱 $=x_{0}LEFT(x_{0}^{2}- {1} over{m^{2}} RIGHT)=it- {1} over{9}$에 $x_{0}=1/3$ 대입: ${1} over{3}LEFT({1} over{9}- {1} over{m^{2}} RIGHT)=it- {1} over{9}$에서 ${1} over{m^{2}}={4} over{9}$, $m^{2}={9} over{4}$',
        '$f$의 최고차항 계수가 음수이므로 $m=it- {3} over{2}$',
        '$x_{0}=it-c/m=1/3$에서 $c=it-m/3=1/2$',
        '$therefore~f(x)=it- {3} over{2}x+ {1} over{2}$. 검산: $f(1/3)=0$, $f(it-1/3)=1$, $f(1)=it-1$',
        '$therefore~B=LEFT{1,~ {1} over{3},~{it- {1} over{3}} RIGHT}$',
        '(2) $g$의 중근 $r$은 $B$의 세 원소 중 하나와 같아야 하므로 $r`in`LEFT{1,~ {1} over{3},~{it- {1} over{3}} RIGHT}$, $g(x)=(x-r)^{2}$',
        '$fLEFT({5} over{3} RIGHT)=it- {3} over{2} times {5} over{3}+ {1} over{2}=it- {5} over{2}+ {1} over{2}=it-2$. $LEFT | fLEFT({5} over{3} RIGHT) RIGHT |=2$',
        '$hLEFT({5} over{3} RIGHT)=log_{2}gLEFT({5} over{3} RIGHT)=2$에서 $gLEFT({5} over{3} RIGHT)=4$',
        '$LEFT({5} over{3}-r RIGHT)^{2}=4$에서 $r={5} over{3}-2=it- {1} over{3}$ 또는 $r={5} over{3}+2={11} over{3}$',
        '$r={11} over{3}$은 $B$의 원소가 아니므로(B가 $4$개로 늘어남) 제외, $therefore~r=it- {1} over{3}$',
        '$g(x)=LEFT(x+ {1} over{3} RIGHT)^{2}$',
        '$f(it-1)=it- {3} over{2} times(it-1)+ {1} over{2}= {3} over{2}+ {1} over{2}=2$. $LEFT | f(it-1) RIGHT |=2$',
        '$g(it-1)=LEFT(it-1+ {1} over{3} RIGHT)^{2}=LEFT(it- {2} over{3} RIGHT)^{2}={4} over{9}$',
        '$therefore~h(it-1)=log_{2}gLEFT(it-1 RIGHT)=log_{2}{4} over{9}$',
        '$=log_{2}4-log_{2}9=2-2log_{2}3$',
    ],
    ch='지수함수와 로그함수', lv='상')
