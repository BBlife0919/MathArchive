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
    questions = [QUESTION]
    exam_pdf = pe.generate_exam_pdf(
        questions,
        title="구조변형 연습문항",
        subtitle="공통수학2 · 평면좌표~도형의 이동 · 대칭이동+두 점 사이 거리",
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
