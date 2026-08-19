import { useEffect, useState } from "react";
import { fetchQuestionsByIds, type QuestionCard as QuestionCardData } from "../../api/questions";
import { useSelection } from "../../context/SelectionContext";
import QuestionList from "../questions/QuestionList";
import PdfOptionsForm from "./PdfOptionsForm";
import BookOptionsForm from "./BookOptionsForm";
import LivePreviewPanel from "./LivePreviewPanel";
import "./ExamPreviewPanel.css";

export type PdfMode = "exam" | "book";

interface Props {
  pdfMode: PdfMode;
  onPdfModeChange: (mode: PdfMode) => void;
}

export default function ExamPreviewPanel({ pdfMode, onPdfModeChange }: Props) {
  const { selectedIds, order, toggle, reorder } = useSelection();
  const [items, setItems] = useState<QuestionCardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // 카드를 한 번이라도 드래그하면 이후 미리보기·PDF 순서를 "직접 순서"로
  // 고정한다. 그 전까지는 기존과 동일하게 단원·난이도 자동 정렬을 쓴다.
  // 순서 개념이 의미 있는 시험지(exam) 모드에서만 켠다 — 교재(book) 모드는
  // 챕터별로 묶어 표지/디바이더를 만들기 때문에 임의 순서를 반영하지 않는다.
  const [manualOrder, setManualOrder] = useState(false);
  const preserveOrder = manualOrder && pdfMode === "exam";

  const ids = preserveOrder ? order : Array.from(selectedIds);

  useEffect(() => {
    if (ids.length === 0) {
      setItems([]);
      return;
    }
    setLoading(true);
    setError(null);
    fetchQuestionsByIds(ids, preserveOrder)
      .then((res) => setItems(res.items))
      .catch(() => setError("불러오는 중 오류가 발생했습니다."))
      // eslint-disable-next-line react-hooks/exhaustive-deps
      .finally(() => setLoading(false));
    // ids 배열은 매 렌더 새 참조라 join 값으로 의존성 고정
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ids.join(","), preserveOrder]);

  function handleReorder(newOrder: number[]) {
    setManualOrder(true);
    // newOrder는 현재 화면에 로드된 카드 기준이라, DB에서 이미 지워진 등의
    // 이유로 items에 안 뜬 선택 항목이 order(context)에 남아있었다면
    // newOrder엔 빠진다 — 드래그 한 번으로 그 항목이 조용히 선택 해제되지
    // 않도록 끝에 그대로 이어붙여 보존한다.
    const missing = order.filter((id) => !newOrder.includes(id));
    reorder([...newOrder, ...missing]);
  }

  if (selectedIds.size === 0) {
    return <p className="empty-state">문제 목록에서 버튼으로 문제를 추가해주세요.</p>;
  }

  const totalPoints = items.reduce((sum, q) => sum + (q.points ?? 0), 0);

  return (
    <div className="exam-preview">
      <div className="exam-preview-list">
        <p className="result-caption">
          {loading ? "불러오는 중..." : `${items.length}문항 선택됨${totalPoints ? ` · 총 배점: ${totalPoints.toFixed(1)}점` : ""}`}
          {pdfMode === "exam" && (manualOrder ? " · 직접 순서" : " · 자동 정렬(드래그로 순서 변경 가능)")}
        </p>
        {error && <p className="exam-builder-error">{error}</p>}
        {!loading && !error && (
          <QuestionList
            items={items} selectedIds={selectedIds} onToggleSelect={toggle}
            sortable={pdfMode === "exam"} onReorder={handleReorder}
          />
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
          <PdfOptionsForm questionIds={ids} preserveOrder={preserveOrder} />
        ) : (
          <BookOptionsForm questionIds={ids} />
        )}
        {pdfMode === "exam" ? (
          <LivePreviewPanel items={items} questionIds={ids} preserveOrder={preserveOrder} />
        ) : (
          <p className="live-preview-unavailable">
            교재 표지·챕터 구성은 미리보기가 지원되지 않습니다 — 다운로드 후 확인해주세요.
          </p>
        )}
      </div>
    </div>
  );
}
