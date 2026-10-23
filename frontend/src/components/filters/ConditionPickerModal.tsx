import { useEffect, useState } from "react";
import CurriculumCascade from "./CurriculumCascade";
import DifficultyButtonGroup from "./DifficultyButtonGroup";
import { EXCLUDE_RECENT_DAYS } from "../../constants";
import type { FiltersResponse, QuestionType } from "../../api/questions";
import "./ConditionPickerModal.css";

export interface ConditionValue {
  subjects: string[];
  majors: string[];
  minors: string[];
  difficulties: string[];
  questionType: QuestionType;
  keyword: string;
  excludeRecentDays: boolean;
}

interface Props {
  open: boolean;
  onClose: () => void;
  filters: FiltersResponse;
  value: ConditionValue;
  onApply: (next: ConditionValue) => void;
}

const QUESTION_TYPE_OPTIONS: [QuestionType, string][] = [
  ["all", "전체"], ["choice", "선택형"], ["subjective", "서답형"],
];

// "단원·난이도"와 "세부조건"을 각자 접이식 섹션으로 사이드바에 펼쳐두니
// 정보가 한꺼번에 다 보여 난잡하다는 피드백(2026-10-24)으로, 학교선택
// 모달과 같은 패턴(트리거 버튼 → 팝업에서 한 화면에 전부)으로 통합한다.
export default function ConditionPickerModal({ open, onClose, filters, value, onApply }: Props) {
  const [draft, setDraft] = useState<ConditionValue>(value);

  useEffect(() => {
    if (open) setDraft(value);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!open) return null;

  const activeCount = draft.subjects.length + draft.majors.length + draft.minors.length
    + draft.difficulties.length + (draft.questionType !== "all" ? 1 : 0)
    + (draft.keyword ? 1 : 0) + (draft.excludeRecentDays ? 1 : 0);

  return (
    <div className="cond-modal-backdrop" onMouseDown={onClose}>
      <div className="cond-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="cond-modal-header">
          <h2>단원 · 난이도 · 세부 조건</h2>
          <button type="button" className="cond-modal-close" onClick={onClose} aria-label="닫기">×</button>
        </div>

        <div className="cond-modal-body">
          <div className="cond-modal-section">
            <div className="cond-modal-section-title">단원 · 난이도</div>
            <CurriculumCascade
              tree={filters.curriculum}
              subjects={draft.subjects}
              majors={draft.majors}
              minors={draft.minors}
              onChange={(next) => setDraft({ ...draft, ...next })}
            />
            <DifficultyButtonGroup
              options={filters.difficulties}
              selected={draft.difficulties}
              onChange={(v) => setDraft({ ...draft, difficulties: v })}
            />
          </div>

          <div className="cond-modal-divider" />

          <div className="cond-modal-section">
            <div className="cond-modal-section-title">세부 조건</div>

            <div className="cond-modal-field">
              <span className="cond-modal-label">문제 유형</span>
              <div className="question-type-radio">
                {QUESTION_TYPE_OPTIONS.map(([v, label]) => (
                  <label key={v}>
                    <input
                      type="radio"
                      name="cond-question-type"
                      checked={draft.questionType === v}
                      onChange={() => setDraft({ ...draft, questionType: v })}
                    />
                    {label}
                  </label>
                ))}
              </div>
            </div>

            <div className="cond-modal-field">
              <span className="cond-modal-label">키워드 검색</span>
              <input
                type="text"
                className="keyword-input"
                placeholder="문제 텍스트 검색..."
                value={draft.keyword}
                onChange={(e) => setDraft({ ...draft, keyword: e.target.value })}
              />
            </div>

            <div className="cond-modal-field">
              <span className="cond-modal-label">추가 옵션</span>
              <label className="exclude-recent-checkbox">
                <input
                  type="checkbox"
                  checked={draft.excludeRecentDays}
                  onChange={(e) => setDraft({ ...draft, excludeRecentDays: e.target.checked })}
                />
                기존 출제 문제 제외 (최근 {EXCLUDE_RECENT_DAYS}일)
              </label>
            </div>
          </div>
        </div>

        <div className="cond-modal-footer">
          <span>
            조건 {activeCount}개 ·{" "}
            <button
              type="button"
              className="cond-modal-reset"
              onClick={() => setDraft({
                subjects: [], majors: [], minors: [], difficulties: [],
                questionType: "all", keyword: "", excludeRecentDays: false,
              })}
            >
              초기화
            </button>
          </span>
          <div className="cond-modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>취소</button>
            <button type="button" className="btn-primary" onClick={() => onApply(draft)}>선택 완료</button>
          </div>
        </div>
      </div>
    </div>
  );
}
