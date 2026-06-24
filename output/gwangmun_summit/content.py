# -*- coding: utf-8 -*-
"""광문고 기말대비 SUMMIT POINT — 문항/해설 콘텐츠 (KaTeX). raw 문자열 사용."""

FIG_DIR = "/private/tmp/claude-501/-Users-youngwoolee-MathDB/6571e9e7-bf0f-4d26-9807-b5fb04a436c9/scratchpad"

# 각 항목: label, source, html(본문), answer(해설용), sol_html(해설)
PROBLEMS = [
{
 "label": "A·01", "source": "[2025년 6월 고3 20번/4점]",
 "answer": "85",
 "prob": r"""
<p>실수 전체의 집합에서 정의된 함수 $f(x)$가 다음 조건을 만족시킨다.</p>
<div class="cbox"><p>$0\le x<4$일 때 $f(x)=-x^2+4x$이고, 모든 실수 $x$에 대하여 $f(x+4)=f(x)$이다.</p></div>
<p>방정식 $f(f(x))=f(x)$의 $0$ 이상인 모든 실근을 작은 수부터 크기순으로 나열할 때 $n$번째 수를 $a_n$이라 하자. 다음은 $a_{20}+a_{21}+a_{22}$의 값을 구하는 과정이다.</p>
<div class="cbox">
<p>방정식 $f(x)=x$의 모든 실근이 $0$, $3$이므로 방정식 $f(f(x))=f(x)$의 실근을 구하는 것은 방정식 $f(x)\{f(x)-3\}=0$의 실근을 구하는 것과 같다.</p>
<p>$0\le x<4$일 때, 방정식 $f(x)\{f(x)-3\}=0$의 모든 실근은 $0$, <span class="bl">가</span>, $3$이므로 $a_1=0$, $a_2=$<span class="bl">가</span>, $a_3=3$이다.</p>
<p>또한, 모든 실수 $x$에 대하여 $f(x+4)=f(x)$이므로 세 수열 $\{a_{3n-2}\}$, $\{a_{3n-1}\}$, $\{a_{3n}\}$은 첫째항이 각각 $0$, <span class="bl">가</span>, $3$이고 공차가 모두 <span class="bl">나</span>인 등차수열이다.</p>
<p>따라서 $a_{20}+a_{21}+a_{22}=$<span class="bl">다</span>이다.</p>
</div>
<p>위의 <span class="bl">가</span>, <span class="bl">나</span>, <span class="bl">다</span>에 알맞은 수를 각각 $p$, $q$, $r$이라 할 때 $p+q+r$의 값을 구하시오.</p>
""",
 "sol": r"""
<p class="lead">주기함수를 이해하고 등차수열의 일반항을 구할 수 있는가?</p>
<p>$0\le x<4$일 때 $f(x)=-x^2+4x$이고 모든 실수 $x$에 대하여 $f(x+4)=f(x)$이므로 함수 $y=f(x)$의 그래프는 다음과 같다.</p>
<div class="figrow"><img src="file://{FIG}/fig_01sol.png"></div>
<p>방정식 $f(x)=x$에서 $-x^2+4x=x$, $-x(x-3)=0$ $\therefore x=0$ 또는 $x=3$</p>
<p>방정식 $f(x)=x$의 모든 실근이 $0$, $3$이므로 방정식 $f(f(x))=f(x)$의 실근을 구하는 것은 방정식 $f(x)\{f(x)-3\}=0$의 실근을 구하는 것과 같다.</p>
<p>$0\le x<4$일 때, $f(x)=0$에서 $x=0$; $f(x)=3$에서 $-x^2+4x=3$, $-(x-1)(x-3)=0$ $\therefore x=1$ 또는 $x=3$</p>
<p>따라서 $0\le x<4$일 때 모든 실근은 $0$, $\boxed{1}$, $3$이므로 $a_1=0$, $a_2=\boxed{1}$, $a_3=3$이다.</p>
<p>세 수열 $\{a_{3n-2}\}$, $\{a_{3n-1}\}$, $\{a_{3n}\}$은 첫째항이 각각 $0$, $1$, $3$이고 공차가 모두 $\boxed{4}$인 등차수열이므로</p>
<p>$a_{20}=a_{3\cdot7-1}=1+6\cdot4=25$, $a_{21}=a_{3\cdot7}=3+6\cdot4=27$, $a_{22}=a_{3\cdot8-2}=0+7\cdot4=28$</p>
<p>$\therefore a_{20}+a_{21}+a_{22}=\boxed{80}$</p>
<p>$p=1$, $q=4$, $r=80$이므로 $p+q+r=85$</p>
""",
},
{
 "label": "A·02", "source": "[2022년 9월 고2 15번/4점]",
 "answer": "⑤",
 "prob": r"""
<p>첫째항이 양수이고 공차가 $2$인 등차수열 $\{a_n\}$의 첫째항부터 제$n$항까지의 합을 $S_n$이라 하자. $a_k=31$, $S_{k+10}=640$을 만족시키는 자연수 $k$에 대하여 $S_k$의 값은?</p>
<div class="choices">
<span class="ch">① $200$</span><span class="ch">② $205$</span><span class="ch">③ $210$</span>
<span class="ch">④ $215$</span><span class="ch">⑤ $220$</span>
</div>
""",
 "sol": r"""
<p class="lead">등차수열의 합을 이해하기</p>
<p>$S_{k+10}=S_k+(a_{k+1}+a_{k+2}+\cdots+a_{k+10})$</p>
<p>수열 $\{a_n\}$의 공차가 $2$이므로</p>
$$640=S_k+\{(a_k+2)+(a_k+4)+\cdots+(a_k+20)\}$$
$$=S_k+\left\{10a_k+\frac{10(2+20)}{2}\right\}=S_k+(10\cdot31+110)$$
<p>$\therefore S_k=640-(310+110)=220$</p>
""",
},
{
 "label": "A·03", "source": "[2019년 9월 고2 이과 14번/4점]",
 "answer": "④",
 "prob": r"""
<p>첫째항과 공차가 모두 $0$이 아닌 등차수열 $\{a_n\}$에 대하여 세 항 $a_2$, $a_5$, $a_{14}$가 이 순서대로 등비수열을 이룰 때, $\dfrac{a_{23}}{a_3}$의 값은?</p>
<div class="choices">
<span class="ch">① $6$</span><span class="ch">② $7$</span><span class="ch">③ $8$</span>
<span class="ch">④ $9$</span><span class="ch">⑤ $10$</span>
</div>
""",
 "sol": r"""
<p class="lead">등차수열과 등비수열의 관계 이해하기</p>
<p>등차수열 $\{a_n\}$의 첫째항을 $a$, 공차를 $d$라 하자. 세 항 $a_2$, $a_5$, $a_{14}$가 이 순서대로 등비수열을 이루므로</p>
$$(a_5)^2=a_2\times a_{14}$$
$$(a+4d)^2=(a+d)(a+13d)$$
$$3d^2=6ad$$
<p>$d\ne0$이므로 $d=2a$</p>
$$\therefore\ \frac{a_{23}}{a_3}=\frac{a+22d}{a+2d}=\frac{45a}{5a}=9$$
""",
},
{
 "label": "A·04", "source": "[2023년 11월 고2 15번/4점]",
 "answer": "①",
 "prob": r"""
<p>수열 $\{a_n\}$의 첫째항부터 제$n$항까지의 합을 $S_n$이라 할 때, 두 수열 $\{a_n\}$, $\{S_n\}$과 상수 $k$가 다음 조건을 만족시킨다.</p>
<div class="cbox"><p>모든 자연수 $n$에 대하여 $a_n+S_n=k$이다.</p></div>
<p>$S_6=189$일 때, $k$의 값은?</p>
<div class="choices">
<span class="ch">① $192$</span><span class="ch">② $196$</span><span class="ch">③ $200$</span>
<span class="ch">④ $204$</span><span class="ch">⑤ $208$</span>
</div>
""",
 "sol": r"""
<p class="lead">등비수열을 활용하여 문제해결하기</p>
<p>$n=1$일 때, $a_1+S_1=2a_1=k$에서 $a_1=\dfrac{k}{2}$</p>
<p>$n\ge2$일 때, $a_n=S_n-S_{n-1}=(k-a_n)-(k-a_{n-1})=-a_n+a_{n-1}$</p>
<p>이므로 $a_n=\dfrac{1}{2}a_{n-1}\ (n\ge2)$</p>
<p>수열 $\{a_n\}$은 첫째항이 $\dfrac{k}{2}$이고 공비가 $\dfrac{1}{2}$인 등비수열이므로</p>
$$a_6=\frac{k}{2}\cdot\left(\frac{1}{2}\right)^5=\frac{k}{64}$$
<p>$S_6=189$이므로 $a_6+S_6=k$에서 $\dfrac{k}{64}+189=k$ $\therefore k=192$</p>
""",
},
{
 "label": "A·05", "source": "[2028학년도 수능 예시문항 27번]",
 "answer": "7",
 "prob": r"""
<p>첫째항이 $1$이고 공차가 양수인 등차수열 $\{a_n\}$과 자연수 $n$에 대하여 곡선 $y=\log_2 x$ 위의 점 $P_n$을 지나고 $x$축에 수직인 직선이 $x$축, 곡선 $y=x^2$과 만나는 점을 각각 $A_n$, $B_n$이라 하고, 삼각형 $A_nB_nP_{n+1}$의 넓이를 $T_n$이라 하자.</p>
<div class="figrow"><img src="file://{FIG}/fig_27.png"></div>
<p>다음은 모든 자연수 $n$에 대하여 $\overline{OA_n}:\overline{OA_{n+1}}=1:4$일 때 $\displaystyle\sum_{n=1}^{5}T_n$의 값을 구하는 과정이다. (단, O는 원점이다.)</p>
<div class="cbox">
<p>$a_n=\log_2 x$일 때 $x=2^{a_n}$이므로 점 $A_n$의 $x$좌표는 $2^{a_n}$이다.</p>
<p>$\overline{OA_n}=2^{a_n}$, $\overline{OA_{n+1}}=2^{a_{n+1}}$이고 $\overline{OA_n}:\overline{OA_{n+1}}=1:4$이므로 $2^{a_n}:2^{a_{n+1}}=1:4$이다. 그러므로 등차수열 $\{a_n\}$의 공차는 <span class="bl">가</span>이다.</p>
<p>점 $B_n$의 좌표는 $(2^{a_n},\,4^{a_n})$이므로</p>
<p>$T_n=\dfrac{1}{2}\times\overline{A_nB_n}\times\overline{A_nA_{n+1}}=\dfrac{1}{2}\times4^{a_n}\times(2^{a_{n+1}}-2^{a_n})=$<span class="bl">나</span>$\times8^{a_n}$이다.</p>
<p>수열 $\{a_n\}$은 첫째항이 $1$인 등차수열이므로 $\displaystyle\sum_{n=1}^{5}T_n=$<span class="bl">다</span>$(2^{30}-1)$이다.</p>
</div>
<p>위의 <span class="bl">가</span>, <span class="bl">나</span>, <span class="bl">다</span>에 알맞은 수를 각각 $p$, $q$, $r$이라 할 때 $\dfrac{p}{q\times r}$의 값을 구하시오.</p>
""",
 "sol": r"""
<p class="lead">로그함수와 등차·등비수열의 합을 이용하여 문제를 해결한다.</p>
<p>$a_n=\log_2 x$일 때 $x=2^{a_n}$이므로 점 $A_n$의 $x$좌표는 $2^{a_n}$이다.</p>
<p>$\overline{OA_n}=2^{a_n}$, $\overline{OA_{n+1}}=2^{a_{n+1}}$이고 $\overline{OA_n}:\overline{OA_{n+1}}=1:4$이므로 $2^{a_n}:2^{a_{n+1}}=1:4$</p>
<p>공차를 $d$라 하면 $\dfrac{2^{a_{n+1}}}{2^{a_n}}=4$, $2^{d}=4$이므로 공차는 <span class="bl">가</span>$=2$이다.</p>
<p>점 $B_n=(2^{a_n},\,4^{a_n})$이므로</p>
$$T_n=\frac{1}{2}\times4^{a_n}\times(4\times2^{a_n}-2^{a_n})=\frac{3}{2}\times8^{a_n}$$
<p>따라서 <span class="bl">나</span>$=\dfrac{3}{2}$이다. $\{a_n\}$은 첫째항 $1$, 공차 $2$이므로 $a_n=2n-1$이고</p>
$$\sum_{n=1}^{5}T_n=\sum_{n=1}^{5}\frac{3}{2}\times8^{\,1+2(n-1)}=\sum_{n=1}^{5}12\times64^{\,n-1}$$
$$=12\times\frac{2^{30}-1}{2^6-1}=\frac{4}{21}\,(2^{30}-1)$$
<p>이므로 <span class="bl">다</span>$=\dfrac{4}{21}$이다.</p>
<p>$p=2$, $q=\dfrac{3}{2}$, $r=\dfrac{4}{21}$이므로 $\dfrac{p}{q\times r}=\dfrac{2}{\dfrac{3}{2}\times\dfrac{4}{21}}=\dfrac{2}{\dfrac{2}{7}}=7$</p>
""",
},
{
 "label": "A·06", "source": "[상명대학교 약술논술]",
 "answer": r"(1) $a_n=2n-1$  (2) $\dfrac{50}{161}$  (3) $m=1,2,3$",
 "prob": r"""
<p>등차수열 $\{a_n\}$에서 $a_4=7$, $a_{11}=21$일 때,</p>
<p>$(1)$ 일반항 $a_n$을 구하시오.</p>
<p>$(2)$ $\displaystyle\sum_{k=1}^{10}\dfrac{1}{a_k\,a_{k+2}}$의 값을 구하시오.</p>
<p>$(3)$ 부등식 $\displaystyle\sum_{k=1}^{m}\dfrac{4}{a_k\,a_{k+2}}<\dfrac{13}{12}$을 만족시키는 자연수 $m$을 모두 구하시오.</p>
""",
 "sol": r"""
<p><b>(1)</b> $a_4=a_1+3d=7$, $a_{11}=a_1+10d=21$</p>
<p>두 식을 빼면 $7d=14$ $\therefore d=2$, $a_1=1$ $\therefore a_n=2n-1$</p>
<p><b>(2)</b> $a_k=2k-1$, $a_{k+2}=2k+3$이므로</p>
$$\frac{1}{a_k\,a_{k+2}}=\frac{1}{(2k-1)(2k+3)}=\frac{1}{4}\!\left(\frac{1}{2k-1}-\frac{1}{2k+3}\right)$$
$$\sum_{k=1}^{10}\frac{1}{a_k\,a_{k+2}}=\frac{1}{4}\!\left(1+\frac{1}{3}-\frac{1}{21}-\frac{1}{23}\right)=\frac{1}{4}\cdot\frac{200}{161}=\frac{50}{161}$$
<p><b>(3)</b> $\dfrac{4}{a_k\,a_{k+2}}=\dfrac{1}{2k-1}-\dfrac{1}{2k+3}$이므로</p>
$$\sum_{k=1}^{m}\frac{4}{a_k\,a_{k+2}}=\frac{4}{3}-\frac{1}{2m+1}-\frac{1}{2m+3}$$
<p>부등식 $\dfrac{4}{3}-\dfrac{1}{2m+1}-\dfrac{1}{2m+3}<\dfrac{13}{12}$에서 $\dfrac{1}{2m+1}+\dfrac{1}{2m+3}>\dfrac{1}{4}$</p>
<p>좌변은 $m$이 커질수록 감소하고, $m=3$이면 $\dfrac{1}{7}+\dfrac{1}{9}=\dfrac{16}{63}>\dfrac{1}{4}$, $m=4$이면 $\dfrac{1}{9}+\dfrac{1}{11}=\dfrac{20}{99}<\dfrac{1}{4}$</p>
<p>$\therefore m=1,\ 2,\ 3$</p>
""",
},
{
 "label": "A·07", "source": "[삼육대학교 약술논술]",
 "answer": "12",
 "prob": r"""
<p>첫째항이 $4$인 수열 $\{a_n\}$이 모든 자연수 $n$에 대하여</p>
$$\sum_{k=1}^{n}\left(\frac{a_k}{k+1}-\frac{a_{k+1}}{k+2}\right)=-2n$$
<p>을 만족시킬 때, $\displaystyle\sum_{n=1}^{9}\left(\dfrac{20}{a_n}+\dfrac{24}{a_{n+2}}\right)$의 값을 구하시오.</p>
""",
 "sol": r"""
<p>주어진 식의 좌변에 $k=1,\,2,\,\cdots,\,n$을 차례로 대입하면</p>
$$\left(\frac{a_1}{2}-\frac{a_2}{3}\right)+\left(\frac{a_2}{3}-\frac{a_3}{4}\right)+\cdots+\left(\frac{a_n}{n+1}-\frac{a_{n+1}}{n+2}\right)$$
<p>이고, 이웃한 항끼리 차례로 소거되므로 그 합은</p>
$$\frac{a_1}{2}-\frac{a_{n+1}}{n+2}=2-\frac{a_{n+1}}{n+2}=-2n$$
<p>$\dfrac{a_{n+1}}{n+2}=2n+2=2(n+1)$ $\therefore a_{n+1}=2(n+1)(n+2)$</p>
<p>즉 $a_n=2n(n+1)\ (n\ge2)$이고 $a_1=4$도 이를 만족하므로 $a_n=2n(n+1)$이다.</p>
<p>$\dfrac{20}{a_n}=\dfrac{10}{n(n+1)}=10\!\left(\dfrac{1}{n}-\dfrac{1}{n+1}\right)$이므로</p>
$$\sum_{n=1}^{9}\frac{20}{a_n}=10\!\left\{\left(\frac{1}{1}-\frac{1}{2}\right)+\left(\frac{1}{2}-\frac{1}{3}\right)+\cdots+\left(\frac{1}{9}-\frac{1}{10}\right)\right\}=10\!\left(1-\frac{1}{10}\right)=9$$
<p>$\dfrac{24}{a_{n+2}}=\dfrac{12}{(n+2)(n+3)}=12\!\left(\dfrac{1}{n+2}-\dfrac{1}{n+3}\right)$이므로</p>
$$\sum_{n=1}^{9}\frac{24}{a_{n+2}}=12\!\left\{\left(\frac{1}{3}-\frac{1}{4}\right)+\cdots+\left(\frac{1}{11}-\frac{1}{12}\right)\right\}=12\!\left(\frac{1}{3}-\frac{1}{12}\right)=3$$
<p>$\therefore\ \displaystyle\sum_{n=1}^{9}\left(\frac{20}{a_n}+\frac{24}{a_{n+2}}\right)=9+3=12$</p>
""",
},
{
 "label": "A·08", "source": "[을지대학교 약술논술]",
 "answer": r"(1) $r=3$  (2) $a_1=\dfrac{2}{9}$  (3) $15$",
 "prob": r"""
<p>공비가 $1$보다 큰 등비수열 $\{a_n\}$의 첫째항부터 제$n$항까지의 합을 $S_n$이라 하자.</p>
$$\frac{a_1}{a_2}+\frac{a_3}{a_2}+\frac{a_3}{a_4}+\frac{a_5}{a_4}+\frac{a_5}{a_6}+\frac{a_7}{a_6}=10$$
<p>이고 $a_4=6$일 때, $S_n>3^{12}$을 만족시키는 자연수 $n$의 최솟값을 구하는 과정을 아래의 단계에 따라 서술하시오.</p>
<p>$(1)$ 등비수열 $\{a_n\}$의 공비를 $r\ (r>1)$이라 할 때, $r$의 값을 구하시오.</p>
<p>$(2)$ 등비수열 $\{a_n\}$의 첫째항 $a_1$을 구하시오.</p>
<p>$(3)$ $S_n>3^{12}$을 만족시키는 자연수 $n$의 최솟값을 구하시오.</p>
""",
 "sol": r"""
<p><b>(1)</b> 주어진 식에서 $\dfrac{a_1}{a_2}=\dfrac{1}{r}$, $\dfrac{a_3}{a_2}=r$, $\cdots$ 이므로</p>
<p>$\dfrac{1}{r}+r+\dfrac{1}{r}+r+\dfrac{1}{r}+r=\dfrac{3}{r}+3r=10$</p>
<p>$3r^2-10r+3=0$, $(3r-1)(r-3)=0$ $r>1$이므로 $r=3$</p>
<p><b>(2)</b> $a_4=a_1\times3^3=6$이므로 $a_1=\dfrac{2}{9}$</p>
<p><b>(3)</b> $S_n=\dfrac{\frac{2}{9}(3^n-1)}{3-1}=\dfrac{1}{9}(3^n-1)>3^{12}$에서 $3^n-1>3^{14}$</p>
<p>$3^n>3^{14}+1$이므로 $n\ge15$ $\therefore$ 최솟값은 $15$</p>
""",
},
{
 "label": "A·09", "source": "[한국기술교육대학교 약술논술]",
 "answer": r"(1) $d=6$  (2) $a_1=-34$",
 "prob": r"""
<p>모든 항이 $0$이 아닌 정수이고 공차 $d$가 양수인 등차수열 $\{a_n\}$의 첫째항부터 제$n$항까지의 합을 $S_n$이라 하자. 수열 $\{S_n\}$의 각 항을 작은 수부터 다시 차례로 나열한 수열을 $\{M_n\}$이라 하면, 수열 $\{M_n\}$이</p>
$$M_2-M_1=M_3-M_2=2$$
<p>를 만족시킨다. $S_n>0$을 만족시키는 자연수 $n$의 최솟값이 $13$일 때, 다음 물음에 답하시오. (단, 수열 $\{S_n\}$의 모든 항은 서로 다르다.)</p>
<p>$(1)$ 공차 $d$의 값을 구하시오.</p>
<p>$(2)$ 첫째항 $a_1$의 값을 구하시오.</p>
""",
 "sol": r"""
<p>$d>0$이므로 $S_n$은 아래로 볼록하고, $\{S_n\}$의 가장 작은 세 항은 꼭짓점에 가까운 연속한 항들이다. $S_k=M_1$이라 하면 다음 두 경우가 있다.</p>
<p class="case"><b>(ⅰ) $S_k=M_1$, $S_{k-1}=M_2$, $S_{k+1}=M_3$인 경우</b></p>
<p>$M_2-M_1=S_{k-1}-S_k=-a_k=2$이므로 $a_k=-2$이고</p>
<p>$M_3-M_2=S_{k+1}-S_{k-1}=a_k+a_{k+1}=2$이므로 $a_{k+1}=4$이다.</p>
<p>따라서 $d=6$이다. 한편 $a_1=a_k-6(k-1)=4-6k$이고</p>
$$S_n=\frac{n\{2a_1+d(n-1)\}}{2}=\frac{n\{2(4-6k)+6(n-1)\}}{2}=n(3n-6k+1)$$
<p>$S_n>0$의 최솟값이 $13$이므로 $n=12$일 때 $3n-6k+1\le0$, 즉 $6k\ge37$이고, $n=13$일 때 $3n-6k+1>0$, 즉 $6k<40$이다. 그러나 $37\le6k<40$을 만족하는 자연수 $k$는 존재하지 않는다.</p>
<p class="case"><b>(ⅱ) $S_k=M_1$, $S_{k+1}=M_2$, $S_{k-1}=M_3$인 경우</b></p>
<p>$M_2-M_1=S_{k+1}-S_k=a_{k+1}=2$이고</p>
<p>$M_3-M_2=S_{k-1}-S_{k+1}=-a_k-a_{k+1}=2$이므로 $a_k=-4$이다.</p>
<p>따라서 $d=6$이다. 한편 $a_1=a_k-6(k-1)=2-6k$이고</p>
$$S_n=\frac{n\{2(2-6k)+6(n-1)\}}{2}=n(3n-6k-1)$$
<p>$S_n>0$의 최솟값이 $13$이므로 $n=12$일 때 $6k\ge35$, $n=13$일 때 $6k<38$이다. 그러면 $35\le6k<38$에서 $k=6$이다.</p>
<p>$\therefore d=6$, $a_1=2-6k=-34$</p>
""",
},
]

for p in PROBLEMS:
    p["prob"] = p["prob"].replace("{FIG}", FIG_DIR)
    p["sol"] = p["sol"].replace("{FIG}", FIG_DIR)
