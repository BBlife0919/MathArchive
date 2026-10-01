#!/usr/bin/env python3
"""단발성 유사(구조변형)문항 1개를 2단 레이아웃 PDF로 출력.

app/pdf_engine.py 의 generate_exam_pdf()가 기본으로 "최대 2열" 페이지를
짜는 엔진(paginate())을 그대로 쓰므로 별도 레이아웃 코드가 필요없다.
출력: 문제 페이지(2단) + 정답/해설 페이지.

usage: python3 scripts/build_variant_problem_pdf.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

import fitz  # noqa: E402
import pdf_engine as pe  # noqa: E402

QUESTION = dict(
    question_id=1,
    file_source="구조변형_원점대칭탈피_1",
    school=None, grade=1, year=2026, semester=2, exam_type="a",
    subject="공수2",
    question_number=1,
    question_text=(
        r"이차함수 $f(x)=x^2+ax+b$의 그래프를 $x$축에 대하여 대칭이동한 후 "
        r"$x$축의 방향으로 $3$만큼 평행이동한 그래프를 나타내는 함수를 $g(x)$라 "
        r"하자. 두 함수 $y=f(x)$, $y=g(x)$의 그래프가 서로 다른 두 점 P, Q에서 "
        r"만난다. 선분 PQ의 중점이 점 $(1,0)$이고 $\overline{PQ}=2\sqrt{10}$일 "
        r"때, $a-b$의 값은? (단, $a,b$는 상수이다.) [4.0점]"
    ),
    choices=[
        {"number": 1, "text": "$2$"},
        {"number": 2, "text": "$3$"},
        {"number": 3, "text": "$4$"},
        {"number": 4, "text": "$5$"},
        {"number": 5, "text": "$6$"},
    ],
    answer="3",
    answer_type="choice",
    is_subjective=0,
    points=4.0,
    chapter="도형의 이동",
    difficulty="상",
    has_image=0,
    images={},
    solution_text=(
        r"$g(x)$는 $y=f(x)$의 그래프를 $x$축에 대하여 대칭이동($y=-f(x)$)한 후 "
        r"$x$축의 방향으로 $3$만큼 평행이동한 것이므로 $g(x)=-f(x-3)$이다.<br>"
        r"$f(x)=x^2+ax+b$이므로 $g(x)=-\{(x-3)^2+a(x-3)+b\}=-x^2+(6-a)x+(3a-9-b)$"
        r"이다.<br>"
        r"$f(x)=g(x)$를 정리하면 $2x^2+(2a-6)x+(2b-3a+9)=0$이다.<br>"
        r"두 교점 P$(x_1,y_1)$, Q$(x_2,y_2)$의 $x$좌표 $x_1,x_2$는 이 방정식의 두 "
        r"근이므로 근과 계수의 관계에 의해 $x_1+x_2=3-a$, "
        r"$x_1x_2=\dfrac{2b-3a+9}{2}$이다.<br>"
        r"$y_1+y_2=f(x_1)+f(x_2)=(x_1^2+x_2^2)+a(x_1+x_2)+2b$이고 "
        r"$x_1^2+x_2^2=(x_1+x_2)^2-2x_1x_2$이므로 대입해 정리하면 $a,b$에 관계없이 "
        r"$y_1+y_2=0$이 항상 성립한다. 즉 선분 PQ의 중점은 항상 $x$축 위에 있다.<br>"
        r"중점의 좌표가 $(1,0)$이므로 $x_1+x_2=2$이고, $x_1+x_2=3-a=2$에서 $a=1$"
        r"이다.<br>"
        r"$y_1-y_2=f(x_1)-f(x_2)=(x_1-x_2)(x_1+x_2+a)=3(x_1-x_2)$이므로 "
        r"$\overline{PQ}^2=(x_1-x_2)^2+(y_1-y_2)^2=10(x_1-x_2)^2$이다.<br>"
        r"$\overline{PQ}=2\sqrt{10}$이므로 $\overline{PQ}^2=40$에서 $(x_1-x_2)^2=4$"
        r"이다.<br>"
        r"$(x_1-x_2)^2=(x_1+x_2)^2-4x_1x_2=4-4x_1x_2=4$이므로 $x_1x_2=0$이다.<br>"
        r"$x_1x_2=\dfrac{2b-3+9}{2}=b+3=0$이므로 $b=-3$이다.<br>"
        r"따라서 $a-b=1-(-3)=4$이다."
    ),
    images_sol={},
)

QUESTION2 = dict(
    question_id=2,
    file_source="구조변형_원점대칭탈피_2",
    school=None, grade=1, year=2026, semester=2, exam_type="a",
    subject="공수2",
    question_number=2,
    question_text=(
        r"원 $C_1:x^2+y^2=25$를 $x$축의 방향으로 $a$, $y$축의 방향으로 $b$"
        r" ($a>0$, $b>0$)만큼 평행이동한 원을 $C_2$라 하자. 두 원의 중심을 "
        r"잇는 선분의 기울기가 $\dfrac34$이고, 두 원 $C_1$, $C_2$가 서로 다른 "
        r"두 점에서 만나 그 두 점 사이의 거리가 $5\sqrt3$일 때, $a+b$의 값은? "
        r"(단, $a,b$는 양수이다.) [4.0점]"
    ),
    choices=[
        {"number": 1, "text": "$5$"},
        {"number": 2, "text": "$6$"},
        {"number": 3, "text": "$7$"},
        {"number": 4, "text": "$8$"},
        {"number": 5, "text": "$9$"},
    ],
    answer="3",
    answer_type="choice",
    is_subjective=0,
    points=4.0,
    chapter="원의 방정식",
    difficulty="중",
    has_image=0,
    images={},
    solution_text=(
        r"$C_1$의 중심은 $O(0,0)$, 반지름은 $5$이고, $C_2$는 $C_1$을 평행이동한 "
        r"것이므로 반지름은 똑같이 $5$이고 중심은 $O'(a,b)$이다.<br>"
        r"두 원의 반지름이 같으므로 공통현(두 교점을 잇는 선분)은 두 중심을 잇는 "
        r"선분 $\overline{OO'}$의 수직이등분선 위에 있고, 공통현의 중점을 M이라 "
        r"하면 $\overline{OM}=\overline{O'M}=\dfrac12\overline{OO'}$이다.<br>"
        r"직각삼각형에서 $\overline{OM}^2=5^2-\left(\dfrac{5\sqrt3}{2}\right)^2"
        r"=25-\dfrac{75}{4}=\dfrac{25}{4}$이므로 $\overline{OM}=\dfrac52$이고, "
        r"$\overline{OO'}=2\overline{OM}=5$이다.<br>"
        r"중심을 잇는 선분의 기울기가 $\dfrac34$이므로 $b=\dfrac34a$이고, "
        r"$\overline{OO'}=\sqrt{a^2+b^2}=\sqrt{a^2+\dfrac9{16}a^2}=\dfrac54a=5$"
        r"에서 $a=4$이다.<br>"
        r"$b=\dfrac34\times4=3$이므로 $a+b=4+3=7$이다."
    ),
    images_sol={},
)

QUESTION3 = dict(
    question_id=3,
    file_source="구조변형_원점대칭탈피_3",
    school=None, grade=1, year=2026, semester=2, exam_type="a",
    subject="공수2",
    question_number=3,
    question_text=(
        r"좌표평면 위의 세 점 $\mathrm{A}(2,10)$, $\mathrm{B}(1,1)$, "
        r"$\mathrm{C}(9,5)$에 대하여 선분 BC의 중점을 D라 하자. 점 A를 점 D에 "
        r"대하여 대칭이동한 점을 E라 할 때, 사각형 ABEC의 넓이는? [4.0점]"
    ),
    choices=[
        {"number": 1, "text": "$60$"},
        {"number": 2, "text": "$64$"},
        {"number": 3, "text": "$68$"},
        {"number": 4, "text": "$72$"},
        {"number": 5, "text": "$76$"},
    ],
    answer="3",
    answer_type="choice",
    is_subjective=0,
    points=4.0,
    chapter="도형의 이동",
    difficulty="중",
    has_image=0,
    images={},
    solution_text=(
        r"점 D는 선분 BC의 중점이므로 $D=\left(\dfrac{1+9}2,\dfrac{1+5}2\right)"
        r"=(5,3)$이다.<br>"
        r"점 A를 점 D에 대하여 대칭이동한 점 E는 D가 선분 AE의 중점이 되도록 "
        r"하는 점이므로 $E=(2\times5-2,\,2\times3-10)=(8,-4)$이다.<br>"
        r"점 D에 대한 대칭이동은 길이를 보존하는 변환이고, D가 선분 BC의 중점"
        r"이므로 이 변환에서 점 A는 E로, 점 B는 C로, 점 C는 B로 옮겨진다. 즉 "
        r"삼각형 ABC 전체가 삼각형 ECB로 옮겨지므로 두 삼각형은 합동이고 넓이가 "
        r"서로 같다. 따라서 사각형 ABEC의 넓이는 삼각형 ABC 넓이의 $2$배이다."
        r"<br>"
        r"직선 BC의 방정식은 기울기가 $\dfrac{5-1}{9-1}=\dfrac12$이므로 "
        r"$y-1=\dfrac12(x-1)$, 즉 $x-2y+1=0$이다.<br>"
        r"$\overline{BC}=\sqrt{(9-1)^2+(5-1)^2}=\sqrt{64+16}=4\sqrt5$이고, 점 "
        r"A와 직선 BC 사이의 거리는 $\dfrac{|2-20+1|}{\sqrt{1^2+(-2)^2}}"
        r"=\dfrac{17}{\sqrt5}$이다.<br>"
        r"삼각형 ABC의 넓이는 $\dfrac12\times4\sqrt5\times\dfrac{17}{\sqrt5}"
        r"=\dfrac12\times4\times17=34$이다.<br>"
        r"따라서 사각형 ABEC의 넓이는 $34\times2=68$이다."
    ),
    images_sol={},
)


def render_answer_key_html(questions: list[dict]) -> str:
    qa = pe._render_quick_answer_table(questions, cols=4)
    sol = pe._render_solution_items(questions, include_source=False)
    body = (
        '<section class="page qa-page">'
        '<h2 class="section-title">빠른 정답</h2>' + qa + '</section>'
        '<section class="page sol-page">'
        '<h2 class="section-title">정답 및 해설</h2>' + sol + '</section>'
    )
    return pe._HTML_WRAP.format(
        title="정답 및 해설", css=pe._CSS, body=body,
        body_class="", postprocess_script=pe._PREVIEW_POSTPROCESS_JS,
    )


def main():
    questions = [QUESTION, QUESTION2, QUESTION3]
    exam_pdf = pe.generate_exam_pdf(
        questions,
        title="구조변형 연습문항",
        subtitle="공통수학2 · 평면좌표~도형의 이동 · 구조변형 3종(함수 대칭·원 공통현·점대칭 넓이)",
        include_source=False,
    )
    key_html = render_answer_key_html(questions)
    key_pdf = pe.html_to_pdf_bytes(key_html)

    book = fitz.open(stream=exam_pdf, filetype="pdf")
    book.insert_pdf(fitz.open(stream=key_pdf, filetype="pdf"))
    out_bytes = book.tobytes()
    book.close()

    out_path = Path.home() / "클로드교재" / "구조변형 연습문항 (원점대칭탈피).pdf"
    out_path.write_bytes(out_bytes)
    import subprocess
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"[OK] {out_path} ({out_path.stat().st_size/1024:.0f}KB)")


if __name__ == "__main__":
    main()
