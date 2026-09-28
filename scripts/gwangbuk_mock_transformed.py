"""광명북고 2026-2학기 중간 실전동형테스트 — 원본 프린트(28문항) 변형 문제 데이터.

원본 출처: 2026년 2학기 중간 광명북고 프린트대비자료.pdf (이영우T, 문항 1~28)
변형 원칙: 주어진 값/구하는 값, 문제 유형(객관식·주관식·보기형), 도형·함수의 종류,
핵심 풀이 기법을 원본과 동일하게 유지하고 구체적인 수치만 새로 설계함.
해설은 공통수학2 교육과정 범위 안의 기법만 사용하고, 논리 단계마다 줄바꿈(<br>)해
가독성을 확보함 (build 스크립트가 <br>→개행으로 변환).
각 항목: chapter/difficulty/points/is_subjective/choices/answer/question_text/solution_text.
choices 는 None(주관식) 또는 [{"number":1,"text":"$...$"}, ...] (5지선다).
"""

TRANSFORMED = {

# ── 1. 평면좌표 / 직선의 방정식 (원본 1~10) ──────────────────────────
1: dict(
    chapter="직선의 방정식", difficulty="하", points=3, is_subjective=False,
    question_text=r"두 직선 $x+2y+1=0$, $2x-y-13=0$의 교점을 지나고 직선 $3x+y-4=0$과 "
                   r"평행한 직선의 $x$절편은?",
    choices=[{"number":1,"text":"$2$"},{"number":2,"text":"$3$"},{"number":3,"text":"$4$"},
             {"number":4,"text":"$5$"},{"number":5,"text":"$6$"}],
    answer="3",
    solution_text=r"두 직선을 연립하면 교점은 $(5,-3)$이다.<br>"
                  r"직선 $3x+y-4=0$의 기울기는 $-3$이므로 구하는 직선의 기울기도 $-3$이다.<br>"
                  r"기울기가 $-3$이고 점 $(5,-3)$을 지나는 직선은 $y+3=-3(x-5)$, 즉 $y=-3x+12$이다.<br>"
                  r"$y=0$을 대입하면 $x$절편은 $4$이다.",
),
2: dict(
    chapter="직선의 방정식", difficulty="하", points=4.2, is_subjective=True,
    question_text=r"직선 $y=(13-3k)x-4$와 직선 $y=4x+2$가 서로 평행할 때, 상수 $k$의 값을 구하시오.",
    choices=None, answer="3",
    solution_text=r"두 직선이 평행하려면 기울기가 같아야 한다.<br>"
                  r"$13-3k=4$에서 $3k=9$이므로 $k=3$이다.",
),
3: dict(
    chapter="직선의 방정식", difficulty="중", points=3, is_subjective=False,
    question_text=r"점 $(m,-m)$과 직선 $4x+y+5=0$ 사이의 거리를 $d_1$, 점 $(0,10)$과 직선 "
                   r"$4x+y+5=0$ 사이의 거리를 $d_2$라 하자. $d_1<d_2$가 되도록 하는 정수 $m$의 개수는?",
    choices=[{"number":1,"text":"$8$"},{"number":2,"text":"$10$"},{"number":3,"text":"$12$"},
             {"number":4,"text":"$14$"},{"number":5,"text":"$16$"}],
    answer="2",
    solution_text=r"$d_1=\dfrac{|4m-m+5|}{\sqrt{17}}=\dfrac{|3m+5|}{\sqrt{17}}$이다.<br>"
                  r"$d_2=\dfrac{|0+10+5|}{\sqrt{17}}=\dfrac{15}{\sqrt{17}}$이다.<br>"
                  r"$d_1<d_2$에서 $|3m+5|<15$이므로 $-\dfrac{20}{3}<m<\dfrac{10}{3}$이다.<br>"
                  r"이를 만족하는 정수 $m$은 $-6,-5,\dots,3$으로 모두 $10$개이다.",
),
4: dict(
    chapter="직선의 방정식", difficulty="중", points=4, is_subjective=False,
    question_text=r"그림과 같이 $\angle A=\angle B=90^\circ$, $\overline{AB}=4$, $\overline{BC}=12$인 "
                   r"사다리꼴 ABCD에 대하여 선분 AD를 $1:2$로 내분하는 점을 P라 하자. 두 직선 AC, "
                   r"BP가 점 Q에서 서로 수직으로 만날 때, 삼각형 AQD의 넓이는?",
    choices=[{"number":1,"text":"$\\dfrac{1}{2}$"},{"number":2,"text":"$\\dfrac{3}{5}$"},
             {"number":3,"text":"$\\dfrac{7}{10}$"},{"number":4,"text":"$\\dfrac{4}{5}$"},
             {"number":5,"text":"$\\dfrac{9}{10}$"}],
    answer="4",
    solution_text=r"B를 원점, $A(0,4)$, $C(12,0)$, $D(t,4)$라 하자.<br>"
                  r"직선 AC는 $y=-\dfrac13x+4$이고, 직선 BP는 AC와 수직이므로 기울기가 $3$인 "
                  r"$y=3x$이다.<br>"
                  r"P는 AD를 $1:2$로 내분하는 점이므로 $P=\left(\dfrac{t}{3},4\right)$이고, P는 BP "
                  r"위의 점이므로 $4=3\cdot\dfrac{t}{3}$에서 $t=4$, 즉 $\overline{AD}=4$이다.<br>"
                  r"두 직선을 연립하면 교점 $Q\left(\dfrac65,\dfrac{18}{5}\right)$을 얻는다.<br>"
                  r"삼각형 AQD의 넓이는 $\dfrac12\cdot4\cdot\left(4-\dfrac{18}{5}\right)=\dfrac12\cdot4"
                  r"\cdot\dfrac25=\dfrac45$이다.",
),
5: dict(
    chapter="직선의 방정식", difficulty="중", points=4, is_subjective=True,
    question_text=r"좌표평면 위의 네 점 $A(0,2)$, $B(0,5)$, $C(\sqrt2,p)$, $D(3\sqrt2,q)$가 다음 "
                   r"조건을 만족시킬 때, $p+q$의 값을 구하시오."
                   r"<<BOX_START>>(가) 직선 CD의 기울기는 음수이다.<br>"
                   r"(나) $\overline{AB}=\overline{CD}$이고 $\overline{AD}\parallel\overline{BC}$이다."
                   r"<<BOX_END>>",
    choices=None, answer="11",
    solution_text=r"$\overline{AB}=3$, $\overline{CD}=\sqrt{8+(q-p)^2}$이므로 $9=8+(q-p)^2$에서 "
                  r"$(q-p)^2=1$이다.<br>"
                  r"조건 (가)에서 $\dfrac{q-p}{2\sqrt2}<0$이므로 $q-p=-1$이다.<br>"
                  r"$\overline{AD}\parallel\overline{BC}$에서 두 직선의 기울기가 같으므로 "
                  r"$\dfrac{q-2}{3\sqrt2}=\dfrac{p-5}{\sqrt2}$, 즉 $q-2=3(p-5)$이다.<br>"
                  r"정리하면 $q=3p-13$이고, 여기에 $q=p-1$을 대입하면 $p-1=3p-13$에서 $p=6$이다.<br>"
                  r"따라서 $q=5$이므로 $p+q=11$이다.",
),
6: dict(
    chapter="직선의 방정식", difficulty="중", points=4, is_subjective=True,
    question_text=r"그림과 같이 좌표평면 위에 직선 $l_1:x-2y-6=0$과 평행하고 $y$절편이 양수인 직선 "
                   r"$l_2$가 있다. 직선 $l_1$이 $x$축, $y$축과 만나는 점을 각각 A, B라 하고 직선 "
                   r"$l_2$가 $x$축, $y$축과 만나는 점을 각각 C, D라 할 때, 사각형 ADCB의 넓이가 "
                   r"$100$이다. 두 직선 $l_1$과 $l_2$ 사이의 거리를 $d$라 할 때, $d^2$의 값을 구하시오.",
    choices=None, answer="80",
    solution_text=r"$l_1$의 $x$절편, $y$절편은 각각 $A(6,0)$, $B(0,-3)$이다.<br>"
                  r"$l_2:x-2y+a=0\,(a>0)$이라 하면 $C(-a,0)$, $D(0,a/2)$이다.<br>"
                  r"(사각형 ADCB의 넓이) $=$ (삼각형 ADC의 넓이) $+$ (삼각형 ACB의 넓이)이므로<br>"
                  r"$\dfrac12(a+6)\cdot\dfrac{a}{2}+\dfrac12(a+6)\cdot3=\dfrac{(a+6)^2}{4}=100$이다.<br>"
                  r"$a>0$이므로 $a+6=20$에서 $a=14$이다.<br>"
                  r"두 직선 사이의 거리는 $d=\dfrac{|(-6)-14|}{\sqrt5}=\dfrac{20}{\sqrt5}=4\sqrt5$이므로 "
                  r"$d^2=80$이다.",
),
7: dict(
    chapter="직선의 방정식", difficulty="중", points=4, is_subjective=False,
    question_text=r"그림과 같이 좌표평면 위에 세 점 $A(-9,a)$, $B(9,4)$, $C(-10,0)$이 있다. 선분 AB를 "
                   r"$2:1$로 내분하는 점을 P라 할 때, 직선 PC가 삼각형 AOB의 넓이를 이등분한다. 양수 "
                   r"$a$의 값은? (단, O는 원점이다.)",
    choices=[{"number":1,"text":"$29$"},{"number":2,"text":"$30$"},{"number":3,"text":"$31$"},
             {"number":4,"text":"$32$"},{"number":5,"text":"$33$"}],
    answer="3",
    solution_text=r"직선 PC와 선분 AO가 만나는 점을 Q, 삼각형 AOB의 넓이를 $S$라 하자.<br>"
                  r"P가 AB를 $2:1$로 내분하므로 $\triangle AOP=\dfrac23S$이고, PC가 넓이를 이등분하므로 "
                  r"$\triangle AQP=\dfrac12S$이다.<br>"
                  r"두 삼각형 AQP, QOP는 밑변 AQ, QO를 공유하고 높이가 같으므로 넓이의 비가 곧 "
                  r"$\overline{AQ}:\overline{QO}$의 비이다. 두 삼각형의 넓이가 각각 $\dfrac12S$, "
                  r"$\dfrac16S$이므로 $\overline{AQ}:\overline{QO}=3:1$이다.<br>"
                  r"따라서 $Q=\dfrac14A=\left(-\dfrac94,\dfrac{a}{4}\right)$이다.<br>"
                  r"점 P는 A, B를 $2:1$로 내분하므로 $P=\left(3,\dfrac{a+8}{3}\right)$이다.<br>"
                  r"직선 PC의 방정식은 $y=\dfrac{a+8}{39}(x+10)$이고, 점 Q가 이 위의 점이므로 "
                  r"$\dfrac{a}{4}=\dfrac{a+8}{39}\cdot\dfrac{31}{4}$이다.<br>"
                  r"정리하면 $39a=31(a+8)$에서 $8a=248$이므로 $a=31$이다.",
),
8: dict(
    chapter="직선의 방정식", difficulty="상", points=5.2, is_subjective=False,
    question_text=r"그림과 같이 기울기와 $y$절편이 모두 양수인 직선 $l$과 이차함수 $y=2x^2$의 그래프가 "
                   r"서로 다른 두 점 A, B에서 만난다. 원점 O에 대하여 삼각형 AOB가 $\angle AOB=90^\circ$"
                   r"이고 넓이가 $3$인 직각삼각형일 때, 직선 $l$의 $y$절편은? (단, 점 A는 제2사분면 "
                   r"위의 점이다.)",
    choices=[{"number":1,"text":"$\\dfrac{1}{8}$"},{"number":2,"text":"$\\dfrac{1}{4}$"},
             {"number":3,"text":"$\\dfrac{1}{3}$"},{"number":4,"text":"$\\dfrac{1}{2}$"},
             {"number":5,"text":"$\\dfrac{2}{3}$"}],
    answer="4",
    solution_text=r"$A(\alpha,2\alpha^2)$, $B(\beta,2\beta^2)$ $(\alpha<0<\beta)$라 하자.<br>"
                  r"직선 OA의 기울기는 $2\alpha$, 직선 OB의 기울기는 $2\beta$이고 두 직선이 수직이므로 "
                  r"$2\alpha\cdot2\beta=-1$, 즉 $\alpha\beta=-\dfrac14$이다.<br>"
                  r"직선 AB의 방정식은 $y=2(\alpha+\beta)x-2\alpha\beta$이므로 $y$절편은 "
                  r"$-2\alpha\beta=\dfrac12$이다.<br>"
                  r"(참고: 이 값은 직각 조건만으로 정해지며, 넓이 $3$이라는 조건은 그런 $\alpha,\beta$가 "
                  r"실제로 존재함을 보장해 준다.)",
),
9: dict(
    chapter="평면좌표", difficulty="상", points=5.2, is_subjective=False,
    question_text=(
        r"0이 아닌 실수 $a$에 대하여 좌표평면 위의 서로 다른 세 점 $A(4a,0)$, $B$, $C$가 다음 "
        r"조건을 만족시킨다."
        r"<<BOX_START>>"
        r"○ 삼각형 ABC의 무게중심의 좌표는 $(0,4)$이다.<br>"
        r"○ $\overline{AB}=\overline{AC}$"
        r"<<BOX_END>>"
        r"다음은 $\overline{BC}=4\sqrt{a^2+1}$일 때, 점 B의 $x$좌표와 $y$좌표의 합을 구하는 "
        r"과정이다. (단, 점 B의 $x$좌표는 점 C의 $x$좌표보다 크다.)"
        r"<<BOX_START>>"
        r"선분 BC의 중점을 M$(b,c)$, 삼각형 ABC의 무게중심을 G라 하면, 점 G$(0,4)$는 선분 AM을 "
        r"2:1로 내분하는 점이므로 $b=-2a$, $c=$(가)이다.<br>"
        r"$\overline{AB}=\overline{AC}$이고 직선 AM의 기울기가 $-\dfrac1a$이므로 직선 BC의 "
        r"방정식은 $y=$(나)$\times\{x-(-2a)\}+$(가)이다.<br>"
        r"점 B의 $x$좌표를 $k$라 하면 점 B의 $y$좌표는 (나)$\times(k+2a)+$(가)이다.<br>"
        r"$\overline{BM}=\dfrac12\overline{BC}$이고 점 B의 $x$좌표가 점 C의 $x$좌표보다 크므로 "
        r"$k=$(다)이다.<br>따라서 점 B의 $x$좌표와 $y$좌표의 합은 (라)이다."
        r"<<BOX_END>>"
        r"위의 (가), (라)에 알맞은 수를 각각 $p$, $q$라 하고, (나), (다)에 알맞은 식을 각각 "
        r"$f(a)$, $g(a)$라 할 때, $f(p)\times g(q)$의 값은?"
    ),
    choices=[{"number":1,"text":"$-98$"},{"number":2,"text":"$-96$"},{"number":3,"text":"$-84$"},
             {"number":4,"text":"$-72$"},{"number":5,"text":"$-70$"}],
    answer="3",
    solution_text=r"무게중심 G는 선분 AM을 $2:1$로 내분하는 점이므로 $M=\dfrac{3G-A}{2}$이다.<br>"
                  r"$A(4a,0)$, $G(0,4)$를 대입하면 $M=(-2a,6)$이므로 (가)$=c=6$이다.<br>"
                  r"$\overline{AB}=\overline{AC}$이므로 직선 BC는 직선 AM과 수직이고, AM의 기울기가 "
                  r"$-\dfrac1a$이므로 BC의 기울기는 $a$이다. 즉 (나)$=a$이다.<br>"
                  r"점 B의 $y$좌표는 $a(k+2a)+6$이고, $\overline{BM}=\dfrac12\overline{BC}"
                  r"=2\sqrt{a^2+1}$에서 $|k-(-2a)|\sqrt{1+a^2}=2\sqrt{a^2+1}$이므로 $|k+2a|=2$이다.<br>"
                  r"점 B의 $x$좌표가 점 C의 $x$좌표보다 크므로 $k=-2a+2$이다. 즉 (다)$=-2a+2$이다.<br>"
                  r"이때 B의 $y$좌표는 $a(2)+6=2a+6$이므로 $x+y=(-2a+2)+(2a+6)=8$이다. 즉 (라)$=8$이다.<br>"
                  r"따라서 $p=6$, $q=8$이고 $f(a)=a$, $g(a)=-2a+2$이므로 $f(p)=f(6)=6$, "
                  r"$g(q)=g(8)=-14$이다.<br>"
                  r"그러므로 $f(p)\times g(q)=6\times(-14)=-84$이다.",
),
10: dict(
    chapter="직선의 방정식", difficulty="중", points=3, is_subjective=False,
    question_text=r"제1사분면 위의 서로 다른 두 점 A, B가 다음 조건을 만족시킨다."
                   r"<<BOX_START>>(가) 점 A는 직선 $y=\dfrac13x$ 위의 점이다.<br>"
                   r"(나) 삼각형 OAB는 $\angle A=90^\circ$인 직각이등변삼각형이다.<br>"
                   r"(다) 삼각형 OAB의 외접원과 내접원 사이의 거리는 $\dfrac{\sqrt{10}}{2}(2-\sqrt2)$"
                   r"이다.<<BOX_END>>삼각형 OAB의 무게중심의 좌표가 $(p,q)$일 때, $6(p+q)$의 값은? "
                   r"(단, O는 원점이다.)",
    choices=[{"number":1,"text":"$16$"},{"number":2,"text":"$18$"},{"number":3,"text":"$20$"},
             {"number":4,"text":"$22$"},{"number":5,"text":"$24$"}],
    answer="3",
    solution_text=r"직각이등변삼각형(직각을 낀 변의 길이 $a$)에서 외심은 빗변의 중점이고, 내접원의 "
                  r"반지름은 $r=\dfrac{a(2-\sqrt2)}{2}$이다. 외심과 내심을 잇는 선분의 길이도 이 값과 "
                  r"같음이 알려져 있다.<br>"
                  r"조건 (다)에서 $\dfrac{a(2-\sqrt2)}{2}=\dfrac{\sqrt{10}}{2}(2-\sqrt2)$이므로 "
                  r"$a=\sqrt{10}$, 즉 $\overline{OA}=\overline{AB}=\sqrt{10}$이다.<br>"
                  r"조건 (가)에서 $A=\left(t,\dfrac t3\right)\,(t>0)$이라 하면 "
                  r"$\overline{OA}=t\cdot\dfrac{\sqrt{10}}{3}=\sqrt{10}$에서 $t=3$, 즉 $A(3,1)$이다.<br>"
                  r"점 A를 지나고 OA에 수직인 직선의 기울기는 $-3$이므로 그 직선 위의 점 "
                  r"$B(x,1-3(x-3))$ 중 $\overline{AB}=\sqrt{10}$, 즉 $(x-3)^2\cdot10=10$을 만족하는 "
                  r"$x=2$ 또는 $x=4$ 가운데 제1사분면 조건을 만족하는 것은 $B(2,4)$이다.<br>"
                  r"삼각형 OAB의 무게중심은 $\left(\dfrac{0+3+2}{3},\dfrac{0+1+4}{3}\right)"
                  r"=\left(\dfrac53,\dfrac53\right)$이므로 $6(p+q)=6\cdot\dfrac{10}{3}=20$이다.",
),

# ── 2. 원의 방정식 (원본 11~18) ──────────────────────────────────────
11: dict(
    chapter="원의 방정식", difficulty="중", points=4, is_subjective=False,
    question_text=r"중심이 원점이고 직선 $y=-3x+k$와 만나는 원 중에서 넓이가 최소인 원을 C라 하자. "
                   r"원 C의 넓이가 $40\pi$일 때, 양의 상수 $k$의 값은?",
    choices=[{"number":1,"text":"$18$"},{"number":2,"text":"$19$"},{"number":3,"text":"$20$"},
             {"number":4,"text":"$21$"},{"number":5,"text":"$22$"}],
    answer="3",
    solution_text=r"직선 $y=-3x+k$와 만나면서 넓이가 최소인 원은 이 직선에 접하는 원이다.<br>"
                  r"그 반지름은 원점과 직선 $3x+y-k=0$ 사이의 거리 $\dfrac{k}{\sqrt{10}}$와 같다.<br>"
                  r"원 C의 넓이가 $40\pi$이므로 반지름은 $2\sqrt{10}$이다.<br>"
                  r"$\dfrac{k}{\sqrt{10}}=2\sqrt{10}$에서 $k=20$이다.",
),
12: dict(
    chapter="원의 방정식", difficulty="중", points=4, is_subjective=False,
    question_text=r"곡선 $y=-x^2+10x$ 위의 서로 다른 두 점 A, B를 지름의 양 끝점으로 하는 원을 C라 "
                   r"하자. 원 C의 넓이가 $32\pi$이고, 점 A를 지나고 기울기가 $1$인 직선이 원 C에 접할 "
                   r"때, 직선 AB의 $y$절편은?",
    choices=[{"number":1,"text":"$\\dfrac{51}{4}$"},{"number":2,"text":"$\\dfrac{53}{4}$"},
             {"number":3,"text":"$\\dfrac{55}{4}$"},{"number":4,"text":"$\\dfrac{57}{4}$"},
             {"number":5,"text":"$\\dfrac{59}{4}$"}],
    answer="4",
    solution_text=r"원 C의 넓이가 $32\pi$이므로 반지름은 $4\sqrt2$이고 $\overline{AB}=8\sqrt2$이다.<br>"
                  r"점 A를 지나는 기울기 $1$인 직선이 원 C에 접하므로 이 직선은 지름 AB와 수직이다. "
                  r"따라서 직선 AB의 기울기는 $-1$이다.<br>"
                  r"직선 AB를 $y=-x+k$라 하고 곡선과 연립하면 $x^2-11x+k=0$이고, 두 근을 "
                  r"$\alpha,\beta$라 하면 $\alpha+\beta=11$, $\alpha\beta=k$이다.<br>"
                  r"직선의 기울기가 $-1$이므로 $\overline{AB}=|\beta-\alpha|\sqrt2=8\sqrt2$에서 "
                  r"$|\beta-\alpha|=8$이다.<br>"
                  r"$(\beta-\alpha)^2=(\alpha+\beta)^2-4\alpha\beta$에서 $64=121-4k$이므로 "
                  r"$k=\dfrac{57}{4}$이다.",
),
13: dict(
    chapter="원의 방정식", difficulty="중", points=5, is_subjective=True,
    question_text=r"좌표평면에서 두 직선 $y=x+9$, $y=-x+9$에 모두 접하고 점 $(3,0)$을 지나는 서로 "
                   r"다른 두 원의 중심을 $O_1$, $O_2$라 할 때, 선분 $\overline{O_1O_2}$의 길이를 구하시오.",
    choices=None, answer="24",
    solution_text=r"두 직선 $y=x+9$, $y=-x+9$는 $y$축에 대하여 대칭이므로, 두 직선에 모두 접하는 "
                  r"원의 중심은 $y$축 위의 점 $(0,b)$ 꼴이다.<br>"
                  r"직선 $x-y+9=0$까지의 거리가 반지름과 같으므로 $r=\dfrac{|9-b|}{\sqrt2}$이다.<br>"
                  r"이 원이 점 $(3,0)$을 지나므로 $r^2=9+b^2$이다.<br>"
                  r"두 식을 연립하면 $\dfrac{(9-b)^2}{2}=9+b^2$이고, 정리하면 $b^2+18b-63=0$, "
                  r"즉 $(b-3)(b+21)=0$에서 $b=3$ 또는 $b=-21$이다.<br>"
                  r"따라서 $\overline{O_1O_2}=|3-(-21)|=24$이다.",
),
14: dict(
    chapter="원의 방정식", difficulty="하", points=4.2, is_subjective=True,
    question_text=r"좌표평면에서 원 $x^2+y^2=169$ 위의 점 $(5,-12)$에서의 접선이 원 "
                   r"$(x-8)^2+(y+2)^2=r^2$과 만나도록 하는 자연수 $r$의 최솟값을 구하시오.",
    choices=None, answer="9",
    solution_text=r"원 $x^2+y^2=169$ 위의 점 $(5,-12)$에서의 접선의 방정식은 $5x-12y=169$이다.<br>"
                  r"이 접선이 원 $(x-8)^2+(y+2)^2=r^2$과 만나려면 중심 $(8,-2)$와 접선 사이의 거리가 "
                  r"반지름 $r$ 이하여야 한다.<br>"
                  r"중심과 접선 사이의 거리는 $\dfrac{|40+24-169|}{13}=\dfrac{105}{13}$이다.<br>"
                  r"$\dfrac{105}{13}=8.07\cdots$이므로 이보다 크거나 같은 자연수 $r$의 최솟값은 $9$이다.",
),
15: dict(
    chapter="원의 방정식", difficulty="중", points=4, is_subjective=False,
    question_text=r"좌표평면 위에 세 점 A(0,8), B(8,8), C(8,0)이 있다. 세 선분 OA, AB, BC를 $m:n$ "
                   r"($m>0$, $n>0$)으로 내분하는 점을 각각 P, Q, R라 하고, 세 점 P, Q, R를 지나는 원을 "
                   r"C라 할 때, <보기>에서 옳은 것만을 있는 대로 고른 것은? (단, O는 원점이다.)"
                   r"<<BOX_START>>ㄱ. $m=n$일 때, 점 P의 좌표는 $(0,4)$이다.<br>"
                   r"ㄴ. 점 $\left(\dfrac{8m}{m+n},0\right)$은 원 C 위의 점이다.<br>"
                   r"ㄷ. 원 C가 $x$축과 만나는 서로 다른 두 점 사이의 거리가 $6$일 때, "
                   r"$\overline{PQ}=5\sqrt2$이다.<<BOX_END>>",
    choices=[{"number":1,"text":"ㄱ"},{"number":2,"text":"ㄷ"},{"number":3,"text":"ㄱ, ㄴ"},
             {"number":4,"text":"ㄱ, ㄷ"},{"number":5,"text":"ㄱ, ㄴ, ㄷ"}],
    answer="5",
    solution_text=r"$s=\dfrac{8m}{m+n}\,(0<s<8)$라 하면 P$(0,s)$, Q$(s,8)$, R$(8,8-s)$이다.<br>"
                  r"ㄱ. $m=n$이면 $s=4$이므로 P$(0,4)$이다. 참이다.<br>"
                  r"ㄴ, ㄷ을 확인하기 위해 원 C를 구하자. 직선 PQ의 기울기는 $\dfrac{8-s}{s}$, 직선 QR의 "
                  r"기울기는 $\dfrac{-s}{8-s}$이고 두 기울기의 곱이 $-1$이므로 $\overline{PQ}\perp"
                  r"\overline{QR}$이다. 또한 $\overline{PQ}=\overline{QR}=\sqrt{s^2+(8-s)^2}$이므로 "
                  r"삼각형 PQR는 $\angle Q=90^\circ$인 직각이등변삼각형이다. 따라서 원 C는 PR을 지름으로 "
                  r"하고 중심은 PR의 중점 $(4,4)$이다.<br>"
                  r"ㄴ. 점 $(s,0)$과 중심 $(4,4)$ 사이의 거리의 제곱은 $(s-4)^2+16$인데, 이는 반지름의 "
                  r"제곱 $\overline{P(4,4)}^2=4^2+(s-4)^2$과 같다. 참이다.<br>"
                  r"ㄷ. 반지름의 제곱이 $(s-4)^2+16$이므로 $x$축과 만나는 두 점 사이의 거리는 "
                  r"$2\sqrt{(s-4)^2+16-16}=2|s-4|$이다. 이 값이 $6$이면 $s=1$ 또는 $s=7$이고, 두 "
                  r"경우 모두 $\overline{PQ}=\sqrt{s^2+(8-s)^2}=\sqrt{1+49}\times\cdots$을 계산하면 "
                  r"$5\sqrt2$이다. 참이다.<br>"
                  r"따라서 옳은 것은 ㄱ, ㄴ, ㄷ이다.",
),
16: dict(
    chapter="원의 방정식", difficulty="상", points=5.2, is_subjective=False,
    question_text=r"좌표평면 위의 제1, 2사분면에 있는 점 A를 중심으로 하고 원점 O를 지나는 원 "
                   r"$C_1$이 있다. $C_1$을 원점에 대하여 대칭이동한 원을 $C_2$라 할 때, 두 원 "
                   r"$C_1,C_2$가 다음 조건을 만족시킨다."
                   r"<<BOX_START>>삼각형 OPQ의 외접원의 중심이 선분 PQ 위에 있도록 하는 $C_1$ 위의 "
                   r"점 P와 $C_2$ 위의 점 Q에 대하여 $\overline{PQ}=2$이다.<<BOX_END>>"
                   r"원 $C_2$가 $x$축과 만나는 점 중 O가 아닌 점을 B라 할 때, 원 $C_2$ 위의 점 B에서의 "
                   r"접선을 $l$이라 하자. 직선 $l$의 기울기가 $\dfrac13$일 때, 점 A와 직선 $l$ 사이의 "
                   r"거리는?",
    choices=[{"number":1,"text":"$\\dfrac{7}{15}$"},{"number":2,"text":"$\\dfrac{8}{15}$"},
             {"number":3,"text":"$\\dfrac{3}{5}$"},{"number":4,"text":"$\\dfrac{2}{3}$"},
             {"number":5,"text":"$\\dfrac{11}{15}$"}],
    answer="3",
    solution_text=r"원 $C_1$의 중심은 A, 반지름은 $\overline{OA}=r$이고, 원 $C_2$의 중심은 A를 원점에 "
                  r"대하여 대칭이동한 $-A$이며 반지름은 역시 $r$이다.<br>"
                  r"삼각형 OPQ의 외접원의 중심이 PQ 위에 있다는 것은 $\angle POQ=90^\circ$라는 뜻이고, "
                  r"이때 직각삼각형 OPQ의 외접원은 빗변 PQ를 지름으로 하는 원이므로 $\overline{PQ}$는 "
                  r"항상 그 지름, 즉 $\overline{PQ}=2r$이다.<br>"
                  r"$\overline{PQ}=2$이므로 $r=1$이다.<br>"
                  r"$A=(a,b)\,(a>0,\,b>0)$라 하면 원 $C_2$의 중심은 $(-a,-b)$이고 $x$축과 만나는 점은 "
                  r"$(-2a,0)$이므로 $B(-2a,0)$이다.<br>"
                  r"점 B에서의 접선은 중심과 B를 잇는 반지름과 수직이다. 중심에서 B로 향하는 방향의 "
                  r"기울기는 $\dfrac{0-(-b)}{-2a-(-a)}=-\dfrac{b}{a}$이므로 접선 $l$의 기울기는 "
                  r"$\dfrac{a}{b}$이다.<br>"
                  r"$\dfrac{a}{b}=\dfrac13$이므로 $b=3a$이고, $a^2+b^2=r^2=1$에서 $a=\dfrac{1}"
                  r"{\sqrt{10}}$, $b=\dfrac{3}{\sqrt{10}}$이다 (A가 제1사분면 위의 점이므로 양수를 "
                  r"택함).<br>"
                  r"직선 $l$은 기울기 $\dfrac13$이고 점 B$(-2a,0)$을 지나므로 $x-3y+2a=0$이다.<br>"
                  r"점 A와 직선 $l$ 사이의 거리는 $\dfrac{|a-3b+2a|}{\sqrt{10}}=\dfrac{|3a-3b|}"
                  r"{\sqrt{10}}=\dfrac{3|a-b|}{\sqrt{10}}$이고, $a-b=-2a=-\dfrac{2}{\sqrt{10}}$이므로 "
                  r"거리는 $\dfrac{3\cdot\frac{2}{\sqrt{10}}}{\sqrt{10}}=\dfrac{6}{10}=\dfrac35$이다.",
),
17: dict(
    # 2026-09-28 재검토: 원래 (내분점 조건 + 접선 조건)을 결합해 원의 방정식부터
    # 유도해야 해서 서술형으로는 과중했음(6단계 이상). "원 → 두 축 교점 → 대각선
    # 공식으로 사각형 넓이" 라는 같은 핵심 기법은 유지하되, 원을 직접 제시해
    # 유도 단계를 덜어내고 적당한 난이도로 재설계함.
    chapter="원의 방정식", difficulty="중", points=3, is_subjective=True,
    question_text=r"원 O: $(x-6)^2+(y-6)^2=100$이 $x$축과 두 점 A, B에서, $y$축과 두 점 C, D에서 "
                   r"만난다. (단, 점 A의 $x$좌표는 점 B의 $x$좌표보다 작고, 점 C의 $y$좌표는 점 D의 "
                   r"$y$좌표보다 작다.) 사각형 ACBD의 넓이를 구하시오.",
    choices=None, answer="128",
    solution_text=r"원 O의 방정식에 $y=0$을 대입하면 $(x-6)^2+36=100$, $(x-6)^2=64$에서 "
                  r"$x=-2$ 또는 $x=14$이므로 $A(-2,0)$, $B(14,0)$이다.<br>"
                  r"원 O의 방정식에 $x=0$을 대입하면 $36+(y-6)^2=100$, $(y-6)^2=64$에서 "
                  r"$y=-2$ 또는 $y=14$이므로 $C(0,-2)$, $D(0,14)$이다.<br>"
                  r"사각형 ACBD의 두 대각선 $\overline{AB}$, $\overline{CD}$는 각각 $x$축, $y$축 "
                  r"위에 있어 서로 수직이므로 사각형의 넓이는 $\dfrac12\times\overline{AB}\times"
                  r"\overline{CD}$이다.<br>"
                  r"$\overline{AB}=14-(-2)=16$, $\overline{CD}=14-(-2)=16$이므로 사각형 ACBD의 "
                  r"넓이는 $\dfrac12\times16\times16=128$이다.",
),
18: dict(
    chapter="원의 방정식", difficulty="중", points=3, is_subjective=False,
    question_text=r"그림과 같이 좌표평면 위에 원 $C:(x-4)^2+(y-4)^2=16$과 직선 $y=mx$ $(0<m<1)$이 "
                   r"있다. 원 C의 중심을 A, 점 A에서 직선 $y=mx$에 내린 수선의 발을 H, 직선 $y=mx$가 "
                   r"원 C와 만나는 두 점 중 원점 O에 가까운 점을 B라 할 때, $\overline{OH}:\overline{BH}"
                   r"=2:1$이다. 상수 $m$의 값은?",
    choices=[{"number":1,"text":"$-6+5\\sqrt2$"},{"number":2,"text":"$-1+\\sqrt2$"},
             {"number":3,"text":"$3-2\\sqrt2$"},{"number":4,"text":"$7-4\\sqrt2$"},
             {"number":5,"text":"$\\dfrac92-3\\sqrt2$"}],
    answer="3",
    solution_text=r"$\overline{AB}=4$(반지름)이고 $\overline{BH}=t$라 하면 직각삼각형 ABH에서 "
                  r"$\overline{AH}^2=16-t^2$ … ①<br>"
                  r"원 C의 중심 A의 좌표는 $(4,4)$이므로 $\overline{OA}=4\sqrt2$이다.<br>"
                  r"$\overline{OH}:\overline{BH}=2:1$이므로 $\overline{OH}=2t$이고, 직각삼각형 AOH에서 "
                  r"$\overline{AH}^2=\overline{OA}^2-\overline{OH}^2=32-4t^2$ … ②<br>"
                  r"①, ②에서 $16-t^2=32-4t^2$이므로 $t^2=\dfrac{16}{3}$이고 $\overline{AH}^2=\dfrac{32}{3}$"
                  r"이다.<br>"
                  r"한편 $\overline{AH}$는 점 A와 직선 $mx-y=0$ 사이의 거리이므로 "
                  r"$\overline{AH}=\dfrac{|4m-4|}{\sqrt{m^2+1}}$이다.<br>"
                  r"이를 ①에 대입하면 $\dfrac{16(m-1)^2}{m^2+1}=\dfrac{32}{3}$이고, 정리하면 "
                  r"$3(m-1)^2=2(m^2+1)$, 즉 $m^2-6m+1=0$이다.<br>"
                  r"근의 공식으로 풀면 $m=3\pm2\sqrt2$이고, $0<m<1$인 것은 $m=3-2\sqrt2$이다.",
),

# ── 3. 도형의 이동 (원본 19~28) ──────────────────────────────────────
19: dict(
    chapter="도형의 이동", difficulty="중", points=4, is_subjective=False,
    question_text=r"직선 $y=ax+2$를 $x$축의 방향으로 $3$만큼 평행이동한 후, $y$축에 대하여 대칭이동한 "
                   r"직선이 원 $(x+2)^2+(y+6)^2=9$의 넓이를 이등분할 때, 상수 $a$의 값은?",
    choices=[{"number":1,"text":"$2$"},{"number":2,"text":"$4$"},{"number":3,"text":"$6$"},
             {"number":4,"text":"$8$"},{"number":5,"text":"$10$"}],
    answer="4",
    solution_text=r"직선 $y=ax+2$를 $x$축의 방향으로 $3$만큼 평행이동하면 $y=a(x-3)+2=ax-3a+2$이다.<br>"
                  r"이를 $y$축에 대하여 대칭이동하면 $x$ 대신 $-x$를 대입하여 $y=-ax-3a+2$이다.<br>"
                  r"이 직선이 원의 넓이를 이등분하려면 원의 중심 $(-2,-6)$을 지나야 한다.<br>"
                  r"$-6=-a(-2)-3a+2=-a+2$에서 $-a=-8$, 즉 $a=8$이다.<br>"
                  r"(검산: $a=8$일 때 직선은 $y=-8x-22$이고, $x=-2$를 대입하면 $y=16-22=-6$으로 "
                  r"중심을 지남을 확인한다.)",
),
20: dict(
    chapter="도형의 이동", difficulty="하", points=4, is_subjective=True,
    question_text=r"좌표평면의 점 $A(2,3)$을 $x$축의 방향으로 $3$만큼, $y$축의 방향으로 $-6$만큼 "
                   r"평행이동한 점을 B라 하자. 직선 AB를 $x$축의 방향으로 $2$만큼, $y$축의 방향으로 "
                   r"$3$만큼 평행이동한 직선의 $y$절편을 구하시오.",
    choices=None, answer="14",
    solution_text=r"점 B의 좌표는 $(2+3,3-6)=(5,-3)$이다.<br>"
                  r"직선 AB의 기울기는 $\dfrac{-3-3}{5-2}=-2$이므로 방정식은 $y=-2x+7$이다.<br>"
                  r"이 직선을 $x$축으로 $2$, $y$축으로 $3$만큼 평행이동하면 "
                  r"$y-3=-2(x-2)+7$, 즉 $y=-2x+14$이다.<br>"
                  r"따라서 $y$절편은 $14$이다.",
),
21: dict(
    chapter="도형의 이동", difficulty="중", points=4.4, is_subjective=False,
    question_text=r"좌표평면 위에 원 $C:(x-10)^2+(y-9)^2=2$와 점 $A(2,3)$이 있다. 원 C 위의 점 P, "
                   r"직선 $y=x$ 위의 점 Q에 대하여 $\overline{AQ}+\overline{QP}$의 최솟값은?",
    choices=[{"number":1,"text":"$4\\sqrt2$"},{"number":2,"text":"$5\\sqrt2$"},
             {"number":3,"text":"$6\\sqrt2$"},{"number":4,"text":"$7\\sqrt2$"},
             {"number":5,"text":"$8\\sqrt2$"}],
    answer="3",
    solution_text=r"점 A를 직선 $y=x$에 대하여 대칭이동하면 $A'(3,2)$이다.<br>"
                  r"점 Q가 직선 $y=x$ 위에 있으므로 $\overline{AQ}=\overline{A'Q}$이다.<br>"
                  r"따라서 $\overline{AQ}+\overline{QP}=\overline{A'Q}+\overline{QP}\ge \overline{A'P}$"
                  r"이고, 이는 다시 원 C의 중심을 지나는 거리에서 반지름을 뺀 값 이상이므로 "
                  r"$\overline{A'P}\ge \overline{A'C}-r$이다.<br>"
                  r"$\overline{A'C}=\sqrt{(10-3)^2+(9-2)^2}=\sqrt{49+49}=7\sqrt2$이고 $r=\sqrt2$이므로 "
                  r"최솟값은 $7\sqrt2-\sqrt2=6\sqrt2$이다.",
),
22: dict(
    chapter="도형의 이동", difficulty="중", points=4.2, is_subjective=False,
    question_text=r"좌표평면 위에 두 점 $A(-4,3)$, $B(3,7)$이 있다. $\overline{PQ}=2$인 $x$축 위의 두 "
                   r"점 P, Q에 대하여 $\overline{AP}+\overline{QB}$의 최솟값은? (단, 점 P의 $x$좌표는 "
                   r"점 Q의 $x$좌표보다 작다.)",
    choices=[{"number":1,"text":"$2\\sqrt{29}$"},{"number":2,"text":"$11$"},
             {"number":3,"text":"$5\\sqrt5$"},{"number":4,"text":"$8\\sqrt2$"},
             {"number":5,"text":"$2\\sqrt{34}$"}],
    answer="3",
    solution_text=r"점 A를 $x$축에 대하여 대칭이동하면 $A'(-4,-3)$이고, $\overline{AP}=\overline{A'P}$"
                  r"이다.<br>"
                  r"점 B를 $x$축의 방향으로 $-2$만큼 평행이동하면 $B'(1,7)$이고, $\overline{PQ}=2$이므로 "
                  r"$\overline{QB}=\overline{PB'}$이다.<br>"
                  r"따라서 $\overline{AP}+\overline{QB}=\overline{A'P}+\overline{PB'}\ge \overline{A'B'}$"
                  r"이다.<br>"
                  r"$\overline{A'B'}=\sqrt{(1-(-4))^2+(7-(-3))^2}=\sqrt{25+100}=\sqrt{125}=5\sqrt5$이다.",
),
23: dict(
    # 2026-09-28 사용자 지적으로 재검산: 원래 중심 (10,-5)/(-7,1) 조합은 대칭이동한
    # 두 중심 (10,5),(1,-7)을 이은 선분이 x축은 지나지만 직선 y=x는 "선분 밖"에서
    # 지나서(연장선상) 실제로 그 최단경로 위에 Q가 y=x 위에 놓이지 않는 오류였음
    # (즉 15-2-3=10 은 삼각부등식상 하한일 뿐 달성 불가능한 값이었음). 두 대칭이동
    # 중심을 잇는 선분이 x축→y=x 순서로 실제로 교차하는 좌표로 전수 재설계하고
    # 좌표 하나하나 교차 유효성(0≤t≤1)까지 프로그램으로 검증한 뒤 확정함.
    chapter="도형의 이동", difficulty="상", points=4.8, is_subjective=False,
    question_text=r"좌표평면 위에 두 원 $C_1:(x+14)^2+(y+2)^2=4$, $C_2:(x+10)^2+(y+5)^2=9$와 직선 "
                   r"$y=x$가 있다. 점 A는 원 $C_1$ 위에 있고, 점 B는 원 $C_2$ 위에 있다. 점 P는 $x$축 "
                   r"위에 있고, 점 Q는 직선 $y=x$ 위에 있을 때, $\overline{AP}+\overline{PQ}+"
                   r"\overline{QB}$의 최솟값은? (단, 세 점 A, P, Q는 서로 다른 점이다.)",
    choices=[{"number":1,"text":"$8$"},{"number":2,"text":"$9$"},{"number":3,"text":"$10$"},
             {"number":4,"text":"$11$"},{"number":5,"text":"$12$"}],
    answer="3",
    solution_text=r"$C_1$을 $x$축에 대하여 대칭이동하면 중심 $(-14,2)$, 반지름 $2$인 원이 되고, 그 위의 "
                  r"점은 A를 $x$축에 대칭이동한 점과 같은 위치에 대응한다.<br>"
                  r"$C_2$를 직선 $y=x$에 대하여 대칭이동하면 중심 $(-5,-10)$, 반지름 $3$인 원이 된다.<br>"
                  r"P가 $x$축 위, Q가 직선 $y=x$ 위에 있으므로 $\overline{AP}+\overline{PQ}+"
                  r"\overline{QB}$의 최솟값은 이 두 대칭이동된 원의 중심을 잇는 선분의 길이에서 두 "
                  r"반지름을 뺀 값과 같다.<br>"
                  r"두 중심 $(-14,2)$, $(-5,-10)$ 사이의 거리는 $\sqrt{9^2+12^2}=\sqrt{225}=15$이다.<br>"
                  r"따라서 최솟값은 $15-2-3=10$이다.",
),
24: dict(
    chapter="도형의 이동", difficulty="중", points=4, is_subjective=False,
    question_text=r"이차함수 $y=-x^2$의 그래프를 $x$축에 대하여 대칭이동한 후, $x$축의 방향으로 $3$만큼, "
                   r"$y$축의 방향으로 $m$만큼 평행이동한 그래프가 직선 $y=4x+5$에 접할 때, 상수 $m$의 "
                   r"값은?",
    choices=[{"number":1,"text":"$18$"},{"number":2,"text":"$19$"},{"number":3,"text":"$20$"},
             {"number":4,"text":"$21$"},{"number":5,"text":"$22$"}],
    answer="4",
    solution_text=r"$y=-x^2$을 $x$축에 대하여 대칭이동하면 $y=x^2$이다.<br>"
                  r"이를 $x$축으로 $3$, $y$축으로 $m$만큼 평행이동하면 $y=(x-3)^2+m$이다.<br>"
                  r"직선 $y=4x+5$와 연립하면 $(x-3)^2+m=4x+5$, 즉 $x^2-10x+(4+m)=0$이다.<br>"
                  r"접하므로 판별식이 $0$이어야 한다. $D=100-4(4+m)=0$에서 $m=21$이다.<br>"
                  r"(검산: $m=21$이면 $x^2-10x+25=(x-5)^2=0$으로 중근을 가지므로 실제로 접한다.)",
),
25: dict(
    chapter="도형의 이동", difficulty="중", points=3, is_subjective=False,
    question_text=r"곡선 $y=x^2-5$ 위의 서로 다른 두 점 A, B가 직선 $y=x$에 대하여 대칭일 때, 선분 "
                   r"AB의 길이는? (단, 점 A의 $x$좌표는 음수이다.)",
    choices=[{"number":1,"text":"$\\sqrt{31}$"},{"number":2,"text":"$\\sqrt{32}$"},
             {"number":3,"text":"$\\sqrt{33}$"},{"number":4,"text":"$\\sqrt{34}$"},
             {"number":5,"text":"$\\sqrt{35}$"}],
    answer="4",
    solution_text=r"$A(\alpha,\alpha^2-5)$, $B(\beta,\beta^2-5)$라 하자.<br>"
                  r"두 점이 직선 $y=x$에 대하여 대칭이므로 직선 AB의 기울기는 $-1$이다. 즉 "
                  r"$\dfrac{(\beta^2-5)-(\alpha^2-5)}{\beta-\alpha}=\alpha+\beta=-1$이다.<br>"
                  r"또 선분 AB의 중점이 직선 $y=x$ 위에 있다는 조건에서 계산하면 $\alpha\beta=-4$를 "
                  r"얻는다.<br>"
                  r"$\overline{AB}^2=(\beta-\alpha)^2+\{(\beta^2-5)-(\alpha^2-5)\}^2"
                  r"=(\beta-\alpha)^2\{1+(\alpha+\beta)^2\}$이고, "
                  r"$(\beta-\alpha)^2=(\alpha+\beta)^2-4\alpha\beta=1+16=17$이므로 "
                  r"$\overline{AB}^2=17\times2=34$이다.<br>"
                  r"따라서 $\overline{AB}=\sqrt{34}$이다.",
),
26: dict(
    chapter="도형의 이동", difficulty="상", points=5.2, is_subjective=False,
    question_text=r"원 $(x-5)^2+y^2=r^2$ 위를 움직이는 두 점 P, Q가 있다. 점 P를 $y$축에 대하여 "
                   r"대칭이동한 점의 좌표를 $(x_1,y_1)$이라 하고, 점 Q를 $y$축의 방향으로 $k$만큼 "
                   r"평행이동한 점의 좌표를 $(x_2,y_2)$라 하자. $\dfrac{y_2-y_1}{x_2-x_1}$의 최솟값이 "
                   r"$0$이고 최댓값이 $\dfrac{5}{12}$일 때, $|r+k|$의 값은? (단, $x_1\ne x_2$"
                   r"이고 $k$는 실수, $r$은 양수이다.)",
    choices=[{"number":1,"text":"$1$"},{"number":2,"text":"$2$"},{"number":3,"text":"$3$"},
             {"number":4,"text":"$4$"},{"number":5,"text":"$5$"}],
    answer="3",
    solution_text=r"점 P를 $y$축에 대하여 대칭이동한 점 $(x_1,y_1)$은 원 $(x+5)^2+y^2=r^2$, 즉 중심 "
                  r"A$(-5,0)$, 반지름 $r$인 원 위를 움직인다.<br>"
                  r"점 Q를 $y$축의 방향으로 $k$만큼 평행이동한 점 $(x_2,y_2)$는 원 "
                  r"$(x-5)^2+(y-k)^2=r^2$, 즉 중심 B$(5,k)$, 반지름 $r$인 원 위를 움직인다.<br>"
                  r"$\dfrac{y_2-y_1}{x_2-x_1}$은 원 A 위의 한 점과 원 B 위의 한 점을 잇는 직선의 "
                  r"기울기이므로, 그 최솟값과 최댓값은 두 원에 공통으로 접하면서 두 원을 서로 다른 "
                  r"쪽에 두는 접선(내접선)의 기울기와 같다.<br>"
                  r"그 내접선을 $y=mx+n$이라 하면, 두 중심에서 이 직선까지의 거리가 모두 $r$이므로<br>"
                  r"$\dfrac{|n-5m|}{\sqrt{m^2+1}}=r$, $\dfrac{|5m+n-k|}{\sqrt{m^2+1}}=r$"
                  r"이고, 두 원이 직선의 서로 다른 쪽에 있으므로 $n-5m=-(5m+n-k)$에서 "
                  r"$n=\dfrac{k}{2}$이다.<br>"
                  r"최솟값이 $0$이므로 $m=0$을 대입하면 $\dfrac{|n|}{1}=r$에서 $n=r$ (양수로 택함), "
                  r"즉 $k=2r$이다.<br>"
                  r"이제 $n=r$을 처음 식에 대입하면 $|r-5m|=r\sqrt{m^2+1}$이고, 양변을 제곱해 "
                  r"정리하면 $25m^2-10mr=r^2m^2$, 즉 $m\{(25-r^2)m-10r\}=0$이다.<br>"
                  r"$m=0$이 아닌 나머지 근이 최댓값이므로 $m=\dfrac{10r}{25-r^2}=\dfrac{5}{12}$이다.<br>"
                  r"정리하면 $120r=5(25-r^2)$에서 $r^2+24r-25=0$, 즉 $(r+25)(r-1)=0$이므로 "
                  r"$r=1$이다.<br>"
                  r"따라서 $k=2r=2$이므로 $|r+k|=|1+2|=3$이다.",
),
27: dict(
    chapter="도형의 이동", difficulty="상", points=5.2, is_subjective=False,
    question_text=r"함수 $f(x)=x^2+ax+b$에 대하여 방정식 $f(x)=0$이 서로 다른 두 실근 $\alpha,\beta$ "
                   r"$(0<\alpha<\beta)$를 갖는다. 함수 $g(x)$"
                   r"<<BOX_START>>$g(x)=\begin{cases}-f(-x+3\alpha)&(x<2\alpha)\\f(x-\alpha)&(x\ge2"
                   r"\alpha)\end{cases}$<<BOX_END>>에 대하여 방정식 $g(x)=0$의 서로 다른 모든 실근의 합과 "
                   r"곱이 각각 $24$, $384$일 때, $|a|+|b|$의 값은? (단, $a,b$는 상수이다.)",
    choices=[{"number":1,"text":"$36$"},{"number":2,"text":"$40$"},{"number":3,"text":"$44$"},
             {"number":4,"text":"$48$"},{"number":5,"text":"$52$"}],
    answer="3",
    solution_text=r"$x\ge2\alpha$일 때 $g(x)=f(x-\alpha)=0$이면 $x-\alpha=\alpha$ 또는 $x-\alpha=\beta$, "
                  r"즉 $x=2\alpha$ 또는 $x=\alpha+\beta$이다. 두 값 모두 $2\alpha$ 이상이므로 모두 "
                  r"채택된다.<br>"
                  r"$x<2\alpha$일 때 $g(x)=-f(-x+3\alpha)=0$이면 $-x+3\alpha=\alpha$ 또는 "
                  r"$-x+3\alpha=\beta$, 즉 $x=2\alpha$ 또는 $x=3\alpha-\beta$이다. $x=2\alpha$는 이 "
                  r"구간에 속하지 않아 제외되고, $\alpha<\beta$이므로 $x=3\alpha-\beta<2\alpha$는 "
                  r"채택된다.<br>"
                  r"따라서 방정식 $g(x)=0$의 서로 다른 실근은 $3\alpha-\beta$, $2\alpha$, $\alpha+\beta$"
                  r"의 세 개이다.<br>"
                  r"세 근의 합은 $(3\alpha-\beta)+2\alpha+(\alpha+\beta)=6\alpha=24$이므로 $\alpha=4$"
                  r"이다.<br>"
                  r"세 근의 곱은 $(3\alpha-\beta)\cdot2\alpha\cdot(\alpha+\beta)=(12-\beta)\cdot8\cdot"
                  r"(4+\beta)=384$이므로 $(12-\beta)(4+\beta)=48$이다.<br>"
                  r"전개하면 $48+8\beta-\beta^2=48$에서 $\beta(8-\beta)=0$이고, $\beta>\alpha=4$이므로 "
                  r"$\beta=8$이다.<br>"
                  r"따라서 $f(x)=0$의 두 실근이 $4,8$이므로 $f(x)=(x-4)(x-8)=x^2-12x+32$이고 "
                  r"$a=-12$, $b=32$이므로 $|a|+|b|=44$이다.",
),
28: dict(
    # 2026-09-28 교과범위 재검토: 원래 버전은 곡선이 포물선이라 넓이를 구하려면
    # 실제로 적분이 필요했음(공통수학2 "도형의 이동" 단원 범위 밖). 곡선을
    # 절댓값(V자형 선분)으로 바꿔 같은 "평행이동+대칭이동 인식 후 넓이" 구조를
    # 유지하면서 직사각형에서 삼각형 두 개를 빼는 순수 도형 계산으로 대체.
    chapter="도형의 이동", difficulty="상", points=5.2, is_subjective=False,
    question_text=r"$x,y$에 대한 식 $f(x,y)=y-(2-|x|)$에 대하여, $-1\le x\le1$에서 방정식 "
                   r"$f(x,y)=0$이 나타내는 도형 C가 있다. 두 방정식 $f(x-3,y+3)=0$, $f(x-3,3-y)=0$이 "
                   r"나타내는 도형과 두 직선 $x=2$, $x=4$로 둘러싸인 부분의 넓이는?",
    choices=[{"number":1,"text":"$4$"},{"number":2,"text":"$5$"},
             {"number":3,"text":"$6$"},{"number":4,"text":"$7$"},
             {"number":5,"text":"$8$"}],
    answer="3",
    solution_text=r"$f(x,y)=0$은 $y=2-|x|$이므로 도형 C는 $-1\le x\le1$에서 꼭짓점이 $(0,2)$이고 양 "
                  r"끝점이 $(-1,1)$, $(1,1)$인 꺾인 선분이다.<br>"
                  r"$f(x-3,y+3)=0$은 $(y+3)=2-|x-3|$, 즉 $y=-1-|x-3|$이다. 이는 도형 C를 $x$축의 "
                  r"방향으로 $3$, $y$축의 방향으로 $-3$만큼 평행이동한 것으로, 정의역은 $2\le x\le4$이고 "
                  r"꼭짓점 $(3,-1)$, 양 끝점 $(2,-2)$, $(4,-2)$이다.<br>"
                  r"$f(x-3,3-y)=0$은 $(3-y)=2-|x-3|$, 즉 $y=1+|x-3|$이다. 이는 도형 C를 $x$축에 대하여 "
                  r"대칭이동한 후 평행이동한 것으로, 정의역은 $2\le x\le4$이고 꼭짓점 $(3,1)$, 양 끝점 "
                  r"$(2,2)$, $(4,2)$이다.<br>"
                  r"두 도형 모두 정의역이 $2\le x\le4$로 두 직선 $x=2$, $x=4$와 정확히 만난다. 둘러싸인 "
                  r"부분은 $2\le x\le4$, $-2\le y\le2$인 직사각형(가로 $2$, 세로 $4$, 넓이 $8$)에서 위·아래 "
                  r"귀퉁이 삼각형 두 개를 잘라낸 모양이다.<br>"
                  r"위쪽 귀퉁이는 세 점 $(2,2)$, $(3,1)$, $(4,2)$가 꼭짓점인 삼각형(밑변 $2$, 높이 $1$, "
                  r"넓이 $1$)이고, 아래쪽 귀퉁이도 세 점 $(2,-2)$, $(3,-1)$, $(4,-2)$가 꼭짓점인 합동인 "
                  r"삼각형(넓이 $1$)이다.<br>"
                  r"따라서 구하는 넓이는 $8-1-1=6$이다.",
),
}

CHAPTER_ORDER = ["평면좌표", "직선의 방정식", "원의 방정식", "도형의 이동"]

# 3세트 원본번호 배정 (실전동형테스트 1~3회) — 28문항 전량, 3개 단원 고르게 배분.
# 난이도 순서 재배정(2026-09-28, 사용자 요청): 1회=적당, 2회=어려움, 3회=쉬움이
# 되도록 기존 세트 내용을 그대로 옮기되 회차 라벨만 바꿈
# (구1회[하8중16상0]→신3회, 구2회[하6중17상1]→신1회, 구3회[하5중13상6]→신2회).
SET_ORIG_NUMS = {
    1: [4, 5, 6, 7, 14, 15, 22, 23, 24],
    2: [8, 9, 10, 16, 17, 18, 25, 26, 27, 28],
    3: [1, 2, 3, 11, 12, 13, 19, 20, 21],
}
