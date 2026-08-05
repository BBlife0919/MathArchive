import type { QuestionCard as QuestionCardData } from "../../api/questions";
import QuestionContent from "../content/QuestionContent";
import Expander from "./Expander";
import "./QuestionCard.css";

const DIFF_COLOR: Record<string, string> = {
  "하": "#10b981", "중": "#f59e0b", "상": "#ef4444", "킬": "#0a1020",
};

function shortChapter(chapter: string | null): string {
  const c = chapter ?? "";
  return c.length <= 6 ? c : `${c.slice(0, 5)}…`;
}

function contentLength(segments: QuestionCardData["content_segments"]): number {
  return segments.reduce((sum, s) => sum + (s.type === "text" ? (s.md?.length ?? 0) : 0), 0);
}

function hasRichContent(segments: QuestionCardData["content_segments"]): boolean {
  return segments.some((s) => s.type === "image" || s.type === "box");
}

interface Props {
  question: QuestionCardData;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

export default function QuestionCard({ question: q, isSelected, onToggleSelect }: Props) {
  const diffColor = DIFF_COLOR[q.difficulty ?? ""] ?? "#94a3b8";
  const richContent = hasRichContent(q.content_segments);
  const longContent = contentLength(q.content_segments) > 400;

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

      {richContent || longContent ? (
        <Expander summary="문제 보기" defaultOpen={!richContent}>
          <QuestionContent segments={q.content_segments} />
        </Expander>
      ) : (
        <QuestionContent segments={q.content_segments} />
      )}

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
