# -*- coding: utf-8 -*-
"""광문고등학교 2학년 2026 1학기 중간 대수 20문항 내용 (선택형 17 + 서술형 3).
출처: 광문고등학교_2학년_수학_2026_1학기_중간고사_원본.pdf (저해상도 스캔, ~150dpi).
학생 체크 답안은 참고만 하고 전 문항 독립적으로 재계산함(일부는 학생 오답 확인·정정).
Q1, Q15, Q16은 스캔 해상도 한계로 판독 불가능한 디테일(선지 근호 지수, 보기 조건문 일부)이 있어
사용자 승인 하에 문제 구조·유형은 원본에 충실히 유지하되 계산이 깔끔하게 맞아떨어지는
숫자로 재구성함.
마크업: $...$ = 수식(HWP 스크립트), 그 외 = 일반 텍스트.
"""

Q = []


def add(**kw):
    Q.append(kw)


add(id='q01', kind='mc', no=1, score=4.2, layout='3+2',
    text='$7^{3/4} times7^{1/4} div7^{-1/2}$의 값은?',
    choices=['$ sqrt{7^{3}}$', '$ sqrt[3]{7^{3}}$', '$ sqrt[4]{7^{3}}$', '$ sqrt[5]{7^{3}}$', '$ sqrt[6]{7^{3}}$'],
    ans='①',
    sol=[
        '지수법칙에 의해 $7^{{3}over{4}} times7^{{1}over{4}} div7^{-{1}over{2}}=7^{{3}over{4}+{1}over{4}+{1}over{2}}$',
        '$=7^{{3}over{2}}$',
        '$therefore~7^{{3}over{2}}= sqrt{7^{3}}$',
    ],
    ch='지수법칙', lv='중')

add(id='q02', kind='mc', no=2, score=4.2, layout='3+2',
    text='$3 log_{2}2 sqrt{2}+ log_{2} sqrt{2}$의 값은?',
    choices=['$3$', '${7}over{2}$', '$4$', '${9}over{2}$', '$5$'],
    ans='⑤',
    sol=[
        '$2 sqrt{2}=2^{{3}over{2}}$이므로 $ log_{2}2 sqrt{2}={3}over{2}$',
        '$3 times{3}over{2}={9}over{2}$',
        '$ log_{2} sqrt{2}={1}over{2}$',
        '$therefore~{9}over{2}+{1}over{2}=5$',
    ],
    ch='로그의 정의', lv='중')

add(id='q03', kind='mc', no=3, score=4.4, layout='3+2',
    text='$3 sqrt[4]{32}- sqrt[4]{512}$의 값은?',
    choices=['$2 sqrt[4]{2}$', '$3 sqrt[4]{2}$', '$4 sqrt[4]{2}$', '$5 sqrt[4]{2}$', '$6 sqrt[4]{2}$'],
    ans='①',
    sol=[
        '$32=2^{5}$이므로 $ sqrt[4]{32}=2^{{5}over{4}}=2 sqrt[4]{2}$이고 $3 sqrt[4]{32}=6 sqrt[4]{2}$',
        '$512=2^{9}$이므로 $ sqrt[4]{512}=2^{{9}over{4}}=4 sqrt[4]{2}$',
        '$therefore~6 sqrt[4]{2}-4 sqrt[4]{2}=2 sqrt[4]{2}$',
    ],
    ch='거듭제곱근', lv='중')

add(id='q04', kind='mc', no=4, score=4.4, layout='3+2',
    text='반지름의 길이가 $5$, 중심각의 크기가 $4$인 부채꼴의 넓이는?',
    choices=['$45$', '$50$', '$55$', '$60$', '$65$'],
    ans='②',
    sol=[
        '부채꼴의 넓이 $S={1}over{2}r^{2} theta$에서',
        '$S={1}over{2} times5^{2} times4={1}over{2} times25 times4$',
        '$therefore~S=50$',
    ],
    ch='호도법과 부채꼴의 넓이', lv='중')

