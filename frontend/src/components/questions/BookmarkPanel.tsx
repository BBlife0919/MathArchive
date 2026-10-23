import { useEffect, useState } from "react";
import { fetchQuestionsByIds, type QuestionCard as QuestionCardData } from "../../api/questions";
import { useBookmark } from "../../context/BookmarkContext";
import { useSelection } from "../../context/SelectionContext";
import QuestionList from "./QuestionList";
import "./BookmarkPanel.css";

interface Props {
  open: boolean;
  onClose: () => void;
}

// 문제 카드의 "책갈피" 버튼으로 모아둔 문제들을 한 화면에서 훑어보고,
// 필요한 것만 골라 시험지 선택(SelectionContext)으로 옮기는 보관함.
// "내가 저장하고 싶은 문제들 모아놓는 곳"(2026-10-24 요청)을 담당한다.
export default function BookmarkPanel({ open, onClose }: Props) {
  const { order, count, clear } = useBookmark();
  const { bulkAdd } = useSelection();
  const [items, setItems] = useState<QuestionCardData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    if (order.length === 0) {
      setItems([]);
      return;
    }
    setLoading(true);
    fetchQuestionsByIds(order, true)
      .then((res) => setItems(res.items))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, order.join(",")]);

  if (!open) return null;

  return (
    <div className="bookmark-modal-backdrop" onMouseDown={onClose}>
      <div className="bookmark-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="bookmark-modal-header">
          <h2>책갈피함 ({count})</h2>
          <button type="button" className="bookmark-modal-close" onClick={onClose} aria-label="닫기">×</button>
        </div>

        <div className="bookmark-modal-body">
          {count === 0 ? (
            <p className="empty-state">
              아직 책갈피한 문제가 없습니다. 문제 카드의 "☆ 책갈피" 버튼으로 모아보세요.
            </p>
          ) : loading ? (
            <p className="empty-state">불러오는 중...</p>
          ) : (
            <QuestionList items={items} layout="list" />
          )}
        </div>

        {count > 0 && (
          <div className="bookmark-modal-footer">
            <span>{count}문항 담김</span>
            <div className="bookmark-modal-actions">
              <button type="button" className="btn-secondary" onClick={clear}>전체 비우기</button>
              <button
                type="button" className="btn-primary"
                onClick={() => { bulkAdd(order); onClose(); }}
              >
                전체 시험지에 담기
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
