import { useEffect, useMemo, useState } from "react";
import type { ExamPaper } from "../../api/questions";
import "./ExamPaperList.css";

const EXAM_TYPE_LABEL: Record<string, string> = { a: "중간고사", b: "기말고사" };
const EXAM_TYPE_ORDER: Record<string, number> = { a: 0, b: 1 };

interface Props {
  papers: ExamPaper[];
  loading: boolean;
  onPick: (paper: ExamPaper) => void;
  pickingKey: string | null;
}

export function paperKey(p: ExamPaper): string {
  // chapter_range까지 포함해야 한다 — list_exam_papers()가 chapter_range로도
  // GROUP BY 하므로, 나머지 필드가 전부 같아도 chapter_range가 다르면
  // 별개 시험지 카드일 수 있다(2026-10-22 검수에서 발견).
  return `${p.school}|${p.grade}|${p.year}|${p.semester}|${p.exam_type}|${p.subject ?? ""}|${p.chapter_range ?? ""}`;
}

function uniqueSortedNum(values: number[], desc = false): number[] {
  const u = Array.from(new Set(values));
  return u.sort((a, b) => (desc ? b - a : a - b));
}

function uniqueSortedExamTypes(values: string[]): string[] {
  const u = Array.from(new Set(values));
  return u.sort((a, b) => (EXAM_TYPE_ORDER[a] ?? 9) - (EXAM_TYPE_ORDER[b] ?? 9));
}

// 년도(1차) → 학기(2차) → 중간·기말(3차) 순으로 드릴다운한 뒤, 그 조건에
// 맞는 시험지만 학교별로 세로 목록에 묶어 보여준다. 여러 학교·학년·연도·
// 학기가 뒤섞인 카드 그리드가 "난잡하다"는 피드백(2026-10-24)으로, 학교
// 선택 모달의 시/도→구 드릴다운과 같은 패턴을 결과 화면에도 적용했다.
export default function ExamPaperList({ papers, loading, onPick, pickingKey }: Props) {
  const [activeYear, setActiveYear] = useState<number | null>(null);
  const [activeSemester, setActiveSemester] = useState<number | null>(null);
  const [activeExamType, setActiveExamType] = useState<string | null>(null);

  const years = useMemo(() => uniqueSortedNum(papers.map((p) => p.year), true), [papers]);

  // 검색 결과가 바뀌면(새 조건으로 재검색) 가장 최신 연도·학기·중간기말로
  // 자동 드릴다운해, 매번 3단계를 다시 클릭하지 않아도 바로 정리된 목록부터
  // 보이게 한다.
  useEffect(() => {
    if (years.length === 0) {
      setActiveYear(null);
      setActiveSemester(null);
      setActiveExamType(null);
      return;
    }
    const y = years[0];
    const sems = uniqueSortedNum(papers.filter((p) => p.year === y).map((p) => p.semester));
    const s = sems[0] ?? null;
    const types = uniqueSortedExamTypes(
      papers.filter((p) => p.year === y && p.semester === s).map((p) => p.exam_type));
    setActiveYear(y);
    setActiveSemester(s);
    setActiveExamType(types[0] ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [papers]);

  const semesters = useMemo(
    () => (activeYear === null ? [] : uniqueSortedNum(papers.filter((p) => p.year === activeYear).map((p) => p.semester))),
    [papers, activeYear],
  );
  const examTypes = useMemo(
    () => (activeYear === null || activeSemester === null ? [] : uniqueSortedExamTypes(
      papers.filter((p) => p.year === activeYear && p.semester === activeSemester).map((p) => p.exam_type))),
    [papers, activeYear, activeSemester],
  );

  function selectYear(y: number) {
    const sems = uniqueSortedNum(papers.filter((p) => p.year === y).map((p) => p.semester));
    const s = sems[0] ?? null;
    const types = uniqueSortedExamTypes(
      papers.filter((p) => p.year === y && p.semester === s).map((p) => p.exam_type));
    setActiveYear(y);
    setActiveSemester(s);
    setActiveExamType(types[0] ?? null);
  }

  function selectSemester(s: number) {
    const types = uniqueSortedExamTypes(
      papers.filter((p) => p.year === activeYear && p.semester === s).map((p) => p.exam_type));
    setActiveSemester(s);
    setActiveExamType(types[0] ?? null);
  }

  const matched = useMemo(
    () => papers.filter((p) => p.year === activeYear && p.semester === activeSemester && p.exam_type === activeExamType),
    [papers, activeYear, activeSemester, activeExamType],
  );

  const bySchool = useMemo(() => {
    const map = new Map<string, ExamPaper[]>();
    for (const p of matched) {
      const list = map.get(p.school) ?? [];
      list.push(p);
      map.set(p.school, list);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b, "ko"));
  }, [matched]);

  if (loading) {
    return <p className="empty-state">시험지를 불러오는 중...</p>;
  }
  if (papers.length === 0) {
    return <p className="empty-state">조건에 맞는 시험지가 없습니다. 조건을 조정해주세요.</p>;
  }

  return (
    <div className="paper-browser">
      <div className="paper-tree-level">
        <span className="paper-tree-label">년도</span>
        <div className="paper-tree-tabs">
          {years.map((y) => (
            <button
              key={y} type="button"
              className={activeYear === y ? "paper-tree-tab active" : "paper-tree-tab"}
              onClick={() => selectYear(y)}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      <div className="paper-tree-level">
        <span className="paper-tree-label">학기</span>
        <div className="paper-tree-tabs">
          {semesters.map((s) => (
            <button
              key={s} type="button"
              className={activeSemester === s ? "paper-tree-tab active" : "paper-tree-tab"}
              onClick={() => selectSemester(s)}
            >
              {s}학기
            </button>
          ))}
        </div>
      </div>

      <div className="paper-tree-level">
        <span className="paper-tree-label">중간 · 기말</span>
        <div className="paper-tree-tabs">
          {examTypes.map((t) => (
            <button
              key={t} type="button"
              className={activeExamType === t ? "paper-tree-tab active accent" : "paper-tree-tab accent"}
              onClick={() => setActiveExamType(t)}
            >
              {EXAM_TYPE_LABEL[t] ?? t}
            </button>
          ))}
        </div>
      </div>

      <div className="paper-school-list">
        {bySchool.length === 0 && (
          <p className="empty-state">이 조건에는 시험지가 없습니다.</p>
        )}
        {bySchool.map(([school, items]) => (
          <div key={school} className="paper-school-row">
            <div className="paper-school-name">{school}</div>
            <div className="paper-school-items">
              {items.map((p) => {
                const key = paperKey(p);
                const busy = pickingKey === key;
                return (
                  <button
                    key={key} type="button" className="paper-item" onClick={() => onPick(p)} disabled={busy}
                  >
                    <span className="paper-item-badge">고{p.grade}</span>
                    {p.subject && <span className="paper-item-subject">{p.subject}</span>}
                    {p.chapter_range && <span className="paper-item-range">{p.chapter_range}</span>}
                    <span className="paper-item-count">{p.question_count}문항</span>
                    <span className="paper-item-cta">{busy ? "담는 중..." : "이 시험지로 →"}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
