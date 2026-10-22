import "./ExamModeSelect.css";

interface Props {
  onSelectType: () => void;
  onSelectSchoolTerm: () => void;
}

export default function ExamModeSelect({ onSelectType, onSelectSchoolTerm }: Props) {
  return (
    <div className="mode-select">
      <button type="button" className="mode-card mode-card-type" onClick={onSelectType}>
        <span className="mode-card-eyebrow">단원 · 유형으로 고르기</span>
        <span className="mode-card-title">유형별 출제</span>
        <span className="mode-card-desc">
          과목·단원을 고른 뒤 자동으로 뽑거나, 문제를 직접 골라 시험지를 만듭니다.
        </span>
        <span className="mode-card-cta">시작하기 →</span>
      </button>

      <button type="button" className="mode-card mode-card-school" onClick={onSelectSchoolTerm}>
        <span className="mode-card-eyebrow">학교 기출로 고르기</span>
        <span className="mode-card-title">학교 · 학기별 출제</span>
        <span className="mode-card-desc">
          지역·학교·학년·학기를 고르면, 실제 치러진 시험지 목록에서 바로 선택합니다.
        </span>
        <span className="mode-card-cta">시작하기 →</span>
      </button>
    </div>
  );
}
