import { useEffect, useState } from "react";
import {
  downloadExamPdf, fetchExamHtmlPreview, type ExamPaperSize, type ExamPdfRequest,
} from "../../api/exam";
import { triggerDownload } from "../../utils/download";
import { TEMPLATE_OPTIONS, type TemplateId } from "./templates";
import "./PdfOptionsForm.css";

interface Props {
  questionIds: number[];
  preserveOrder?: boolean;
  // 실물 미리보기는 이제 이 폼 안이 아니라 STEP2 왼쪽(큰 화면)에 떠 있다.
  // 폼은 자기 설정값이 바뀔 때마다 "지금 이 설정으로 미리보기 다시 그려줘"를
  // 부모(ExamPreviewPanel)에 보고만 하고, 실제 렌더는 부모가 한다.
  onPreviewChange: (fetchHtml: (() => Promise<string>) | null, depsKey: string) => void;
}

export default function PdfOptionsForm({ questionIds, preserveOrder = false, onPreviewChange }: Props) {
  const [template, setTemplate] = useState<TemplateId>("default");
  const [title, setTitle] = useState("수학 시험지");
  const [showSubtitle, setShowSubtitle] = useState(false);
  const [subtitle, setSubtitle] = useState("");
  const [includeSource, setIncludeSource] = useState(true);
  const [includeLogo, setIncludeLogo] = useState(false);
  const [showPoints, setShowPoints] = useState(false);
  const [showDifficulty, setShowDifficulty] = useState(false);
  const [paperSize, setPaperSize] = useState<ExamPaperSize>("A4");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request: ExamPdfRequest = {
    question_ids: questionIds,
    title,
    subtitle: showSubtitle ? subtitle : null,
    include_source: includeSource,
    include_logo: includeLogo,
    preserve_order: preserveOrder,
    show_points: showPoints,
    show_difficulty: showDifficulty,
    paper_size: paperSize,
  };
  const depsKey = JSON.stringify(request);

  useEffect(() => {
    onPreviewChange(
      questionIds.length > 0 ? () => fetchExamHtmlPreview(request) : null,
      depsKey,
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [depsKey]);

  async function handleDownload() {
    setGenerating(true);
    setError(null);
    try {
      const blob = await downloadExamPdf(request);
      triggerDownload(blob, "exam.pdf");
    } catch {
      setError("PDF 생성 중 오류가 발생했습니다.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="pdf-options">
      <div className="pdf-section-title">용지 · 디자인</div>
      <label className="pdf-field">
        <span>학습지 템플릿</span>
        <select value={template} onChange={(e) => setTemplate(e.target.value as TemplateId)}>
          {TEMPLATE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </label>
      <div className="pdf-field">
        <span>용지 크기</span>
        <div className="pdf-paper-size">
          {(["A4", "A3"] as ExamPaperSize[]).map((size) => (
            <button
              key={size}
              type="button"
              className={paperSize === size ? "pdf-paper-btn active" : "pdf-paper-btn"}
              onClick={() => setPaperSize(size)}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      <div className="pdf-section-title">문구</div>
      <label className="pdf-field">
        <span>제목</span>
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
      </label>

      <label className="pdf-toggle">
        <input
          type="checkbox" checked={showSubtitle}
          onChange={(e) => setShowSubtitle(e.target.checked)}
        />
        부제 표시
      </label>
      {showSubtitle && (
        <input
          type="text" className="pdf-subtitle-input"
          placeholder="예: 2026학년도 1학기 중간대비"
          value={subtitle} onChange={(e) => setSubtitle(e.target.value)}
        />
      )}

      <label className="pdf-toggle">
        <input
          type="checkbox" checked={includeLogo}
          onChange={(e) => setIncludeLogo(e.target.checked)}
        />
        로고 표시
      </label>

      <div className="pdf-section-title">문제지 표시</div>
      <label className="pdf-toggle">
        <input
          type="checkbox" checked={!includeSource}
          onChange={(e) => setIncludeSource(!e.target.checked)}
        />
        출처 숨기기 (학교·연도·학기 표시 안 함)
      </label>
      <label className="pdf-toggle">
        <input
          type="checkbox" checked={showPoints}
          onChange={(e) => setShowPoints(e.target.checked)}
        />
        배점 표시
      </label>
      <label className="pdf-toggle">
        <input
          type="checkbox" checked={showDifficulty}
          onChange={(e) => setShowDifficulty(e.target.checked)}
        />
        난이도 표시
      </label>

      <div className="pdf-save-buttons">
        <button
          type="button" className="btn-secondary pdf-hwpx-btn"
          disabled
          title="HWPX 저장은 준비 중입니다."
        >
          HWPX 저장 (준비 중)
        </button>
        <button
          type="button" className="btn-primary pdf-download-btn"
          disabled={generating || questionIds.length === 0}
          onClick={handleDownload}
        >
          {generating ? "PDF 생성 중..." : "PDF 저장"}
        </button>
      </div>

      {error && <p className="pdf-error">{error}</p>}
    </div>
  );
}