add(id='q05', kind='mc', no=5, score=4.4, layout='3+2',
    text='$ theta$가 제$2$사분면의 각이고 $ sintheta+costheta= sqrt{3}/3$일 때, $ sintheta costheta$의 값은?',
    choices=['$-{1}over{2}$', '$-{1}over{3}$', '$-{1}over{4}$', '$-{1}over{5}$', '$-{1}over{6}$'],
    ans='②',
    sol=[
        '$( sintheta+costheta)^{2}=1+2 sintheta costheta$',
        '$ LEFT({ sqrt{3}}over{3} RIGHT)^{2}={1}over{3}$이므로 $1+2 sintheta costheta={1}over{3}$',
        '$2 sintheta costheta=-{2}over{3}$',
        '$therefore~ sintheta costheta=-{1}over{3}$',
    ],
    ch='삼각함수 사이의 관계', lv='중')

add(id='q06', kind='mc', no=6, score=4.6, layout='3+2',
    text='어느 악취 물질의 농도가 $x$ppm일 때 악취의 세기를 $I$라 하면 $I=3/2 log x+5/2$인 관계가 성립한다고 한다. 이 물질의 농도가 $100$ppm일 때 악취의 세기를 $I_{1}$, 농도가 $1$ppm일 때 악취의 세기를 $I_{2}$라 할 때, $I_{1}/I_{2}$의 값은?',
    choices=['${5}over{11}$', '${9}over{11}$', '${11}over{9}$', '$2$', '${11}over{5}$'],
    ans='⑤',
    sol=[
        '$I_{1}={3}over{2} log100+{5}over{2}={3}over{2} times2+{5}over{2}={11}over{2}$',
        '$I_{2}={3}over{2} log1+{5}over{2}=0+{5}over{2}={5}over{2}$',
        '$therefore~{I_{1}}over{I_{2}}={11}over{2} times{2}over{5}={11}over{5}$',
    ],
    ch='상용로그의 활용', lv='중')

add(id='q07', kind='mc', no=7, score=4.6, layout='3+2', box=True,
    text=['$a$가 $1$이 아닌 양의 실수일 때, 함수 $f(x)=a^{x}$와 함수 $g(x)= log_{a}x$에 대해 옳은 것만을 <보기>에서 있는 대로 고른 것은? (단, $m,~n$은 $0$보다 큰 실수이다.)'],
    box_items=[
        '$f(-m)={1}over{f(m)}$',
        '$a^{f^{-1}(m)} times log_{a}f(m)=1$',
        '$g(mn^{-1})=g(m)+g(n)$',
    ],
    choices=['ㄱ', 'ㄱ,~ㄴ', 'ㄱ,~ㄷ', 'ㄴ,~ㄷ', 'ㄱ,~ㄴ,~ㄷ'],
    ans='①',
    sol=[
        'ㄱ. $f(-m)=a^{-m}={1}over{a^{m}}={1}over{f(m)}$이므로 항상 참이다.',
        'ㄴ. $f^{-1}(m)=g(m)$이므로 $a^{f^{-1}(m)}=a^{g(m)}=m$이고 $ log_{a}f(m)=g(f(m))=m$',
        '즉 $a^{f^{-1}(m)} times log_{a}f(m)=m times m=m^{2}$이므로 $m=1$일 때만 성립하여 거짓이다.',
        'ㄷ. $g(mn^{-1})= log_{a}(m/n)= log_{a}m- log_{a}n=g(m)-g(n)$이므로 거짓이다.',
        '$therefore$ 옳은 것은 ㄱ뿐이다.',
    ],
    ch='로그함수의 성질', lv='상')

add(id='q08', kind='mc', no=8, score=4.8, layout='3+2',
    text='$x=3^{1/3}-3^{-1/3}$일 때, $x^{3}+3x$의 값은?',
    choices=['${4}over{3}$', '$2$', '${7}over{3}$', '${8}over{3}$', '$3$'],
    ans='④',
    sol=[
        '$a=3^{{1}over{3}}$, $b=3^{-{1}over{3}}$라 하면 $x=a-b$이고 $ab=3^{{1}over{3}-{1}over{3}}=1$',
        '$x^{3}=(a-b)^{3}=a^{3}-b^{3}-3ab(a-b)=LEFT(3-{1}over{3}RIGHT)-3x$',
        '$therefore~x^{3}+3x=3-{1}over{3}={8}over{3}$',
    ],
    ch='거듭제곱의 활용', lv='상')

