import { useEffect, useRef, useState } from "react";
import type { QuestionCard as QuestionCardData } from "../../api/questions";
import "./SortMenu.css";

export type SortCriterion = "chapter" | "difficulty" | "choice-first" | "random";

const DIFF_RANK: Record<string, number> = { "하": 0, "중": 1, "상": 2, "킬": 3 };

const OPTIONS: { value: SortCriterion; label: string }[] = [
  { value: "chapter", label: "유형 오름차순" },
  { value: "difficulty", label: "난이도 오름차순" },
  { value: "choice-first", label: "객관식 상단배치" },
  { value: "random", label: "무작위" },
];

export function sortQuestionIds(items: QuestionCardData[], criterion: SortCriterion): number[] {
  const arr = [...items];
  switch (criterion) {
    case "chapter":
      arr.sort((a, b) => (a.chapter ?? "").localeCompare(b.chapter ?? "", "ko"));
      break;
    case "difficulty":
      arr.sort((a, b) => (DIFF_RANK[a.difficulty ?? ""] ?? 99) - (DIFF_RANK[b.difficulty ?? ""] ?? 99));
      break;
    case "choice-first":
      arr.sort((a, b) => Number(a.is_subjective) - Number(b.is_subjective));
      break;
    case "random":
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      break;
  }
  return arr.map((q) => q.question_id);
}

interface Props {
  value: SortCriterion | null;
  onSelect: (c: SortCriterion) => void;
}

// 드래그로 한 건씩 옮기는 것 말고, 기준 하나로 전체 순서를 한 번에 재배열하고
// 싶다는 요청(2026-10-24)으로 추가 — 고른 기준은 드래그 재정렬과 같은
// "직접 순서" 파이프라인에 올라탄다(그 뒤로도 드래그로 더 다듬을 수 있음).
export default function SortMenu({ value, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const currentLabel = OPTIONS.find((o) => o.value === value)?.label ?? "정렬 기준 선택";

  return (
    <div className="sort-menu" ref={rootRef}>
      <button type="button" className="sort-menu-trigger" onClick={() => setOpen((v) => !v)}>
        문제 {currentLabel}
        <span className={open ? "sort-menu-caret open" : "sort-menu-caret"}>▲</span>
      </button>
      {open && (
        <div className="sort-menu-dropdown">
          <p className="sort-menu-hint">모든 단원의 정렬 순서가 변경됩니다.</p>
          {OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              className="sort-menu-option"
              onClick={() => { onSelect(opt.value); setOpen(false); }}
            >
              {opt.label}
              {value === opt.value && <span className="sort-menu-check">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
