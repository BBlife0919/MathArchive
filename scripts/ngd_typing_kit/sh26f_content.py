# -*- coding: utf-8 -*-
"""소하고등학교 2학년 2026 1학기 기말 대수(삼각함수의 활용~수학적귀납법) 19문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ---------------------------------------------------------------- 객관식
add(id='q01', kind='mc', no=1, score=4.2, layout='3+2',
    text='$bar{rmAB}=6$ , $bar{rmBC}=8$ , $ angle {rmB}=60^{circ}$인 삼각형 $rmABC$의 넓이는?',
    choices=['$12$', '$12 sqrt{3}$', '$24$', '$24 sqrt{2}$', '$24 sqrt{3}$'],
    ans='②',
    sol=[
        '삼각형의 넓이 $={1} over{2} timesbar{rmAB} timesbar{rmBC} times sin{LEFT( angle {rmB} RIGHT)}$',
        '$={1} over{2} times6 times8 times sin60^{circ}$',
        '$=24 times{ sqrt{3}} over{2}$',
        '$therefore$ 삼각형의 넓이는',
        '$=12 sqrt{3}$',
    ],
    ch='삼각함수의 활용', lv='하')

add(id='q02', kind='mc', no=2, score=4.2, layout='3+2',
    text='$sum^{6}_{k=1}a_{k}=10$일 때, $sum^{6}_{n=1}(2a_{n}-1)$의 값은?',
    choices=['$14$', '$16$', '$18$', '$20$', '$22$'],
    ans='①',
    sol=[
        '$sum^{6}_{n=1}(2a_{n}-1)=2 sum^{6}_{n=1}a_{n}-sum^{6}_{n=1}1$',
        '$=2 times10-6 times1$',
        '$=20-6$',
        '$therefore$ 구하는 값은',
        '$=14$',
    ],
    ch='수열의 합', lv='하')

add(id='q03', kind='mc', no=3, score=4.3, layout='3+2',
    text='첫째항이 $3$이고 공차가 $d$인 등차수열의 첫째항부터 제$5$항까지의 합이 $20$일 때, $d$의 값은?',
    choices=['${1} over{2}$', '$1$', '${3} over{2}$', '$2$', '${5} over{2}$'],
    ans='①',
    sol=[
        '첫째항부터 제$5$항까지의 합 $=5 times3+{5 times4} over{2}d=15+10d$',
        '$15+10d=20$에서 $10d=5$',
        '$therefore~d$',
        '$={1} over{2}$',
    ],
    ch='등차수열', lv='하')

add(id='q04', kind='mc', no=4, score=4.4, layout='3+2',
    text='등비수열 $LEFT{a_{n} RIGHT}$의 공비가 $2$이고 $a_{6}=18$일 때, $a_{4}$의 값은?',
    choices=['${3} over{2}$', '$2$', '$3$', '$4$', '${9} over{2}$'],
    ans='⑤',
    sol=[
        '$a_{6}=a_{4} times2^{2}$이므로 $a_{4}={a_{6}} over{4}={18} over{4}$',
        '$therefore~a_{4}$',
        '$={9} over{2}$',
    ],
    ch='등비수열', lv='하')

add(id='q05', kind='mc', no=5, score=4.5, layout='1x5', emptybox={'paras': [
        '$(1)$ $n=1$일 때, (좌변)$=a_{1}=(가)$, (우변)$=2^{1}-1=1$',
        '따라서, $n=1$일 때, $a_{n}=2^{n}-1$이 성립한다.',
        '$(2)$ $n=(나)$일 때, $a_{n}=2^{n}-1$이 성립한다고 가정하면',
        '$a_{k}=2^{k}-1$이다.',
        '$n=k+1$일 때, $a_{k+1}=2a_{k}+1=(다)$',
        '따라서, $n=(라)$일 때도 $a_{n}=2^{n}-1$이 성립한다.',
        '$(1)$, $(2)$에 의하여 모든 자연수 $n$에 대하여 $(마)$이 성립한다.',
    ]},
    text='다음은 수열 $LEFT{a_{n} RIGHT}$이 $a_{1}=1$, $a_{n+1}=2a_{n}+1$을 만족시킬 때, $a_{n}=2^{n}-1$임을 수학적 귀납법으로 증명하는 과정이다. 위의 (가)~(마)에 들어갈 수와 식으로 옳지 않은 것은?',
    choices=['(가)$=1$', '(나)$=k$', '(다)$=2^{k}-1$', '(라)$=k+1$', '(마)$: a_{n}=2^{n}-1$'],
    ans='③',
    sol=[
        '$(1)$에서 $a_{1}=1$이므로 $(가)=1$ (옳음)',
        '$(2)$는 $n=k$일 때를 가정하는 단계이므로 $(나)=k$ (옳음)',
        '$a_{k+1}=2a_{k}+1=2(2^{k}-1)+1=2^{k+1}-2+1=2^{k+1}-1$이므로 $(다)=2^{k+1}-1$',
        '제시된 $(다)=2^{k}-1$은 지수가 틀렸으므로 옳지 않다.',
        '$n=k+1$일 때도 성립함을 보인 것이므로 $(라)=k+1$ (옳음)',
        '$(마)$는 최종 결론이므로 $a_{n}=2^{n}-1$ (옳음)',
        '$therefore$ 옳지 않은 것은',
        '$=(다)$',
    ],
    ch='수학적 귀납법', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2', fig='sh26f_q06',
    text='그림과 같이 반지름의 길이가 $5$이고 원의 중심이 $rmO$인 원이 있다. 원 위의 서로 다른 두 점 $rmA$, $rmB$에 대하여 원의 중심 $rmO$와 현 $rmAB$ 사이의 거리가 $3$일 때, $rmA$, $rmB$가 아닌 원 위의 점 $rmC$에 대하여 $sin{LEFT( angle {rmACB} RIGHT)}$의 값은?',
    choices=['${2} over{5}$', '${3} over{5}$', '${3} over{4}$', '${4} over{5}$', '${5} over{6}$'],
    ans='④',
    sol=[
        '현 $rmAB$의 중점을 $rmH$라 하면 $bar{rmOH}=3$, $bar{rmOA}=5$이므로 직각삼각형 $rmOAH$에서',
        '$bar{rmAH}= sqrt{5^{2}-3^{2}}= sqrt{16}=4$',
        '$bar{rmAB}=2 timesbar{rmAH}=8$',
        '사인법칙에 의해 $ {bar{rmAB}} over{sin{LEFT( angle {rmACB} RIGHT)}}=2 times5=10$',
        '$therefore~sin{LEFT( angle {rmACB} RIGHT)}={bar{rmAB}} over{10}={8} over{10}$',
        '$={4} over{5}$',
    ],
    ch='삼각함수의 활용', lv='중')

add(id='q07', kind='mc', no=7, score=4.8, layout='3+2',
    text='등차수열 $LEFT{a_{n} RIGHT}$에 대하여 $a_{6}=it-4$, $a_{2}+a_{3}+a_{8}=a_{4}+a_{5}+a_{9}-15$일 때, $a_{9}$의 값은?',
    choices=['$5$', '$6$', '$7$', '$8$', '$9$'],
    ans='①',
    sol=[
        '첫째항을 $a_{1}$, 공차를 $d$라 하면 $a_{2}+a_{3}+a_{8}=3a_{1}+10d$, $a_{4}+a_{5}+a_{9}=3a_{1}+15d$',
        '$3a_{1}+10d=3a_{1}+15d-15$에서 $5d=15$',
        '$therefore~d=3$',
        '$a_{6}=a_{1}+5d=it-4$에서 $a_{1}=it-4-15$',
        '$=it-19$',
        '$therefore~a_{9}=a_{1}+8d=it-19+24$',
        '$=5$',
    ],
    ch='등차수열', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2',
    text='$a_{1}=10$, $a_{n+1}=a_{n}+(it-1)^{n} times{1} over{2}$라 정의된 수열 $LEFT{a_{n} RIGHT}$의 제$25$항의 값은?',
    choices=['$8$', '${17} over{2}$', '$9$', '${19} over{2}$', '$10$'],
    ans='⑤',
    sol=[
        '$a_{25}=a_{1}+ sum^{24}_{n=1}(it-1)^{n} times{1} over{2}$',
        '$ sum^{24}_{n=1}(it-1)^{n}$은 $it-1$과 $1$이 번갈아 $12$번씩 나타나 $0$이다.',
        '$therefore~a_{25}=10+0$',
        '$=10$',
    ],
    ch='수열의 귀납적 정의', lv='중')

add(id='q09', kind='mc', no=9, score=5.0, layout='1x5',
    text='$cos^{2}C-1=sin^{2}(A+C)-sin^{2}A$를 만족시키는 삼각형 $rmABC$에 대한 설명으로 옳은 것은? (단, $a,~c$는 각각 $ angle {rmA},~ angle {rmC}$의 대변의 길이이다.)',
    choices=[
        '$a=c$인 이등변삼각형이다.',
        '$ angle {rmA}=90^{circ}$인 직각삼각형이다.',
        '$ angle {rmB}=90^{circ}$인 직각삼각형이다.',
        '$ angle {rmC}=90^{circ}$인 직각삼각형이다.',
        '$a=c$이고 $ angle {rmB}=90^{circ}$인 직각이등변삼각형이다.',
    ],
    ans='②',
    sol=[
        '$ angle {rmA}+ angle {rmB}+ angle {rmC}=180^{circ}$이므로 $A+C=180^{circ}-B$, $sin(A+C)=sinB$',
        '(좌변) $cos^{2}C-1=it-sin^{2}C$',
        '(우변) $sin^{2}(A+C)-sin^{2}A=sin^{2}B-sin^{2}A$',
        '$it-sin^{2}C=sin^{2}B-sin^{2}A$에서 $sin^{2}A=sin^{2}B+sin^{2}C$',
        '사인법칙에 의해 $sinA`:`sinB`:`sinC=a`:`b`:`c$이므로 $a^{2}=b^{2}+c^{2}$',
        '이는 피타고라스 정리의 역이므로 변 $a$가 빗변인 직각삼각형, 즉 $ angle {rmA}=90^{circ}$',
        '$therefore$ 삼각형 $rmABC$는',
        '$ angle {rmA}=90^{circ}$인 직각삼각형이다.',
    ],
    ch='삼각함수의 활용', lv='중')

add(id='q10', kind='mc', no=10, score=5.1, layout='1x5',
    text='연이율이 $3$%이고, $2026$년부터 $1$년마다 복리로 매년 초에 $300$만원씩 적립할 때, $2035$년 말까지 적립금의 원리합계의 값은? (단, $1.03^{10}=1.34$로 계산한다.)',
    choices=['$3400$만원', '$3442$만원', '$3480$만원', '$3502$만원', '$3600$만원'],
    ans='④',
    sol=[
        '$2026$년 초에 적립한 $300$만원은 $2035$년 말까지 $10$년간 복리로 늘어나 $300 times1.03^{10}$',
        '$2027$년 초에 적립한 $300$만원은 $9$년간 늘어나 $300 times1.03^{9}$, $cdots$, $2035$년 초에 적립한 $300$만원은 $1$년간 늘어나 $300 times1.03$',
        '원리합계 $= sum^{10}_{k=1}300 times1.03^{k}=300 times1.03 timesLEFT({1.03^{10}-1} over{1.03-1} RIGHT)$',
        '$=300 times1.03 timesLEFT({1.34-1} over{0.03} RIGHT)=300 times1.03 times{0.34} over{0.03}$',
        '$=300 times{0.3502} over{0.03}=300 times11. overline{6}$',
        '$therefore$ 원리합계는',
        '$=3502$만원',
    ],
    ch='등비수열의 활용', lv='중')

add(id='q11', kind='mc', no=11, score=5.2, layout='3+2',
    text='$bar{rmAB}`:`bar{rmBC}`:`bar{rmCA}=1`:`3`:` sqrt{6}$인 삼각형 $rmABC$가 있다. 삼각형 $rmABC$의 외접원의 넓이가 $45 pi$일 때, 변 $rmAB$의 길이는?',
    choices=['${5 sqrt{6}} over{9}$', '${5 sqrt{6}} over{6}$', '${5 sqrt{6}} over{3}$', '$5$', '$10$'],
    ans='③',
    sol=[
        '$bar{rmAB}=k$, $bar{rmBC}=3k$, $bar{rmCA}= sqrt{6}k$ ($k>0$)라 하자.',
        '외접원의 넓이가 $45 pi$이므로 외접원의 반지름 $R$에 대해 $R^{2}=45$',
        '$cosLEFT( angle {rmA} RIGHT)={bar{rmCA}^{2}+bar{rmAB}^{2}-bar{rmBC}^{2}} over{2 timesbar{rmCA} timesbar{rmAB}}={6k^{2}+k^{2}-9k^{2}} over{2 sqrt{6}k^{2}}={it-2} over{2 sqrt{6}}$',
        '$=it- {1} over{ sqrt{6}}$',
        '$sinLEFT( angle {rmA} RIGHT)= sqrt{1-{1} over{6}}= sqrt{{5} over{6}}$',
        '사인법칙에 의해 ${bar{rmBC}} over{sinLEFT( angle {rmA} RIGHT)}=2R$에서 $3k= 2 times sqrt{45} times sqrt{{5} over{6}}$',
        '$2 sqrt{45} times sqrt{{5} over{6}}=2 sqrt{{225} over{6}}=2 times{15} over{ sqrt{6}}={30} over{ sqrt{6}}={30 sqrt{6}} over{6}=5 sqrt{6}$',
        '$3k=5 sqrt{6}$에서 $k={5 sqrt{6}} over{3}$',
        '$therefore~bar{rmAB}=k$',
        '$={5 sqrt{6}} over{3}$',
    ],
    ch='삼각함수의 활용', lv='중')

add(id='q12', kind='mc', no=12, score=5.3, layout='3+2',
    text='$sum^{20}_{k=1}(2k-1)^{2}-sum^{19}_{n=7}(2n+1)^{2}$의 값은?',
    choices=['$449$', '$455$', '$506$', '$819$', '$1240$'],
    ans='②',
    sol=[
        '$n=7, cdots,~19$에서 $(2n+1)$은 $k=n+1=8, cdots,~20$에서의 $(2k-1)$과 같으므로',
        '$ sum^{19}_{n=7}(2n+1)^{2}= sum^{20}_{k=8}(2k-1)^{2}$',
        '$therefore~ sum^{20}_{k=1}(2k-1)^{2}-sum^{20}_{k=8}(2k-1)^{2}= sum^{7}_{k=1}(2k-1)^{2}$',
        '$=1^{2}+3^{2}+5^{2}+7^{2}+9^{2}+11^{2}+13^{2}$',
        '$=1+9+25+49+81+121+169$',
        '$therefore$ 구하는 값은',
        '$=455$',
    ],
    ch='수열의 합', lv='중')

add(id='q13', kind='mc', no=13, score=5.3, layout='2+2+1', fig='sh26f_q13',
    text='그림과 같이 높이가 $20 sqrt{3}$인 건물의 밑에서 옆 건물의 끝을 올려본 각의 크기가 $60^{circ}$이고 이 건물의 옥상에서 옆 건물의 끝을 올려본 각의 크기가 $15^{circ}$이다. 이때, 두 건물의 높이의 차는? (단, 건물의 크기는 무시하고 $cos15^{circ}={ sqrt{6}+ sqrt{2}} over{4}$로 계산한다.)',
    choices=['$5 sqrt{3}-5$', '$15 sqrt{3}-15$', '$15-5 sqrt{3}$', '$15+5 sqrt{3}$', '$15+15 sqrt{3}$'],
    ans='③',
    sol=[
        '두 건물 사이의 거리를 $d$, 옆 건물의 높이를 $H$라 하면 $tan60^{circ}={H} over{d}$에서 $H=d sqrt{3}$',
        '옥상에서 본 각 $15^{circ}$에 대하여 $tan15^{circ}={H-20 sqrt{3}} over{d}$',
        '$cos15^{circ}={ sqrt{6}+ sqrt{2}} over{4}$이므로 $sin15^{circ}={ sqrt{6}- sqrt{2}} over{4}$, $tan15^{circ}={ sqrt{6}- sqrt{2}} over{ sqrt{6}+ sqrt{2}}=2- sqrt{3}$',
        '$d={H} over{ sqrt{3}}$를 대입하면 $ sqrt{3}(H-20 sqrt{3})/H=2- sqrt{3}$',
        '$ sqrt{3}H-60=(2- sqrt{3})H$에서 $(2 sqrt{3}-2)H=60$',
        '$H={60} over{2 sqrt{3}-2}={30} over{ sqrt{3}-1}={30( sqrt{3}+1)} over{2}=15 sqrt{3}+15$',
        '$therefore$ 두 건물의 높이의 차 $=H-20 sqrt{3}=15 sqrt{3}+15-20 sqrt{3}$',
        '$=15-5 sqrt{3}$',
    ],
    ch='삼각함수의 활용', lv='중')

add(id='q14', kind='mc', no=14, score=5.5, layout='3+2',
    text='모든 항이 양수인 등비수열 $LEFT{a_{n} RIGHT}$의 첫째항부터 제$n$항까지의 합을 $S_{n}$이라 하자. ${S_{9}} over{S_{3}}=13$이고 $ sum^{6}_{k=1}a_{3k}=364$일 때, $a_{7} times a_{8}$의 값은?',
    choices=['$27$', '$28$', '$30$', '$32$', '$33$'],
    ans='①',
    sol=[
        '공비를 $r$ $(r>0)$이라 하면 ${S_{9}} over{S_{3}}=1+r^{3}+r^{6}=13$에서 $r^{6}+r^{3}-12=0$',
        '$(r^{3}+4)(r^{3}-3)=0$이고 $r^{3}>0$이므로 $r^{3}=3$',
        '$ sum^{6}_{k=1}a_{3k}=a_{1}r^{2}(1+r^{3}+r^{6}+r^{9}+r^{12}+r^{15})=a_{1}r^{2} times{3^{6}-1} over{3-1}=a_{1}r^{2} times364$',
        '$a_{1}r^{2} times364=364$에서 $a_{1}r^{2}=1$',
        '$a_{7} times a_{8}=a_{1}r^{6} times a_{1}r^{7}=a_{1}^{2}r^{13}=(a_{1}r^{2})^{2}r^{9}$',
        '$=1^{2} times(r^{3})^{3}=3^{3}$',
        '$therefore~a_{7} times a_{8}$',
        '$=27$',
    ],
    ch='등비수열', lv='중')

add(id='q15', kind='mc', no=15, score=5.6, layout='1x5',
    text='수열 $LEFT{a_{n} RIGHT}$이 모든 자연수 $n$에 대하여 $3a_{n+1}=a_{n}(a_{n}+3)$을 만족시킨다. $a_{6}=a_{1}+21$, $a_{1}a_{6}=3$일 때, $ sum^{5}_{k=1}{1} over{a_{k}+3}$의 값은?',
    choices=['${17} over{3}$', '$6$', '${19} over{3}$', '${20} over{3}$', '$7$'],
    ans='⑤',
    sol=[
        '$3a_{n+1}=a_{n}(a_{n}+3)$에서 ${1} over{a_{n+1}}={3} over{a_{n}(a_{n}+3)}$',
        '부분분수로 ${3} over{a_{n}(a_{n}+3)}={1} over{a_{n}}-{1} over{a_{n}+3}$이므로 ${1} over{a_{n+1}}={1} over{a_{n}}-{1} over{a_{n}+3}$',
        '$therefore~{1} over{a_{n}+3}={1} over{a_{n}}-{1} over{a_{n+1}}$',
        '$ sum^{5}_{k=1}{1} over{a_{k}+3}= sum^{5}_{k=1}LEFT({1} over{a_{k}}-{1} over{a_{k+1}} RIGHT)={1} over{a_{1}}-{1} over{a_{6}}={a_{6}-a_{1}} over{a_{1}a_{6}}$',
        '$={21} over{3}$',
        '$therefore$ 구하는 값은',
        '$=7$',
    ],
    ch='부분분수를 이용한 수열의 합', lv='상')

add(id='q16', kind='mc', no=16, score=5.7, layout='1x5',
    text='함수 $f(x)=log_{2}x$와 자연수 $n$에 대하여 함수 $y=f(x)$ 위의 점 중 $y$좌표가 $n$인 점을 $rmA_{n}$이라 하자. 점 $rmA_{n}$을 지나고 기울기가 $it-1$인 직선이 함수 $y=f^{it-1}(x)$와 만나는 점을 $rmB_{n}$이라 하고, $rmB_{n}$에서 $x$축에 내린 수선의 발을 $rmH_{n}$이라 할 때, 사각형 $rmB_{n}H_{n}H_{n+1}B_{n+1}$의 넓이를 $S_{n}$이라 하자. $ sum^{7}_{k=1}S_{k}$의 값은?',
    choices=['$375$', '$377$', '$379$', '$381$', '$383$'],
    ans='④',
    sol=[
        '$rmA_{n}LEFT(2^{n},~n RIGHT)$이고 $f^{it-1}(x)=2^{x}$이다.',
        '기울기 $it-1$인 직선은 $y=x$에 대한 대칭축에 수직이므로, 그 직선 위의 점을 $y=x$에 대해 대칭이동해도 같은 직선 위에 있다.',
        '$rmA_{n}$을 $y=x$에 대해 대칭이동하면 $(n,~2^{n})$이고, 이는 $y=f^{it-1}(x)$ 위의 점이므로 $rmB_{n}(n,~2^{n})$',
        '$rmH_{n}(n,~0)$',
        '$S_{n}$은 평행한 두 변 $bar{rmB_{n}H_{n}}=2^{n}$, $bar{rmB_{n+1}H_{n+1}}=2^{n+1}$이고 높이가 $1$인 사다리꼴의 넓이이므로',
        '$S_{n}={1} over{2}LEFT(2^{n}+2^{n+1} RIGHT) times1=3 times2^{n-1}$',
        '$ sum^{7}_{k=1}S_{k}= sum^{7}_{k=1}3 times2^{k-1}=3 times(2^{7}-1)=3 times127$',
        '$therefore$ 구하는 값은',
        '$=381$',
    ],
    ch='수열의 합과 도형', lv='상')

add(id='q17', kind='mc', no=17, score=5.7, layout='3+2',
    text='등차수열 $LEFT{a_{n} RIGHT}$이 모든 자연수 $n$에 대하여 $a_{n+3}-2a_{n+1}+a_{n}=2$를 만족한다. 수열 $LEFT{( sqrt{3})^{a_{n}} RIGHT}$의 첫째항부터 제$4$항까지의 합이 $40$일 때, $a_{5}$의 값은?',
    choices=['$6$', '$7$', '$8$', '$9$', '$10$'],
    ans='③',
    sol=[
        '공차를 $d$라 하면 $a_{n+3}-2a_{n+1}+a_{n}=(a_{n}+3d)-2(a_{n}+d)+a_{n}=d$',
        '$d=2$',
        '$LEFT{( sqrt{3})^{a_{n}} RIGHT}$은 공비가 $( sqrt{3})^{2}=3$인 등비수열이므로 첫째항을 $T$라 하면',
        '$T(1+3+9+27)=40T=40$에서 $T=1$',
        '$( sqrt{3})^{a_{1}}=1$에서 $a_{1}=0$',
        '$a_{n}=0+2(n-1)=2n-2$',
        '$therefore~a_{5}=2 times5-2$',
        '$=8$',
    ],
    ch='등차수열과 등비수열', lv='상')

add(id='q18', kind='mc', no=18, score=5.8, layout='3+2',
    text='$ sum^{n}_{k=1}a_{k}=3(2^{n}+1)$일 때, $ sum^{5}_{n=1}a_{n}a_{n+1}$의 값은?',
    choices=['$6138$', '$6174$', '$6210$', '$6246$', '$6282$'],
    ans='②',
    sol=[
        '$a_{1}=S_{1}=3(2+1)$',
        '$=9$',
        '$n GEQ 2$일 때, $a_{n}=S_{n}-S_{n-1}=3(2^{n}+1)-3(2^{n-1}+1)=3 times2^{n-1}$',
        '$a_{2}=6$, $a_{3}=12$, $a_{4}=24$, $a_{5}=48$, $a_{6}=96$',
        '$ sum^{5}_{n=1}a_{n}a_{n+1}=a_{1}a_{2}+a_{2}a_{3}+a_{3}a_{4}+a_{4}a_{5}+a_{5}a_{6}$',
        '$=9 times6+6 times12+12 times24+24 times48+48 times96$',
        '$=54+72+288+1152+4608$',
        '$therefore$ 구하는 값은',
        '$=6174$',
    ],
    ch='수열의 합', lv='상')

# ---------------------------------------------------------------- 서술형
add(id='q19', kind='sub', no=1, score=10.0, fig='sh26f_q19',
    text='그림과 같이 원에 내접하는 둔각삼각형 $rmABC$에서 $bar{rmAB}=4$이다. $ angle {rmBAC}= angle {rmCAD}$를 만족하는 원 위의 점 $rmD$에 대하여 현 $rmBD$와 현 $rmAC$의 교점을 $rmE$라 할 때, $bar{rmAE}=5$, $cosLEFT( angle {rmBAC} RIGHT)={3} over{4}$이다. 다음 물음에 답하시오. (단, 점 $rmD$는 $rmB$가 아니며, $bar{rmAB}<bar{rmAD}$이다.)',
    text2=['(1) 선분 $rmBE$의 길이를 구하시오. [$2$점]',
           '(2) 선분 $rmAD$의 길이를 구하고, 그 과정을 서술하시오. [$3$점]',
           '(3) $bar{rmEC}=x$라 할 때, $x$의 값을 구하고, 그 과정을 서술하시오. [$5$점]'],
    ans_mix='(1) $bar{rmBE}= sqrt{11}$ (2) $bar{rmAD}=20$ (3) $x=11$',
    sol=[
        '(1) 삼각형 $rmABE$에서 $ angle {rmBAE}= angle {rmBAC}$이고 $cosLEFT( angle {rmBAC} RIGHT)={3} over{4}$이므로 코사인법칙에 의해',
        '$bar{rmBE}^{2}=bar{rmAB}^{2}+bar{rmAE}^{2}-2 timesbar{rmAB} timesbar{rmAE} times cosLEFT( angle {rmBAC} RIGHT)$',
        '$=4^{2}+5^{2}-2 times4 times5 times{3} over{4}=16+25-30$',
        '$=11$',
        '$therefore~bar{rmBE}$',
        '$= sqrt{11}$',
        '(2) 원에서 $rmB$, $rmC$는 현 $rmAD$에 대하여 같은 쪽에 있으므로, 호 $rmAD$에 대한 원주각 $ angle {rmABD}= angle {rmACD}$이다.',
        '$ angle {rmABE}= angle {rmABD}$ (같은 각)이므로 $ angle {rmABE}= angle {rmACD}$이고, $ angle {rmBAE}= angle {rmBAC}= angle {rmDAC}$이므로 삼각형 $rmABE$와 삼각형 $rmACD$는 닮음이다. ($rmAA$닮음, 대응: $rmA↔A$, $rmB↔C$, $rmE↔D$)',
        '${bar{rmAB}} over{bar{rmAC}}={bar{rmAE}} over{bar{rmAD}}={bar{rmBE}} over{bar{rmCD}}$ $ cdots$ ㉠',
        '또한 $rmC$, $rmD$는 현 $rmAB$에 대하여 같은 쪽에 있으므로 호 $rmAB$에 대한 원주각 $ angle {rmADB}= angle {rmACB}$이고, $ angle {rmADE}= angle {rmADB}$ (같은 각)이므로 $ angle {rmADE}= angle {rmACB}$이다.',
        '$ angle {rmDAE}= angle {rmDAC}= angle {rmBAC}$이므로 삼각형 $rmADE$와 삼각형 $rmACB$도 닮음이다. ($rmAA$닮음, 대응: $rmA↔A$, $rmD↔C$, $rmE↔B$)',
        '${bar{rmAD}} over{bar{rmAC}}={bar{rmAE}} over{bar{rmAB}}={bar{rmDE}} over{bar{rmCB}}$ $ cdots$ ㉡',
        '㉡에서 ${bar{rmAD}} over{bar{rmAC}}={bar{rmAE}} over{bar{rmAB}}={5} over{4}$',
        '$therefore~bar{rmAD}={5} over{4} timesbar{rmAC}$',
        '$bar{rmAC}=bar{rmAE}+bar{rmEC}=5+x$이므로 $bar{rmAD}={5(5+x)} over{4}$',
        '㉠에서 $bar{rmCD}={bar{rmBE} timesbar{rmAC}} over{bar{rmAB}}={ sqrt{11}(5+x)} over{4}$',
        '㉡에서 $bar{rmCB}={4} over{5}bar{rmDE}$',
        '원의 두 현의 교차 성질(방멱)에 의해 $bar{rmAE} timesbar{rmEC}=bar{rmBE} timesbar{rmED}$이므로 $5x= sqrt{11} timesbar{rmED}$, $bar{rmED}={5x} over{ sqrt{11}}$',
        '$bar{rmCB}={4} over{5} times{5x} over{ sqrt{11}}={4x} over{ sqrt{11}}$',
        '한편 $ angle {rmBAC}= angle {rmDAC}$이므로 호 $rmBC$와 호 $rmDC$의 크기가 같고, 따라서 현의 길이도 같아 $bar{rmBC}=bar{rmDC}$이다.',
        '$bar{rmBC}=bar{rmDC}$이므로 ${4x} over{ sqrt{11}}={ sqrt{11}(5+x)} over{4}$',
        '양변에 $4 sqrt{11}$을 곱하면 $16x=11(5+x)=55+11x$에서 $5x=55$, $x=11$',
        '$bar{rmAD}={5(5+11)} over{4}={5 times16} over{4}=20$',
        '$therefore~bar{rmAD}$',
        '$=20$',
        '(3) (2)의 풀이 과정에서 $5x=55$를 얻었으므로',
        '$therefore~x$',
        '$=11$',
    ],
    ch='삼각함수의 활용', lv='상')
