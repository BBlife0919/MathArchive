import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext, rectSortingStrategy, verticalListSortingStrategy,
  useSortable, arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { ReactNode } from "react";
import type { QuestionCard as QuestionCardData } from "../../api/questions";
import QuestionCard from "./QuestionCard";
import "./QuestionList.css";

interface Props {
  items: QuestionCardData[];
  selectedIds?: Set<number>;
  onToggleSelect?: (id: number) => void;
  sortable?: boolean;
  onReorder?: (newOrder: number[]) => void;
  // "grid"(기본, 여러 열로 카드 나열 — 검색결과 훑어보기용) vs
  // "list"(한 열로 폭 넓게 — 담은 문제 미리보기처럼 정독이 필요한 화면용).
  // 카드 폭이 좁으면 박스/선지 줄바꿈이 잦아져 가독성이 떨어진다는 피드백으로
  // 추가(2026-09-19).
  layout?: "grid" | "list";
}

export default function QuestionList({
  items, selectedIds, onToggleSelect, sortable, onReorder, layout = "grid",
}: Props) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }));
  const containerClass = layout === "list" ? "question-list-single" : "question-grid";

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id || !onReorder) return;
    const ids = items.map((q) => q.question_id);
    const oldIndex = ids.indexOf(active.id as number);
    const newIndex = ids.indexOf(over.id as number);
    if (oldIndex === -1 || newIndex === -1) return;
    onReorder(arrayMove(ids, oldIndex, newIndex));
  }

  const cards = items.map((q) => (
    <QuestionCard
      key={q.question_id}
      question={q}
      isSelected={selectedIds?.has(q.question_id)}
      onToggleSelect={onToggleSelect ? () => onToggleSelect(q.question_id) : undefined}
    />
  ));

  if (!sortable) {
    return <div className={containerClass}>{cards}</div>;
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext
        items={items.map((q) => q.question_id)}
        strategy={layout === "list" ? verticalListSortingStrategy : rectSortingStrategy}
      >
        <div className={containerClass}>
          {items.map((q, i) => (
            <SortableCard key={q.question_id} id={q.question_id}>
              {cards[i]}
            </SortableCard>
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}

function SortableCard({ id, children }: { id: number; children: ReactNode }) {
  const {
    attributes, listeners, setNodeRef, transform, transition, isDragging,
  } = useSortable({ id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="sortable-card">
      <button
        type="button" className="drag-handle-bar" aria-label="드래그로 순서 변경"
        {...attributes} {...listeners}
      >
        ⠿ 드래그로 순서 변경
      </button>
      {children}
    </div>
  );
}
