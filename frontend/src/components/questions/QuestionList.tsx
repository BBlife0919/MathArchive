import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext, rectSortingStrategy, useSortable, arrayMove,
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
}

export default function QuestionList({
  items, selectedIds, onToggleSelect, sortable, onReorder,
}: Props) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }));

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
    return <div className="question-grid">{cards}</div>;
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={items.map((q) => q.question_id)} strategy={rectSortingStrategy}>
        <div className="question-grid">
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
