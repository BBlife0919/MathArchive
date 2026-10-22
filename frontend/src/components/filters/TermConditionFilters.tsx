import type { FiltersResponse } from "../../api/questions";
import "./TermConditionFilters.css";

const EXAM_TYPE_LABEL: Record<string, string> = { a: "중간", b: "기말" };

export interface TermConditionValue {
  grades: number[];
  years: number[];
  semesters: number[];
  examTypes: string[];
}

interface Props {
  filters: FiltersResponse;
  value: TermConditionValue;
  onChange: (next: TermConditionValue) => void;
}

function toggleIn<T>(list: T[], v: T): T[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}

// 학년/년도/학기/중간·기말 — 학교 선택과 같이 고르는 조건이라 항상
// SchoolPickerModal의 extraFilters 슬롯 안에서만 쓴다(유형별출제 사이드바,
// 학교학기별출제 패널 둘 다 공유). "밖에 따로 필터 두지 말아달라"는
// 피드백(2026-10-22)으로 두 군데 다 모달 안으로 옮겼다.
export default function TermConditionFilters({ filters, value, onChange }: Props) {
  return (
    <div className="term-cond">
      <div className="term-picker-row">
        <div className="term-picker-field">
          <span className="term-picker-label">학년</span>
          <div className="term-picker-pills">
            {filters.grades.map((g) => (
              <button
                key={g} type="button"
                className={value.grades.includes(g) ? "term-pill active" : "term-pill"}
                onClick={() => onChange({ ...value, grades: toggleIn(value.grades, g) })}
              >
                고{g}
              </button>
            ))}
          </div>
        </div>

        <div className="term-picker-field">
          <span className="term-picker-label">년도</span>
          <div className="term-picker-pills">
            {filters.years.map((y) => (
              <button
                key={y} type="button"
                className={value.years.includes(y) ? "term-pill active" : "term-pill"}
                onClick={() => onChange({ ...value, years: toggleIn(value.years, y) })}
              >
                {y}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="term-picker-row">
        <div className="term-picker-field">
          <span className="term-picker-label">학기</span>
          <div className="term-picker-pills">
            {filters.semesters.map((s) => (
              <button
                key={s} type="button"
                className={value.semesters.includes(s) ? "term-pill active" : "term-pill"}
                onClick={() => onChange({ ...value, semesters: toggleIn(value.semesters, s) })}
              >
                {s}학기
              </button>
            ))}
          </div>
        </div>

        <div className="term-picker-field">
          <span className="term-picker-label">중간 · 기말</span>
          <div className="term-picker-pills">
            {filters.exam_types.map((e) => (
              <button
                key={e} type="button"
                className={value.examTypes.includes(e) ? "term-pill active" : "term-pill"}
                onClick={() => onChange({ ...value, examTypes: toggleIn(value.examTypes, e) })}
              >
                {EXAM_TYPE_LABEL[e] ?? e}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
