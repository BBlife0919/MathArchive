"""검수 페이지 — DB 품질 자동 진단.

매주 한 번 열어보면 충분. CLI 명령 칠 필요 없음.
- 누락된 HWP 토큰 자동 발굴 (백슬래시 없는 영문 단어 빈도)
- 구조 무결성 검사 (BOX 짝, shadow text, code block 오인 등)
- 지난 실행과 비교 — 새로 등장한 토큰만 강조
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import auth
from auth_ui import require_auth, render_user_menu_in_sidebar
from db import get_connection as _get_db_connection

# scripts 경로 등록 — detect_bare_math_words 모듈 import
SCRIPTS_DIR = APP_DIR.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


st.set_page_config(page_title="검수 — MathArchive", page_icon="🔍", layout="wide")

require_auth()
if not auth.is_admin():
    st.error("⛔ 이 페이지는 관리자 전용입니다.")
    st.stop()

render_user_menu_in_sidebar()


# ─────────────────────────────────────────────────────────
# 캐시: 지난 실행 결과 저장 (새 토큰 비교용)
# ─────────────────────────────────────────────────────────
HISTORY_DIR = APP_DIR.parent / "output" / "audit_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _load_last_run() -> dict:
    files = sorted(HISTORY_DIR.glob("audit_*.json"), reverse=True)
    if not files:
        return {}
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_run(data: dict):
    fname = HISTORY_DIR / f"audit_{datetime.now():%Y%m%d_%H%M%S}.json"
    fname.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                     encoding="utf-8")


# ─────────────────────────────────────────────────────────
# 검사 로직
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def run_bare_word_detection(min_len: int = 3) -> list:
    """\$...\$ 안의 백슬래시 없는 영문 단어 빈도 추출."""
    from detect_bare_math_words import (
        extract_bare_words, KNOWN_TOKENS, COMMON_VARS,
    )
    conn = _get_db_connection()
    cur = conn.execute("SELECT question_text FROM questions")
    qrows = cur.fetchall()
    cur = conn.execute("SELECT solution_text FROM solutions")
    srows = cur.fetchall()

    total = Counter()
    for r in qrows:
        total.update(extract_bare_words(r[0] or "", min_len))
    for r in srows:
        total.update(extract_bare_words(r[0] or "", min_len))

    # 화이트리스트 제거
    for w in list(total.keys()):
        if w in KNOWN_TOKENS or w.lower() in KNOWN_TOKENS \
                or w.upper() in KNOWN_TOKENS:
            del total[w]
        elif w in COMMON_VARS:
            del total[w]

    return total.most_common(50)


@st.cache_data(ttl=300)
def run_structural_scan() -> dict:
    """scan_db_issues 의 핵심 검사 단순 재구현."""
    conn = _get_db_connection()
    cur = conn.execute("SELECT question_id, question_text FROM questions")
    rows = cur.fetchall()

    box_mismatch = 0
    code_block_oversight = 0
    nested_box_with_dump = 0

    for qid, txt in rows:
        if not txt:
            continue
        n_bs = txt.count("<<BOX_START>>")
        n_be = txt.count("<<BOX_END>>")
        if n_bs != n_be:
            box_mismatch += 1
        body = re.sub(r"<<BOX_START>>.*?<<BOX_END>>", "", txt, flags=re.S)
        if re.search(r"(?:^|\n)(?:\t|    )\s*\$", body):
            code_block_oversight += 1

    return {
        "box_mismatch": box_mismatch,
        "code_block_oversight": code_block_oversight,
        "total_questions": len(rows),
    }


# ─────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────
st.title("🔍 검수")
st.caption("매주 한 번 열어보면 충분. DB가 커져도 CLI 명령 칠 필요 없음.")

# 지난 실행 비교
last = _load_last_run()
last_words = {w: n for w, n in (last.get("bare_words") or [])}

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔤 누락 HWP 토큰 자동 발굴")
    st.caption("수식($...$) 안에서 백슬래시 없이 등장하는 영문 단어 — "
               "새 \\xxx 매핑 후보")

    with st.spinner("DB 전체 스캔 중..."):
        bare_words = run_bare_word_detection()

    new_words = []
    if last_words:
        for w, n in bare_words:
            if w not in last_words:
                new_words.append((w, n))

    if new_words:
        st.warning(f"⚠️ 지난 실행 이후 **새로 등장한 토큰 {len(new_words)}개**")
        for w, n in new_words[:10]:
            st.markdown(f"  - `{w}` ({n}건) — 새 매핑 검토 필요")

    st.markdown("**전체 빈도 상위 30**")

    # 표 형태로 표시
    import pandas as pd
    df = pd.DataFrame(bare_words[:30], columns=["토큰", "빈도"])
    df["상태"] = df["토큰"].apply(
        lambda w: "🆕 신규" if w not in last_words else "기존"
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🏗 구조 무결성")
    with st.spinner("검사 중..."):
        struct = run_structural_scan()

    st.metric("전체 문항", f"{struct['total_questions']:,}")
    st.metric("BOX 짝 어긋남", struct["box_mismatch"],
              delta=struct["box_mismatch"] - last.get("box_mismatch", 0),
              delta_color="inverse")
    st.metric("코드블록 오인 (탭 들여쓰기)",
              struct["code_block_oversight"],
              delta=struct["code_block_oversight"]
                    - last.get("code_block_oversight", 0),
              delta_color="inverse")

# 저장
if st.button("이번 결과 저장 (지난 실행으로 남기기)"):
    _save_run({
        "timestamp": datetime.now().isoformat(),
        "bare_words": bare_words,
        "box_mismatch": struct["box_mismatch"],
        "code_block_oversight": struct["code_block_oversight"],
    })
    st.success("저장됨. 다음 검수 때 이 결과와 비교됩니다.")
    st.rerun()

st.divider()

# ─────────────────────────────────────────────────────────
# 가이드
# ─────────────────────────────────────────────────────────
with st.expander("ℹ️ 이 페이지는 어떻게 쓰나요?"):
    st.markdown("""
**매주 1번 5분이면 충분합니다.**

1. 페이지 열면 자동으로 DB 전체 스캔 — 결과가 위에 나옴
2. **🆕 신규 토큰**이 있으면 한 번 보세요
   - 예: `prec` 30건 등장 → "아 부등호의 일종이네 → `\\prec` 매핑 추가" 라고 알려주세요
3. **구조 무결성** 숫자가 줄어들고 있는지 확인
4. 끝나면 **"이번 결과 저장"** 클릭 → 다음 주에 차이 비교 가능

**도움 필요한 경우**:
- 토큰 의미 모르겠으면 강사 또는 LLM에게 "HWP 수식편집기에서 X는 뭐야?" 질문
- 매핑 추가는 코드 수정 필요하니 매번 저에게 알려주세요
""")
