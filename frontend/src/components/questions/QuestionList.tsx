import type { QuestionCard as QuestionCardData } from "../../api/questions";
import QuestionCard from "./QuestionCard";
import "./QuestionList.css";

interface Props {
  items: QuestionCardData[];
  selectedIds?: Set<number>;
  onToggleSelect?: (id: number) => void;
}

export default function QuestionList({ items, selectedIds, onToggleSelect }: Props) {
  return (
    <div className="question-grid">
      {items.map((q) => (
        <QuestionCard
          key={q.question_id}
          question={q}
          isSelected={selectedIds?.has(q.question_id)}
          onToggleSelect={onToggleSelect ? () => onToggleSelect(q.question_id) : undefined}
        />
      ))}
    </div>
  );
}
