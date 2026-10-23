import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type ReactNode,
} from "react";

const STORAGE_KEY = "mathdb_bookmarked_question_ids";

interface BookmarkContextValue {
  bookmarkedIds: Set<number>;
  order: number[];
  count: number;
  toggle: (id: number) => void;
  remove: (id: number) => void;
  clear: () => void;
}

const BookmarkContext = createContext<BookmarkContextValue | undefined>(undefined);

function dedupePreserveOrder(ids: number[]): number[] {
  const seen = new Set<number>();
  const out: number[] = [];
  for (const id of ids) {
    if (!seen.has(id)) {
      seen.add(id);
      out.push(id);
    }
  }
  return out;
}

function loadFromStorage(): number[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as number[];
    return dedupePreserveOrder(arr);
  } catch {
    return [];
  }
}

// SelectionContext(시험지 담기)와 같은 패턴 — 브라우저 로컬저장소에 보관되는
// "책갈피함". 문제 하나 보다가 바로 담지는 않고 일단 모아뒀다가 나중에
// 한꺼번에 검토/담기 위한 용도라 선택(SelectionContext)과는 별개 목록이다.
export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [order, setOrder] = useState<number[]>(() => loadFromStorage());
  const bookmarkedIds = useMemo(() => new Set(order), [order]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
  }, [order]);

  const toggle = useCallback((id: number) => {
    setOrder((prev) => (
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    ));
  }, []);

  const remove = useCallback((id: number) => {
    setOrder((prev) => prev.filter((x) => x !== id));
  }, []);

  const clear = useCallback(() => setOrder([]), []);

  const value = useMemo(
    () => ({ bookmarkedIds, order, count: order.length, toggle, remove, clear }),
    [bookmarkedIds, order, toggle, remove, clear],
  );

  return (
    <BookmarkContext.Provider value={value}>{children}</BookmarkContext.Provider>
  );
}

export function useBookmark(): BookmarkContextValue {
  const ctx = useContext(BookmarkContext);
  if (!ctx) throw new Error("useBookmark must be used within BookmarkProvider");
  return ctx;
}
