import { memo } from "react";
import type { QuestionCard as QuestionCardData } from "../../api/questions";
import { useSelection } from "../../context/SelectionContext";
import QuestionContent from "../content/QuestionContent";

// 적녹색약 접근성 규칙: 색만으로 구분 금지, 남색↔주황 2색만 (QuestionCard.tsx 와 동일)
const DIFF_COLOR: Record<string, string> = {
  "하": "#3b6ea5", "중": "#13203c", "상": "#c2703d", "킬": "#9c3d0a",
};

interface Props {
  loading: boolean;
  error: boolean;
  items: QuestionCardData[] | null;
}

// useSelection() 을 QuestionCard 본체가 아니라 이 패널(열려있을 때만 마운트)에서만
// 구독한다 — QuestionCard 전체가 구독하면 어디서든 "담기"를 누를 때마다 화면에 떠
// 있는 모든 카드(대량 리스트)가 다시 렌더링돼, 드래그 버벅임 수정(2026-10-24,
// React.memo 도입)이 선택 액션 경로로 재발한다.
function SimilarQuestionsPanel({ loading, error, items }: Props) {
  const { selectedIds, toggle } = useSelection();

  if (loading) {
    return (
      <div className="similar-panel">
        <p className="meta-muted">불러오는 중…</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="similar-panel">
        <p className="meta-muted">유사문항을 불러오지 못했습니다.</p>
      </div>
    );
  }
  if (!items || items.length === 0) {
    return (
      <div className="similar-panel">
        <p className="meta-muted">같은 단원에서 유사한 문항을 찾지 못했습니다.</p>
      </div>
    );
  }

  return (
    <div className="similar-panel">
      {items.map((s) => {
        const sColor = DIFF_COLOR[s.difficulty ?? ""] ?? "#94a3b8";
        const added = selectedIds.has(s.question_id);
        return (
          <div key={s.question_id} className="similar-item">
            <div className="similar-item-meta">
              <span
                className="diff-badge"
                style={{ background: `${sColor}1a`, color: sColor }}
              >
                {s.difficulty ?? "?"}
              </span>
              <span className="meta-muted">{s.meta_short}</span>
            </div>
            <div className="similar-item-content">
              <QuestionContent segments={s.content_segments} />
            </div>
            <button
              type="button"
              className={added ? "select-btn selected" : "select-btn"}
              onClick={() => toggle(s.question_id)}
            >
              {added ? "제거" : "담기"}
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default memo(SimilarQuestionsPanel);
