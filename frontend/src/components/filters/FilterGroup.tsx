import { useState, type ReactNode } from "react";
import "./FilterGroup.css";

interface Props {
  title: string;
  activeCount: number;
  defaultOpen?: boolean;
  children: ReactNode;
}

// 필터 사이드바가 항목 10여 개를 한 화면에 전부 펼쳐 보여줘서 정보過多로
// 느껴진다는 피드백(2026-10-20)으로 도입. 관련 필터를 묶어 접어두고,
// 이미 값이 선택된 그룹만 기본으로 펼친다 — 아무것도 안 골랐으면 접힘.
export default function FilterGroup({ title, activeCount, defaultOpen = false, children }: Props) {
  const [open, setOpen] = useState(defaultOpen || activeCount > 0);

  return (
    <div className="filter-group">
      <button
        type="button"
        className="filter-group-header"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className="filter-group-title">
          {title}
          {activeCount > 0 && <span className="filter-group-count">{activeCount}</span>}
        </span>
        <span className={open ? "filter-group-caret open" : "filter-group-caret"}>▾</span>
      </button>
      {open && <div className="filter-group-body">{children}</div>}
    </div>
  );
}
