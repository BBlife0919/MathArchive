import { useEffect, useState } from "react";
import { fetchQuestionsByIds, type QuestionCard as QuestionCardData } from "../../api/questions";
import { useSelection } from "../../context/SelectionContext";
import QuestionList from "../questions/QuestionList";
import PdfOptionsForm from "./PdfOptionsForm";
import BookOptionsForm from "./BookOptionsForm";
import "./ExamPreviewPanel.css";

export type PdfMode = "exam" | "book";

interface Props {
  pdfMode: PdfMode;
  onPdfModeChange: (mode: PdfMode) => void;
}

export default function ExamPreviewPanel({ pdfMode, onPdfModeChange }: Props) {
  const { selectedIds, toggle } = useSelection();
  const [items, setItems] = useState<QuestionCardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ids = Array.from(selectedIds);

  useEffect(() => {
    if (ids.length === 0) {
      setItems([]);
      return;
    }
    setLoading(true);
    setError(null);
    fetchQuestionsByIds(ids)
      .then((res) => setItems(res.items))
      .catch(() => setError("불러오는 중 오류가 발생했습니다."))
      // eslint-disable-next-line react-hooks/exhaustive-deps
      .finally(() => setLoading(false));
    // ids 배열은 매 렌더 새 참조라 selectedIds.size + 정렬된 join 값으로 의존성 고정
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Array.from(selectedIds).sort((a, b) => a - b).join(",")]);

  if (selectedIds.size === 0) {
    return <p className="empty-state">문제 목록에서 버튼으로 문제를 추가해주세요.</p>;
  }

  const totalPoints = items.reduce((sum, q) => sum + (q.points ?? 0), 0);

  return (
    <div className="exam-preview">
      <div className="exam-preview-list">
        <p className="result-caption">
          {loading ? "불러오는 중..." : `${items.length}문항 선택됨${totalPoints ? ` · 총 배점: ${totalPoints.toFixed(1)}점` : ""}`}
        </p>
        {error && <p className="exam-builder-error">{error}</p>}
        {!loading && !error && (
          <QuestionList items={items} selectedIds={selectedIds} onToggleSelect={toggle} />
        )}
      </div>
      <div className="exam-preview-sidebar">
        <div className="pdf-mode-toggle">
          <button
            type="button" className={pdfMode === "exam" ? "tab-btn active" : "tab-btn"}
            onClick={() => onPdfModeChange("exam")}
          >
            시험지 PDF
          </button>
          <button
            type="button" className={pdfMode === "book" ? "tab-btn active" : "tab-btn"}
            onClick={() => onPdfModeChange("book")}
          >
            교재 PDF
          </button>
        </div>
        {pdfMode === "exam" ? (
          <PdfOptionsForm questionIds={ids} />
        ) : (
          <BookOptionsForm questionIds={ids} />
        )}
      </div>
    </div>
  );
}
