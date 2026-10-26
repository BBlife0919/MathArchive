import { useEffect, useState } from "react";
import { fetchQuestionsByIds, type QuestionCard as QuestionCardData } from "../../api/questions";
import { useSelection } from "../../context/SelectionContext";
import QuestionList from "../questions/QuestionList";
import Expander from "../questions/Expander";
import RealPagePreview from "./RealPagePreview";
import PdfOptionsForm from "./PdfOptionsForm";
import BookOptionsForm from "./BookOptionsForm";
import SimilarDrawer from "./SimilarDrawer";
import SortMenu, { sortQuestionIds, type SortCriterion } from "./SortMenu";
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
  const [sortCriterion, setSortCriterion] = useState<SortCriterion | null>(null);
  // 유사문항 전용 드로어(화면 왼쪽 고정) — 문항이 많은 이 화면에서는 카드
  // 안에 펼치는 대신 따로 스크롤할 수 있는 패널로 보여달라는 요청
  // (2026-10-26). SimilarDrawer.tsx 참고.
  const [similarDrawerFor, setSimilarDrawerFor] = useState<number | null>(null);

  // 실물 미리보기는 이제 이 패널 왼쪽(큰 화면)에서 그린다 — PdfOptionsForm/
  // BookOptionsForm은 자기 설정이 바뀔 때마다 이 콜백으로 "다시 그려줘"만
  // 보고하고, 실제 fetch+렌더는 여기서 한다.
  const [previewFetch, setPreviewFetch] = useState<(() => Promise<string>) | null>(null);
  const [previewDepsKey, setPreviewDepsKey] = useState("");
  function handlePreviewChange(fetchHtml: (() => Promise<string>) | null, depsKey: string) {
    setPreviewFetch(() => fetchHtml);
    setPreviewDepsKey(depsKey);
  }
  // 시험지↔교재 탭 전환 시 이전 모드의 미리보기가 한 렌더 동안 잔상으로
  // 남지 않도록 즉시 비운다 — 새로 마운트되는 폼의 effect가 곧 다시 채운다.
  useEffect(() => {
    setPreviewFetch(null);
    setPreviewDepsKey("");
  }, [pdfMode]);

  const ids = preserveOrder ? order : Array.from(selectedIds);

  useEffect(() => {
    if (ids.length === 0) {
      setItems([]);
      return;
    }
    // 이미 로드된 문항이면(제거·드래그 재정렬처럼 집합의 부분집합/순서만
    // 바뀐 경우) 서버 재요청 없이 즉시 반영 — 매번 재요청하면 로딩 중
    // QuestionList가 통째로 unmount돼 "제거 누를 때마다 새로고침되는"
    // 것처럼 보이는 문제가 있었다(2026-09-19 발견).
    const currentMap = new Map(items.map((it) => [it.question_id, it]));
    const missingIds = ids.filter((id) => !currentMap.has(id));
    if (missingIds.length === 0) {
      setItems(ids.map((id) => currentMap.get(id)!));
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

  function handleSort(criterion: SortCriterion) {
    setSortCriterion(criterion);
    handleReorder(sortQuestionIds(items, criterion));
  }

  if (selectedIds.size === 0) {
    return <p className="empty-state">문제 목록에서 버튼으로 문제를 추가해주세요.</p>;
  }

  const totalPoints = items.reduce((sum, q) => sum + (q.points ?? 0), 0);

  return (
    <div className="exam-preview">
      <SimilarDrawer
        questionId={similarDrawerFor}
        onClose={() => setSimilarDrawerFor(null)}
      />
      <div className="exam-preview-main">
        <p className="result-caption">
          {loading ? "불러오는 중..." : `${items.length}문항 선택됨${totalPoints ? ` · 총 배점: ${totalPoints.toFixed(1)}점` : ""}`}
          {pdfMode === "exam" && (manualOrder ? " · 직접 순서" : " · 자동 정렬(드래그로 순서 변경 가능)")}
        </p>
        {error && <p className="exam-builder-error">{error}</p>}
        <Expander summary={`문항 목록 (${items.length}문항 · 보기 · 순서 변경 · 제거)`}>
          {!loading && !error && (
            <>
              {pdfMode === "exam" && items.length > 1 && (
                <div className="question-list-toolbar">
                  <SortMenu value={sortCriterion} onSelect={handleSort} />
                </div>
              )}
              <QuestionList
                items={items} selectedIds={selectedIds} onToggleSelect={toggle}
                sortable={pdfMode === "exam"} onReorder={handleReorder}
                layout="list"
                onOpenSimilarDrawer={setSimilarDrawerFor}
                similarDrawerOpenId={similarDrawerFor}
              />
            </>
          )}
        </Expander>
        <RealPagePreview fetchHtml={previewFetch} depsKey={previewDepsKey} />
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
          <PdfOptionsForm questionIds={ids} preserveOrder={preserveOrder} onPreviewChange={handlePreviewChange} />
        ) : (
          <BookOptionsForm questionIds={ids} onPreviewChange={handlePreviewChange} />
        )}
      </div>
    </div>
  );
}
