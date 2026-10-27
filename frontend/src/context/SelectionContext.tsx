import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type ReactNode,
} from "react";

const STORAGE_KEY = "mathdb_selected_question_ids";

interface SelectionContextValue {
  selectedIds: Set<number>;
  order: number[];
  count: number;
  toggle: (id: number) => void;
  bulkAdd: (ids: number[]) => void;
  replaceAll: (ids: number[]) => void;
  replaceOne: (oldId: number, newId: number) => void;
  reorder: (newOrder: number[]) => void;
  clear: () => void;
}

const SelectionContext = createContext<SelectionContextValue | undefined>(undefined);

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

function loadOrderFromStorage(): number[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as number[];
    return dedupePreserveOrder(arr);
  } catch {
    return [];
  }
}

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [order, setOrder] = useState<number[]>(() => loadOrderFromStorage());
  const selectedIds = useMemo(() => new Set(order), [order]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
  }, [order]);

  const toggle = useCallback((id: number) => {
    setOrder((prev) => (
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    ));
  }, []);

  const bulkAdd = useCallback((ids: number[]) => {
    setOrder((prev) => dedupePreserveOrder([...prev, ...ids]));
  }, []);

  // main.py의 미니테스트 자동생성처럼 기존 선택을 완전히 대체해야 하는
  // 경우용 (st.session_state.selected_ids = set(picks) 와 동일한 의미).
  const replaceAll = useCallback((ids: number[]) => {
    setOrder(dedupePreserveOrder(ids));
  }, []);

  // 유사문항 "교체" 버튼용 — oldId 자리에 newId 를 끼워넣는다(목록 안
  // 위치 보존, 끝으로 밀려나지 않게).
  const replaceOne = useCallback((oldId: number, newId: number) => {
    setOrder((prev) => {
      // newId 를 이미 다른 경로("추가")로 담아둔 상태면 자기 자리를 이미
      // 가지고 있으니 그대로 두고 oldId 만 뺀다 — map+dedupe 로 처리하면
      // "둘 중 먼저 나오는 위치가 이긴다"는 예측하기 어려운 결과가 된다.
      if (prev.includes(newId)) {
        return prev.filter((x) => x !== oldId);
      }
      if (!prev.includes(oldId)) {
        return [...prev, newId];
      }
      return prev.map((x) => (x === oldId ? newId : x));
    });
  }, []);

  // 시험지 미리보기에서 드래그로 순서를 바꿀 때 씀.
  const reorder = useCallback((newOrder: number[]) => {
    setOrder(dedupePreserveOrder(newOrder));
  }, []);

  const clear = useCallback(() => setOrder([]), []);

  const value = useMemo(
    () => ({
      selectedIds, order, count: order.length,
      toggle, bulkAdd, replaceAll, replaceOne, reorder, clear,
    }),
    [selectedIds, order, toggle, bulkAdd, replaceAll, replaceOne, reorder, clear],
  );

  return (
    <SelectionContext.Provider value={value}>{children}</SelectionContext.Provider>
  );
}

export function useSelection(): SelectionContextValue {
  const ctx = useContext(SelectionContext);
  if (!ctx) throw new Error("useSelection must be used within SelectionProvider");
  return ctx;
}
