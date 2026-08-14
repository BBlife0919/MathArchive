import type { QuestionCard as QuestionCardData } from "../../api/questions";
import QuestionContent from "../content/QuestionContent";
import Expander from "./Expander";
import "./QuestionCard.css";

// 적녹색약 접근성 규칙: 색만으로 구분 금지, 남색↔주황 2색만 사용 (텍스트 라벨이 1차 구분자)
const DIFF_COLOR: Record<string, string> = {
  "하": "#3b6ea5", "중": "#13203c", "상": "#c2703d", "킬": "#9c3d0a",
};

function shortChapter(chapter: string | null): string {
  const c = chapter ?? "";
  return c.length <= 6 ? c : `${c.slice(0, 5)}…`;
}

interface Props {
  question: QuestionCardData;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

export default function QuestionCard({ question: q, isSelected, onToggleSelect }: Props) {
  const diffColor = DIFF_COLOR[q.difficulty ?? ""] ?? "#94a3b8";

  return (
    <div className="question-card">
      <div className="question-card-header">
        <div className="question-card-meta">
          <b>{q.meta_short}</b> ·{" "}
          <span
            className="diff-badge"
            style={{ background: `${diffColor}1a`, color: diffColor }}
          >
            {q.difficulty ?? "?"}
          </span>{" "}
          · <span className="meta-muted">{shortChapter(q.chapter)}</span>
          {" · "}
          <span className="meta-muted">{q.points ? `${q.points}점` : ""}</span>
          {q.is_subjective && <span className="badge-subjective">서술형</span>}
          {q.error_note && <span className="badge-error">오류</span>}
        </div>
        {onToggleSelect && (
          <button
            type="button"
            className={isSelected ? "select-btn selected" : "select-btn"}
            onClick={onToggleSelect}
          >
            {isSelected ? "제거" : "담기"}
          </button>
        )}
      </div>

      <QuestionContent segments={q.content_segments} />

      {q.choices_text && (
        <div className="choices-caption">
          <QuestionContent segments={[{ type: "text", md: q.choices_text }]} />
        </div>
      )}

      <Expander summary={`정답: ${q.answer_display ?? "?"} · 해설 보기`}>
        {q.solution_segments.length > 0 ? (
          <QuestionContent segments={q.solution_segments} />
        ) : (
          <p className="meta-muted">해설 없음</p>
        )}
      </Expander>

      {isSelected && <p className="selected-caption">선택됨</p>}
    </div>
  );
}