add(id='q09', kind='mc', no=9, score=4.8, layout='3+2', box=True,
    text=['$ theta$가 제$2$사분면의 각일 때, 옳은 것만을 <보기>에서 있는 대로 고른 것은?'],
    box_items=[
        '$4^{ log_{2} sintheta}+3^{2 log_{3} LEFT|costheta RIGHT|}=1$',
        '$ sintheta- sqrt[3]{( sintheta-costheta)^{3}}+ sqrt[4]{cos^{4}theta}=0$',
        '${1}over{1-costheta}+{1}over{1+costheta}=3$일 때, $ tantheta=- sqrt{2}$',
    ],
    choices=['ㄱ', 'ㄷ', 'ㄱ,~ㄴ', 'ㄴ,~ㄷ', 'ㄱ,~ㄴ,~ㄷ'],
    ans='⑤',
    sol=[
        'ㄱ. $4^{ log_{2} sintheta}=(2^{ log_{2} sintheta})^{2}= sin^{2}theta$이고 같은 방법으로 $3^{2 log_{3} LEFT|costheta RIGHT|}=cos^{2}theta$',
        '$therefore~ sin^{2}theta+ cos^{2}theta=1$이므로 참이다.',
        'ㄴ. $ sqrt[3]{( sintheta-costheta)^{3}}= sintheta-costheta$ (세제곱근은 부호를 그대로 보존한다)',
        '$ sqrt[4]{cos^{4}theta}= LEFT|costheta RIGHT|=-costheta$ ($theta$가 제$2$사분면이므로 $costheta<0$)',
        '$therefore~ sintheta-( sintheta-costheta)+(-costheta)=0$이므로 참이다.',
        'ㄷ. ${1}over{1-costheta}+{1}over{1+costheta}={2}over{1-cos^{2}theta}={2}over{ sin^{2}theta}=3$에서 $ sin^{2}theta={2}over{3}$',
        '$theta$가 제$2$사분면이므로 $ sintheta={ sqrt{6}}over{3}$이고, $cos^{2}theta={1}over{3}$, $costheta<0$이므로 $costheta=-{ sqrt{3}}over{3}$',
        '$ tantheta={ sintheta}over{costheta}=-{ sqrt{6}}over{ sqrt{3}}=- sqrt{2}$이므로 참이다.',
        '$therefore$ ㄱ,~ㄴ,~ㄷ 모두 참이다.',
    ],
    ch='삼각함수의 성질', lv='상')

add(id='q10', kind='mc', no=10, score=4.8, layout='3+2',
    text='이차방정식 $x^{2}-10x+4=0$의 두 근이 $ log a$, $ log b$일 때, $ log_{a}b+ log_{b}a$의 값은? (단, $a,~b$는 $1$이 아닌 양의 실수이다.)',
    choices=['$21$', '$22$', '$23$', '$24$', '$25$'],
    ans='③',
    sol=[
        '근과 계수의 관계에서 $ log a+ log b=10$, $ log a times log b=4$',
        '$ log_{a}b+ log_{b}a={( log a)^{2}+( log b)^{2}}over{ log a times log b}$',
        '$( log a)^{2}+( log b)^{2}=( log a+ log b)^{2}-2 log a log b=100-8=92$',
        '$therefore~{92}over{4}=23$',
    ],
    ch='로그방정식과 근과 계수의 관계', lv='상')

add(id='q11', kind='mc', no=11, score=4.8, layout='3+2',
    text='지수함수 $f(x)=3^{x-3}$에 대하여 부등식 $ log_{1/9}f(x) GEQit-2$를 만족시키는 자연수 $x$의 개수는?',
    choices=['$5$', '$6$', '$7$', '$8$', '$9$'],
    ans='③',
    sol=[
        '밑 ${1}over{9}$이 $1$보다 작으므로 $ log_{{1}over{9}}f(x) GEQit-2$에서 $f(x) LEQ LEFT({1}over{9} RIGHT)^{-2}=81$',
        '$3^{x-3} LEQ 81=3^{4}$에서 $x-3 LEQ 4$',
        '$therefore~x LEQ 7$',
        '자연수 조건과 함께 $x=1,~2,~3,~4,~5,~6,~7$의 $7$개',
    ],
    ch='로그부등식', lv='상')

