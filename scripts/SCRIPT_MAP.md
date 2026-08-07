# SCRIPT_MAP — /scripts 파일명 기반 분류

파일 내용은 읽지 않고 **파일명·날짜·버전 넘버**로만 분류했습니다.
"삭제 후보"는 "이름상 그렇게 보인다"는 의미이지, 실제 사용 여부는 사용자님 확인 필수입니다.

범례
- ⭐ 현재 표준/활성 (메모리에 명시된 것)
- 🟡 여러 버전 중 최신 하나만 남기면 됨
- 🔴 이름상 레거시/일회성으로 보임 → 삭제 후보
- ❓ 이름만으로는 판단 불가

---

## 1. 코어 파이프라인 (파싱 / DB)
- ⭐ `parse_hwpx.py` — HWPX 파서 본체
- ⭐ `build_db.py` — DB 빌드
- ⭐ `strip_review_notes.py` — 오검·벌점 메모 제거 (파서가 자동 호출)
- `strip_editorial_memo.py` — 이름 유사, 중복 여부 확인 필요 ❓
- `scan_db_issues.py` — 파서 리빌드 후 품질 스캔 (자동 리포트 룰 있음) ⭐
- `hwp2odt_no_validate.py` / `hwp2pdf.sh` / `hwp_to_hwpx.sh` — 원본 변환 유틸

## 2. 데이터 정제 / 텍스트 보정 (fix_*, normalize_*, wrap_*)
- `fix_ang_angle.py`
- `fix_db_text_tokens.py`
- `fix_dfrac_to_frac.py`
- `fix_latex_dollars.py`
- `fix_leading_indent.py`
- `fix_lim_to_inf_over.py`
- `fix_matrix_rowsep.py`
- `fix_misparsed_filename_meta.py`
- `fix_nested_boxes.py`
- `fix_subsup_spacing.py`
- `fix_sup_intfromto.py`
- `fix_unmapped_hwp_tokens.py`
- `wrap_hangul_math.py`
- `normalize_chapters_2026_04_26.py` 🔴 (날짜 박힌 일회성)
- `normalize_chapters_subjects.py`
- `normalize_unicode.py`
- `repair_box_mismatch.py`
- `dedupe_questions.py` / `dedupe_same_question.py` 🟡 (둘 중 하나만?)
- `enhance_source_text.py`
- `audit_latex_dollars.py`
- `detect_bare_math_words.py`
- `detect_composite_images.py`

→ 대부분 일회성 보정 스크립트. 이미 DB에 반영됐다면 다수 삭제 가능. 다만 파서 리빌드 시 다시 필요할 수 있으니 사용자님 판단 필수.

## 3. 교재 제작 — 활성 (2026 표준)
- ⭐ `build_pyeongjwapyo_by_difficulty.py` — **표준 교재 템플릿** (다음 교재는 전부 이 포맷)

## 4. 교재 제작 — 개별 교재 빌더
### 정단원(중단원 정리)
- `build_jungdan_book.py` 🔴 (v2/v4 존재)
- `build_jungdan_book4.py` 🟡 (최신?)
- `build_jungdan_eval.py`
- `build_jungdan_quick_answer.py`
- `build_jungdan_solutions.py`
- `build_jungdan_v2.py` 🔴
- `extract_jungdan_problems.py`
- `extract_jungdan_solutions.py`
- `merge_jungdan_book.py`

### 커널 포인트
- `build_kernel_book4.py`
- `build_kernel_point_book.py`
- `build_kernel_quick_answer.py`
- `extract_kernel_problems.py`
- `merge_kernel_book.py`

### 대수 (학교별/최종본)
- `build_daesu_school_books.py`
- `make_daesu_final.py`
- `merge_daesu_kernel.py`

### 공수 1
- `build_gongsu1_by_difficulty.py`
- `build_gongsu1_kernel_book.py`

### 광북 / 광명 / 명문
- `build_gwangbuk_book.py`
- `build_gwangbuk_modu2.py`
- `build_gwangmyeong_g1_book.py`
- `build_myongmoon_book.py`

### 서밋 포인트
- `renumber_summit.py`
- `merge_summit_book.py`
- `add_summit_ui.py` ❓

### 베이직 / 기타
- `build_basic_point_final.py`
- `build_book.py` 🔴 (초창기?)
- `build_2col_problems.py`
- `build_quick_answer.py`
- `build_font_compare.py` 🔴 (샘플?)
- `font_sampler.py` 🔴

### PPT/기타 매체
- `build_memory_psych_ppt.py` 🔴 (다른 프로젝트?)
- `build_og_thumbnail.py` 🔴 (랜딩용 1회)

## 5. 표지 / 구분자 (make_*_cover / make_*_dividers)
- `make_cover.py` 🔴 (초창기?)
- `make_cover_basic_point.py`
- `make_chapter_pages.py`
- `make_choisimwha_cover.py` / `..._vol2.py`
- `make_daesu_kernel_cover.py` / `..._dividers.py`
- `make_gwangbuk_cover.py`
- `make_gwangbuk_modu2_cover.py` / `..._dividers.py`
- `make_jungdan_cover.py` / `..._dividers.py`
- `make_kernel_dividers.py`
- `make_kernel_point_cover.py`
- `make_myongmoon_cover.py` / `..._dividers.py`
- `make_summit_point_cover.py` / `..._dividers.py`

→ 교재 4번 항목과 짝. 그 교재가 종료되면 표지/구분자도 같이 정리 대상.

