import { useEffect, useState } from "react";
import { fetchLayoutPreview, type LayoutPage } from "../../api/exam";
import type { QuestionCard as QuestionCardData } from "../../api/questions";
import QuestionContent from "../content/QuestionContent";
import "./LivePreviewPanel.css";

interface Props {
  items: QuestionCardData[];
  questionIds: number[];
  preserveOrder: boolean;
}

// Playwright PDF는 매 요청 새 브라우저를 띄우는 무거운 파이프라인이라
// 라이브 미리보기로 쓸 수 없다. 대신 실제 인쇄 배치를 계산하는 순수
// 파이썬 로직(app/pdf_engine.py 의 estimate_layout/paginate)만 얇게
// 재사용하는 /api/exam/layout-preview 를 짧은 디바운스로 호출해,
// 이미 로드된 문항 데이터(items)를 기존 KaTeX 렌더 스택으로 그린다.
const DEBOUNCE_MS = 250;

export default function LivePreviewPanel({ items, questionIds, preserveOrder }: Props) {
  const [pages, setPages] = useState<LayoutPage[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (questionIds.length === 0) {
      setPages([]);
      setError(null);
      return;
    }
    let cancelled = false;
    const timer = setTimeout(() => {
      fetchLayoutPreview({ question_ids: questionIds, preserve_order: preserveOrder })
        .then((res) => {
          if (cancelled) return;
          setPages(res.pages);
          setError(null);
        })
        .catch(() => {
          if (!cancelled) setError("미리보기를 불러오지 못했습니다.");
        });
    }, DEBOUNCE_MS);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [questionIds.join(","), preserveOrder]);

  if (questionIds.length === 0) return null;

  const byId = new Map(items.map((q) => [q.question_id, q]));

  return (
    <div className="live-preview">
      <p className="live-preview-caption">실시간 미리보기 (실제 인쇄 배치 기준, 참고용)</p>
      {error && <p className="live-preview-error">{error}</p>}
      {pages.map((page, pi) => (
        <div key={pi} className="live-preview-page">
          <div className="live-preview-page-label">페이지 {pi + 1}</div>
          <div className="live-preview-columns">
            {page.columns.map((col, ci) => (
              <div key={ci} className="live-preview-col">
                {col.slots.map((slot) => {
                  const q = byId.get(slot.question_id);
                  if (!q) return null;
                  return (
                    <div key={slot.question_id} className="live-preview-slot">
                      <div className="live-preview-slot-meta">{q.meta_short}</div>
                      <QuestionContent segments={q.content_segments} />
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