add(id='q12', kind='mc', no=12, score=4.8, layout='3+2', fig='gmun26m1_q12',
    text=['그림과 같이 두 함수 $y=(1/2)^{x}$, $y=(1/4)^{x}$의 그래프와 직선 $y=8$이 만나는 점을 각각 A, B라 할 때, 삼각형 AOB의 넓이는? (단, O는 원점이다.)'],
    choices=['$4$', '${9}over{2}$', '$5$', '${11}over{2}$', '$6$'],
    ans='⑤',
    sol=[
        '$ LEFT({1}over{2} RIGHT)^{x}=8$에서 $2^{-x}=2^{3}$이므로 $x=it-3$, 즉 $ rmA(it-3,~{it8})$',
        '$ LEFT({1}over{4} RIGHT)^{x}=8$에서 $2^{-2x}=2^{3}$이므로 $x=it-{3}over{2}$, 즉 $ rmBLEFT(it-{3}over{2},~{it8}RIGHT)$',
        '두 점 A, B의 $y$좌표가 같으므로 $bar{rmAB}$는 $x$축에 평행하고 $bar{rmAB}=it-{3}over{2}-(it-3)={3}over{2}$',
        '원점 O에서 직선 $y=8$까지의 거리는 $8$이므로',
        '$therefore$ 삼각형 $ rmAOB$의 넓이는 ${1}over{2} times{3}over{2} times8=6$',
    ],
    ch='지수함수의 그래프', lv='중')

add(id='q13', kind='mc', no=13, score=4.8, layout='3+2',
    text='함수 $y= log_{a}x$의 그래프를 $x$축 대칭이동한 후, $y$축의 방향으로 $-3$만큼 평행이동한 그래프가 $y=(1/2)^{x}$의 그래프를 $x$축의 방향으로 $m$만큼 평행이동한 그래프와 직선 $y=x$에 대하여 대칭일 때, 상수 $m$의 값은?',
    choices=['$-3$', '$-2$', '$1$', '$2$', '$3$'],
    ans='①',
    sol=[
        '$y= log_{a}x$를 $x$축 대칭이동하면 $y=- log_{a}x$, $y$축 방향으로 $-3$만큼 평행이동하면 $y=- log_{a}x-3$',
        '이 그래프와 $y= LEFT({1}over{2} RIGHT)^{x-m}$이 직선 $y=x$에 대하여 대칭이므로 서로 역함수 관계이다.',
        '$y=- log_{a}x-3$의 역함수를 구하면 $x=- log_{a}y-3$에서 $ log_{a}y=-x-3$, $y=a^{-x-3}$',
        '$a^{-x-3}$과 $ LEFT({1}over{2} RIGHT)^{x-m}=2^{-x+m}$이 항등식이 되려면 $a=2$',
        '$a=2$이므로 $2^{-x-3}=2^{-x+m}$에서 $therefore~m=-3$',
    ],
    ch='로그함수의 역함수', lv='상')

add(id='q14', kind='mc', no=14, score=5.0, layout='3+2',
    text='부등식 $(3^{x}-243) LEFT((1/2)^{x}-16 RIGHT)>0$을 만족시키는 모든 정수 $x$의 개수는?',
    choices=['$5$', '$6$', '$7$', '$8$', '$9$'],
    ans='④',
    sol=[
        '$243=3^{5}$이므로 $3^{x}-243<0$은 $x<5$, $3^{x}-243>0$은 $x>5$와 같다.',
        '$16= LEFT({1}over{2} RIGHT)^{-4}$이므로 $ LEFT({1}over{2} RIGHT)^{x}-16<0$은 $x>-4$, $>0$은 $x<-4$와 같다.',
        '두 인수의 부호가 같아야 하는데, 둘 다 양수이려면 $x>5$이면서 $x<-4$여야 하므로 불가능하다.',
        '둘 다 음수이면 $x<5$이고 $x>-4$, 즉 $-4<x<5$',
        '$therefore$ 정수는 $x=-3,~-2,~-1,~0,~1,~2,~3,~4$의 $8$개',
    ],
    ch='지수부등식', lv='상')