## 6. 적중분석 리포트
- 🔴 `build_pirate_analysis.py` (v1)
- 🔴 `build_pirate_v2.py`
- 🔴 `build_pirate_v3.py`
- 🔴 `build_school_report_v4.py`
- ⭐ `build_school_report_v5.py` — **현재 표준 (v5)**
- `build_consolidated_report.py` ❓
- `build_unified_vision_report.py` ❓
- `merge_school_configs.py`
- `sync_key_problems_from_db.py`
- `pirate_2026_report/` (폴더) — ⭐ **신규 2026 워크플로우**
  - `build.py`, `build_g2.py`, `build_m3.py`, `label_overlay.py`, `blur_copyright.py`

→ v1~v4 는 이름상 완전 레거시. v5 및 pirate_2026_report/ 만 유지 후보.

## 7. 클리닉 / 학생 카드 / 데모
- `build_clinic_sample.py`
- `render_student_card_pdf.py`
- `render_demo_report.py`
- `seed_demo_student.py`
- `build_student_templates.py`
- `build_curriculum_map.py`

## 8. 유형 분류 / NGD 분석
- `classify_types.py`
- `label_problem_types.py`
- `cluster_types.py` / `cluster_clip.py`
- `select_diverse.py` / `select_problems.py`
- `reconcile_classifications.py`
- `extract_chapter_keywords.py`
- `extract_problems.py`
- `ngd_analysis/` (폴더) — NGD 라벨링 실험
  - `build_bundle.py`, `build_study_book.py`, `consensus.py`, `make_book.py`, `match_db_per_type.py`, `parse_pdfs.py`, `*.json`

→ "클리닉 알고리즘 의존 금지" 메모 기준, 상당수가 실험/미사용 상태로 보임. 사용자님 판단 필수.

## 9. 교과서 매칭 (textbook_match/)
- `match.py` 🔴 / `match_v2.py` 🔴
- `v3_*` 🔴 (build_grids, build_report, index_textbooks, match, render_exam)
- `v4_build_report.py` 🔴 / `v4_build_report_11.py` 🔴
- `v5_*` 🟡 (build_grids, build_report, extract_exam, index_new_tb, match)
- `build_match_grids.py` / `build_report.py` / `build_report_visual.py`
- `clip_match.py`
- `crop_all_textbook.py` / `crop_textbook.py`
- `ocr_gmun.py` / `ocr_textbook_crops.py`
- `parse_gmun_ocr.py` / `parse_textbooks.py`
- `render_exam_images.py`

→ v1~v4 는 이름상 레거시. v5 만 남기는 게 자연스러워 보임.

## 10. 이미지 처리
- `blur_faces.py` / `blur_persons.py`
- `clean_capture_metadata.py`
- `crop_problems.py`
- `index_textbook_captures.py`
- `pdf_to_images.py`
- `strip_meta_from_captures.py`
- `make_pdf_viewer_safe.py` ⭐ (PDF quarantine 함정 메모 관련)

## 11. 마이그레이션 (migrate_*)
- `migrate_auth_schema.py`
- `migrate_clinic_external.py`
- `migrate_clinic_schema.py`
- `migrate_clinic_v3.py`
- `migrate_images_to_r2.py`
- `migrate_kakao_queue.py`
- `migrate_prism_assessment.py`
- `migrate_student_assessment.py`
- `migrate_student_card_v1.py`
- `migrate_to_supabase.py` 🔴 (Supabase 미사용 메모)

→ 마이그레이션은 대개 1회 실행 후 불필요. 스키마 히스토리로만 참고할지 결정 필요.

## 12. 인증 / 배포 / 알림
- `auth_schema.sql`
- `make_admin.py`
- `send_kakao_notify.py`
- `sync_new_to_cloud.py` / `sync_new_to_cloud_v2.py` 🟡
- `sync_missing_children.py`
- `r2_parallel_finish.py` 🔴 (R2 이전 관련 1회?)

## 13. 학부모 문자 (parent_sms_image/)
- ⭐ `build.py` / `build_txt.py` — **매 시험 재사용 워크플로우**

## 14. 탑반 교재 (top_class_reference/)
- `build_jikseon_v2.py` 🟡
- `build_jikseon_workbook.py`
- `finalize_jikseon_v2.py`

## 15. 기타 / 검증 / 라이브러리
- `validate_equations.py`
- `inspect_pdf.py`
- `lib_deliver.py`
- `CLAUDE.md` (스크립트 폴더 자체 지침)

---

## 삭제 후보 요약 (사용자 확인 필수)

**높은 확신도 (버전 넘버로 상위 존재):**
- `build_pirate_analysis.py`, `build_pirate_v2.py`, `build_pirate_v3.py`, `build_school_report_v4.py` → v5 존재
- `textbook_match/match.py`, `match_v2.py`, `v3_*`, `v4_*` → v5 존재
- `build_jungdan_book.py`, `build_jungdan_v2.py` → book4 존재
- `sync_new_to_cloud.py` → v2 존재
- `migrate_to_supabase.py` (Supabase 미사용)

**중간 확신도 (날짜/1회성 냄새):**
- `normalize_chapters_2026_04_26.py`
- `build_memory_psych_ppt.py`, `build_og_thumbnail.py`, `build_book.py`
- `make_cover.py` (교재별 커버가 따로 있음)
- `build_font_compare.py`, `font_sampler.py`
- `r2_parallel_finish.py`
- `ngd_analysis/*.json` (실험 산출물)

**중복 의심 (둘 중 하나만):**
- `dedupe_questions.py` vs `dedupe_same_question.py`
- `strip_editorial_memo.py` vs `strip_review_notes.py` (활성)

**대량 정리 대상 (사용자님 판단 필요):**
- `fix_*.py` 다수 — DB 반영 완료된 것은 삭제 가능
- `migrate_*.py` — 1회 실행 완료된 것
- 종료된 교재의 build/make/extract/merge 3~4종 세트
