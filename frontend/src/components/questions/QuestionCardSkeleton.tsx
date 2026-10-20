import "./QuestionCardSkeleton.css";

// 검색/필터 변경 시 카드 자리를 미리 잡아 체감 로딩속도를 높이기 위한 스켈레톤.
// 실제 QuestionCard 와 동일한 그리드 셀에 들어가도록 높이만 비슷하게 맞춘다.
export default function QuestionCardSkeleton() {
  return (
    <div className="question-card-skeleton" aria-hidden="true">
      <div className="skeleton-row">
        <span className="skeleton-bar skeleton-badge" />
        <span className="skeleton-bar skeleton-select" />
      </div>
      <span className="skeleton-bar skeleton-line" style={{ width: "95%" }} />
      <span className="skeleton-bar skeleton-line" style={{ width: "80%" }} />
      <span className="skeleton-bar skeleton-line" style={{ width: "60%" }} />
    </div>
  );
}

export function QuestionGridSkeleton({ count = 15 }: { count?: number }) {
  return (
    <div className="question-grid">
      {Array.from({ length: count }, (_, i) => (
        <QuestionCardSkeleton key={i} />
      ))}
    </div>
  );
}