add(id='q15', kind='mc', no=15, score=5.0, layout='3+2', jogeon=True,
    text=['두 정수 $a,~b$와 자연수 $k$에 대하여 다음을 만족시키는 모든 $k$의 개수를 $A$, 모든 $ab$의 값의 합을 $B$라 할 때, $A-B$의 값은? (단, $ sqrt[k]{a}$, $ sqrt[k]{b}$는 실수이다.)'],
    jogeon_items=[
        '$5 LEQ k LEQ 45$',
        '$ sqrt[k]{a} times sqrt[k]{b}=- sqrt[k]{3}$',
    ],
    choices=['$63$', '$120$', '$273$', '$336$', '$451$'],
    ans='③',
    sol=[
        '$k$가 짝수이면 $ sqrt[k]{a}$, $ sqrt[k]{b}$가 실수이려면 $a GEQ 0$, $b GEQ 0$이어야 하고, 이때 $ sqrt[k]{a} times sqrt[k]{b}= sqrt[k]{ab} GEQ 0$이므로 음수인 $- sqrt[k]{3}$과 같을 수 없다.',
        '$k$가 홀수이면 $ sqrt[k]{a} times sqrt[k]{b}= sqrt[k]{ab}$가 항상 성립하고, $- sqrt[k]{3}= sqrt[k]{-3}$이므로 $ab=-3$',
        '$5 LEQ k LEQ 45$인 홀수 $k$는 $5,~7,~9, cdots,~45$로 $21$개이므로 $A=21$',
        '$ab=-3$을 만족시키는 정수 $(a,~b)$는 $(1,~-3),~(-1,~3),~(3,~-1),~(-3,~1)$의 $4$개이고, 각 쌍의 $ab$값은 모두 $-3$이다.',
        '$k$ 하나당 $4$개의 $(a,~b)$ 순서쌍이 있으므로 $ab$의 값의 합은 $B=21 times4 times(-3)=-252$',
        '$therefore~A-B=21-(-252)=273$',
    ],
    ch='실수의 거듭제곱근', lv='상')

add(id='q16', kind='mc', no=16, score=5.2, layout='3+2', jogeon=True,
    text=['서로 다른 두 실수 $a,~b$와 $0<alpha<beta$가 다음을 만족시킨다.'],
    jogeon_items=[
        '$ log_{3}x+a log_{x}3=b$의 두 근의 합은 $-2$, 곱은 $-1$이다.',
        '$ log_{3}x-b log_{x}(1/3)=a$의 두 근은 $alpha,~beta$이다.',
    ],
    text2='$(a+b)/(alpha beta)$의 값은? (단, $x$는 $1$이 아닌 양의 실수이다.)',
    choices=['$-9$', '$-3$', '$0$', '$1$', '$9$'],
    ans='①',
    sol=[
        '$t= log_{3}x$라 하면 $ log_{x}3={1}over{t}$이므로 $ log_{3}x+a log_{x}3=b$는 $t+{a}over{t}=b$, 즉 $t^{2}-bt+a=0$',
        '이 방정식의 두 근의 합이 $-2$, 곱이 $-1$이므로 $b=-2$, $a=-1$',
        '$ log_{x} LEFT({1}over{3} RIGHT)=-{1}over{t}$이므로 $ log_{3}x-b log_{x} LEFT({1}over{3} RIGHT)=a$는 $t+{b}over{t}=a$, 즉 $t^{2}-at+b=0$',
        '$a=-1$, $b=-2$를 대입하면 $t^{2}+t-2=0$, $(t+2)(t-1)=0$에서 $t=-2$ 또는 $t=1$',
        '$alpha,~beta$는 각각 $x=3^{-2}$, $x=3^{1}$에 대응하므로 $alpha={1}over{9}$, $beta=3$이고 $alpha beta={1}over{3}$',
        '$a+b=it-1+(it-2)=it-3$이므로',
        '$therefore~{a+b}over{alpha beta}={it-3}over{ {1}over{3} }=it-3 times3=it-9$',
    ],
    ch='로그방정식과 역함수', lv='최상')

