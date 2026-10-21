import { useEffect, useMemo, useState } from "react";
import "./SchoolPickerModal.css";

interface Props {
  open: boolean;
  onClose: () => void;
  regions: string[];
  regionSchools: Record<string, string[]>;
  allSchools: string[];
  selected: string[];
  onApply: (schools: string[]) => void;
}

const ALL_TAB = "전체";

export default function SchoolPickerModal({
  open, onClose, regions, regionSchools, allSchools, selected, onApply,
}: Props) {
  const [draft, setDraft] = useState<string[]>(selected);
  const [activeRegion, setActiveRegion] = useState<string>(ALL_TAB);
  const [search, setSearch] = useState("");

  // 모달 열릴 때마다 현재 적용된 선택값으로 초기화 (이전에 취소했던 임시
  // 상태가 남아있지 않도록).
  useEffect(() => {
    if (open) {
      setDraft(selected);
      setSearch("");
      setActiveRegion(ALL_TAB);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const schoolPool = useMemo(() => {
    const pool = activeRegion === ALL_TAB ? allSchools : (regionSchools[activeRegion] ?? []);
    if (!search.trim()) return pool;
    const q = search.trim();
    return pool.filter((s) => s.includes(q));
  }, [activeRegion, allSchools, regionSchools, search]);

  if (!open) return null;

  function toggle(school: string) {
    setDraft((prev) =>
      prev.includes(school) ? prev.filter((s) => s !== school) : [...prev, school]);
  }

  return (
    <div className="school-modal-backdrop" onMouseDown={onClose}>
      <div className="school-modal" onMouseDown={(e) => e.stopPropagation()}>
        <div className="school-modal-header">
          <h2>학교 선택</h2>
          <button type="button" className="school-modal-close" onClick={onClose} aria-label="닫기">×</button>
        </div>

        <input
          type="text"
          className="school-modal-search"
          placeholder="학교명을 검색해주세요"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="school-modal-region-tabs">
          <button
            type="button"
            className={activeRegion === ALL_TAB ? "region-tab active" : "region-tab"}
            onClick={() => setActiveRegion(ALL_TAB)}
          >
            전체
          </button>
          {regions.map((r) => (
            <button
              key={r}
              type="button"
              className={activeRegion === r ? "region-tab active" : "region-tab"}
              onClick={() => setActiveRegion(r)}
            >
              {r}
            </button>
          ))}
        </div>

        <div className="school-modal-pool-header">
          <span>{activeRegion} 학교 {schoolPool.length}개</span>
          <span className="school-modal-pool-selected">{draft.length}개 선택됨</span>
        </div>

        <div className="school-modal-grid">
          {schoolPool.map((school) => (
            <button
              key={school}
              type="button"
              className={draft.includes(school) ? "school-chip selected" : "school-chip"}
              onClick={() => toggle(school)}
            >
              {school}
            </button>
          ))}
          {schoolPool.length === 0 && (
            <p className="school-modal-empty">검색 결과가 없습니다.</p>
          )}
        </div>

        <div className="school-modal-footer">
          <span>
            {draft.length}개 학교 선택됨 ·{" "}
            <button type="button" className="school-modal-reset" onClick={() => setDraft([])}>
              초기화
            </button>
          </span>
          <div className="school-modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>취소</button>
            <button type="button" className="btn-primary" onClick={() => onApply(draft)}>선택 완료</button>
          </div>
        </div>
      </div>
    </div>
  );
}
