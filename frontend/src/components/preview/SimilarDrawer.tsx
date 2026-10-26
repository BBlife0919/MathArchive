import { useEffect, useState } from "react";
import {
  fetchSimilarQuestions,
  type QuestionCard as QuestionCardData,
} from "../../api/questions";
import { useSelection } from "../../context/SelectionContext";
import QuestionContent from "../content/QuestionContent";
import "./SimilarDrawer.css";

const DIFF_COLOR: Record<string, string> = {
  "하": "#3b6ea5", "중": "#13203c", "상": "#c2703d", "킬": "#9c3d0a",
};

interface Props {
  // 열려있는 기준 문항 id. null 이면 드로어를 닫는다.
  questionId: number | null;
  onClose: () => void;
}

// 화면 왼쪽에 고정으로 떠서 유사문항만 따로 스크롤하며 고를 수 있는 전용
// 패널(2026-10-26 요청) — 문항이 150개 넘는 미리보기 화면에서, 카드 안에
// 펼치면 전체 목록을 스크롤해야 유사문항을 보기 힘들다는 피드백 대응.
// 컴포넌트 하나만 마운트돼 있어 useSelection() 구독이 전체 리스트를
// 리렌더시키지 않는다(SimilarQuestionsPanel.tsx 와 같은 이유).
export default function SimilarDrawer({ questionId, onClose }: Props) {
  const { selectedIds, toggle } = useSelection();
  const [items, setItems] = useState<QuestionCardData[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [baseMeta, setBaseMeta] = useState("");

  useEffect(() => {
    if (questionId === null) return;
    setItems(null);
    setError(false);
    setLoading(true);
    setBaseMeta(`#${questionId}`);
    fetchSimilarQuestions(questionId)
      .then((res) => setItems(res.items))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [questionId]);

  if (questionId === null) return null;

  return (
    <div className="similar-drawer">
      <div className="similar-drawer-header">
        <h3>유사문항{baseMeta && <span className="meta-muted"> · {baseMeta}</span>}</h3>
        <button type="button" className="icon-btn" onClick={onClose}>닫기</button>
      </div>
      <div className="similar-drawer-body">
        {loading && <p className="meta-muted">불러오는 중…</p>}
        {error && <p className="meta-muted">유사문항을 불러오지 못했습니다.</p>}
        {!loading && !error && items?.length === 0 && (
          <p className="meta-muted">같은 단원에서 유사한 문항을 찾지 못했습니다.</p>
        )}
        {items?.map((s) => {
          const sColor = DIFF_COLOR[s.difficulty ?? ""] ?? "#94a3b8";
          const added = selectedIds.has(s.question_id);
          return (
            <div key={s.question_id} className="similar-drawer-item">
              <div className="similar-item-meta">
                <span
                  className="diff-badge"
                  style={{ background: `${sColor}1a`, color: sColor }}
                >
                  {s.difficulty ?? "?"}
                </span>
                <span className="meta-muted">{s.meta_short}</span>
                <button
                  type="button"
                  className={added ? "select-btn selected" : "select-btn"}
                  onClick={() => toggle(s.question_id)}
                >
                  {added ? "제거" : "담기"}
                </button>
              </div>
              <QuestionContent segments={s.content_segments} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
