"""KERNEL POINT 빠른정답 — src p85~p93 임베드 + 라벨 SB 어그로 주황 덮어쓰기.

첫 페이지(p85)는 좌측 컬럼만 y=134부터 시프트 임베드 (박스 영역 스킵).
라벨이 "N. ANS" 한 span 이면 답을 라벨 우측에 별도 임베드 (간격 확보).
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

from extract_kernel_problems import SRC_PDF, OUT_DIR, QUICK_ANSWER_PAGES

OUT_PDF = OUT_DIR / "quick_answer.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
_cafe = fitz.Font(fontfile=FONT_CAFE24)
_aggro = fitz.Font(fontfile=FONT_AGGRO)

NAVY = (15/255, 25/255, 50/255)
ORANGE = (240/255, 125/255, 35/255)
GREY_LIGHT = (200/255, 205/255, 220/255)

PAGE_W = 595.0
PAGE_H = 842.0
LEFT_MARGIN = 28
RIGHT_MARGIN = 28
HEADER_Y = 38
HEADER_LINE_Y = 42

# src 본문 영역 (머리말/꼬리말 제외)
SRC_BODY_TOP = 56.0
SRC_BODY_BOT = 795.0
SRC_BODY_L = 18.0
SRC_BODY_MID = 300.0   # 좌/우 컬럼 분리 x
SRC_BODY_R = 578.0

# p85 좌측 컬럼 첫 라벨 y (박스 영역 스킵을 위한 시프트 시작)
P0_LEFT_TOP = 130.0


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_header(page):
    text_at(page, LEFT_MARGIN, HEADER_Y,
            "KERNEL POINT · A N S W E R   K E Y",
            "aggro", FONT_AGGRO, 8, NAVY)
    right = "정답 및 해설"
    tw = _cafe.text_length(right, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y),
                   (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def find_ans_labels(page) -> list[dict]:
    """빠른정답 페이지 'N.' 라벨 검출.

    반환: [{rect, n, prefix_len, t}]. prefix_len = "N. " 글자 수 (자릿수+2).
    """
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                fnt = sp["font"]
                sz = sp["size"]
                t = sp["text"]
                if "Haansoft" not in fnt:
                    continue
                if not (9.0 <= sz <= 11.0):
                    continue
                m = re.match(r"^(\d+)\.\s*", t)
                if not m:
                    continue
                bb = sp["bbox"]
                if not (35 < bb[0] < 70 or 300 < bb[0] < 335):
                    continue
                n = int(m.group(1))
                if not (1 <= n <= 400):
                    continue
                prefix = m.group(0)
                rest = t[len(prefix):].strip()
                out.append({
                    "rect": fitz.Rect(*bb),
                    "n": n,
                    "digits": len(m.group(1)),
                    "rest_text": rest,
                    "span_text": t,
                    "is_left": bb[0] < 200,
                })
    return out


def main():
    src = fitz.open(str(SRC_PDF))
    out = fitz.open()

    # dest 영역 (페이지 본문 영역)
    dest_top = 60
    dest_bot = PAGE_H - 36
    dest_h = dest_bot - dest_top
    dest_l = LEFT_MARGIN
    dest_r = PAGE_W - RIGHT_MARGIN

    # src 전체 폭 fit 시 scale (좌/우 컬럼 같은 scale 유지)
    src_w_full = SRC_BODY_R - SRC_BODY_L
    src_h_full = SRC_BODY_BOT - SRC_BODY_TOP
    scale = min((dest_r - dest_l) / src_w_full, dest_h / src_h_full)
    tw_full = src_w_full * scale
    th_full = src_h_full * scale
    tx_full = (PAGE_W - tw_full) / 2
    ty_full = dest_top

    # 좌측/우측 컬럼 dest 영역
    # 정상 페이지: 좌측 = src (SRC_BODY_L ~ SRC_BODY_MID), 우측 = (SRC_BODY_MID ~ SRC_BODY_R)
    L_src_w = SRC_BODY_MID - SRC_BODY_L
    R_src_w = SRC_BODY_R - SRC_BODY_MID
    L_dest_w = L_src_w * scale
    R_dest_w = R_src_w * scale
    L_dest_x = tx_full
    R_dest_x = tx_full + L_dest_w

    for idx, src_pg in enumerate(QUICK_ANSWER_PAGES):
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        draw_header(page)

        if idx == 0:
            # 좌측 컬럼: y=P0_LEFT_TOP 부터 시프트 임베드 (박스 영역 스킵)
            L_src_top = P0_LEFT_TOP
            L_src_h = SRC_BODY_BOT - L_src_top
            L_th = L_src_h * scale
            page.show_pdf_page(
                fitz.Rect(L_dest_x, dest_top, L_dest_x + L_dest_w, dest_top + L_th),
                src, src_pg,
                clip=fitz.Rect(SRC_BODY_L, L_src_top, SRC_BODY_MID, SRC_BODY_BOT),
            )
            # 우측 컬럼: 정상 임베드
            R_src_top = SRC_BODY_TOP
            R_src_h = SRC_BODY_BOT - R_src_top
            R_th = R_src_h * scale
            page.show_pdf_page(
                fitz.Rect(R_dest_x, dest_top, R_dest_x + R_dest_w, dest_top + R_th),
                src, src_pg,
                clip=fitz.Rect(SRC_BODY_MID, R_src_top, SRC_BODY_R, SRC_BODY_BOT),
            )
        else:
            # 통째 임베드
            page.show_pdf_page(
                fitz.Rect(tx_full, ty_full, tx_full + tw_full, ty_full + th_full),
                src, src_pg,
                clip=fitz.Rect(SRC_BODY_L, SRC_BODY_TOP, SRC_BODY_R, SRC_BODY_BOT),
            )

        # 라벨 검출 → 마스킹 + 새 라벨 + (필요 시) 답 별도 임베드
        labels = find_ans_labels(src[src_pg])
        for lab in labels:
            rect = lab["rect"]
            n = lab["n"]
            digits = lab["digits"]
            rest = lab["rest_text"]
            is_left = lab["is_left"]

            # src → dest 변환
            if idx == 0 and is_left:
                # 좌측 시프트
                src_top_used = P0_LEFT_TOP
                src_x_origin = SRC_BODY_L
                dest_x_origin = L_dest_x
                dest_y_origin = dest_top
            elif idx == 0 and not is_left:
                src_top_used = SRC_BODY_TOP
                src_x_origin = SRC_BODY_MID
                dest_x_origin = R_dest_x
                dest_y_origin = dest_top
            else:
                src_top_used = SRC_BODY_TOP
                src_x_origin = SRC_BODY_L
                dest_x_origin = tx_full
                dest_y_origin = ty_full

            # 클립 밖 라벨 스킵
            if rect.y0 < src_top_used:
                continue

            dx0 = dest_x_origin + (rect.x0 - src_x_origin) * scale
            dy0 = dest_y_origin + (rect.y0 - src_top_used) * scale
            dx1 = dest_x_origin + (rect.x1 - src_x_origin) * scale
            dy1 = dest_y_origin + (rect.y1 - src_top_used) * scale

            # prefix src 폭 = 자릿수 * 4.5 + 5 (대략, Haansoft 9.8pt)
            prefix_w_src = digits * 4.5 + 5.0
            ans_src_x0 = rect.x0 + prefix_w_src
            ans_src_x1 = rect.x1

            # 새 라벨 폰트 7pt
            label_text = f"{n:03d}"
            new_size = 7.0
            new_label_w = _aggro.text_length(label_text, fontsize=new_size)
            GAP = 4.0
            baseline = dy1 - 0.18 * new_size

            if rest:
                # 라벨 + 답 한 span → 전체 가림 + 답 별도 임베드
                page.draw_rect(
                    fitz.Rect(dx0 - 0.5, dy0 - 0.5, dx1 + 0.5, dy1 + 0.5),
                    color=(1, 1, 1), fill=(1, 1, 1), overlay=True,
                )
                # 새 라벨
                page.insert_text((dx0, baseline), label_text,
                                 fontname="aggro", fontfile=FONT_AGGRO,
                                 fontsize=new_size, color=ORANGE)
                # 답 별도 임베드 (라벨 우측 + gap)
                ans_w = (ans_src_x1 - ans_src_x0) * scale
                ans_h = (rect.y1 - rect.y0) * scale
                ans_dx = dx0 + new_label_w + GAP
                ans_dy = dy0
                if ans_w > 0:
                    page.show_pdf_page(
                        fitz.Rect(ans_dx, ans_dy, ans_dx + ans_w, ans_dy + ans_h),
                        src, src_pg,
                        clip=fitz.Rect(ans_src_x0, rect.y0, ans_src_x1, rect.y1),
                    )
            else:
                # 라벨 only span → 라벨 영역만 가림 + 새 라벨 (답은 별도 span으로 보임)
                page.draw_rect(
                    fitz.Rect(dx0 - 0.5, dy0 - 0.5, dx1 + 0.5, dy1 + 0.5),
                    color=(1, 1, 1), fill=(1, 1, 1), overlay=True,
                )
                page.insert_text((dx0, baseline), label_text,
                                 fontname="aggro", fontfile=FONT_AGGRO,
                                 fontsize=new_size, color=ORANGE)

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n = len(out)
    out.close()
    src.close()
    print(f"[OK] {OUT_PDF}  ({n} pages)")


if __name__ == "__main__":
    main()
