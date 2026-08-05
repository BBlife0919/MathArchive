import { useState, type KeyboardEvent } from "react";

interface Props {
  active: string;
  onApply: (value: string) => void;
  onClear: () => void;
}

export default function QuickSearchBox({ active, onApply, onClear }: Props) {
  const [draft, setDraft] = useState(active);

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") onApply(draft.trim());
  }

  return (
    <div className="quick-search">
      <label className="ms-label">빠른 검색</label>
      <input
        type="text"
        placeholder="예: 수도여고 2023 1학기 기말"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyDown}
        className="quick-search-input"
      />
      <div className="quick-search-buttons">
        <button type="button" className="btn-primary" onClick={() => onApply(draft.trim())}>
          검색
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => { setDraft(""); onClear(); }}
        >
          해제
        </button>
      </div>
      {active && <p className="quick-search-active">🔎 적용 중: {active}</p>}
    </div>
  );
}