add(id='q17', kind='mc', no=17, score=5.2, layout='3+2',
    text='$a>1$과 $0 LEQ theta<2 pi$가 $ sintheta+ log_{3}a+ log_{a}3 LEQ 1$을 만족시킬 때, $ cos(a theta/2)$의 값은?',
    choices=['$-1$', '$-{1}over{2}$', '$0$', '${ sqrt{2}}over{2}$', '${ sqrt{3}}over{2}$'],
    ans='④',
    sol=[
        '$u= log_{3}a$라 하면 $a>1$이므로 $u>0$이고, 밑의 변환에 의해 $ log_{a}3={1}over{u}$',
        '주어진 부등식은 $ sintheta+u+{1}over{u} LEQ 1$, 즉 $ sintheta LEQ 1-LEFT(u+{1}over{u}RIGHT)$',
        '산술평균과 기하평균에 의해 $u+{1}over{u} GEQ 2$이므로 $1- LEFT(u+{1}over{u} RIGHT) LEQit-1$',
        '즉 $ sintheta LEQit-1$인데 항상 $ sintheta GEQit-1$이므로 $ sintheta=it-1$이 되어야 한다.',
        '이때 등호 조건에 의해 $u+{1}over{u}=2$도 성립해야 하므로 $u=1$, 즉 $ log_{3}a=1$에서 $a=3$',
        '$0 LEQ theta<2 pi$에서 $ sintheta=it-1$인 $theta$는 ${3 pi}over{2}$',
        '$therefore~ cos LEFT({a theta}over{2} RIGHT)= cos LEFT({3 times{3 pi}over{2}}over{2} RIGHT)= cos{9 pi}over{4}= cos{pi}over{4}={ sqrt{2}}over{2}$',
    ],
    ch='삼각함수와 로그의 활용', lv='최상')

add(id='q18', kind='sub', no=1, score=6.0, layout='1x5',
    text=[
        '$1$이 아닌 두 양수 $a,~b$에 대하여 다음 물음에 답하시오.',
        '(1-1) $a^{log b}=b^{log a}$임을 보이는 과정을 반드시 로그의 정의와 로그의 밑의 변환을 사용하여 서술하시오. [$4$점]',
        '(1-2) $0.01^{log2}$의 값을 구하고 그 과정을 서술하시오. [$2$점]',
    ],
    ans_mix='(1-1) 풀이 참조 (1-2) ${1}over{4}$',
    sol=[
        '(1-1) $n= log_{a}b$라 하면 로그의 밑의 변환에 의해 $n={ log b}over{ log a}$이므로 $ log b=n log a$',
        '로그의 정의에 의해 $ log_{a}b=n$은 $a^{n}=b$와 같은 의미이다.',
        '따라서 $a^{log b}=a^{n log a}=(a^{n})^{log a}=b^{log a}$',
        '$therefore~a^{log b}=b^{log a}$ (증명 끝)',
        '(1-2) $0.01=10^{-2}$이므로 $0.01^{log2}=(10^{-2})^{log2}=10^{-2log2}$',
        '$=10^{log2^{-2}}=10^{log{1}over{4}}$',
        '$therefore~0.01^{log2}={1}over{4}$',
    ],
    ch='로그의 성질과 정의', lv='상')

add(id='q19', kind='sub', no=2, score=6.0, layout='1x5',
    text=[
        '모든 실수 $x$에 대하여 이차부등식 $x^{2}-2x log a+ log a+6 GEQ 0$이 항상 성립하도록 하는 실수 $a$의 값의 범위를 구하고 그 과정을 서술하시오. [$6$점]',
    ],
    ans_eq='${1}over{100} LEQ a LEQ 1000$',
    sol=[
        '$t= log a$라 하면 주어진 이차부등식은 $x^{2}-2tx+(t+6) GEQ 0$',
        '모든 실수 $x$에 대하여 성립하려면 판별식 ${D}over{4}=t^{2}-(t+6) LEQ 0$',
        '$t^{2}-t-6 LEQ 0$, $(t-3)(t+2) LEQ 0$에서 $-2 LEQ t LEQ 3$',
        '$-2 LEQ log a LEQ 3$에서 $10^{-2} LEQ a LEQ 10^{3}$',
        '$therefore~{1}over{100} LEQ a LEQ 1000$',
    ],
    ch='이차부등식의 판별식 활용', lv='상')

