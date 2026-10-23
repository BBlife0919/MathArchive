import { useState } from "react";
import QuickSearchBox from "./QuickSearchBox";
import SchoolPickerModal from "./SchoolPickerModal";
import TermConditionFilters from "./TermConditionFilters";
import ConditionPickerModal from "./ConditionPickerModal";
import type { FiltersResponse, QuestionType } from "../../api/questions";
import "./FilterSidebar.css";

export interface FilterState {
  quickSearch: string;
  regions: string[];
  schools: string[];
  grades: number[];
  years: number[];
  semesters: number[];
  examTypes: string[];
  subjects: string[];
  majors: string[];
  minors: string[];
  difficulties: string[];
  questionType: QuestionType;
  keyword: string;
  excludeRecentDays: boolean;
}

export const EMPTY_FILTER_STATE: FilterState = {
  quickSearch: "",
  regions: [],
  schools: [],
  grades: [],
  years: [],
  semesters: [],
  examTypes: [],
  subjects: [],
  majors: [],
  minors: [],
  difficulties: [],
  questionType: "all",
  keyword: "",
  excludeRecentDays: false,
};

interface Props {
  filters: FiltersResponse | null;
  state: FilterState;
  onChange: (next: FilterState) => void;
  selectedCount: number;
  onResetSelection: () => void;
  onApply: () => void;
  hasPendingChanges: boolean;
}

export default function FilterSidebar({
  filters, state, onChange, selectedCount, onResetSelection, onApply, hasPendingChanges,
}: Props) {
  const [schoolModalOpen, setSchoolModalOpen] = useState(false);
  const [conditionModalOpen, setConditionModalOpen] = useState(false);

  if (!filters) {
    return <aside className="filter-sidebar">필터 불러오는 중...</aside>;
  }

  return (
    <aside className="filter-sidebar">
      <h2 className="filter-sidebar-title">문제 필터</h2>

      <QuickSearchBox
        active={state.quickSearch}
        onApply={(v) => onChange({ ...state, quickSearch: v })}
        onClear={() => onChange({ ...state, quickSearch: "" })}
      />

      <div className="ms-field">
        <label className="ms-label">지역 · 학교 · 학년 · 년도 · 학기</label>
        <button
          type="button"
          className="ms-trigger school-trigger"
          onClick={() => setSchoolModalOpen(true)}
        >
          <span>
            {state.schools.length === 0 ? "전체" : `${state.schools.length}개 학교 선택됨`}
            {state.grades.length + state.years.length + state.semesters.length + state.examTypes.length > 0
              && ` · 조건 ${state.grades.length + state.years.length + state.semesters.length + state.examTypes.length}개`}
          </span>
          <span className="ms-caret">▾</span>
        </button>
      </div>
      <SchoolPickerModal
        open={schoolModalOpen}
        onClose={() => setSchoolModalOpen(false)}
        provinces={filters.provinces}
        provinceDistricts={filters.province_districts}
        regionSchools={filters.region_schools}
        allSchools={filters.schools}
        selected={state.schools}
        extraFilters={
          <TermConditionFilters
            filters={filters}
            value={{
              grades: state.grades, years: state.years,
              semesters: state.semesters, examTypes: state.examTypes,
            }}
            onChange={(next) => onChange({ ...state, ...next })}
          />
        }
        onApply={(schools) => {
          onChange({ ...state, schools });
          setSchoolModalOpen(false);
        }}
      />

      <div className="ms-field">
        <label className="ms-label">단원 · 난이도 · 세부 조건</label>
        <button
          type="button"
          className="ms-trigger"
          onClick={() => setConditionModalOpen(true)}
        >
          <span>
            {state.subjects.length === 0 && state.majors.length === 0
              && state.minors.length === 0 && state.difficulties.length === 0
              && state.questionType === "all" && !state.keyword && !state.excludeRecentDays
              ? "조건 선택하기"
              : `조건 ${
                state.subjects.length + state.majors.length + state.minors.length
                + state.difficulties.length + (state.questionType !== "all" ? 1 : 0)
                + (state.keyword ? 1 : 0) + (state.excludeRecentDays ? 1 : 0)
              }개 선택됨`}
          </span>
          <span className="ms-caret">▾</span>
        </button>
      </div>
      <ConditionPickerModal
        open={conditionModalOpen}
        onClose={() => setConditionModalOpen(false)}
        filters={filters}
        value={{
          subjects: state.subjects, majors: state.majors, minors: state.minors,
          difficulties: state.difficulties, questionType: state.questionType,
          keyword: state.keyword, excludeRecentDays: state.excludeRecentDays,
        }}
        onApply={(next) => {
          onChange({ ...state, ...next });
          setConditionModalOpen(false);
        }}
      />

      <button
        type="button"
        className={hasPendingChanges ? "filter-apply-btn pending" : "filter-apply-btn"}
        onClick={onApply}
      >
        {hasPendingChanges ? "변경한 조건 적용하기" : "조건 적용됨"}
      </button>

      <hr className="filter-divider" />
      <div className="cart-summary">
        <span>시험지 ({selectedCount}문항)</span>
        <button type="button" className="btn-secondary" onClick={onResetSelection}>
          초기화
        </button>
      </div>
    </aside>
  );
}
