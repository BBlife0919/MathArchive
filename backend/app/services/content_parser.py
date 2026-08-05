"""문제 본문 텍스트 → 프론트 렌더용 세그먼트 리스트 변환.

app/main.py 의 `render_question_content()`/`_render_image()` 파싱 로직을
그대로 포팅한다 (정규식·분기 100% 동일 유지 — 계획서 "B등급" 항목).
차이점은 `st.markdown()`/`st.image()`/`st.container()` 호출 대신
세그먼트 dict 를 만들어 리스트에 쌓는 것뿐이다.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

from .. import legacy_bridge  # noqa: F401

import main as legacy_main  # type: ignore  (재사용: _flatten_grid_box, _ensure_line_breaks, _safe_image_url, IMAGE_DIR)

try:
    from pdf_engine import _normalize_math_text  # type: ignore
except Exception:  # pragma: no cover
    def _normalize_math_text(text):
        return text

IMAGE_DIR: Path = legacy_main.IMAGE_DIR
_IMG_TOKEN_RE = re.compile(r"<<IMG:(image\d+)>>")


def _resolve_image_url(image_ref: str, file_stem: str, img_map: dict,
                       static_base_url: str) -> str | None:
    """main.py:_render_image() 의 URL 판정 로직 그대로 (st.* 호출만 URL 반환으로 치환)."""
    src = (img_map or {}).get(image_ref)
    if src and src.startswith("http"):
        return legacy_main._safe_image_url(src)
    if src:
        p = Path(src)
        if p.exists():
            return f"{static_base_url}/{quote(p.name)}"

    if file_stem and IMAGE_DIR.exists():
        for f in IMAGE_DIR.iterdir():
            if image_ref in f.name and file_stem in f.name:
                return f"{static_base_url}/{quote(f.name)}"
        for f in IMAGE_DIR.iterdir():
            if f.stem == image_ref or image_ref in f.name:
                return f"{static_base_url}/{quote(f.name)}"
    return None


def parse_question_content(text: str, file_source: str = "",
                           img_map: dict | None = None,
                           static_base_url: str = "/static/images") -> list[dict]:
    """render_question_content() 와 동일한 파싱 결과를 세그먼트 리스트로 반환.

    반환 세그먼트 타입:
    - {"type": "text", "md": str}
    - {"type": "box", "md": str}
    - {"type": "image", "url": str}
    - {"type": "image", "ref": str, "url": None}  (파일을 못 찾은 경우)
    """
    if text is None:
        return []
    try:
        text = _normalize_math_text(text)
    except Exception:
        pass
    text = re.sub(r"\n{3,}", "\n\n", text)

    file_stem = Path(file_source).stem if file_source else ""
    img_map = img_map or {}

    parts = re.split(r"(<<BOX_START>>|<<BOX_END>>|<<IMG:image\d+>>)", text)

    segments: list[dict] = []
    in_box = False
    box_content: list[str] = []

    for part in parts:
        if part == "<<BOX_START>>":
            in_box = True
            box_content = []
            continue
        elif part == "<<BOX_END>>":
            in_box = False
            content = "".join(box_content).strip()
            if content:
                lines = [ln.lstrip() for ln in content.split("\n")]
                content = "\n".join(lines)
                content = legacy_main._flatten_grid_box(content)
                segments.append({"type": "box", "md": content})
            continue

        m = _IMG_TOKEN_RE.match(part)
        if m:
            ref = m.group(1)
            url = _resolve_image_url(ref, file_stem, img_map, static_base_url)
            segments.append({"type": "image", "ref": ref, "url": url})
            continue

        if in_box:
            box_content.append(part)
        else:
            stripped = part.strip()
            if stripped:
                stripped = legacy_main._ensure_line_breaks(stripped)
                segments.append({"type": "text", "md": stripped})

    return segments
