import { useEffect, useMemo, useState } from "react";
import "./SchoolPickerModal.css";

interface Props {
  open: boolean;
  onClose: () => void;
  provinces: string[];
  provinceDistricts: Record<string, string[]>;
  regionSchools: Record<string, string[]>;
  allSchools: string[];
  selected: string[];
  onApply: (schools: string[]) => void;
}

// 지역 접두어를 뗀 district 표시용 라벨. "경기가평군"→"가평군",
// 구 미상 bare row("대구"→province 자신과 동일한 district)는 떼면 빈
// 문자열이 되니 원본 그대로 되돌린다.
function districtLabel(province: string, district: string): string {
  if (district.startsWith(province)) {
    const rest = district.slice(province.length);
    return rest || district;
  }
  return district;
}

export default function SchoolPickerModal({
  open, onClose, provinces, provinceDistricts, regionSchools, allSchools, selected, onApply,
}: Props) {
  const [draft, setDraft] = useState<string[]>(selected);
  const [activeProvince, setActiveProvince] = useState<string | null>(null);
  const [activeDistrict, setActiveDistrict] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  // 모달 열릴 때마다 현재 적용된 선택값/탐색 상태를 초기화 (이전에
  // 취소했던 임시 상태가 남아있지 않도록).
  useEffect(() => {
    if (open) {
      setDraft(selected);
      setSearch("");
      setActiveProvince(null);
      setActiveDistrict(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const districts = activeProvince ? (provinceDistricts[activeProvince] ?? []) : [];

  function selectProvince(p: string) {
    setActiveProvince(p);
    const ds = provinceDistricts[p] ?? [];
    // 구/시/군이 1개뿐인 지역(세종·제주·광주 등 단일 행정)은 한 번 더
    // 탭하게 하지 않고 바로 학교 목록까지 보여준다.
    setActiveDistrict(ds.length === 1 ? ds[0] : null);
  }

  const searching = search.trim() !== "";
  const searchResults = useMemo(() => {
    if (!searching) return [];
    const q = search.trim();
    return allSchools.filter((s) => s.includes(q));
  }, [searching, search, allSchools]);

  const districtSchools = activeDistrict ? (regionSchools[activeDistrict] ?? []) : [];

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

        <div className="school-modal-body">
          {searching ? (
            <>
              <div className="school-modal-pool-header">
                <span>검색 결과 {searchResults.length}개</span>
                <span className="school-modal-pool-selected">{draft.length}개 선택됨</span>
              </div>
              <div className="school-modal-grid">
                {searchResults.map((school) => (
                  <button
                    key={school}
                    type="button"
                    className={draft.includes(school) ? "school-chip selected" : "school-chip"}
                    onClick={() => toggle(school)}
                  >
                    {school}
                  </button>
                ))}
                {searchResults.length === 0 && (
                  <p className="school-modal-empty">검색 결과가 없습니다.</p>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="school-modal-province-tabs">
                {provinces.map((p) => (
                  <button
                    key={p}
                    type="button"
                    className={activeProvince === p ? "province-tab active" : "province-tab"}
                    onClick={() => selectProvince(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>

              {!activeProvince && (
                <p className="school-modal-hint">시/도를 먼저 선택해주세요.</p>
              )}

              {activeProvince && (
                <div className="school-modal-district-box">
                  <div className="school-modal-district-title">{activeProvince} 지역</div>
                  <div className="school-modal-district-tabs">
                    {districts.map((d) => (
                      <button
                        key={d}
                        type="button"
                        className={activeDistrict === d ? "district-tab active" : "district-tab"}
                        onClick={() => setActiveDistrict(d)}
                      >
                        {districtLabel(activeProvince, d)}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {activeProvince && !activeDistrict && (
                <p className="school-modal-hint">구/시/군을 선택해주세요.</p>
              )}

              {activeDistrict && (
                <>
                  <div className="school-modal-pool-header">
                    <span>{districtLabel(activeProvince!, activeDistrict)} 학교 {districtSchools.length}개</span>
                    <span className="school-modal-pool-selected">{draft.length}개 선택됨</span>
                  </div>
                  <div className="school-modal-grid">
                    {districtSchools.map((school) => (
                      <button
                        key={school}
                        type="button"
                        className={draft.includes(school) ? "school-chip selected" : "school-chip"}
                        onClick={() => toggle(school)}
                      >
                        {school}
                      </button>
                    ))}
                    {districtSchools.length === 0 && (
                      <p className="school-modal-empty">등록된 기출이 없습니다.</p>
                    )}
                  </div>
                </>
              )}
            </>
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
