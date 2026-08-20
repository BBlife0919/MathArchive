import { useState } from "react";
import { downloadBookPdf, type CoverStyle } from "../../api/exam";
import { triggerDownload } from "../../utils/download";
import "./PdfOptionsForm.css";

interface Props {
  questionIds: number[];
}

function orNull(s: string): string | null {
  const trimmed = s.trim();
  return trimmed ? trimmed : null;
}

// 챕터모드: 기존 그대로(챕터 디바이더 + 문항별 적응형 half/full).
// 일반모드: 디바이더 없이 연속 배치, 전 문항에 강제로 half(2단 4분할=페이지당
// 4문항)/full(2단 2분할=페이지당 2문항) 적용.
type BookLayoutMode = "chapter" | "flat_half" | "flat_full";
const LAYOUT_LABELS: Record<BookLayoutMode, string> = {
  chapter: "챕터모드 (단원별 디바이더)",
  flat_half: "일반모드 (2단 4분할)",
  flat_full: "일반모드 (2단 2분할)",
};

export default function BookOptionsForm({ questionIds }: Props) {
  const [layoutMode, setLayoutMode] = useState<BookLayoutMode>("chapter");
  const [title, setTitle] = useState("수학 교재");
  const [showSubtitle, setShowSubtitle] = useState(false);
  const [subtitle, setSubtitle] = useState("");
  const [includeSource, setIncludeSource] = useState(true);
  const [includeLogo, setIncludeLogo] = useState(false);

  const [coverStyle, setCoverStyle] = useState<CoverStyle>("final");
  // final/diagonal 표지 필드는 원본 Streamlit 위젯처럼 서로 별개 상태 —
  // 스타일 전환해도 이전에 입력한 값이 사라지지 않는다.
  const [finalKicker, setFinalKicker] = useState("MATH WORKBOOK · 2026");
  const [finalBigWord, setFinalBigWord] = useState("FINAL");
  const [finalFooterMain, setFinalFooterMain] = useState("Algebra Final Workbook · 2026");
  const [finalFooterSub, setFinalFooterSub] = useState("필수유형으로 끝내는 기말 마무리");
  const [diagKicker, setDiagKicker] = useState("2학기 중간대비");
  const [diagSubject, setDiagSubject] = useState("공통수학2");
  const [diagLevel, setDiagLevel] = useState("난이도 상");
  const [diagFooterMain, setDiagFooterMain] = useState("MATHOLOGY · 2026");

  const [showKicker, setShowKicker] = useState(true);
  const [kickerMark, setKickerMark] = useState("#01");
  const [kickerText, setKickerText] = useState("MATHOLOGY");

  const [dividerMetaTop, setDividerMetaTop] = useState("대수 1학기 기말 · FINAL");
  const [dividerFooterTitle, setDividerFooterTitle] = useState("대수 1학기 기말고사 · 필수유형 FINAL");
  const [dividerFooterSub, setDividerFooterSub] = useState("이영우 T");

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setGenerating(true);
    setError(null);
    try {
      const blob = await downloadBookPdf({
        question_ids: questionIds,
        title,
        subtitle: showSubtitle ? orNull(subtitle) : null,
        include_source: includeSource,
        include_logo: includeLogo,
        cover_style: coverStyle,
        cover_kicker: coverStyle === "final" ? orNull(finalKicker) : orNull(diagKicker),
        cover_big_word: coverStyle === "final" ? orNull(finalBigWord) : null,
        cover_footer_main: coverStyle === "final" ? orNull(finalFooterMain) : orNull(diagFooterMain),
        cover_footer_sub: coverStyle === "final" ? orNull(finalFooterSub) : null,
        dcov_subject: coverStyle === "diagonal" ? orNull(diagSubject) : null,
        dcov_level: coverStyle === "diagonal" ? orNull(diagLevel) : null,
        kicker_mark: showKicker ? orNull(kickerMark) : null,
        kicker_text: showKicker ? orNull(kickerText) : null,
        divider_meta_top: orNull(dividerMetaTop),
        divider_footer_title: orNull(dividerFooterTitle),
        divider_footer_sub: orNull(dividerFooterSub),
        book_mode: layoutMode === "chapter" ? "chapter" : "flat",
        flat_layout: layoutMode === "flat_full" ? "full" : "half",
      });
      triggerDownload(blob, "book.pdf");
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
        <input type="checkbox" checked={showSubtitle} onChange={(e) => setShowSubtitle(e.target.checked)} />
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
        <input type="checkbox" checked={includeSource} onChange={(e) => setIncludeSource(e.target.checked)} />
        출처 삽입 (학교·연도·학기 표시)
      </label>

      <label className="pdf-toggle">
        <input type="checkbox" checked={includeLogo} onChange={(e) => setIncludeLogo(e.target.checked)} />
        로고 표시
      </label>

      <label className="pdf-field">
        <span>교재모드</span>
        <select
          value={layoutMode}
          onChange={(e) => setLayoutMode(e.target.value as BookLayoutMode)}
        >
          {(Object.keys(LAYOUT_LABELS) as BookLayoutMode[]).map((m) => (
            <option key={m} value={m}>{LAYOUT_LABELS[m]}</option>
          ))}
        </select>
      </label>

      <div className="pdf-section-title">표지 스타일 & 커스텀</div>
      <div className="question-type-radio">
        <label>
          <input type="radio" checked={coverStyle === "final"} onChange={() => setCoverStyle("final")} />
          FINAL — MATH WORKBOOK (기본)
        </label>
        <label>
          <input type="radio" checked={coverStyle === "diagonal"} onChange={() => setCoverStyle("diagonal")} />
          평면좌표 — 사선 편집형
        </label>
      </div>

      {coverStyle === "final" ? (
        <>
          <label className="pdf-field">
            <span>상단 kicker</span>
            <input type="text" value={finalKicker} onChange={(e) => setFinalKicker(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>가운데 큰 워드</span>
            <input type="text" value={finalBigWord} onChange={(e) => setFinalBigWord(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>좌하단 메인 문구</span>
            <input type="text" value={finalFooterMain} onChange={(e) => setFinalFooterMain(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>좌하단 부제</span>
            <input type="text" value={finalFooterSub} onChange={(e) => setFinalFooterSub(e.target.value)} />
          </label>
        </>
      ) : (
        <>
          <label className="pdf-field">
            <span>상단 kicker (좌측 상단)</span>
            <input type="text" value={diagKicker} onChange={(e) => setDiagKicker(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>우측 대과목명</span>
            <input type="text" value={diagSubject} onChange={(e) => setDiagSubject(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>우측 배지</span>
            <input type="text" value={diagLevel} onChange={(e) => setDiagLevel(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>좌하단 문구</span>
            <input type="text" value={diagFooterMain} onChange={(e) => setDiagFooterMain(e.target.value)} />
          </label>
        </>
      )}

      <label className="pdf-toggle">
        <input type="checkbox" checked={showKicker} onChange={(e) => setShowKicker(e.target.checked)} />
        상단 라벨 표시
      </label>
      {showKicker && (
        <>
          <label className="pdf-field">
            <span>포인트 (주황)</span>
            <input type="text" value={kickerMark} onChange={(e) => setKickerMark(e.target.value)} />
          </label>
          <label className="pdf-field">
            <span>브랜드</span>
            <input type="text" value={kickerText} onChange={(e) => setKickerText(e.target.value)} />
          </label>
        </>
      )}

      <div className="pdf-section-title">챕터 디바이더 메타</div>
      {layoutMode !== "chapter" && (
        <p className="pdf-caption">
          일반모드는 디바이더 페이지가 없어 "우상단"·"좌하단 제목"은 무시되고,
          "좌하단 부제"만 표지 강사명으로 쓰입니다.
        </p>
      )}
      <label className="pdf-field">
        <span>우상단</span>
        <input type="text" value={dividerMetaTop} onChange={(e) => setDividerMetaTop(e.target.value)} />
      </label>
      <label className="pdf-field">
        <span>좌하단 제목</span>
        <input type="text" value={dividerFooterTitle} onChange={(e) => setDividerFooterTitle(e.target.value)} />
      </label>
      <label className="pdf-field">
        <span>좌하단 부제</span>
        <input type="text" value={dividerFooterSub} onChange={(e) => setDividerFooterSub(e.target.value)} />
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
