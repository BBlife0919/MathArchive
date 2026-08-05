import { useEffect, useMemo } from "react";
import MultiSelectField from "./MultiSelectField";
import {
  allMinorChaptersInSubjects, majorChapters, minorChapters,
  type CurriculumTree,
} from "../../utils/curriculum";

interface Props {
  tree: CurriculumTree;
  subjects: string[];
  majors: string[];
  minors: string[];
  onChange: (next: { subjects: string[]; majors: string[]; minors: string[] }) => void;
}

export default function CurriculumCascade({
  tree, subjects, majors, minors, onChange,
}: Props) {
  const subjectOptions = useMemo(
    () => Object.keys(tree).map((s) => ({ value: s, label: s })),
    [tree],
  );
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
    <div>
      <div className="filter-section-label">단원</div>
      <MultiSelectField
        label="과목"
        options={subjectOptions}
        selected={subjects}
        onChange={(next) => onChange({ subjects: next, majors, minors })}
      />
      <MultiSelectField
        label="대단원"
        options={majorsPool.map((m) => ({ value: m, label: m }))}
        selected={majors}
        onChange={(next) => onChange({ subjects, majors: next, minors })}
        disabled={!subjects.length}
      />
      <MultiSelectField
        label="중단원"
        options={minorsPool.map((m) => ({ value: m, label: m }))}
        selected={minors}
        onChange={(next) => onChange({ subjects, majors, minors: next })}
        disabled={!minorsPool.length}
      />
    </div>
  );
}
