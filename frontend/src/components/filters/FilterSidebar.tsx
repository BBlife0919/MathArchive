import MultiSelectField from "./MultiSelectField";
import DifficultyButtonGroup from "./DifficultyButtonGroup";
import CurriculumCascade from "./CurriculumCascade";
import QuickSearchBox from "./QuickSearchBox";
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

const EXAM_TYPE_LABEL: Record<string, string> = { a: "중간", b: "기말" };

interface Props {
  filters: FiltersResponse | null;
  state: FilterState;
  onChange: (next: FilterState) => void;
  selectedCount: number;
  onResetSelection: () => void;
}

export default function FilterSidebar({
  filters, state, onChange, selectedCount, onResetSelection,
}: Props) {
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
      <hr className="filter-divider" />

      <MultiSelectField
        label="지역"
        options={filters.regions.map((r) => ({ value: r, label: r }))}
        selected={state.regions}
        onChange={(v) => onChange({ ...state, regions: v })}
      />
      <MultiSelectField
        label="학교"
        options={filters.schools.map((s) => ({ value: s, label: s }))}
        selected={state.schools}
        onChange={(v) => onChange({ ...state, schools: v })}
      />
      <MultiSelectField
        label="학년"
        options={filters.grades.map((g) => ({ value: g, label: `고${g}` }))}
        selected={state.grades}
        onChange={(v) => onChange({ ...state, grades: v })}
      />
      <MultiSelectField
        label="년도"
        options={filters.years.map((y) => ({ value: y, label: `${y}년` }))}
        selected={state.years}
        onChange={(v) => onChange({ ...state, years: v })}
      />
      <MultiSelectField
        label="학기"
        options={filters.semesters.map((s) => ({ value: s, label: `${s}학기` }))}
        selected={state.semesters}
        onChange={(v) => onChange({ ...state, semesters: v })}
      />
      <MultiSelectField
        label="중간/기말"
        options={filters.exam_types.map((e) => ({ value: e, label: EXAM_TYPE_LABEL[e] ?? e }))}
        selected={state.examTypes}
        onChange={(v) => onChange({ ...state, examTypes: v })}
      />

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

      <hr className="filter-divider" />
      <div className="filter-section-label">추가 옵션</div>
      <label className="exclude-recent-checkbox">
        <input
          type="checkbox"
          checked={state.excludeRecentDays}
          onChange={(e) => onChange({ ...state, excludeRecentDays: e.target.checked })}
        />
        기존 출제 문제 제외 (최근 {EXCLUDE_RECENT_DAYS}일)
      </label>

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
