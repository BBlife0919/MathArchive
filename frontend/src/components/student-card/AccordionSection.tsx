import { useState, type ReactNode } from "react";
import "./AccordionSection.css";

interface Props {
  title: string;
  defaultOpen?: boolean;
  badge?: ReactNode;
  // "미입력"처럼 아직 채워지지 않은 상태를 주황으로 구분(적녹색약 규칙:
  // 남색=기록 있음/정상, 주황=비어있음/주의 — 색만으로 구분하지 않도록
  // 텍스트 자체가 1차 구분자이고 색은 보조 신호).
  badgeTone?: "filled" | "empty";
  children: ReactNode;
}

// 6개 학생카드 섹션을 한번에 다 펼쳐두지 말고 클릭한 것만 보이게
// 해달라는 요청(2026-10-27)으로 도입. sc-section 카드 자체를 아코디언
// 헤더/바디로 쪼갠다 — 기존 섹션 컴포넌트들은 제목(h2)만 빼고 그대로 둔다.
export default function AccordionSection({ title, defaultOpen = false, badge, badgeTone = "filled", children }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className={open ? "sc-section sc-accordion open" : "sc-section sc-accordion"}>
      <button type="button" className="sc-accordion-header" onClick={() => setOpen((v) => !v)}>
        <span className="sc-accordion-caret">{open ? "▾" : "▸"}</span>
        <h2 className="sc-section-title">{title}</h2>
        {badge && (
          <span className={badgeTone === "empty" ? "sc-accordion-badge empty" : "sc-accordion-badge"}>
            {badge}
          </span>
        )}
      </button>
      {open && <div className="sc-accordion-body">{children}</div>}
    </section>
  );
}
