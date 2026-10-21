import "./DifficultyBar.css";

// 하=1칸, 중=2칸, 상=3칸, 킬=4칸. 색이 아니라 "채운 칸 수"로 구분하므로
// 적녹색약 규칙(색만으로 구분 금지)을 만족한다 — 채움 여부(칠함/테두리만)가
// 1차 구분자, 색은 보조 표시일 뿐이다.
const DIFF_LEVEL: Record<string, number> = { "하": 1, "중": 2, "상": 3, "킬": 4 };
const TOTAL_CELLS = 4;

interface Props {
  difficulty: string | null;
}

export default function DifficultyBar({ difficulty }: Props) {
  const level = DIFF_LEVEL[difficulty ?? ""] ?? 0;
  if (level === 0) return null;

  return (
    <span className="difficulty-bar" aria-label={`난이도 ${difficulty}`} title={`난이도: ${difficulty}`}>
      {Array.from({ length: TOTAL_CELLS }, (_, i) => (
        <span key={i} className={i < level ? "difficulty-bar-cell filled" : "difficulty-bar-cell"} />
      ))}
    </span>
  );
}
