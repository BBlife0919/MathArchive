import type { ExamPaper } from "../../api/questions";
import "./ExamPaperList.css";

const EXAM_TYPE_LABEL: Record<string, string> = { a: "중간고사", b: "기말고사" };

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

export default function ExamPaperList({ papers, loading, onPick, pickingKey }: Props) {
  if (loading) {
    return <p className="empty-state">시험지를 불러오는 중...</p>;
  }
  if (papers.length === 0) {
    return <p className="empty-state">조건에 맞는 시험지가 없습니다. 조건을 조정해주세요.</p>;
  }

  return (
    <div className="paper-list">
      {papers.map((p) => {
        const key = paperKey(p);
        const busy = pickingKey === key;
        return (
          <button
            key={key} type="button" className="paper-card"
            onClick={() => onPick(p)} disabled={busy}
          >
            <div className="paper-card-top">
              <span className="paper-card-school">{p.school}</span>
              <span className="paper-card-badge">고{p.grade}</span>
            </div>
            <div className="paper-card-meta">
              <span>{p.year}년 {p.semester}학기</span>
              <span className="paper-card-dot">·</span>
              <span>{EXAM_TYPE_LABEL[p.exam_type] ?? p.exam_type}</span>
              {p.subject && (<><span className="paper-card-dot">·</span><span>{p.subject}</span></>)}
            </div>
            {p.chapter_range && <p className="paper-card-range">{p.chapter_range}</p>}
            <div className="paper-card-bottom">
              <span className="paper-card-count">{p.question_count}문항</span>
              <span className="paper-card-cta">{busy ? "담는 중..." : "이 시험지로 →"}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
