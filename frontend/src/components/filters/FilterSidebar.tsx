import { useState } from "react";
import DifficultyButtonGroup from "./DifficultyButtonGroup";
import CurriculumCascade from "./CurriculumCascade";
import QuickSearchBox from "./QuickSearchBox";
import FilterGroup from "./FilterGroup";
import SchoolPickerModal from "./SchoolPickerModal";
import TermConditionFilters from "./TermConditionFilters";
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

// 백엔드 exclude_recent_days 파라미터에 실어 보낼 고정 기간(일). 최근 이
// 기간 안에 실제로 출제(PDF 다운로드)된 문항을 검색/미니테스트/균등배분
// 결과에서 제외한다.
export const EXCLUDE_RECENT_DAYS = 30;

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

      <FilterGroup
        title="출처"
        activeCount={
          state.schools.length + state.grades.length
          + state.years.length + state.semesters.length + state.examTypes.length
        }
      >
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
      </FilterGroup>

      <FilterGroup
        title="단원 · 난이도"
        activeCount={
          state.subjects.length + state.majors.length + state.minors.length
          + state.difficulties.length
        }
      >
        <CurriculumCascade
          tree={filters.curriculum}
          subjects={state.subjects}
          majors={state.majors}
          minors={state.minors}
          onChange={({ subjects, majors, minors }) =>
            onChange({ ...state, subjects, majors, minors })}
        />
        <DifficultyButtonGroup
          options={filters.difficulties}
          selected={state.difficulties}
          onChange={(v) => onChange({ ...state, difficulties: v })}
        />
      </FilterGroup>

      <FilterGroup
        title="세부 조건"
        activeCount={
          (state.questionType !== "all" ? 1 : 0)
          + (state.keyword ? 1 : 0)
          + (state.excludeRecentDays ? 1 : 0)
        }
      >
        <div className="filter-section-label">문제 유형</div>
        <div className="question-type-radio">
          {([
            ["all", "전체"], ["choice", "선택형"], ["subjective", "서답형"],
          ] as [QuestionType, string][]).map(([value, label]) => (
            <label key={value}>
              <input
                type="radio"
                name="question-type"
                checked={state.questionType === value}
                onChange={() => onChange({ ...state, questionType: value })}
              />
              {label}
            </label>
          ))}
        </div>

        <div className="filter-section-label">키워드 검색</div>
        <input
          type="text"
          className="keyword-input"
          placeholder="문제 텍스트 검색..."
          value={state.keyword}
          onChange={(e) => onChange({ ...state, keyword: e.target.value })}
        />

        <div className="filter-section-label">추가 옵션</div>
        <label className="exclude-recent-checkbox">
          <input
            type="checkbox"
            checked={state.excludeRecentDays}
            onChange={(e) => onChange({ ...state, excludeRecentDays: e.target.checked })}
          />
          기존 출제 문제 제외 (최근 {EXCLUDE_RECENT_DAYS}일)
        </label>
      </FilterGroup>

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
