# JSON_MAP — /output JSON 파일 분류

총 **111개** JSON. 각 파일 상위 ~300바이트만 봐서 용도만 판단했습니다.
전체 내용은 읽지 않았으므로 삭제 결정 전 사용자님 확인 필수.

범례
- ⭐ 현재 사용 중 (활성 워크플로우 산출물)
- 🟡 최신 버전 하나만 남기면 됨
- 🔴 이름·버전상 레거시로 보임 → 삭제 후보
- ❓ 이름만으로는 판단 불가

---

## 1. 루트 / (일회성 감사 산출물)
| 파일 | 크기 | 내용 | 판정 |
|---|---|---|---|
| `hangul_math_review.json` | 1.4MB | before/after 텍스트 diff (한글수식 감싸기 검토) | 🔴 일회성 감사 결과 |
| `hangul_math_backup.json` | 1.4MB | 위 작업의 백업본 | 🔴 백업, 이미 반영됐다면 폐기 |
| `composite_image_qids.json` | 78B | qid 배열 (합성이미지 대상) | 🔴 일회 태깅 결과 |

## 2. 교재 빌드 산출물 (build_*_book.py 부산물)
| 파일 | 크기 | 내용 | 판정 |
|---|---|---|---|
| `jungdan_eval_2_2/problems_page_breaks.json` | 35B | 페이지 분할 인덱스 | 교재 종료 시 폐기 |
| `jungdan_eval_2_2/problems_meta.json` | 87KB | 문제 클립 좌표·라벨 | 교재 종료 시 폐기 |
| `jungdan_eval_2_2/solutions_meta.json` | 87KB | 해설 클립 좌표 | 교재 종료 시 폐기 |
| `kernel_point/problems_page_breaks.json` | 17B | 위와 동일 형태 | 교재 종료 시 폐기 |
| `kernel_point/problems_meta.json` | 149KB | 문제 클립 메타 | 교재 종료 시 폐기 |
| `summit_point/problems_meta.json` | 63KB | 문제 클립 메타 | 교재 종료 시 폐기 |

→ 이 셋은 이미 배포된 교재 산출물. 재빌드가 없다면 정리 대상.

## 3. textbook_match/ (v1 - 교과서 매칭 초기 실험)
| 파일 | 크기 | 내용 | 판정 |
|---|---|---|---|
| `textbooks_index.json` | 452KB | 교과서(수특 등) 전체 문제 인덱스 | ❓ v5에서 재사용? |
| `textbook_ocr_index.json` | 272KB | 교과서 OCR 결과 인덱스 | ❓ |
| `matches.json` | 213KB | v1 매칭 결과 | 🔴 v5 존재 |
| `matches_v2.json` | 638KB | v2 매칭 결과 | 🔴 v5 존재 |
| `clip_matches.json` | 285KB | CLIP 임베딩 매칭 결과 | 🔴 |
| `visual_matches_광명고.json` (외 광명북고·광문고) | 3~4KB | 학교별 시각 매칭 verdict | 🔴 |
| `agent_input/{학교}.json` (3개) | 90KB대 | 에이전트 입력 (Q+후보) | 🔴 |
| `gmun_ocr/ocr_raw.json` | 5KB | 광문고 OCR 원본 | 🔴 |
| `parsed/{학교}.json`, `{학교}_pdf.json`, `{학교}_ocr.json` (6개) | 4~20KB | 시험지 파싱 결과 | 🔴 |

→ 전부 v3/v4/v5 워크플로우로 대체됨. **폴더 통째로 삭제 후보 (단, textbooks_index.json / textbook_ocr_index.json 은 v5가 참조하는지 확인 필요).**

## 4. textbook_match_v3/ (레거시)
| 파일 | 크기 | 판정 |
|---|---|---|
| `visual_matches_{4개 학교}.json` | 3~5KB | 🔴 |
| `final_verdicts.json` | 62KB | 🔴 |
| `text_candidates.json` | 1.27MB | 🔴 |
| `exam_input/{4개 학교}.json` | ~20KB | 🔴 |
| `pages_ocr/{교재}/pages.json` × **26개** | 20KB대 | ❓ **v5가 이 페이지 OCR을 참조**할 가능성 있음 (v5 tb_crop_tasks 안에 `pages_png/{tb_key}/` 경로 언급) |

→ pages_ocr/ 를 뺀 나머지는 v5로 대체됨. **v5 스크립트가 v3/pages_ocr/ 을 재활용하는지만 확인 후 대량 삭제 가능.**

