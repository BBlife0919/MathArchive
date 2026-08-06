import { useState } from "react";
import { downloadExamPdf } from "../../api/exam";
import { triggerDownload } from "../../utils/download";
import "./PdfOptionsForm.css";

interface Props {
  questionIds: number[];
}

export default function PdfOptionsForm({ questionIds }: Props) {
  const [title, setTitle] = useState("수학 시험지");
  const [showSubtitle, setShowSubtitle] = useState(false);
  const [subtitle, setSubtitle] = useState("");
  const [includeSource, setIncludeSource] = useState(true);
  const [includeLogo, setIncludeLogo] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setGenerating(true);
    setError(null);
    try {
      const blob = await downloadExamPdf({
        question_ids: questionIds,
        title,
        subtitle: showSubtitle ? subtitle : null,
        include_source: includeSource,
        include_logo: includeLogo,
      });
      triggerDownload(blob, "exam.pdf");
    } catch {
      setError("PDF 생성 중 오류가 발생했습니다.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="pdf-options">
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
          type="checkbox" checked={includeSource}
          onChange={(e) => setIncludeSource(e.target.checked)}
        />
        출처 삽입 (학교·연도·학기 표시)
      </label>

      <label className="pdf-toggle">
        <input
          type="checkbox" checked={includeLogo}
          onChange={(e) => setIncludeLogo(e.target.checked)}
        />
        로고 표시
      </label>

      <button
        type="button" className="btn-primary pdf-download-btn"
        disabled={generating || questionIds.length === 0}
        onClick={handleDownload}
      >
        {generating ? "PDF 생성 중..." : "PDF 다운로드"}
      </button>

      {error && <p className="pdf-error">{error}</p>}
    </div>
  );
}
