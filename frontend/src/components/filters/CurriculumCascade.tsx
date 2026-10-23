import { useEffect, useMemo } from "react";
import {
  allMinorChaptersInSubjects, majorChapters, minorChapters,
  type CurriculumTree,
} from "../../utils/curriculum";
import "./CurriculumCascade.css";

interface Props {
  tree: CurriculumTree;
  subjects: string[];
  majors: string[];
  minors: string[];
  onChange: (next: { subjects: string[]; majors: string[]; minors: string[] }) => void;
}

function toggleIn(list: string[], v: string): string[] {
  return list.includes(v) ? list.filter((x) => x !== v) : [...list, v];
}

interface ChipGroupProps {
  label: string;
  options: string[];
  selected: string[];
  onToggle: (v: string) => void;
  emptyHint?: string;
}

function ChipGroup({ label, options, selected, onToggle, emptyHint }: ChipGroupProps) {
  return (
    <div className="curr-field">
      <span className="curr-label">{label}</span>
      {options.length === 0 ? (
        <p className="curr-empty-hint">{emptyHint}</p>
      ) : (
        <div className="curr-chip-grid">
          {options.map((opt) => (
            <button
              key={opt}
              type="button"
              className={selected.includes(opt) ? "curr-chip selected" : "curr-chip"}
              onClick={() => onToggle(opt)}
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// 학교선택 모달처럼 "칩을 직접 눌러 고르는" 방식으로 통일한다 — 드롭다운
// 안에서 체크박스를 찾아야 하던 기존 방식이 "여기도 저기처럼 해달라"는
// 피드백(2026-10-24)으로 바뀌었다.
export default function CurriculumCascade({
  tree, subjects, majors, minors, onChange,
}: Props) {
  const subjectOptions = useMemo(() => Object.keys(tree), [tree]);
  const majorsPool = useMemo(
    () => (subjects.length ? majorChapters(tree, subjects) : []),
    [tree, subjects],
  );
  const minorsPool = useMemo(() => {
    if (majors.length) return minorChapters(tree, subjects, majors);
    if (subjects.length) return allMinorChaptersInSubjects(tree, subjects);
    return [];
  }, [tree, subjects, majors]);

  // main.py 의 Streamlit multiselect 동작과 동일하게: 상위 선택이 바뀌어
  // 하위 pool 에서 빠진 값은 자동으로 선택 해제한다.
  useEffect(() => {
    const validMajors = majors.filter((m) => majorsPool.includes(m));
    if (validMajors.length !== majors.length) {
      onChange({ subjects, majors: validMajors, minors });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [majorsPool]);

  useEffect(() => {
    const validMinors = minors.filter((m) => minorsPool.includes(m));
    if (validMinors.length !== minors.length) {
      onChange({ subjects, majors, minors: validMinors });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minorsPool]);

  return (
    <div className="curr-cascade">
      <ChipGroup
        label="과목"
        options={subjectOptions}
        selected={subjects}
        onToggle={(v) => onChange({ subjects: toggleIn(subjects, v), majors, minors })}
      />
      <ChipGroup
        label="대단원"
        options={majorsPool}
        selected={majors}
        onToggle={(v) => onChange({ subjects, majors: toggleIn(majors, v), minors })}
        emptyHint="먼저 과목을 선택해주세요."
      />
      <ChipGroup
        label="중단원"
        options={minorsPool}
        selected={minors}
        onToggle={(v) => onChange({ subjects, majors, minors: toggleIn(minors, v) })}
        emptyHint="먼저 과목을 선택해주세요."
      />
    </div>
  );
}
