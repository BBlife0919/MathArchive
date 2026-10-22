import { useState } from "react";
import type { FiltersResponse } from "../../api/questions";
import SchoolPickerModal from "../filters/SchoolPickerModal";
import "./SchoolTermPicker.css";

const EXAM_TYPE_LABEL: Record<string, string> = { a: "중간", b: "기말" };

export interface SchoolTermValue {
  subjects: string[];
  schools: string[];
  grades: number[];
  semesters: number[];
  examTypes: string[];
}

export const EMPTY_SCHOOL_TERM: SchoolTermValue = {
  subjects: [], schools: [], grades: [], semesters: [], examTypes: [],
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
        <span className="term-picker-label">지역 · 학교</span>
        <button type="button" className="term-school-trigger" onClick={() => setSchoolModalOpen(true)}>
          <span>{value.schools.length === 0 ? "전체 학교" : `${value.schools.length}개 학교 선택됨`}</span>
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
          onApply={(schools) => {
            onChange({ ...value, schools });
            setSchoolModalOpen(false);
          }}
        />
      </div>

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