add(id='q20', kind='sub', no=3, score=8.0, layout='1x5', fig='gmun26m1_q20', jogeon=True,
    text=[
        '그림과 같이 좌표평면 위의 네 점 $ rmA(it2,~{it2})$, $ rmB(it4,~{it6})$, $ rmP(x,~{it0})$, $Q$를 꼭짓점으로 하는 평행사변형 $ rmAPBQ$가 있다. 평행사변형 $ rmAPBQ$의 넓이를 $f(x)$, 선분 $ rmPQ$의 길이를 $g(x)$라 하자. 다음 물음에 답하시오.',
        '(3-1) $2 LEQ x LEQ 16$일 때, 다음을 만족시키는 실수 $a,~b,~c$를 구하고, 그 과정을 서술하시오. [$3$점]',
    ],
    jogeon_items=[
        '$f(x)$는 $x=a$에서 최댓값, $x=b$에서 최솟값을 갖는다.',
        '$g(x)$는 $x=c$에서 최솟값을 갖는다.',
    ],
    text2='(3-2) (3-1)에서 구한 실수 $a,~b,~c$에 대하여 $t$에 관한 방정식 $( log_{c}9)t^{2}-( log_{b}a) LEFT|t RIGHT|= sin(7 pi/6)$의 모든 실근의 곱을 구하고, 그 과정을 서술하시오. [$5$점]',
    ans_mix='(3-1) $a=16,~b=2,~c=3$ (3-2) ${1}over{16}$',
    sol=[
        '(3-1) 평행사변형 $APBQ$에서 대각선 $AB$, $PQ$는 서로 다른 두 쌍의 대변을 이루는 꼭짓점을 잇는 선분이므로 서로를 이등분한다.',
        '$AB$의 중점은 $ LEFT({2+4}over{2},~{2+6}over{2} RIGHT)=(3,~4)$이고 이는 $PQ$의 중점과 같으므로 $Q$의 좌표는 $(6-x,~8)$',
        '네 점 $A(2,~2)$, $P(x,~0)$, $B(4,~6)$, $Q(6-x,~8)$의 좌표로 사각형의 넓이 공식을 적용하면',
        '$f(x)={1}over{2} LEFT| (2 times0-xtimes2)+(xtimes6-4times0)+(4times8-(6-x)times6)+((6-x)times2-2times8) RIGHT|$',
        '$={1}over{2} LEFT|8x-8 RIGHT|= LEFT|4x-4 RIGHT|$',
        '$2 LEQ x LEQ 16$에서 $x-1>0$이므로 $f(x)=4(x-1)$은 증가함수이다.',
        '따라서 $f(x)$는 $x=16$에서 최댓값, $x=2$에서 최솟값을 가지므로 $a=16$, $b=2$',
        '$ bar{rmPQ}$의 길이는 $g(x)= sqrt{(6-2x)^{2}+8^{2}}$이고, $(6-2x)^{2} GEQ 0$이 최소가 되는 $x$는 $6-2x=0$, 즉 $x=3$',
        '$x=3$은 $2 LEQ x LEQ 16$에 포함되므로 $g(x)$는 $x=3$에서 최솟값을 갖는다. $c=3$',
        '(3-2) $a=16$, $b=2$, $c=3$이므로 $ log_{c}9= log_{3}9=2$, $ log_{b}a= log_{2}16=4$',
        '$ sin LEFT({7 pi}over{6} RIGHT)=- sin{pi}over{6}=-{1}over{2}$',
        '방정식은 $2t^{2}-4 LEFT|t RIGHT|=-{1}over{2}$, 양변에 $2$를 곱하면 $4t^{2}-8 LEFT|t RIGHT|+1=0$',
        '$u= LEFT|t RIGHT| GEQ 0$이라 하면 $4u^{2}-8u+1=0$',
        '이 방정식의 두 근을 $u_{1},~u_{2}$라 하면 근과 계수의 관계에서 $u_{1}+u_{2}=2>0$, $u_{1}u_{2}={1}over{4}>0$이므로 두 근 모두 양수이다.',
        '각 양의 근 $u$마다 $t=u$ 또는 $t=-u$인 두 실근이 대응하므로, 모든 실근의 곱은 $u_{1} times(-u_{1}) times u_{2} times(-u_{2})=(u_{1}u_{2})^{2}$',
        '$therefore~(u_{1}u_{2})^{2}= LEFT({1}over{4} RIGHT)^{2}={1}over{16}$',
    ],
    ch='평행사변형의 넓이와 로그방정식의 활용', lv='최상')
