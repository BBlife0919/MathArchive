import { memo } from "react";
import type { QuestionCard as QuestionCardData } from "../../api/questions";
import { useBookmark } from "../../context/BookmarkContext";
import QuestionContent from "../content/QuestionContent";
import Expander from "./Expander";
import DifficultyBar from "./DifficultyBar";
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

function QuestionCard({ question: q, isSelected, onToggleSelect }: Props) {
  const diffColor = DIFF_COLOR[q.difficulty ?? ""] ?? "#94a3b8";
  const { bookmarkedIds, toggle: toggleBookmark } = useBookmark();
  const isBookmarked = bookmarkedIds.has(q.question_id);

  return (
    <div className="question-card">
      <div className="question-card-header">
        <div className="question-card-meta">
          <span className="meta-title">{q.meta_short}</span>
          <span
            className="diff-badge"
            style={{ background: `${diffColor}1a`, color: diffColor }}
          >
            {q.difficulty ?? "?"}
          </span>
          <DifficultyBar difficulty={q.difficulty} />
          {q.chapter && <span className="meta-chip">{shortChapter(q.chapter)}</span>}
          {q.points != null && <span className="meta-chip">{q.points}점</span>}
          {q.is_subjective && <span className="badge-subjective">서술형</span>}
          {q.error_note && <span className="badge-error">오류</span>}
        </div>
        <div className="question-card-actions">
          <button
            type="button"
            className="icon-btn"
            title="유사 문제 추천 (준비중)"
            onClick={() => {}}
          >
            유사
          </button>
          <button
            type="button"
            className={isBookmarked ? "icon-btn bookmarked" : "icon-btn"}
            title={isBookmarked ? "책갈피 해제" : "책갈피에 담기"}
            aria-pressed={isBookmarked}
            onClick={() => toggleBookmark(q.question_id)}
          >
            {isBookmarked ? "★ 책갈피" : "☆ 책갈피"}
          </button>
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

// STEP2 문항 목록(188문항 등 대량)을 드래그로 재정렬할 때, 실제로 위치가
// 바뀐 카드만 다시 그리도록 React.memo로 감싼다 — 안 그러면 드래그 중
// 모든 카드가 매 포인터 이동마다 통째로 재평가돼 버벅인다(2026-10-24 피드백).
export default memo(QuestionCard);
