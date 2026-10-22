import { useState } from "react";
import type { FiltersResponse } from "../../api/questions";
import SchoolPickerModal from "../filters/SchoolPickerModal";
import TermConditionFilters from "../filters/TermConditionFilters";
import "./SchoolTermPicker.css";

export interface SchoolTermValue {
  subjects: string[];
  schools: string[];
  grades: number[];
  years: number[];
  semesters: number[];
  examTypes: string[];
}

export const EMPTY_SCHOOL_TERM: SchoolTermValue = {
  subjects: [], schools: [], grades: [], years: [], semesters: [], examTypes: [],
};

interface Props {
  filters: FiltersResponse;
  value: SchoolTermValue;
  onChange: (next: SchoolTermValue) => void;
  onSearch: () => void;
  searching: boolean;
}

function toggleIn<T>(list: T[], v: T): T[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}

export default function SchoolTermPicker({ filters, value, onChange, onSearch, searching }: Props) {
  const [schoolModalOpen, setSchoolModalOpen] = useState(false);
  const subjects = Object.keys(filters.curriculum);

  const conditionCount = value.grades.length + value.years.length
    + value.semesters.length + value.examTypes.length;

  return (
    <div className="term-picker">
      <div className="term-picker-field">
        <span className="term-picker-label">과목</span>
        <div className="term-picker-pills">
          {subjects.map((s) => (
            <button
              key={s} type="button"
              className={value.subjects.includes(s) ? "term-pill active" : "term-pill"}
              onClick={() => onChange({ ...value, subjects: toggleIn(value.subjects, s) })}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="term-picker-field">
        <span className="term-picker-label">지역 · 학교 · 학년 · 년도 · 학기</span>
        <button type="button" className="term-school-trigger" onClick={() => setSchoolModalOpen(true)}>
          <span>
            {value.schools.length === 0 ? "전체 학교" : `${value.schools.length}개 학교 선택됨`}
            {conditionCount > 0 && ` · 조건 ${conditionCount}개`}
          </span>
          <span className="term-school-caret">▾</span>
        </button>
        <SchoolPickerModal
          open={schoolModalOpen}
          onClose={() => setSchoolModalOpen(false)}
          provinces={filters.provinces}
          provinceDistricts={filters.province_districts}
          regionSchools={filters.region_schools}
          allSchools={filters.schools}
          selected={value.schools}
          extraFilters={
            <TermConditionFilters
              filters={filters}
              value={{
                grades: value.grades, years: value.years,
                semesters: value.semesters, examTypes: value.examTypes,
              }}
              onChange={(next) => onChange({ ...value, ...next })}
            />
          }
          onApply={(schools) => {
            onChange({ ...value, schools });
            setSchoolModalOpen(false);
          }}
        />
      </div>

      <button
        type="button" className="btn-primary term-search-btn" onClick={onSearch}
        disabled={searching || (value.schools.length === 0 && value.subjects.length === 0)}
      >
        {searching ? "불러오는 중..." : "시험지 찾기"}
      </button>
      {value.schools.length === 0 && value.subjects.length === 0 && (
        <p className="term-picker-hint">과목 또는 학교를 하나 이상 선택해주세요.</p>
      )}
    </div>
  );
}
