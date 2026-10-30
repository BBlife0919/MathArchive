# -*- coding: utf-8 -*-
"""광휘고등학교 2학년 2026 1학기 기말 대수(삼각함수의 활용~수열의 귀납적 정의) 20문항 내용.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.5, layout='3+2',
    text='첫째항이 $1$이고 공차가 $2$인 등차수열 ${a_{n}}$의 제$5$항은?',
    choices=['$3$', '$5$', '$7$', '$9$', '$11$'],
    ans='④',
    sol=[
        '$a_{n}=1+(n-1) times2=2n-1$',
        '$therefore~a_{5}=2 times5-1$',
        '$=9$',
    ],
    ch='등차수열의 일반항', lv='하')

add(id='q02', kind='mc', no=2, score=4.5, layout='3+2',
    text='$a_{1}=3$, $a_{n+1}=a_{n}-2n$($n=1,~2,~3,~ cdots$)과 같이 정의된 수열 ${a_{n}}$에서 $a_{3}$의 값은?',
    choices=['$it-3$', '$it-2$', '$it-1$', '$0$', '$1$'],
    ans='①',
    sol=[
        '$a_{2}=a_{1}-2(1)=3-2=1$',
        '$a_{3}=a_{2}-2(2)=1-4$',
        '$therefore~a_{3}$',
        '$=it-3$',
    ],
    ch='수열의 귀납적 정의', lv='하')

add(id='q03', kind='mc', no=3, score=4.5, layout='3+2',
    text='$bar{AB}=4$, $∠ACB= pi/6$인 삼각형 $ABC$의 외접원의 반지름의 길이는?',
    choices=['$2 sqrt{2}$', '$4$', '$4 sqrt{2}$', '$8$', '$8 sqrt{2}$'],
    ans='②',
    sol=[
        '사인법칙: ${bar{AB}} over{ sin( ∠ ACB)}=2R$이므로 $2R={4} over{ sin30^{ circ}}={4} over{1/2}=8$',
        '$therefore~R$',
        '$=4$',
    ],
    ch='사인법칙', lv='하')

add(id='q04', kind='mc', no=4, score=4.5, layout='3+2',
    text='두 수열 ${a_{n}},~{b_{n}}$에 대하여 $ sum^{10}_{k=1}a_{k}=10$이고 $ sum^{10}_{k=1}b_{k}=2$일 때, $ sum^{10}_{k=1}(a_{k}+2b_{k})$의 값은?',
    choices=['$10$', '$12$', '$14$', '$16$', '$18$'],
    ans='③',
    sol=[
        '$ sum^{10}_{k=1}(a_{k}+2b_{k})= sum^{10}_{k=1}a_{k}+2 sum^{10}_{k=1}b_{k}=10+2(2)$',
        '$therefore$ 구하는 값은',
        '$=14$',
    ],
    ch='수열의 합의 성질', lv='하')

add(id='q05', kind='mc', no=5, score=4.5, layout='3+2',
    text='등비수열 ${a_{n}}$의 일반항이 $a_{n}=2 times3^{2n-3}$일 때, 첫째항 $a_{1}$과 공비 $r$에 대하여 $a_{1} times r$의 값은?',
    choices=['$2$', '$3$', '$4$', '$5$', '$6$'],
    ans='⑤',
    sol=[
        '$a_{1}=2 times3^{2(1)-3}=2 times3^{it-1}={2} over{3}$',
        '$r={a_{n+1}} over{a_{n}}=3^{2}=9$',
        '$therefore~a_{1} times r={2} over{3} times9$',
        '$=6$',
    ],
    ch='등비수열의 일반항과 공비', lv='하')

add(id='q06', kind='mc', no=6, score=4.5, layout='3+2',
    text='$bar{AB}=2$, $bar{BC}=4$, $bar{CA}=5$인 삼각형 $ABC$의 세 내각 중에서 크기가 가장 작은 내각의 크기를 $ theta$라 할 때, $ cos theta$의 값은?',
    choices=['${33} over{40}$', '${17} over{20}$', '${7} over{8}$', '${9} over{10}$', '${37} over{40}$'],
    ans='⑤',
    sol=[
        '가장 작은 내각은 가장 짧은 변 $bar{AB}=2$의 대각, 즉 각 $C$이다.',
        '코사인법칙: $ cos C={bar{CA}^{2}+bar{CB}^{2}-bar{AB}^{2}} over{2 times bar{CA} times bar{CB}}={25+16-4} over{2 times5 times4}={37} over{40}$',
        '$therefore~ cos theta$',
        '$={37} over{40}$',
    ],
    ch='코사인법칙', lv='하')

add(id='q07', kind='mc', no=7, score=4.7, layout='3+2',
    text='세 수 $2a,~a^{2}-2,~20$이 순서대로 등차수열을 이룰 때, 양수 $a$의 값은?',
    choices=['$1$', '$2$', '$3$', '$4$', '$5$'],
    ans='④',
    sol=[
        '등차중항의 성질에 의해 $2(a^{2}-2)=2a+20$',
        '$2a^{2}-4=2a+20$에서 $2a^{2}-2a-24=0$, $a^{2}-a-12=0$',
        '$(a-4)(a+3)=0$이고 $a$는 양수이므로',
        '$therefore~a$',
        '$=4$',
    ],
    ch='등차중항', lv='중')

add(id='q08', kind='mc', no=8, score=4.8, layout='1x5',
    text='$0<x<2 pi$에서 방정식 $ tan LEFT(x+ pi/6 RIGHT)=1$의 모든 실근의 합은?',
    choices=['${5} over{6} pi$', '$ pi$', '${7} over{6} pi$', '${4} over{3} pi$', '${3} over{2} pi$'],
    ans='③',
    sol=[
        '$x+{ pi} over{6}={ pi} over{4}+n pi$ ($n$은 정수)에서 $x={ pi} over{12}+n pi$',
        '$0<x<2 pi$를 만족시키는 $x$는 $n=0$일 때 $x={ pi} over{12}$, $n=1$일 때 $x={ pi} over{12}+ pi={13} over{12} pi$',
        '$therefore$ 모든 실근의 합은 ${ pi} over{12}+{13} over{12} pi={14} over{12} pi$',
        '$={7} over{6} pi$',
    ],
    ch='삼각방정식', lv='중')

add(id='q09', kind='mc', no=9, score=4.9, layout='1x5',
    text='이차방정식 $x^{2}+3x+1=0$의 두 근을 $ alpha$와 $ beta$라 할 때, $ sum^{10}_{k=1}(k-2 alpha)(k-2 beta)$의 값은?',
    choices=['$755$', '$760$', '$765$', '$770$', '$775$'],
    ans='①',
    sol=[
        '근과 계수의 관계에 의해 $ alpha+ beta=it-3$, $ alpha beta=1$',
        '$(k-2 alpha)(k-2 beta)=k^{2}-2k( alpha+ beta)+4 alpha beta=k^{2}+6k+4$',
        '$ sum^{10}_{k=1}(k^{2}+6k+4)= sum^{10}_{k=1}k^{2}+6 sum^{10}_{k=1}k+4 times10$',
        '$={10 times11 times21} over{6}+6 times{10 times11} over{2}+40=385+330+40$',
        '$therefore$ 구하는 값은',
        '$=755$',
    ],
    ch='이차방정식의 근과 수열의 합', lv='중')

add(id='q10', kind='mc', no=10, score=5.0, layout='1x5',
    text='수열 ${a_{n}}$에 대하여 $ sum^{13}_{k=1}(ka_{k}+2)=46$, $ sum^{14}_{k=2}(ka_{k-1}-1)=116$일 때, $ sum^{13}_{k=1}a_{k}$의 값은?',
    choices=['$109$', '$111$', '$113$', '$115$', '$117$'],
    ans='①',
    sol=[
        '$ sum^{13}_{k=1}(ka_{k}+2)= sum^{13}_{k=1}ka_{k}+26=46$에서 $ sum^{13}_{k=1}ka_{k}=20$',
        '$ sum^{14}_{k=2}(ka_{k-1}-1)$에서 $j=k-1$로 치환하면 $ sum^{13}_{j=1}LEFT{(j+1)a_{j}-1 RIGHT}= sum^{13}_{j=1}(j+1)a_{j}-13=116$',
        '$ sum^{13}_{j=1}(j+1)a_{j}=129$에서 $ sum ja_{j}+ sum a_{j}=129$',
        '$20+ sum^{13}_{j=1}a_{j}=129$',
        '$therefore~ sum^{13}_{k=1}a_{k}$',
        '$=109$',
    ],
    ch='수열의 합과 일반항', lv='중')

add(id='q11', kind='mc', no=11, score=5.1, layout='1x5', jogeon=True,
    text='첫째항이 자연수인 등비수열 ${a_{n}}$이 다음 조건을 만족시킬 때 $a_{2}$의 값은?',
    jogeon_items=[
        '$a_{3} times a_{5}=16$',
        '${a_{5}+a_{7}} over{a_{6}}={5} over{2}$',
    ],
    choices=['$2$', '$4$', '$8$', '$16$', '$32$'],
    ans='④',
    sol=[
        '(가)에서 $a_{3} times a_{5}=a_{4}^{2}=16$이므로 $a_{4}= pm4$',
        '(나)에서 ${a_{5}+a_{7}} over{a_{6}}={a_{1}r^{4}+a_{1}r^{6}} over{a_{1}r^{5}}={1} over{r}+r={5} over{2}$',
        '$2r^{2}-5r+2=0$에서 $(2r-1)(r-2)=0$이므로 $r=2$ 또는 $r={1} over{2}$',
        '$r=2$: $a_{4}=a_{1} times8= pm4$에서 $a_{1}= pm{1} over{2}$, 자연수가 아니므로 모순',
        '$r={1} over{2}$: $a_{4}=a_{1} times{1} over{8}= pm4$에서 $a_{1}= pm32$, 자연수 조건에서 $a_{1}=32$',
        '$therefore~a_{2}=a_{1} times r=32 times{1} over{2}$',
        '$=16$',
    ],
    ch='등비수열의 조건', lv='상')

add(id='q12', kind='mc', no=12, score=5.2, layout='1x5',
    text='수열 ${a_{n}}$이 모든 자연수 $n$에 대하여 $a_{n+1}= cases{a_{n}-3~~(a_{n}이~홀수인~경우)#4a_{n}+2~~(a_{n}이~짝수인~경우)}$를 만족시킬 때, $a_{3}=42$가 되도록 하는 모든 $a_{1}$의 값의 합은?',
    choices=['$14$', '$15$', '$16$', '$17$', '$18$'],
    ans='②',
    sol=[
        '$a_{3}=42$가 되는 $a_{2}$를 역추적: $a_{2}$가 홀수이면 $a_{2}-3=42$에서 $a_{2}=45$(홀수, 성립)',
        '$a_{2}$가 짝수이면 $4a_{2}+2=42$에서 $a_{2}=10$(짝수, 성립)',
        '[$a_{2}=45$인 경우] $a_{1}$이 홀수이면 $a_{1}-3=45$에서 $a_{1}=48$인데 짝수이므로 모순. $a_{1}$이 짝수이면 $4a_{1}+2=45$는 정수해 없음. 따라서 $a_{2}=45$가 되는 $a_{1}$은 없다.',
        '[$a_{2}=10$인 경우] $a_{1}$이 홀수이면 $a_{1}-3=10$에서 $a_{1}=13$(홀수, 성립). $a_{1}$이 짝수이면 $4a_{1}+2=10$에서 $a_{1}=2$(짝수, 성립)',
        '따라서 $a_{1}=13$ 또는 $a_{1}=2$',
        '$therefore$ 모든 $a_{1}$의 값의 합은',
        '$=15$',
    ],
    ch='수열의 귀납적 정의(역추적)', lv='상')

add(id='q13', kind='mc', no=13, score=5.3, layout='1x5',
    text='수열 ${a_{n}}$의 첫째항부터 제$n$항까지의 합 $S_{n}$이 $S_{n}=2n^{2}-kn$이다. 모든 자연수 $n$에 대하여 $S_{n} GEQ S_{8}$을 만족할 때, 모든 정수 $k$의 값의 합은?',
    choices=['$158$', '$160$', '$162$', '$164$', '$166$'],
    ans='②',
    sol=[
        '$a_{n}=S_{n}-S_{n-1}=4n-2-k$ ($n GEQ 2$)',
        '$S_{n}$이 $n=8$에서 최소가 되려면 $a_{8} LEQ 0$이고 $a_{9} GEQ 0$이어야 한다.',
        '$a_{8}=32-2-k=30-k LEQ 0$에서 $k GEQ 30$',
        '$a_{9}=36-2-k=34-k GEQ 0$에서 $k LEQ 34$',
        '따라서 $30 LEQ k LEQ 34$인 정수 $k$는 $30,~31,~32,~33,~34$',
        '$therefore$ 모든 $k$의 값의 합은 $30+31+32+33+34$',
        '$=160$',
    ],
    ch='수열의 합의 최솟값', lv='상')

add(id='q14', kind='mc', no=14, score=5.4, layout='1x5', fig='gh26f_q14',
    text='그림과 같이 $bar{AB}=4$, $∠B= pi/4$인 삼각형 $ABC$에서 선분 $BC$ 위에 점 $D$를 $bar{AD}=bar{CD}=3$이 되도록 잡는다. 선분 $AC$의 길이는? (단, $∠ADB< pi/2$)',
    choices=['$2 sqrt{5}$', '$ sqrt{22}$', '$2 sqrt{6}$', '$ sqrt{26}$', '$2 sqrt{7}$'],
    ans='③',
    sol=[
        '삼각형 $ABD$에서 코사인법칙: $bar{AD}^{2}=bar{AB}^{2}+bar{BD}^{2}-2 times bar{AB} times bar{BD} times cos B$',
        '$9=16+bar{BD}^{2}-8 bar{BD} times{ sqrt{2}} over{2}$에서 $bar{BD}^{2}-4 sqrt{2} bar{BD}+7=0$',
        '$bar{BD}={4 sqrt{2} pm sqrt{32-28}} over{2}=2 sqrt{2} pm1$',
        '$ cos( ∠ ADB)={bar{AD}^{2}+bar{BD}^{2}-bar{AB}^{2}} over{2 times bar{AD} times bar{BD}}={bar{BD}^{2}-7} over{6 bar{BD}}$',
        '$bar{BD}=2 sqrt{2}+1$이면 $bar{BD}^{2}-7=2+4 sqrt{2}>0$이므로 $ cos( ∠ ADB)>0$ ($ ∠ ADB$가 예각, 조건에 부합)',
        '$ ∠ ADC= pi- ∠ ADB$이므로 $ cos( ∠ ADC)=it- cos( ∠ ADB)$',
        '검산을 통해 $ cos( ∠ ADB)={1} over{3}$임을 확인할 수 있으므로 $ cos( ∠ ADC)=it-{1} over{3}$',
        '삼각형 $ADC$에서 $bar{AD}=bar{DC}=3$이므로 $bar{AC}^{2}=9+9-2(9) cos( ∠ ADC)=18-18LEFT(it-{1} over{3} RIGHT)=18+6$',
        '$therefore~bar{AC}= sqrt{24}$',
        '$=2 sqrt{6}$',
    ],
    ch='사인법칙과 코사인법칙의 활용', lv='최상')

add(id='q15', kind='mc', no=15, score=5.5, layout='1x5',
    text=[
        '첫째항이 $a$이고 공비가 $r$인 등비수열 ${a_{n}}$과 첫째항이 $ar$이고 공비가 $r^{2}$인 등비수열 ${b_{n}}$에 대하여',
        '$a_{1}+a_{2}+a_{3}=13$, $b_{1}+b_{2}+b_{3}=273$이다.',
        '$1/a_{1}+1/a_{2}+1/a_{3}+1/a_{4}+1/a_{5}=q/p$일 때, $p+q$의 값은? (단, $r>0$이고, $p$와 $q$는 서로소인 자연수이다.)',
    ],
    choices=['$198$', '$199$', '$200$', '$201$', '$202$'],
    ans='⑤',
    sol=[
        '$b_{n}=ar times(r^{2})^{n-1}=ar^{2n-1}=a_{2n}$이므로 $b_{1}+b_{2}+b_{3}=a_{2}+a_{4}+a_{6}=273$',
        '${a_{2}+a_{4}+a_{6}} over{a_{1}+a_{2}+a_{3}}={ar+ar^{3}+ar^{5}} over{a+ar+ar^{2}}=r times{1+r^{2}+r^{4}} over{1+r+r^{2}}={273} over{13}=21$',
        '$1+r^{2}+r^{4}=(1+r+r^{2})(1-r+r^{2})$이므로 $r(1-r+r^{2})=21$',
        '$r=3$을 대입하면 $3(1-3+9)=3 times7=21$이 성립하므로 $r=3$',
        '$a(1+3+9)=13$에서 $a=1$이므로 $a_{n}=3^{n-1}$',
        '${1} over{a_{1}}+ cdots+{1} over{a_{5}}=1+{1} over{3}+{1} over{9}+{1} over{27}+{1} over{81}={81+27+9+3+1} over{81}={121} over{81}$',
        '$121=11^{2}$, $81=3^{4}$이므로 서로소이다. $p=81$, $q=121$',
        '$therefore~p+q=81+121$',
        '$=202$',
    ],
    ch='등비수열의 변형과 합', lv='최상')

add(id='q16', kind='mc', no=16, score=5.6, layout='1x5',
    text='자연수 $n$에 대하여 곡선 $y=2^{x}$가 직선 $x=n$과 만나는 점을 $A_{n}$이라 하고, 두 점 $A_{n},~A_{n+1}$을 지나는 직선이 $x$축과 만나는 점을 $P_{n}$이라 하자. $ sum^{15}_{k=2}bar{OP_{k}}$의 값은? (단, $O$는 원점이다.)',
    choices=['$100$', '$105$', '$110$', '$115$', '$120$'],
    ans='②',
    sol=[
        '$A_{n}=(n,~2^{n})$. 두 점 $A_{n}(n,~2^{n})$, $A_{n+1}(n+1,~2^{n+1})$을 지나는 직선의 기울기는 ${2^{n+1}-2^{n}} over{1}=2^{n}$',
        '직선의 방정식: $y-2^{n}=2^{n}(x-n)$. $y=0$을 대입하면 $it-2^{n}=2^{n}(x-n)$에서 $x=n-1$',
        '즉 $P_{n}=(n-1,~0)$이므로 $bar{OP_{n}}=n-1$',
        '$therefore~ sum^{15}_{k=2}bar{OP_{k}}= sum^{15}_{k=2}(k-1)= sum^{14}_{j=1}j={14 times15} over{2}$',
        '$=105$',
    ],
    ch='지수함수와 수열의 합', lv='상')

add(id='q17', kind='mc', no=17, score=5.7, layout='1x5',
    text=[
        '$0<t<1$인 상수 $t$에 대하여 $0 LEQ x LEQ 5 pi/2$일 때, 부등식',
        '$ sin x<t$를 만족시키는 모든 $x$의 값의 범위는 $0 LEQ x< alpha$ 또는 $ beta<x< gamma$이다. $4( beta- alpha)= gamma- beta$일 때, 집합',
        '$LEFT{n LEFT | cos(n pi/10)>t,~n은~30이하의~자연수 RIGHT.RIGHT}$의 모든 원소의 합은?',
    ],
    choices=['$57$', '$59$', '$61$', '$63$', '$65$'],
    ans='③',
    sol=[
        '$s= arcsin(t)$ ($0<s<{ pi} over{2}$)라 하면, $0 LEQ x LEQ{5} over{2} pi$에서 $ sin x GEQ t$인 구간은 $[s,~ pi-s]$와 $[2 pi+s,~{5} over{2} pi]$이다.',
        '따라서 $ sin x<t$인 범위는 $[0,~s) cup( pi-s,~2 pi+s)$이므로 $ alpha=s$, $ beta= pi-s$, $ gamma=2 pi+s$',
        '$4( beta- alpha)=4( pi-2s)$, $ gamma- beta=( pi+2s)$',
        '$4 pi-8s= pi+2s$에서 $3 pi=10s$이므로 $s={3} over{10} pi$',
        '$t= sin{3} over{10} pi= cos LEFT({ pi} over{2}-{3} over{10} pi RIGHT)= cos{ pi} over{5}$',
        '$ cos LEFT({n} over{10} pi RIGHT)> cos{ pi} over{5}= cos LEFT({2} over{10} pi RIGHT)$을 만족시키는 조건은 ${n} over{10} pi in LEFT(2k pi-{ pi} over{5},~2k pi+{ pi} over{5} RIGHT)$',
        '즉 $n in(20k-2,~20k+2)$. $k=0$: $n=1$. $k=1$: $n=19,~20,~21$. ($30$ 이하의 자연수 범위에서 그 외의 $k$는 해당 없음)',
        '$therefore$ 모든 원소의 합은 $1+19+20+21$',
        '$=61$',
    ],
    ch='삼각부등식과 수열의 합', lv='최상')

add(id='q18', kind='mc', no=18, score=5.8, layout='1x5', fig='gh26f_q18', jogeon=True,
    text='그림과 같이 선분 $AB$를 지름으로 하는 반원에 대하여 선분 $AB$의 중점을 $C$라 하자. 호 $AB$ 위의 두 점 $D,~E$가 다음 조건을 만족시킨다.',
    jogeon_items=[
        '$bar{DE}=2 sqrt{7}$',
        '$ sin( ∠ CDE)={3} over{4}$, $ sin( ∠ CAE)={ sqrt{15}} over{8}$',
    ],
    text2=['선분 $AD$의 길이가 이차방정식 $2x^{2}-21x+a=0$의 한 근일 때 실수 $a$의 값은? (단, $bar{AD}<bar{AE}$)'],
    choices=['$42$', '$43$', '$44$', '$45$', '$46$'],
    ans='①',
    sol=[
        '$C$가 중심이므로 $bar{CA}=bar{CB}=bar{CD}=bar{CE}=r$(반지름)이다.',
        '삼각형 $CDE$는 $bar{CD}=bar{CE}=r$인 이등변삼각형. $ ∠ CDE= ∠ CED= phi$라 하면 $ sin phi={3} over{4}$, $ cos phi={ sqrt{7}} over{4}$',
        '$ ∠ DCE= pi-2 phi$이고 사인법칙으로 $r$을 구하면 $r=4$',
        '삼각형 $CAE$도 $bar{CA}=bar{CE}=4$인 이등변삼각형. $ ∠ CAE= ∠ CEA= psi$라 하면 $ sin psi={ sqrt{15}} over{8}$, $ cos psi={7} over{8}$',
        '$bar{AE}=2r cos psi$ (이등변삼각형의 성질에서 유도)$=8 times{7} over{8}$',
        '$=7$',
        '같은 방법으로 두 중심각의 관계를 이용해 $ ∠ ACD=2( phi- psi)$를 얻고, $bar{AD}^{2}=2r^{2}LEFT(1- cos( ∠ ACD) RIGHT)$로 $bar{AD}$를 구할 수 있다.',
        '직접 대입·계산하면 $bar{AD} approx2.69$를 얻고, 이를 $2x^{2}-21x+a=0$에 대입하여 $a=21 bar{AD}-2 bar{AD}^{2}$를 계산하면',
        '$therefore~a$',
        '$=42$',
    ],
    ch='원과 삼각형의 활용', lv='최상')

add(id='q19', kind='sub', no=1, score=7.0, layout='1x5',
    text='$a=4,~b=6$인 삼각형 $ABC$의 외접원의 반지름의 길이를 $R$이라 하자. $R=2c$일 때, 삼각형 $ABC$의 넓이를 구하고 그 과정을 서술하시오. (단, $bar{BC}=a$, $bar{CA}=b$, $bar{AB}=c$)',
    ans_mix='$3$',
    sol=[
        '사인법칙에 의해 $R={c} over{2 sin C}$이므로, $R=2c$라는 조건에서 $2c={c} over{2 sin C}$',
        '양변에서 $c$를 소거하면 $2={1} over{2 sin C}$에서 $ sin C={1} over{4}$',
        '삼각형의 넓이 공식 $S={1} over{2}ab sin C$를 이용하면',
        '$S={1} over{2} times4 times6 times{1} over{4}={1} over{2} times6$',
        '$therefore~S$',
        '$=3$',
    ],
    ch='사인법칙과 삼각형의 넓이', lv='중')

add(id='q20', kind='sub', no=2, score=8.0, layout='1x5',
    text='$ sum^{30}_{k=1}1/(4k^{2}-1)$의 값을 구하고 그 과정을 서술하시오.',
    ans_mix='${30} over{61}$',
    sol=[
        '$4k^{2}-1=(2k-1)(2k+1)$이므로 ${1} over{4k^{2}-1}={1} over{(2k-1)(2k+1)}={1} over{2}LEFT({1} over{2k-1}-{1} over{2k+1} RIGHT)$',
        '$ sum^{30}_{k=1}{1} over{4k^{2}-1}={1} over{2} sum^{30}_{k=1}LEFT({1} over{2k-1}-{1} over{2k+1} RIGHT)$',
        '망원급수로 중간항이 모두 소거되어 ${1} over{2}LEFT({1} over{1}-{1} over{61} RIGHT)={1} over{2} times{60} over{61}$',
        '$therefore$ 구하는 값은',
        '$={30} over{61}$',
    ],
    ch='수열의 합(부분분수)', lv='중')
