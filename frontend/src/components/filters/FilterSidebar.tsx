import { useEffect, useMemo, useState } from "react";
import MultiSelectField from "./MultiSelectField";
import DifficultyButtonGroup from "./DifficultyButtonGroup";
import CurriculumCascade from "./CurriculumCascade";
import QuickSearchBox from "./QuickSearchBox";
import FilterGroup from "./FilterGroup";
import SchoolPickerModal from "./SchoolPickerModal";
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
  onApply: () => void;
  hasPendingChanges: boolean;
}

export default function FilterSidebar({
  filters, state, onChange, selectedCount, onResetSelection, onApply, hasPendingChanges,
}: Props) {
  const [schoolModalOpen, setSchoolModalOpen] = useState(false);

  // 지역을 고르면 학교 후보도 그 지역 소속으로만 좁힌다 (CurriculumCascade의
  // 단원 캐스케이드와 동일 패턴). 지역을 안 고르면 전국 학교 전체가 후보.
  const schoolPool = useMemo(() => {
    if (!filters || state.regions.length === 0) return filters?.schools ?? [];
    const set = new Set<string>();
    for (const r of state.regions) {
      for (const s of filters.region_schools[r] ?? []) set.add(s);
    }
    return Array.from(set).sort();
  }, [filters, state.regions]);

  // 학교 선택 모달도 "지역" 필터가 이미 좁혀져 있으면 그 범위로만 시/도·
  // 구/시/군·학교를 보여준다 — 안 그러면 지역 필터와 모달에서 고른 학교가
  // 서로 다른 지역을 가리켜 검색이 조용히 0건이 되는 문제가 생긴다(AND
  // 결합 WHERE 절).
  const modalProvinceDistricts = useMemo(() => {
    if (!filters) return {};
    if (state.regions.length === 0) return filters.province_districts;
    const allowed = new Set(state.regions);
    const out: Record<string, string[]> = {};
    for (const [province, districts] of Object.entries(filters.province_districts)) {
      const kept = districts.filter((d) => allowed.has(d));
      if (kept.length > 0) out[province] = kept;
    }
    return out;
  }, [filters, state.regions]);

  const modalProvinces = useMemo(
    () => (filters?.provinces ?? []).filter((p) => p in modalProvinceDistricts),
    [filters, modalProvinceDistricts],
  );

  // 지역 변경으로 후보에서 빠진 학교는 자동으로 선택 해제.
  useEffect(() => {
    const validSchools = state.schools.filter((s) => schoolPool.includes(s));
    if (validSchools.length !== state.schools.length) {
      onChange({ ...state, schools: validSchools });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [schoolPool]);

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
          state.regions.length + state.schools.length + state.grades.length
          + state.years.length + state.semesters.length + state.examTypes.length
        }
      >
        <MultiSelectField
          label="지역"
          options={filters.regions.map((r) => ({ value: r, label: r }))}
          selected={state.regions}
          onChange={(v) => onChange({ ...state, regions: v })}
        />
        <div className="ms-field">
          <label className="ms-label">학교</label>
          <button
            type="button"
            className="ms-trigger"
            onClick={() => setSchoolModalOpen(true)}
          >
            <span>{state.schools.length === 0 ? "전체" : `${state.schools.length}개 선택`}</span>
            <span className="ms-caret">▾</span>
          </button>
        </div>
        <SchoolPickerModal
          open={schoolModalOpen}
          onClose={() => setSchoolModalOpen(false)}
          provinces={modalProvinces}
          provinceDistricts={modalProvinceDistricts}
          regionSchools={filters.region_schools}
          allSchools={schoolPool}
          selected={state.schools}
          onApply={(schools) => {
            onChange({ ...state, schools });
            setSchoolModalOpen(false);
          }}
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
