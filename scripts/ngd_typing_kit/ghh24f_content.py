# -*- coding: utf-8 -*-
"""광휘고등학교 2학년 2024 1학기 기말 수학1 18문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


# ---------------------------------------------------------------- 객관식
add(id='q01', kind='mc', no=1, score=4.2, layout='3+2',
    text='첫째항과 공차가 같은 등차수열 $LEFT{a_{n} RIGHT}$이 $a_{3}+a_{8}=44$를 만족시킬 때, 첫째항의 값은?',
    choices=['$4$', '$5$', '$6$', '$7$', '$8$'],
    ans='①',
    sol=[
        '첫째항과 공차를 모두 $a$라 하면',
        '$a_{3}=a+2a=3a$, $a_{8}=a+7a=8a$',
        '$a_{3}+a_{8}=11a=44$',
        '$therefore~a=4$',
    ],
    ch='등차수열', lv='하')

add(id='q02', kind='mc', no=2, score=4.2, layout='3+2',
    text='첫째항이 $1$이고, 공비가 $2$인 등비수열 $LEFT{a_{n} RIGHT}$에서 $a_{5}$의 값은?',
    choices=['$2$', '$4$', '$8$', '$16$', '$32$'],
    ans='④',
    sol=[
        '$a_{5}=a_{1} times r^{4}=1 times2^{4}$',
        '$=16$',
    ],
    ch='등비수열', lv='하')

add(id='q03', kind='mc', no=3, score=4.3, layout='3+2',
    text='$sum^{20}_{k=1}LEFT{k(k+1) RIGHT}$의 값은?',
    choices=['$3000$', '$3020$', '$3040$', '$3060$', '$3080$'],
    ans='⑤',
    sol=[
        '$sum^{20}_{k=1}LEFT{k(k+1) RIGHT}=sum^{20}_{k=1}k^{2}+sum^{20}_{k=1}k$',
        '$sum^{20}_{k=1}k^{2}={20 times21 times41} over{6}=2870$',
        '$sum^{20}_{k=1}k={20 times21} over{2}=210$',
        '$therefore~2870+210$',
        '$=3080$',
    ],
    ch='수열의 합', lv='중')

add(id='q04', kind='mc', no=4, score=4.3, layout='3+2',
    text='첫째항이 $11$, 제$11$항이 $it-1$인 등차수열의 첫째항부터 제$6$항까지의 합은?',
    choices=['$24$', '$30$', '$36$', '$42$', '$48$'],
    ans='⑤',
    sol=[
        '공차 $d={a_{11}-a_{1}} over{10}={it-1-11} over{10}=it- {6} over{5}$',
        '$S_{6}=6a_{1}+{6 times5} over{2}d=6 times11+15 timesLEFT(it- {6} over{5} RIGHT)$',
        '$=66-18$',
        '$=48$',
    ],
    ch='등차수열', lv='중')

add(id='q05', kind='mc', no=5, score=4.4, layout='3+2',
    text='다음은 모든 자연수 $n$에 대하여 ${1} over {1 times3}+{1} over {3 times5}+ cdots+{1} over {(2n-1)(2n+1)}={n} over {2n+1}$ $ cdots$ ㉠ 이 성립함을 수학적 귀납법으로 증명한 것이다.',
    emptybox={'paras': [
        'ⅰ) $n=1$일 때, (좌변)$={1} over {3}$, (우변)$={1} over {2+1}={1} over {3}$',
        '따라서 $n=1$일 때, ㉠이 성립한다.',
        'ⅱ) $n=k$일 때, ㉠이 성립한다고 가정하면',
        '${1} over {1 times3}+{1} over {3 times5}+{1} over {5 times7}+ cdots+{1} over {(2k-1)(2k+1)}={k} over {2k+1}$',
        '$n=k+1$일 때,',
        '${1} over {1 times3}+{1} over {3 times5}+{1} over {5 times7}+ cdots+{1} over {(2k+1)(2k+3)}$',
        '$=LEFT{{1} over {1 times3}+ cdots+{1} over {(2k-1)(2k+1)} RIGHT}+{1} over {(2k+1)(2k+3)}$',
        '$=(가)+{1} over {(2k+1)(2k+3)}={(나)} over {2k+3}$',
        '따라서 $n=k+1$일 때도 ㉠이 성립한다.',
        'ⅰ), ⅱ)에 의하여 모든 자연수 $n$에 대하여 ㉠이 성립한다.',
    ]},
    text2=['위의 (가),(나)에 알맞은 식을 각각 $f(k)$, $g(k)$라 할 때, $f(2) times g(4)$의 값은?'],
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='②',
    sol=[
        '(가)는 귀납적 가정을 대입한 것이므로 $(가)=f(k)={k} over {2k+1}$',
        '$(가)+{1} over{(2k+1)(2k+3)}={k} over{2k+1}+{1} over{(2k+1)(2k+3)}={k(2k+3)+1} over{(2k+1)(2k+3)}$',
        '$={2k^{2}+3k+1} over{(2k+1)(2k+3)}={(2k+1)(k+1)} over{(2k+1)(2k+3)}={k+1} over{2k+3}$',
        '따라서 $(나)=g(k)=k+1$',
        '$f(2)={2} over {5}$, $g(4)=4+1=5$',
        '$therefore~f(2) times g(4)={2} over{5} times5$',
        '$=2$',
    ],
    ch='수학적 귀납법', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2',
    text='지름의 길이가 $6$인 원에 내접하는 삼각형 $rm ABC$에서 $sin rm A+sin rm B+sin rm C={4} over {3}$일 때, 이 삼각형의 둘레의 길이는?',
    choices=['$7$', '$8$', '$9$', '$10$', '$11$'],
    ans='②',
    sol=[
        '외접원의 반지름 $R=3$',
        '사인법칙에서 $bar{rm BC}=2Rsin rm A$, $bar{rm CA}=2Rsin rm B$, $bar{rm AB}=2Rsin rm C$',
        '둘레 $=2R(sin rm A+sin rm B+sin rm C)=2 times3 times{4} over{3}$',
        '$=8$',
    ],
    ch='사인법칙과 코사인법칙', lv='중')

add(id='q07', kind='mc', no=7, score=4.6, layout='3+2', fig='ghh24f_q7',
    text='그림과 같이 사각형 $rm ABCD$가 한 원에 내접하고 $bar{rm AB}=3$, $bar{rm AD}=4$, $bar{rm BD}=sqrt{17}$이다. 삼각형 $rm BCD$의 넓이가 $2 sqrt{2}$일 때, $bar{rm BC} timesbar{rm CD}$의 값은?',
    choices=['$3$', '$4$', '$5$', '$6$', '$7$'],
    ans='④',
    sol=[
        '삼각형 $rm ABD$에서 코사인법칙에 의하여 $bar{rm BD}^{2}=bar{rm AB}^{2}+bar{rm AD}^{2}-2 timesbar{rm AB} timesbar{rm AD} times cos rm A$',
        '$17=9+16-24cos rm A$',
        '$cos rm A={1} over{3}$',
        '사각형이 원에 내접하므로 $∠ rm BCD=pi-∠ rm A$',
        '$cos(∠ rm BCD)=it- cos rm A=it- {1} over{3}$, $sin(∠ rm BCD)=sin rm A=sqrt{1-{1} over{9}}={2 sqrt{2}} over{3}$',
        '삼각형 $rm BCD$의 넓이 $={1} over{2} timesbar{rm BC} timesbar{rm CD} times sin(∠ rm BCD)=2 sqrt{2}$',
        '${1} over{2} timesbar{rm BC} timesbar{rm CD} times{2 sqrt{2}} over{3}=2 sqrt{2}$',
        '$therefore~bar{rm BC} timesbar{rm CD}=2 sqrt{2} times{3} over{sqrt{2}}$',
        '$=6$',
    ],
    ch='사인법칙과 코사인법칙', lv='중')

add(id='q08', kind='mc', no=8, score=4.7, layout='3+2',
    text='등비수열 $LEFT{a_{n} RIGHT}$의 첫째항부터 제$n$항까지의 합을 $S_{n}$이라 할 때, $S_{10}=10$, $S_{20}=40$이다. $S_{40}$의 값은?',
    choices=['$100$', '$200$', '$400$', '$800$', '$1600$'],
    ans='③',
    sol=[
        '$B_{1}=S_{10}=10$, $B_{2}=S_{20}-S_{10}=30$이라 하면',
        '등비수열의 성질에 의하여 $B_{1}$, $B_{2}$, $B_{3}$, $B_{4}$($10$개씩 묶은 합)도 등비수열을 이룬다.',
        '공비 $t=B_{2} over B_{1}$, 즉 $B_{2}=tB_{1}$에서 $30=10t$',
        '$therefore~t=3$',
        '$B_{3}=tB_{2}=3 times30=90$',
        '$B_{4}=tB_{3}=3 times90=270$',
        '$S_{40}=B_{1}+B_{2}+B_{3}+B_{4}=10+30+90+270$',
        '$=400$',
    ],
    ch='등비수열', lv='중')

add(id='q09', kind='mc', no=9, score=4.7, layout='3+2',
    text='첫째항이 $1$이고 공차가 ${1} over {3}$인 등차수열 $LEFT{a_{n} RIGHT}$에 대하여 $sum^{10}_{k=1}{1} over {a_{k}a_{k+1}}={q} over {p}$일 때, $p+q$의 값은? (단, $p$, $q$는 서로소인 자연수)',
    choices=['$41$', '$42$', '$43$', '$44$', '$45$'],
    ans='③',
    sol=[
        '$a_{k+1}-a_{k}={1} over{3}$이므로 ${1} over{a_{k}a_{k+1}}=3LEFT({1} over{a_{k}}-{1} over{a_{k+1}} RIGHT)$',
        '$sum^{10}_{k=1}{1} over{a_{k}a_{k+1}}=3LEFT({1} over{a_{1}}-{1} over{a_{11}} RIGHT)$',
        '$a_{1}=1$, $a_{11}=1+10 times{1} over{3}={13} over{3}$이므로 ${1} over{a_{11}}={3} over{13}$',
        '$=3LEFT(1-{3} over{13} RIGHT)=3 times{10} over{13}$',
        '$={30} over{13}$',
        '$p=13$, $q=30$이므로 $therefore~p+q=43$',
    ],
    ch='수열의 합', lv='중')

add(id='q10', kind='mc', no=10, score=4.8, layout='3+2', fig='ghh24f_q10',
    text='선분 $rm AB$가 지름인 반원 위에 한 점 $rm P$가 있다. $∠ rm PAB=alpha$, $∠ rm PBA=beta$, $bar{rm AP}=5$, $bar{rm BP}=12$일 때, $cos(alpha+2 beta)$의 값은?',
    choices=['$it- {12} over {13}$', '$it- {5} over {13}$', '${5} over {12}$', '${5} over {13}$', '${12} over {13}$'],
    ans='②',
    sol=[
        '$bar{rm AB}$가 지름이므로 $∠ rm APB=90 DEG$',
        '$bar{rm AB}=sqrt{5^{2}+12^{2}}=13$',
        '$sinalpha={12} over{13}$, $cosalpha={5} over{13}$ (직각삼각형 $rm APB$에서)',
        '$alpha+beta=90 DEG$이므로 $beta=90 DEG-alpha$',
        '$sinbeta=cosalpha={5} over{13}$',
        '$cos(alpha+2 beta)=cosLEFT{(alpha+beta)+beta RIGHT}=cos(90 DEG+beta)=it- sinbeta$',
        '$=it- {5} over{13}$',
    ],
    ch='사인법칙과 코사인법칙', lv='중')

add(id='q11', kind='mc', no=11, score=4.8, layout='1x5',
    text='$na_{n+1}=2(n+1)a_{n}$ $(n=1,~2,~3,~ cdots)$이 성립하는 수열 $LEFT{a_{n} RIGHT}$에서 $a_{40}=10$이다. $a_{5}={5} over {2^{p}}$일 때, 자연수 $p$의 값은?',
    choices=['$35$', '$36$', '$37$', '$38$', '$39$'],
    ans='③',
    sol=[
        '${a_{n+1}} over{a_{n}}={2(n+1)} over{n}$이므로',
        '${a_{2}} over{a_{1}} times{a_{3}} over{a_{2}} times cdots times{a_{n}} over{a_{n-1}}={4} over{1} times{6} over{2} times cdots times{2n} over{n-1}$',
        '좌변은 ${a_{n}} over{a_{1}}$로 소거되고, 우변은 $2^{n-1}$배 한 ${2 times3 times cdots times n} over{1 times2 times cdots times(n-1)}=2^{n-1}n$',
        '$therefore~a_{n}=a_{1} times2^{n-1}n$',
        '$a_{40}=a_{1} times2^{39} times40=10$',
        '$therefore~a_{1}={10} over{40 times2^{39}}={1} over{4 times2^{39}}={1} over{2^{41}}$',
        '$a_{5}=a_{1} times2^{4} times5={1} over{2^{41}} times2^{4} times5={5} over{2^{37}}$',
        '$therefore~p=37$',
    ],
    ch='등비수열', lv='중')

add(id='q12', kind='mc', no=12, score=4.9, layout='1x5',
    text='함수 $f(x)=2cospix$ $(x GEQ 0)$의 그래프와 직선 $y={4} over {3}$가 만나는 점의 $x$좌표를 작은 것부터 차례대로 $alpha$, $beta$, $gamma$라 할 때, $fLEFT(alpha+3 beta+3 gamma RIGHT)+fLEFT(beta+gamma+{1} over {3} RIGHT)$의 값은?',
    choices=['$it- {7} over {3}$', '$it- {4} over {3}$', '$0$', '${4} over {3}$', '${7} over {3}$'],
    ans='⑤',
    sol=[
        '$2cospix={4} over{3}$에서 $cospix={2} over{3}$',
        '$t=arccosLEFT({2} over{3} RIGHT) div pi$ ($0<pit<{pi} over{2}$인 각)라 하면 해는 $pix=pm pit+2kpi$',
        '$x GEQ 0$에서 작은 것부터 $alpha=pit$, $beta=2-pit$, $gamma=2+pit$',
        '$alpha+3 beta+3 gamma=pit+3(2-pit)+3(2+pit)=pit+12$',
        '$fLEFT(alpha+3 beta+3 gamma RIGHT)=2cosLEFT(pi(pit+12) RIGHT)=2cos(pi times pit+12 pi)=2cos(pi times pit)$',
        '$pi times pit$는 바로 $cospix$의 정의 각이므로 $2cos(pi times pit)=2 times{2} over{3}={4} over{3}$',
        '$beta+gamma+{1} over{3}=(2-pit)+(2+pit)+{1} over{3}=4+{1} over{3}={13} over{3}$',
        '$fLEFT({13} over{3} RIGHT)=2cosLEFT(pi times{13} over{3} RIGHT)=2cosLEFT(4 pi+{pi} over{3} RIGHT)=2cosLEFT({pi} over{3} RIGHT)=2 times{1} over{2}=1$',
        '$therefore~{4} over{3}+1$',
        '$={7} over{3}$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q13', kind='mc', no=13, score=5.1, layout='1x5',
    text='$x$에 대한 방정식 $LEFT | sinLEFT({3} over {2}pi+x RIGHT)-{1} over {3} RIGHT |=k$가 서로 다른 $3$개의 실근을 갖도록 하는 실수 $k$의 값을 $alpha$라 할 때, $6 alpha$의 값은? (단, $0 LEQ x<2 pi$)',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='④',
    sol=[
        '$sinLEFT({3} over{2}pi+x RIGHT)=it- cosx$이므로 방정식은 $LEFT | it- cosx-{1} over{3} RIGHT |=k$, 즉 $LEFT | cosx+{1} over{3} RIGHT |=k$',
        '$u=cosx$라 하면 $0 LEQ x<2 pi$에서 $u in LEFT[ {it-1},~1 RIGHT]$이고,',
        '$u=1$($x=0$)과 $u=it-1$($x=pi$)은 각각 $x$ 하나씩만, 그 외 $u in(it-1,~1)$은 $x$ 두 개씩 대응된다.',
        '$LEFT | u+{1} over{3} RIGHT |=k$의 해는 $u=it- {1} over{3}+k$ 또는 $u=it- {1} over{3}-k$',
        '실근이 정확히 $3$개가 되려면 두 $u$값 중 하나는 $LEFT[ {it-1},~1 RIGHT]$의 경계($pm1$)이고 다른 하나는 내부에 있어야 한다.',
        '$u=it-1$이 되는 경우: $it- {1} over{3}-k=it-1$에서 $k={2} over{3}$',
        '이때 다른 해는 $u=it- {1} over{3}+{2} over{3}={1} over{3}$ (내부, 유효) $therefore~k={2} over{3}$ 가능',
        '($u=1$이 되는 경우는 다른 해가 범위를 벗어나 실근 개수가 맞지 않음, $k$가 음수가 되는 경우도 제외)',
        '$therefore~alpha={2} over{3}$',
        '$6 alpha=6 times{2} over{3}$',
        '$=4$',
    ],
    ch='삼각함수와 그래프', lv='상')

add(id='q14', kind='mc', no=14, score=5.2, layout='1x5',
    text='$sum^{60}_{k=1}LEFT{ksinLEFT({kpi} over {2} RIGHT)-kcos(k+1)pi RIGHT}$의 값은?',
    choices=['$it-120$', '$it-60$', '$0$', '$60$', '$120$'],
    ans='③',
    sol=[
        '$cos(k+1)pi=(it-1)^{k+1}$이므로 $it- kcos(k+1)pi=it-k(it-1)^{k+1}=k(it-1)^{k+2}=k(it-1)^{k}$',
        '$k=4m+1,~4m+2,~4m+3,~4m+4$ (네 개씩 묶어서) 계산하면',
        '$k=4m+1$: $sinLEFT({kpi} over{2} RIGHT)=1$, $(it-1)^{k}=it-1$ $to$ 항$=k times1+k times(it-1)=0$',
        '$k=4m+2$: $sinLEFT({kpi} over{2} RIGHT)=0$, $(it-1)^{k}=1$ $to$ 항$=k times0+k times1=k=4m+2$',
        '$k=4m+3$: $sinLEFT({kpi} over{2} RIGHT)=it-1$, $(it-1)^{k}=it-1$ $to$ 항$=k times(it-1)+k times(it-1)=it-2k=it-8m-6$',
        '$k=4m+4$: $sinLEFT({kpi} over{2} RIGHT)=0$, $(it-1)^{k}=1$ $to$ 항$=k times0+k times1=k=4m+4$',
        '네 항의 합 $=0+(4m+2)+(it-8m-6)+(4m+4)=0$',
        '$60=4 times15$이므로 이러한 묶음이 $15$개 있고, 각 묶음의 합이 $0$이므로',
        '$therefore$ 전체 합은',
        '$=0$',
    ],
    ch='수열의 합', lv='상')

add(id='q15', kind='mc', no=15, score=5.2, layout='3+2', fig='ghh24f_q15',
    text='그림과 같이 평행사변형 $rm ABCD$에서 $bar{rm AB}=3$, $bar{rm AD}=4$이고, 두 대각선이 이루는 각의 크기가 $120 DEG$일 때, 평행사변형 $rm ABCD$의 넓이는?',
    choices=['${7} over {2} sqrt{3}$', '$4 sqrt{3}$', '${9} over {2} sqrt{3}$', '$5 sqrt{3}$', '${11} over {2} sqrt{3}$'],
    ans='①',
    sol=[
        '두 대각선의 길이를 $p$, $q$라 하면 평행사변형의 대각선 성질에 의하여 $p^{2}+q^{2}=2LEFT(bar{rm AB}^{2}+bar{rm AD}^{2} RIGHT)=2(9+16)=50$',
        '대각선의 교점을 $rm O$라 하면 삼각형 $rm AOB$, 삼각형 $rm AOD$의 끼인각은 각각 $60 DEG$, $120 DEG$ (서로 보각) 중 하나씩이다.',
        '$bar{rm AB}^{2}=9=LEFT({p} over{2} RIGHT)^{2}+LEFT({q} over{2} RIGHT)^{2}-2LEFT({p} over{2} RIGHT)LEFT({q} over{2} RIGHT)cos60 DEG={p^{2}+q^{2}-pq} over{4}$',
        '$therefore~p^{2}+q^{2}-pq=36$',
        '$bar{rm AD}^{2}=16=LEFT({p} over{2} RIGHT)^{2}+LEFT({q} over{2} RIGHT)^{2}-2LEFT({p} over{2} RIGHT)LEFT({q} over{2} RIGHT)cos120 DEG={p^{2}+q^{2}+pq} over{4}$',
        '$therefore~p^{2}+q^{2}+pq=64$',
        '두 식을 빼면 $2pq=28$',
        '$therefore~pq=14$',
        '평행사변형의 넓이 $={1} over{2}pqsin120 DEG={1} over{2} times14 times{sqrt{3}} over{2}$',
        '$={7} over{2} sqrt{3}$',
    ],
    ch='사인법칙과 코사인법칙', lv='상')

# ---------------------------------------------------------------- 서술형(서답형)
add(id='q16', kind='sub', no=1, score=10,
    text='다음 물음에 답하시오.',
    text2=[
        '(1) 수열 ${sqrt{3}} over {1+sqrt{5}}$, ${sqrt{5}} over {sqrt{3}+sqrt{7}}$, ${sqrt{7}} over {sqrt{5}+sqrt{9}}$, $ cdots$의 첫째항부터 제$12$항까지의 합을 구하고, 그 과정을 서술하시오. [$4.0$점]',
        '(2) 자연수 $n$에 대하여 함수 $y=(x-2n)^{2}$과 $y=nx-2n^{2}$의 그래프가 만나는 서로 다른 두 점의 $x$좌표를 각각 $alpha_{n}$, $beta_{n}$ $(alpha_{n}<beta_{n})$이라 한다. $sum^{10}_{n=1}LEFT{(alpha_{n}-1)(beta_{n}-1) RIGHT}$의 값을 구하고, 그 과정을 서술하시오. [$6.0$점]',
    ],
    ans_mix='(1) ${7} over {2} sqrt{3}$ (2) $2045$',
    sol=[
        '(1) 일반항 $c_{n}={sqrt{2n+1}} over{sqrt{2n-1}+sqrt{2n+3}}$의 분모를 유리화하면',
        '$c_{n}={sqrt{2n+1}LEFT(sqrt{2n+3}-sqrt{2n-1} RIGHT)} over{(2n+3)-(2n-1)}={sqrt{(2n+1)(2n+3)}-sqrt{(2n+1)(2n-1)}} over{4}$',
        '$b_{n}=sqrt{(2n-1)(2n+1)}$이라 하면 $c_{n}={b_{n+1}-b_{n}} over{4}$ (망원급수)',
        '$sum^{12}_{n=1}c_{n}={b_{13}-b_{1}} over{4}$',
        '$b_{1}=sqrt{1 times3}=sqrt{3}$, $b_{13}=sqrt{25 times27}=sqrt{675}=15 sqrt{3}$',
        '$={15 sqrt{3}-sqrt{3}} over{4}={14 sqrt{3}} over{4}$',
        '$={7} over{2} sqrt{3}$',
        '(2) $(x-2n)^{2}=nx-2n^{2}$에서 $x^{2}-4nx+4n^{2}=nx-2n^{2}$',
        '$x^{2}-5nx+6n^{2}=0$',
        '$(x-2n)(x-3n)=0$',
        '$therefore~alpha_{n}=2n$, $beta_{n}=3n$',
        '$(alpha_{n}-1)(beta_{n}-1)=(2n-1)(3n-1)=6n^{2}-5n+1$',
        '$sum^{10}_{n=1}LEFT(6n^{2}-5n+1 RIGHT)=6 times sum^{10}_{n=1}n^{2}-5 times sum^{10}_{n=1}n+sum^{10}_{n=1}1$',
        '$=6 times385-5 times55+10$',
        '$=2310-275+10$',
        '$=2045$',
    ],
    ch='수열의 합', lv='중')

add(id='q17', kind='sub', no=2, score=10,
    text='첫째항이 $a$ $(a NEQ 0)$이고 공비가 음수인 등비수열 $LEFT{a_{n} RIGHT}$의 첫째항부터 제$n$항까지의 합을 $S_{n}$이라 할 때, $LEFT(S_{n+1}-2S_{n}+S_{n-1} RIGHT)^{2}=7LEFT(a_{n} RIGHT)^{2}-a_{n}a_{n+1}$ $(n GEQ 2)$이 성립한다. 다음 물음에 답하시오. (단, $a_{1}=S_{1}$이다.)',
    text2=[
        '(1) 수열 $LEFT{a_{n} RIGHT}$의 공비를 구하고, 그 과정을 서술하시오. [$4.0$점]',
        '(2) 수열 $LEFT{T_{n} RIGHT}$에 대하여 $T_{n}=LEFT({1} over {a_{1}}+{1} over {a_{2}}+ cdots+{1} over {a_{n}} RIGHT) timesLEFT{(a_{1})^{2}+(a_{2})^{2}+ cdots+(a_{n})^{2} RIGHT}$ $(n=1,~2,~3,~ cdots)$일 때, 일반항 $T_{n}$을 $a$와 $n$의 식으로 표현한 후, ${T_{4}} over {a}$의 값을 구하고, 그 과정을 서술하시오. [$6$점]',
    ],
    ans_mix='(1) $it-2$ (2) ${425} over {8}$',
    sol=[
        '(1) $S_{n+1}-S_{n}=a_{n+1}$, $S_{n}-S_{n-1}=a_{n}$이므로 $S_{n+1}-2S_{n}+S_{n-1}=a_{n+1}-a_{n}$',
        '$(a_{n+1}-a_{n})^{2}=7a_{n}^{2}-a_{n}a_{n+1}$',
        '공비를 $r$이라 하면 양변을 $a_{n}^{2}$으로 나누어 $(r-1)^{2}=7-r$',
        '$r^{2}-2r+1=7-r$',
        '$r^{2}-r-6=0$',
        '$(r-3)(r+2)=0$',
        '$r=3$ 또는 $r=it-2$',
        '공비가 음수이므로 $therefore~r=it-2$',
        '(2) $a_{n}=a timesLEFT(it-2 RIGHT)^{n-1}$',
        '${1} over{a_{1}}+ cdots+{1} over{a_{n}}={1} over{a}sum^{n}_{k=1}LEFT(it- {1} over{2} RIGHT)^{k-1}={1} over{a} times{1-LEFT(it- {1} over{2} RIGHT)^{n}} over{1-LEFT(it- {1} over{2} RIGHT)}={2} over{3a}LEFT{1-LEFT(it- {1} over{2} RIGHT)^{n} RIGHT}$',
        '$(a_{1})^{2}+ cdots+(a_{n})^{2}=a^{2}sum^{n}_{k=1}4^{k-1}=a^{2} times{4^{n}-1} over{3}$',
        '$T_{n}={2} over{3a}LEFT{1-LEFT(it- {1} over{2} RIGHT)^{n} RIGHT} times a^{2} times{4^{n}-1} over{3}={2a} over{9}LEFT{1-LEFT(it- {1} over{2} RIGHT)^{n} RIGHT}(4^{n}-1)$',
        '$n=4$일 때 $LEFT(it- {1} over{2} RIGHT)^{4}={1} over{16}$이므로 $1-{1} over{16}={15} over{16}$, $4^{4}-1=255$',
        '$T_{4}={2a} over{9} times{15} over{16} times255$',
        '$={2 times15 times255} over{9 times16}a={7650} over{144}a={425} over{8}a$',
        '$therefore~{T_{4}} over{a}$',
        '$={425} over{8}$',
    ],
    ch='등비수열', lv='상')

add(id='q18', kind='sub', no=3, score=10,
    text='곡선 $y=3tanLEFT({1} over {6}(x-pi) RIGHT)$ $(0 LEQ x LEQ 15 pi)$와 직선 $y=sqrt {3}$에 대하여 다음 물음에 답하시오.',
    text2=[
        '(1) 곡선 $y=3tanLEFT({1} over {6}(x-pi) RIGHT)$ $(0 LEQ x LEQ 15 pi)$의 주기와 점근선을 구하시오. [$2.0$점]',
        '(2) 점 $rm P(9 pi,~a)$가 곡선 $y=3tanLEFT({1} over {6}(x-pi) RIGHT)$ $(0 LEQ x LEQ 15 pi)$ 위의 점일 때, 점 $rm P$의 $y$좌표 $a$을 구하고 그 과정을 서술하시오. [$3.0$점]',
        '(3) 곡선 $y=3tanLEFT({1} over {6}(x-pi) RIGHT)$ $(0 LEQ x LEQ 15 pi)$와 직선 $y=sqrt{3}$의 교점을 $rm A$, $rm B$라 할 때, 삼각형 $rm PAB$의 넓이의 최댓값을 구하고 그 과정을 서술하시오. [$5.0$점]',
    ],
    ans_mix='(1) 주기 $6 pi$, 점근선 $x=4 pi,~x=10 pi$ (2) $a=3 sqrt{3}$ (3) $12 sqrt{3}pi$',
    sol=[
        '(1) 주기 $={pi} over {LEFT | {1} over{6} RIGHT |}=6 pi$',
        '점근선은 ${1} over{6}(x-pi)={pi} over{2}+kpi$에서 $x=4 pi+6kpi$ ($k$는 정수)',
        '$0 LEQ x LEQ 15 pi$를 만족시키는 것은 $k=0,~1$일 때이므로 점근선은 $x=4 pi$, $x=10 pi$',
        '(2) $a=3tanLEFT{{1} over{6}(9 pi-pi) RIGHT}=3tanLEFT({8 pi} over{6} RIGHT)=3tanLEFT({4} over{3}pi RIGHT)$',
        '$tanLEFT({4} over{3}pi RIGHT)=tanLEFT(pi+{pi} over{3} RIGHT)=tanLEFT({pi} over{3} RIGHT)=sqrt{3}$',
        '$therefore~a=3 sqrt{3}$',
        '(3) $3tanLEFT({1} over{6}(x-pi) RIGHT)=sqrt{3}$에서 $tanLEFT({1} over{6}(x-pi) RIGHT)={1} over{sqrt{3}}$',
        '${1} over{6}(x-pi)={pi} over{6}+kpi$에서 $x=2 pi+6kpi$',
        '$0 LEQ x LEQ 15 pi$를 만족시키는 $x$는 $k=0,~1,~2$일 때 $x=2 pi,~8 pi,~14 pi$로 모두 $3$개이다.',
        {'fig': 'ghh24f_q18_sol'},
        '점 $rm P(9 pi,~3 sqrt{3})$은 직선 $y=sqrt{3}$ 위에 있지 않으므로 $rm P$에서 이 직선까지의 거리는 $LEFT | 3 sqrt{3}-sqrt{3} RIGHT |=2 sqrt{3}$으로 일정하다.',
        '세 교점 $(2 pi,~sqrt{3})$, $(8 pi,~sqrt{3})$, $(14 pi,~sqrt{3})$ 중 두 점을 $rm A$, $rm B$로 잡을 때,',
        '삼각형 $rm PAB$의 넓이 $={1} over{2} timesbar{rm AB} times2 sqrt{3}=sqrt{3} timesbar{rm AB}$이므로 $bar{rm AB}$가 최대일 때 넓이도 최대이다.',
        '세 점 중 거리가 가장 먼 두 점은 $(2 pi,~sqrt{3})$과 $(14 pi,~sqrt{3})$이고 $bar{rm AB}=14 pi-2 pi=12 pi$',
        '$therefore$ 넓이의 최댓값 $=sqrt{3} times12 pi$',
        '$=12 sqrt{3}pi$',
    ],
    ch='삼각함수와 그래프', lv='상')