## 5. textbook_match_v4/ (레거시)
| 파일 | 크기 | 판정 |
|---|---|---|
| `tb_bboxes_광명고.json` (외 광명북·광문·명문) | 1~3KB | 🔴 v5 존재 |
| `tb_bboxes_all.json` / `tb_bboxes_fixed.json` | ~8KB | 🔴 |
| `{학교}_bboxes.json` / `{학교}_bboxes_v2.json` (8개) | 1~3KB | 🔴 v2 도 v4 안에 |
| `tb_crop_tasks_{학교}.json` (4개) | 6~7KB | 🔴 v5 존재 |
| `crop_tasks.json` | 18KB | 🔴 |
| `final_matches.json` | 21KB | 🔴 v5 존재 |

→ **폴더 통째로 삭제 후보.**

## 6. textbook_match_v5/ (현재 표준 - 활성)
| 파일 | 크기 | 판정 |
|---|---|---|
| `tb_bboxes_{학교}.json` (광명·광명북) | 1KB대 | ⭐ |
| `tb_bboxes_new.json` | 766B | ⭐ 신규 추가분 |
| `tb_crop_tasks_{학교}.json` (2개) | 3KB | ⭐ |
| `visual_matches_광명고.json` / `_v2` / `_final` | 3~8KB | 🟡 `_final` 만 유지 후보 |
| `visual_matches_광명북고.json` / `_v2` / `_final` | 유사 | 🟡 `_final` 만 유지 후보 |
| `final_matches.json` | 8KB | ⭐ 최종 매칭 |
| `text_candidates.json` | 640KB | ⭐ |
| `exam_crops_meta.json` | 5KB | ⭐ |
| `new_matches_for_crop.json` | 1KB | ⭐ |

→ v5 안에서도 `visual_matches_*` `_v2` 는 중간본. `_final` 만 남기면 됩니다.

## 7. audit_history/ (감사 스냅샷)
| 파일 | 크기 | 판정 |
|---|---|---|
| `audit_20260510_015930.json` | 2KB | 🔴 날짜 박힌 스냅샷 |
| `audit_20260510_020138.json` | ~2KB | 🔴 같은 날 2회차, 폐기 가능 |

→ 감사 이력 보관 목적이 아니라면 삭제.

## 8. pirate_analysis/configs/ (⭐ 활성 - 학교별 리포트 설정)
| 파일 | 크기 | 판정 |
|---|---|---|
| `광명고.json` / `광명북고.json` / `광문고.json` / `명문고.json` / `소하고.json` / `운산고.json` (6개) | ~13KB | ⭐ 매 학기 재사용 |
| `광명지역_통합리포트.json` | ~13KB | ⭐ |

→ **build_school_report_v5.py 및 pirate_2026_report/ 워크플로우 입력 파일. 유지 필수.**

## 9. pirate_analysis_middle/configs/ (중학교 리포트)
| 파일 | 크기 | 판정 |
|---|---|---|
| `철산중.json` | ~14KB | ⭐ 사용자 학원 담당 학교 |
| `철산중_리포트.json` | ~5KB | ⭐ |

---

## 삭제 후보 요약 (사용자 확인 필수)

### 높은 확신도 — 통째 폴더 삭제 후보
- `textbook_match/` (v1) — v5로 완전 대체
- `textbook_match_v3/` — pages_ocr/ 하위 폴더가 v5에서 재사용되는지만 확인
- `textbook_match_v4/` — 전부 v5로 대체

### 중간 확신도 — 개별 파일 정리
- 루트의 `hangul_math_review.json`, `hangul_math_backup.json` — DB 반영 완료됐다면 폐기
- `composite_image_qids.json` — 일회성 태깅 결과
- `audit_history/audit_20260510_*.json` — 이력 보관 필요 없으면 폐기
- `textbook_match_v5/visual_matches_*_v2.json` — `_final` 있으면 폐기

### 교재 종료 후 정리 대상
- `jungdan_eval_2_2/*.json` — 재빌드 없으면
- `kernel_point/*.json` — 재빌드 없으면
- `summit_point/*.json` — 재빌드 없으면

### 반드시 유지
- `pirate_analysis/configs/**` — v5·2026 리포트 입력
- `pirate_analysis_middle/configs/**` — 철산중 리포트
- `textbook_match_v5/` (visual_matches `_v2` 제외 나머지)

---

## 대략적 용량 절감 추정 (파일 사이즈 합산)

- textbook_match/ v1 폴더 전부: **≈ 1.75MB**
- textbook_match_v3/ (pages_ocr 제외): **≈ 1.4MB**
- textbook_match_v3/pages_ocr/ 26개: **≈ 550KB**
- textbook_match_v4/ 전부: **≈ 80KB**
- 루트 hangul_math_* 2개: **≈ 2.8MB**

→ 안전하게 정리 가능한 후보만 합쳐도 **약 6MB** 정도 절감 가능. 용량보다는 **작업 시 뒤져야 하는 파일 수 감소가 실질 이득**입니다.
