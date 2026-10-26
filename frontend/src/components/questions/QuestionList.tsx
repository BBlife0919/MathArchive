import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent, type Modifier,
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
  // 넘겨주면 "유사" 버튼이 카드 안에서 펼치는 대신 이 콜백으로 question_id를
  // 보고한다 — 부모가 화면 한쪽에 스크롤 가능한 전용 유사문항 패널(드로어)을
  // 띄울 때 씀(2026-10-26, 문항이 많은 미리보기 화면에서 요청됨).
  onOpenSimilarDrawer?: (id: number) => void;
  // 드로어 모드에서, 지금 드로어가 보여주고 있는 문항 id — 버튼 활성 표시용.
  similarDrawerOpenId?: number | null;
}

// 세로 목록(list)에서는 위아래로만 움직이면 충분하고, 가로 흔들림을 없애면
// 드래그 중 체감 반응도 더 또렷해진다(2026-10-24 "버벅인다" 피드백 대응).
const restrictToVerticalAxis: Modifier = ({ transform }) => ({ ...transform, x: 0 });

export default function QuestionList({
  items, selectedIds, onToggleSelect, sortable, onReorder, layout = "grid",
  onOpenSimilarDrawer, similarDrawerOpenId,
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
      onOpenSimilarDrawer={onOpenSimilarDrawer ? () => onOpenSimilarDrawer(q.question_id) : undefined}
      isSimilarDrawerOpen={similarDrawerOpenId === q.question_id}
    />
  ));

  if (!sortable) {
    return <div className={containerClass}>{cards}</div>;
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
      modifiers={layout === "list" ? [restrictToVerticalAxis] : undefined}
      // measuring 전략은 dnd-kit 기본값(WhileDragging)을 그대로 둔다 —
      // 문제 카드에는 그림(has_image, loading="lazy")이 섞여 있어, 드래그 중
      // 자동스크롤로 화면에 처음 들어오는 카드는 그제서야 이미지가 로드되며
      // 높이가 바뀐다. "드래그 시작 시 1회만 측정"으로 바꿨다가 그 높이 변화를
      // 못 따라가 엉뚱한 자리에 꽂히는 문제를 검수에서 발견해 되돌렸다
      // (2026-10-24). 렉은 다른 조치(React.memo·전체카드 드래그·autoScroll
      // 가속)로 줄인다.
      // 기본 acceleration(10)로는 리스트 끝까지 드래그로 끌고가는 스크롤이
      // "웹페이지를 손가락으로 아주 천천히 내리는" 속도처럼 느껴진다는
      // 피드백(2026-10-24) — 가속도를 올리고, 가장자리 반응 영역(threshold)도
      // 넓혀 더 일찍·더 빠르게 스크롤되게 한다.
      autoScroll={{ acceleration: 40, threshold: { x: 0.2, y: 0.3 } }}
    >
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
    // 드래그 중인 카드 자신은 트랜지션을 꺼서 포인터를 그대로 따라가게 하고
    // (렉처럼 느껴지던 지연의 큰 부분), 자리를 비켜주는 다른 카드들만 부드럽게
    // 움직인다.
    transition: isDragging ? undefined : transition,
    opacity: isDragging ? 0.6 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={isDragging ? "sortable-card dragging" : "sortable-card"}
      {...attributes}
      {...listeners}
    >
      <div className="drag-handle-bar" aria-hidden="true">⠿ 문제 박스를 어디든 눌러서 드래그</div>
      {children}
    </div>
  );
}
