# -*- coding: utf-8 -*-
"""소하고등학교 2학년 2024 1학기 중간 수학1 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ---------------------------------------------------------------- 객관식
add(id='q01', kind='mc', no=1, score=4.4, layout='3+2',
    text='$LEFT(root{5} of{27^{10}} RIGHT)^{{1} over {4}} div3^{{3} over {4}}$의 값은?',
    choices=['$3^{it- {3} over {4}}$', '$3^{it- {1} over {4}}$', '$1$', '$3^{{1} over {4}}$', '$3^{{3} over {4}}$'],
    ans='⑤',
    sol=[
        '$27=3^{3}$이므로 $27^{10}=3^{30}$',
        '$root{5} of{3^{30}}=3^{{30} over{5}}=3^{6}$',
        '$LEFT(3^{6} RIGHT)^{{1} over{4}}=3^{{6} over{4}}=3^{{3} over{2}}$',
        '$therefore~3^{{3} over{2}} div3^{{3} over{4}}=3^{{3} over{2}-{3} over{4}}=3^{{3} over{4}}$',
    ],
    ch='지수', lv='하')

add(id='q02', kind='mc', no=2, score=4.5, layout='3+2',
    text='동경 $rm OP$가 나타내는 한 각의 크기가 $135 DEG$일 때, 다음 중 동경 $rm OP$가 나타내는 각이 아닌 것은?',
    choices=['$it- {13} over {4}pi$', '$it- {5} over {4}pi$', '$it- {3} over {4}pi$', '${3} over {4}pi$', '${11} over {4}pi$'],
    ans='③',
    sol=[
        '$135 DEG={3} over{4}pi$',
        '동경 $rm OP$가 나타내는 각은 ${3} over{4}pi+2kpi$ ($k$는 정수) 꼴이다.',
        '$it- {13} over{4}pi={3} over{4}pi+2 times(it-2)pi$이므로 해당한다. (①)',
        '$it- {5} over{4}pi={3} over{4}pi+2 times(it-1)pi$이므로 해당한다. (②)',
        '${3} over{4}pi$는 $k=0$일 때이므로 해당한다. (④)',
        '${11} over{4}pi={3} over{4}pi+2 times1 times pi$이므로 해당한다. (⑤)',
        '$it- {3} over{4}pi$는 ${3} over{4}pi+2kpi$ 꼴이 될 수 없다.',
        '$therefore$ 동경 $rm OP$가 나타내는 각이 아닌 것은 ③이다.',
    ],
    ch='일반각과 호도법', lv='중')

add(id='q03', kind='mc', no=3, score=4.6, layout='3+2',
    text='${1} over {log_{9}12}+2log_{12}5 times log_{5}4$의 값은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='②',
    sol=[
        '${1} over{log_{9}12}=log_{12}9$',
        '$2log_{12}5 timeslog_{5}4=2log_{12}4$',
        '$therefore~log_{12}9+2log_{12}4=log_{12}9+log_{12}16=log_{12}(9 times16)$',
        '$=log_{12}144=log_{12}12^{2}$',
        '$=2$',
    ],
    ch='로그', lv='중')

add(id='q04', kind='mc', no=4, score=4.6, layout='3+2',
    text='$a>0$이고 $a^{{1} over {2}}-a^{it- {1} over {2}}=5$일 때, $a^{{3} over {2}}-a^{it- {3} over {2}}$의 값은?',
    choices=['$120$', '$125$', '$130$', '$135$', '$140$'],
    ans='⑤',
    sol=[
        '$p=a^{{1} over{2}}$, $q=a^{it- {1} over{2}}$라 하면 $p-q=5$, $pq=1$',
        '$(p-q)^{3}=p^{3}-q^{3}-3pq(p-q)$이므로',
        '$5^{3}=LEFT(a^{{3} over{2}}-a^{it- {3} over{2}} RIGHT)-3 times1 times5$',
        '$125=LEFT(a^{{3} over{2}}-a^{it- {3} over{2}} RIGHT)-15$',
        '$therefore~a^{{3} over{2}}-a^{it- {3} over{2}}=140$',
    ],
    ch='지수', lv='중')

add(id='q05', kind='mc', no=5, score=4.7, layout='3+2',
    text='함수 $y=3^{x+1}-1$의 그래프 위의 점 $(a,~b)$와 함수 $y=3^{x+1}-1$의 그래프의 점근선 사이의 거리가 $3$일 때, $a+b$의 값은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='②',
    sol=[
        '점근선은 $y=it-1$이므로 점 $(a,~b)$와의 거리는 $LEFT | b-(it-1) RIGHT |=LEFT | b+1 RIGHT |=3$',
        '$b=3^{a+1}-1$이므로 $b+1=3^{a+1}>0$',
        '$therefore~b+1=3$',
        '$3^{a+1}=3$에서 $a+1=1$',
        '$therefore~a=0$',
        '$b=3^{1}-1=2$',
        '$therefore~a+b=0+2=2$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q06', kind='mc', no=6, score=4.7, layout='3+2',
    text='소리의 크기가 $A`rm(dB)$와 소리의 세기 $I`rm(W/m^{2})$ 사이에는 $A=10logLEFT({I} over {10^{it-12}} RIGHT)$의 관계가 성립한다고 한다. 기차 소리의 크기가 $100`rm(dB)$일 때의 소리의 세기를 $I_{x}`rm(W/m^{2})$이라 할 때, $I_{x}$의 값은?',
    choices=['${1} over {10^{2}}$', '${1} over {10}$', '$1$', '$10$', '$10^{2}$'],
    ans='①',
    sol=[
        '$100=10logLEFT({I_{x}} over{10^{it-12}} RIGHT)$',
        '$logLEFT({I_{x}} over{10^{it-12}} RIGHT)=10$',
        '${I_{x}} over{10^{it-12}}=10^{10}$',
        '$therefore~I_{x}=10^{10} times10^{it-12}=10^{it-2}$',
        '$={1} over{10^{2}}$',
    ],
    ch='지수함수와 로그함수의 활용', lv='중')

add(id='q07', kind='mc', no=7, score=4.8, layout='3+2',
    text='$20$ 이하의 자연수 $n$에 대하여 $root{6} of{3} times root{3} of{9}$가 어떤 자연수 $a$의 $n$제곱근이 되도록 하는 모든 $a$값의 곱은?',
    choices=['$3^{15}$', '$3^{20}$', '$3^{25}$', '$3^{30}$', '$3^{35}$'],
    ans='④',
    sol=[
        '$root{6} of{3}=3^{{1} over{6}}$, $root{3} of{9}=9^{{1} over{3}}=3^{{2} over{3}}$',
        '$root{6} of{3} times root{3} of{9}=3^{{1} over{6}+{2} over{3}}=3^{{5} over{6}}$',
        '이 값이 자연수 $a$의 $n$제곱근이면 $LEFT(3^{{5} over{6}} RIGHT)^{n}=a$, 즉 $a=3^{{5n} over{6}}$',
        '$a$가 자연수이려면 ${5n} over{6}$이 음이 아닌 정수여야 하고, $gcd(5,~6)=1$이므로 $n$은 $6$의 배수이어야 한다.',
        '$20$ 이하의 $6$의 배수는 $n=6,~12,~18$',
        '$n=6$일 때 $a=3^{5}$, $n=12$일 때 $a=3^{10}$, $n=18$일 때 $a=3^{15}$',
        '$therefore$ 모든 $a$값의 곱은 $3^{5} times3^{10} times3^{15}=3^{30}$',
    ],
    ch='지수', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2',
    text='$sintheta-costheta={1} over {2}$일 때, ${1-tantheta} over {sintheta}$의 값은?',
    choices=['$it-2$', '$it- {4} over {3}$', '$it- {1} over {3}$', '${2} over {3}$', '$2$'],
    ans='②',
    sol=[
        '${1-tantheta} over{sintheta}={1-{sintheta} over{costheta}} over{sintheta}={costheta-sintheta} over{sinthetacostheta}=it- {sintheta-costheta} over{sinthetacostheta}$',
        '$(sintheta-costheta)^{2}=1-2sinthetacostheta=LEFT({1} over{2} RIGHT)^{2}={1} over{4}$',
        '$2sinthetacostheta=1-{1} over{4}={3} over{4}$',
        '$sinthetacostheta={3} over{8}$',
        '$therefore~it- LEFT({1} over{2} RIGHT) div LEFT({3} over{8} RIGHT)=it- {1} over{2} times{8} over{3}=it- {4} over{3}$',
    ],
    ch='삼각함수와 그래프', lv='중')

add(id='q09', kind='mc', no=9, score=4.9, layout='1x5', fig='shg24s_q9',
    text='그림과 같이 원점 $rm O$를 지나고 $x$축의 양의 방향과 이루는 각의 크기가 $theta$, $2 theta$인 직선을 각각 $l$, $m$이라 하고, 직선 $y=sqrt{3}$과 두 직선 $l$, $m$이 만나는 점을 각각 $rm A$, $rm B$라 하자. 삼각형 $rm OAB$의 넓이가 $sqrt{3}$일 때, $cos4 theta+tan7 theta$의 값은? (단, $0<theta<{pi} over {4}$)',
    choices=[
        '${it-3-2 sqrt{3}} over {6}$',
        '${3-2 sqrt{3}} over {6}$',
        '${it-3+2 sqrt{3}} over {6}$',
        '${3+2 sqrt{3}} over {6}$',
        '${it-1-sqrt{3}} over {2}$',
    ],
    ans='③',
    sol=[
        '직선 $l$: $y=tantheta times x$가 $y=sqrt{3}$과 만나는 점은 $rm A LEFT(sqrt{3}cottheta,~sqrt{3} RIGHT)$',
        '직선 $m$: $y=tan2 theta times x$가 $y=sqrt{3}$과 만나는 점은 $rm B LEFT(sqrt{3}cot2 theta,~sqrt{3} RIGHT)$',
        '두 점은 모두 직선 $y=sqrt{3}$ 위에 있으므로 $bar{rm AB}=sqrt{3}LEFT(cottheta-cot2 theta RIGHT)$',
        '원점 $rm O$에서 직선 $y=sqrt{3}$까지의 거리는 $sqrt{3}$이므로',
        '삼각형 $rm OAB$의 넓이 $={1} over{2} timesbar{rm AB} timessqrt{3}={3} over{2}LEFT(cottheta-cot2 theta RIGHT)=sqrt{3}$',
        '$therefore~cottheta-cot2 theta={2} over {sqrt{3}}$',
        '$cottheta-cot2 theta={costheta} over{sintheta}-{cos2 theta} over{sin2 theta}={costhetasin2 theta-cos2 thetasintheta} over{sinthetasin2 theta}={sinLEFT(2 theta-theta RIGHT)} over{sinthetasin2 theta}={1} over{sin2 theta}$',
        '$therefore~{1} over{sin2 theta}={2} over{sqrt{3}}$에서 $sin2 theta={sqrt{3}} over {2}$',
        '$0<theta<{pi} over{4}$에서 $0<2 theta<{pi} over{2}$이므로 $2 theta={pi} over{3}$',
        '$therefore~theta={pi} over{6}$',
        '$4 theta={2} over{3}pi$이므로 $cos4 theta=cosLEFT({2} over{3}pi RIGHT)=it- {1} over{2}$',
        '$7 theta={7} over{6}pi$이므로 $tan7 theta=tanLEFT({7} over{6}pi RIGHT)=tanLEFT({pi} over{6} RIGHT)={sqrt{3}} over{3}$',
        '$therefore~cos4 theta+tan7 theta=it- {1} over{2}+{sqrt{3}} over{3}={it-3+2 sqrt{3}} over{6}$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q10', kind='mc', no=10, score=4.9, layout='3+2',
    text='두 곡선 $y=log_{2}(x-2)$, $y=log_{4}(x+10)+{1} over {2}$의 교점의 $y$좌표는?',
    choices=['$0$', '$1$', '$log_{2}3$', '$log_{2}3+1$', '$2log_{2}3$'],
    ans='④',
    sol=[
        '$log_{4}(x+10)={1} over{2}log_{2}(x+10)$이므로',
        '${1} over{2}log_{2}(x+10)+{1} over{2}={1} over{2}LEFT{log_{2}(x+10)+1 RIGHT}={1} over{2}log_{2}LEFT{2(x+10) RIGHT}$',
        '$log_{2}(x-2)={1} over{2}log_{2}(2x+20)$의 양변에 $2$를 곱하면',
        '$2log_{2}(x-2)=log_{2}(2x+20)$',
        '$log_{2}LEFT{(x-2)^{2} RIGHT}=log_{2}(2x+20)$',
        '$(x-2)^{2}=2x+20$',
        '$x^{2}-4x+4=2x+20$',
        '$x^{2}-6x-16=0$',
        '$(x-8)(x+2)=0$',
        '진수 조건 $x>2$에서 $therefore~x=8$',
        '$y=log_{2}(8-2)=log_{2}6=log_{2}(2 times3)$',
        '$=1+log_{2}3$',
    ],
    ch='지수함수와 로그함수', lv='중')

add(id='q11', kind='mc', no=11, score=5.0, layout='1x5', emptybox={'paras': [
        '$n$은 $15$ 이하의 자연수이다.',
        '$a$는 음의 정수이고, $LEFT | a RIGHT |<n$이다.',
        '$a$의 $n$제곱근 중 실수인 것이 존재한다.',
    ]},
    text='다음 조건을 만족시키는 모든 순서쌍 $(a,~n)$의 개수는?',
    choices=['$56$개', '$57$개', '$58$개', '$59$개', '$60$개'],
    ans='①',
    sol=[
        '$a$가 음수이므로 $a$의 $n$제곱근 중 실수인 것이 존재하려면 $n$이 홀수이어야 한다.',
        '$15$ 이하의 홀수 $n$은 $1,~3,~5,~7,~9,~11,~13,~15$',
        '각 $n$에 대하여 $LEFT | a RIGHT |<n$을 만족시키는 음의 정수 $a$는 $it-1,~it-2,~ cdots,~it-(n-1)$의 $(n-1)$개',
        '$n=1$일 때 $0$개, $n=3$일 때 $2$개, $n=5$일 때 $4$개, $n=7$일 때 $6$개,',
        '$n=9$일 때 $8$개, $n=11$일 때 $10$개, $n=13$일 때 $12$개, $n=15$일 때 $14$개',
        '$therefore$ 모든 순서쌍의 개수는 $0+2+4+6+8+10+12+14=56$개',
    ],
    ch='지수', lv='상')

add(id='q12', kind='mc', no=12, score=5.0, layout='3+2',
    text='두 양수 $a$, $b$ $(a>b)$에 대하여 $7^{(a-b)^{2}}=27$, $ab={1} over {4}log_{7}3$일 때, ${b} over {a}+{a} over {b}$의 값은?',
    choices=['$7$', '$8 sqrt{3}$', '$14$', '$16 sqrt{3}$', '$21$'],
    ans='③',
    sol=[
        '$7^{(a-b)^{2}}=27=3^{3}$의 양변에 밑이 $7$인 로그를 취하면 $(a-b)^{2}=3log_{7}3$',
        '$ab={1} over{4}log_{7}3$에서 $log_{7}3=4ab$',
        '$therefore~(a-b)^{2}=3 times4ab=12ab$',
        '$a^{2}-2ab+b^{2}=12ab$',
        '$a^{2}+b^{2}=14ab$',
        '${b} over{a}+{a} over{b}={a^{2}+b^{2}} over{ab}={14ab} over{ab}$',
        '$=14$',
    ],
    ch='로그', lv='상')

add(id='q13', kind='mc', no=13, score=5.0, layout='3+2',
    text='부등식 $log_{2}x times log_{2}4x LEQ 15$를 만족시키는 자연수의 개수는?',
    choices=['$2$개', '$4$개', '$6$개', '$8$개', '$10$개'],
    ans='④',
    sol=[
        '$log_{2}4x=2+log_{2}x$',
        '$t=log_{2}x$라 하면 $t(t+2) LEQ 15$',
        '$t^{2}+2t-15 LEQ 0$',
        '$(t+5)(t-3) LEQ 0$',
        '$therefore~it-5 LEQ t LEQ 3$',
        '$it-5 LEQ log_{2}x LEQ 3$에서 $2^{it-5} LEQ x LEQ 2^{3}$',
        '${1} over{32} LEQ x LEQ 8$',
        '이를 만족시키는 자연수 $x$는 $1,~2,~ cdots,~8$의 $8$개',
    ],
    ch='로그', lv='중')

add(id='q14', kind='mc', no=14, score=5.1, layout='1x5',
    text='도형 $LEFT | x RIGHT |+LEFT | y RIGHT |=k$ $(k>1)$가 두 함수 $y=a^{x}$, $y=log_{a}x$의 그래프와 제$1$사분면에서 만나는 점을 각각 $rm A$, $rm B$라 하고, 도형 $LEFT | x RIGHT |+LEFT | y RIGHT |=k$ $(k>1)$가 함수 $y=it- log_{a}(it-x)$의 그래프와 제$3$사분면에서 만나는 점을 $rm C$라 하자. 삼각형 $rm ABC$의 무게중심의 좌표가 $(2,~1)$일 때, ${k} over {a^{6}}$의 값은? (단, $a NEQ 1$이다.)',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='①',
    sol=[
        '함수 $y=a^{x}$와 $y=log_{a}x$는 서로 역함수 관계이므로 직선 $y=x$에 대하여 대칭이다.',
        '$rm A(p,~q)$이면 $y=x$ 대칭점 $(q,~p)$가 $y=log_{a}x$ 위에 있고, 도형 $LEFT | x RIGHT |+LEFT | y RIGHT |=k$도 $y=x$ 대칭이므로 $rm B(q,~p)$',
        '함수 $y=it- log_{a}(it-x)$는 $y=log_{a}x$를 원점에 대하여 대칭이동한 것이고, 도형도 원점 대칭이므로 $rm C(it-q,~it-p)$',
        '무게중심 $=LEFT({p+q-q} over{3},~{q+p-p} over{3} RIGHT)=LEFT({p} over{3},~{q} over{3} RIGHT)=(2,~1)$',
        '$therefore~p=6$, $q=3$',
        '$rm A(6,~3)$은 $y=a^{x}$ 위의 점이므로 $a^{6}=3$',
        '$rm A$는 도형 위의 점이므로 $k=LEFT | 6 RIGHT |+LEFT | 3 RIGHT |=9$',
        '$therefore~{k} over{a^{6}}={9} over{3}$',
        '$=3$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q15', kind='mc', no=15, score=5.1, layout='1x5', fig='shg24s_q15',
    text='어느 하수처리장에 서식하고 있는 박테리아를 제거하기 위해서 약품을 투여하려고 한다. 하수처리장에 있는 물 $1`rm mL$당 초기 박테리아 수를 $C_{0}$, 약품을 투여한 지 $t$시간이 지나는 순간 물 $1`rm mL$당 박테리아 수를 $C$라 할 때, 다음 관계식이 성립한다고 하자. $logC=logC_{0}-kt$ ($k$는 양의 상수) 물 $1`rm mL$당 초기 박테리아 수가 $12 times10^{5}$이고, 약품을 투여한 지 $5$시간이 지나는 순간 물 $1`rm mL$당 박테리아 수는 $6 times10^{5}$이 된다고 한다. 약품을 투여한 지 $7$시간이 지나는 순간 물 $1`rm mL$당 박테리아 수는 초기 박테리아 수의 몇 $%$인가? (단, $log2=0.3$으로 계산한다.)',
    choices=['$35 %$', '$36.5 %$', '$37 %$', '$37.5 %$', '$38 %$'],
    ans='⑤',
    sol=[
        '$logC-logC_{0}=it-kt$이므로 $logLEFT({C} over{C_{0}} RIGHT)=it-kt$',
        '$t=5$일 때 ${C} over{C_{0}}={6 times10^{5}} over{12 times10^{5}}={1} over{2}$이므로 $logLEFT({1} over{2} RIGHT)=it-log2=it-0.3=it-5k$',
        '$therefore~k=0.06$',
        '$t=7$일 때 $logLEFT({C} over{C_{0}} RIGHT)=it-7k=it-0.42=it-1+0.58$',
        '표에서 $log3.80=0.580$이므로 ${C} over{C_{0}}=10^{it-1+0.58}=10^{it-1} times10^{0.58}=0.1 times3.80$',
        '$=0.38$',
        '$therefore$ 초기 박테리아 수의 $38 %$이다.',
    ],
    ch='지수함수와 로그함수의 활용', lv='중')

add(id='q16', kind='mc', no=16, score=5.2, layout='1x5', box=True,
    text='${1} over {3}<a<1$인 실수 $a$에 대하여 두 곡선 $y=log_{a}x$, $y=log_{3a}x$과 직선 $y=1$이 만나는 점을 각각 $rm A$, $rm B$라 하고, 두 곡선 $y=log_{a}x$, $y=log_{3a}x$과 직선 $y=it-1$이 만나는 점을 각각 $rm C$, $rm D$라 하자. <보기>에서 옳은 것만을 있는 대로 고른 것은?',
    box_items=[
        '선분 $rm CD$를 $3`:`1$로 외분하는 점은 $y$축 위에 있다.',
        '선분 $rm AC$와 선분 $rm BD$의 교점은 $x$축 위에 있다.',
        '$bar{rm AB}=bar{rm CD}$이면 사각형 $rm ABCD$는 직사각형이다.',
    ],
    choices=['ㄱ', 'ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ'],
    ans='③',
    sol=[
        '$y=log_{a}x=1$에서 $x=a$이므로 $rm A(a,~1)$',
        '$y=log_{3a}x=1$에서 $x=3a$이므로 $rm B(3a,~1)$',
        '$y=log_{a}x=it-1$에서 $x={1} over{a}$이므로 $rm C LEFT({1} over{a},~it-1 RIGHT)$',
        '$y=log_{3a}x=it-1$에서 $x={1} over{3a}$이므로 $rm D LEFT({1} over{3a},~it-1 RIGHT)$',
        {'fig': 'shg24s_q16_sol'},
        'ㄱ. $rm C$, $rm D$를 $3`:`1$로 외분하는 점의 $x$좌표는 ${3 timesLEFT({1} over{3a} RIGHT)-1 timesLEFT({1} over{a} RIGHT)} over{3-1}={LEFT({1} over{a} RIGHT)-LEFT({1} over{a} RIGHT)} over{2}=0$',
        '$x$좌표가 $0$이므로 $y$축 위에 있다. (참)',
        'ㄴ. 직선 $rm AC$, 직선 $rm BD$의 교점의 $y$좌표를 구하면 ${1-3a^{2}} over{3a^{2}+1}$이고, 이는 $a={1} over{sqrt{3}}$일 때만 $0$이 되므로 모든 $a$에 대해 성립하지는 않는다. (거짓)',
        'ㄷ. $bar{rm AB}=LEFT | 3a-a RIGHT |=2a$, $bar{rm CD}=LEFT | {1} over{a}-{1} over{3a} RIGHT |={2} over{3a}$',
        '$bar{rm AB}=bar{rm CD}$이면 $2a={2} over{3a}$에서 $a^{2}={1} over{3}$, $a={1} over{sqrt{3}}$',
        '이때 $rm A LEFT({1} over{sqrt{3}},~1 RIGHT)$, $rm B(sqrt{3},~1)$, $rm C(sqrt{3},~it-1)$, $rm D LEFT({1} over{sqrt{3}},~it-1 RIGHT)$로',
        '$rm A$, $rm D$의 $x$좌표가 같고 $rm B$, $rm C$의 $x$좌표가 같으며 윗변·아랫변이 평행하므로 직사각형이다. (참)',
        '따라서 옳은 것은 ㄱ, ㄷ이다.',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q17', kind='mc', no=17, score=5.3, layout='3+2',
    text='$a>1$인 실수 $a$에 대하여 두 곡선 $y=2^{x}$, $y=it- 2^{it-x}+2a$가 만나는 두 점을 $rm A$, $rm B$라 하자. 선분 $rm AB$의 중점이 직선 $3x-8y+17=0$ 위에 있을 때, 두 점 $rm A$, $rm B$를 지나는 직선의 기울기는?',
    choices=['${11} over {16}$', '${3} over {4}$', '${13} over {16}$', '${7} over {8}$', '${15} over {16}$'],
    ans='⑤',
    sol=[
        '$u=2^{x}$ $(u>0)$라 하면 $2^{x}=it- 2^{it-x}+2a$에서 $u=it- {1} over{u}+2a$',
        '$u^{2}-2au+1=0$',
        '두 근 $u_{1}$, $u_{2}$에 대하여 $u_{1}u_{2}=1$, $u_{1}+u_{2}=2a$',
        '$u_{1}u_{2}=1$에서 $2^{x_{1}} times2^{x_{2}}=1$이므로 $x_{1}+x_{2}=0$',
        '두 점의 $y$좌표의 합은 $u_{1}+u_{2}=2a$이므로 중점은 $LEFT(0,~a RIGHT)$',
        '이 점이 $3x-8y+17=0$ 위에 있으므로 $3(0)-8a+17=0$',
        '$therefore~a={17} over{8}$',
        '$x_{1}=t$, $x_{2}=it-t$ $(t>0)$라 하면 $u_{1}+u_{2}=2^{t}+2^{it-t}=2a={17} over{4}$',
        '$w=2^{t}$라 하면 $w+{1} over{w}={17} over{4}$에서 $4w^{2}-17w+4=0$',
        '$w={17 pm sqrt{289-64}} over{8}={17 pm15} over{8}$',
        '$w>1$이므로 $w=4$, 즉 $t=2$',
        '$rm A(2,~4)$, $rm B LEFT(it-2,~{1} over{4} RIGHT)$',
        '기울기 $=LEFT(4-{1} over{4} RIGHT) div LEFT(2-(it-2) RIGHT)={15} over{4} div4$',
        '$={15} over{16}$',
    ],
    ch='지수함수와 로그함수', lv='상')

add(id='q18', kind='mc', no=18, score=5.4, layout='3+2', emptybox={'paras': [
        '(가) 임의의 실수 $x$에 대하여 $g(x+2)=g(it-x+2)$이다.',
        '(나) 실수 $t$에 대하여 $t-1 LEQ x LEQ t+1$에서의 $g(x)$의 최댓값을 $h(t)$라 할 때, $h(t)$의 최솟값은 $3$이다.',
    ]},
    text='이차항의 계수가 $1$이고, 그래프가 $x$축과 만나지 않는 이차함수 $f(x)$에 대하여, 함수 $g(x)=log_{2}f(x)$라 하자. 함수 $g(x)$가 다음 조건을 만족시킬 때, $4^{g(4)}$의 값은?',
    choices=['$100$', '$121$', '$144$', '$169$', '$196$'],
    ans='②',
    sol=[
        '조건 (가)에서 $g$는 $x=2$에 대하여 대칭이므로 $f(x)=(x-2)^{2}+c$ ($c$는 상수, $c>0$)',
        '$g(x)=log_{2}LEFT{(x-2)^{2}+c RIGHT}$는 $x=2$에서 최소이고 $LEFT | x-2 RIGHT |$가 커질수록 증가한다.',
        '구간 $LEFT[t-1,~t+1 RIGHT]$의 최댓값은 두 끝점 중 $x=2$에서 더 먼 쪽에서 나타나며, 그 거리는 $LEFT | t-3 RIGHT |$와 $LEFT | t-1 RIGHT |$ 중 큰 값이다.',
        '이 값은 $t=2$일 때 최소(둘 다 거리 $1$)가 되므로 $h(t)$의 최솟값은 $x=2$에서 거리 $1$인 점에서의 $g$값, 즉 $log_{2}(1+c)$',
        '$therefore~log_{2}(1+c)=3$에서 $1+c=8$, $c=7$',
        '$f(x)=(x-2)^{2}+7$',
        '$g(4)=log_{2}LEFT{(4-2)^{2}+7 RIGHT}=log_{2}11$',
        '$therefore~4^{g(4)}=4^{log_{2}11}=LEFT(2^{2} RIGHT)^{log_{2}11}=2^{2log_{2}11}=2^{log_{2}121}$',
        '$=121$',
    ],
    ch='지수함수와 로그함수', lv='상')

# ---------------------------------------------------------------- 서술형(논술형)
add(id='q19', kind='sub', no=1, score=5,
    text='호의 길이가 $10 pi$, 넓이가 $65 pi$인 부채꼴 $rm OAB$가 있다. 이 부채꼴을 접어 만든 원뿔 모양의 용기는 밑면의 둘레의 길이가 호 $rm AB$의 길이와 같을 때, 이 용기의 부피를 구하고, 그 과정을 서술하시오.',
    ans_eq='100 pi',
    sol=[
        '부채꼴의 반지름을 $r$, 중심각을 $theta$라 하면',
        '호의 길이 $rtheta=10 pi$, 넓이 ${1} over{2}r^{2}theta=65 pi$',
        '넓이 식에 $rtheta=10 pi$를 대입하면 ${1} over{2}r times10 pi=65 pi$',
        '$5 pi r=65 pi$',
        '$therefore~r=13$',
        '이 부채꼴을 접어 만든 원뿔의 모선의 길이는 $r=13$이고, 밑면의 둘레의 길이는 호 $rm AB$의 길이와 같으므로 $2 pi R=10 pi$',
        '$therefore~R=5$ ($R$은 원뿔의 밑면의 반지름)',
        '원뿔의 높이 $h=sqrt{13^{2}-5^{2}}=sqrt{169-25}=sqrt{144}=12$',
        '$therefore$ 부피 $={1} over{3} piR^{2}h={1} over{3} pi times5^{2} times12$',
        '$=100 pi$',
    ],
    ch='일반각과 호도법', lv='중')

add(id='q20', kind='sub', no=2, score=7, emptybox={'paras': [
        '$log_{3}(2na-a^{2})=log_{3}(2nb-b^{2})=m$',
        '$0<b-a LEQ n$인 두 실수 $a$, $b$가 존재한다.',
    ]},
    text='두 자연수 $m$, $n$에 대하여 다음 조건을 만족시킬 때, $10$ 이하의 모든 자연수 $n$의 값의 합을 구하고, 그 풀이과정을 서술하시오.',
    ans_eq='18',
    sol=[
        '$g(x)=2nx-x^{2}=it-(x-n)^{2}+n^{2}$이라 하면',
        '$g(a)=g(b)=3^{m}=k$ $(k>0)$라 할 때, $g(x)=k$의 두 근은 $x=n pm sqrt{n^{2}-k}$',
        '$d=sqrt{n^{2}-k}$라 하면 $a=n-d$, $b=n+d$ $(d>0)$이고 $b-a=2d$',
        '조건 (나)에서 $0<2d LEQ n$, 즉 $0<d LEQ {n} over{2}$',
        '$k=n^{2}-d^{2}$이고 $d in LEFT(0,~{n} over{2} RIGHT]$이므로 $k in LEFT[{3n^{2}} over{4},~n^{2} RIGHT)$',
        '이 범위에 $3$의 거듭제곱 $3^{m}$ ($m$은 자연수)이 존재하는 $n$을 $10$ 이하에서 찾는다.',
        '$n=2$: ${3n^{2}} over{4}=3$, $n^{2}=4$이므로 범위 $LEFT[3,~4 RIGHT)$에 $3^{1}=3$이 포함된다.',
        '$n=6$: ${3n^{2}} over{4}=27$, $n^{2}=36$이므로 범위 $LEFT[27,~36 RIGHT)$에 $3^{3}=27$이 포함된다.',
        '$n=10$: ${3n^{2}} over{4}=75$, $n^{2}=100$이므로 범위 $LEFT[75,~100 RIGHT)$에 $3^{4}=81$이 포함된다.',
        '그 외의 $n=1,~3,~4,~5,~7,~8,~9$에서는 범위 안에 $3$의 거듭제곱이 존재하지 않는다.',
        '$therefore$ 조건을 만족시키는 $n$은 $2,~6,~10$이고, 그 합은 $2+6+10$',
        '$=18$',
    ],
    ch='로그', lv='상')
