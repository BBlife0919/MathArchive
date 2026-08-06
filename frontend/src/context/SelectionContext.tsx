import {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
  type ReactNode,
} from "react";

const STORAGE_KEY = "mathdb_selected_question_ids";

interface SelectionContextValue {
  selectedIds: Set<number>;
  count: number;
  toggle: (id: number) => void;
  bulkAdd: (ids: number[]) => void;
  replaceAll: (ids: number[]) => void;
  clear: () => void;
}

const SelectionContext = createContext<SelectionContextValue | undefined>(undefined);

function loadFromStorage(): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw) as number[];
    return new Set(arr);
  } catch {
    return new Set();
  }
}

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(() => loadFromStorage());

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(selectedIds)));
  }, [selectedIds]);

  const toggle = useCallback((id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }, []);

  const bulkAdd = useCallback((ids: number[]) => {
    setSelectedIds((prev) => new Set([...prev, ...ids]));
  }, []);

  // main.py의 미니테스트 자동생성처럼 기존 선택을 완전히 대체해야 하는
  // 경우용 (st.session_state.selected_ids = set(picks) 와 동일한 의미).
  const replaceAll = useCallback((ids: number[]) => {
    setSelectedIds(new Set(ids));
  }, []);

  const clear = useCallback(() => setSelectedIds(new Set()), []);

  const value = useMemo(
    () => ({ selectedIds, count: selectedIds.size, toggle, bulkAdd, replaceAll, clear }),
    [selectedIds, toggle, bulkAdd, replaceAll, clear],
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
