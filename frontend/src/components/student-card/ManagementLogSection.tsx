import { useState } from "react";
import { addManagementLog, type StudentDashboard } from "../../api/students";
import Expander from "../questions/Expander";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

const today = () => new Date().toISOString().slice(0, 10);
const LOG_TYPES = ["보호자", "출결", "메모"] as const;
const TABS = ["전체", ...LOG_TYPES] as const;

export default function ManagementLogSection({ sid, dashboard, onUpdate }: Props) {
  const { logs } = dashboard;

  const [mlDate, setMlDate] = useState(today());
  const [mlType, setMlType] = useState<(typeof LOG_TYPES)[number]>("보호자");
  const [summary, setSummary] = useState("");
  const [detail, setDetail] = useState("");
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState<(typeof TABS)[number]>("전체");

  async function handleSave() {
    setSaving(true);
    try {
      const d = await addManagementLog(sid, {
        log_date: mlDate, log_type: mlType,
        summary: summary.trim() || null, detail: detail.trim() || null,
      });
      onUpdate(d);
      setSummary(""); setDetail("");
    } finally {
      setSaving(false);
    }
  }

  const filtered = tab === "전체" ? logs : logs.filter((l) => l.log_type === tab);

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">6. 관리 로그 — 보호자·출결·메모</h2>
      <p className="sc-caption">학부모 신뢰의 핵심. 모든 연락/결석/특이사항을 1줄씩 누적합니다.</p>

      <Expander summary="관리 로그 추가">
        <div className="sc-form">
          <label>일자<input type="date" value={mlDate} onChange={(e) => setMlDate(e.target.value)} /></label>
          <label>
            유형
            <select value={mlType} onChange={(e) => setMlType(e.target.value as typeof mlType)}>
              {LOG_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
          <label>요약 (1줄)<input value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="예: 어머니께 단원평가 결과 공유" /></label>
          <label>상세<textarea rows={3} value={detail} onChange={(e) => setDetail(e.target.value)} /></label>
          <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
            {saving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>

      {logs.length === 0 ? (
        <p className="sc-empty">아직 관리 로그가 없습니다.</p>
      ) : (
        <>
          <div className="tab-bar">
            {TABS.map((t) => (
              <button
                key={t} type="button"
                className={tab === t ? "tab-btn active" : "tab-btn"}
                onClick={() => setTab(t)}
              >
                {t}
              </button>
            ))}
          </div>
          {filtered.length === 0 ? (
            <p className="sc-caption">기록 없음</p>
          ) : (
            filtered.map((l, i) => (
              <div key={i} className="sc-log-card">
                <p className="sc-caption">{l.log_date} · <b>{l.log_type}</b></p>
                <p>{l.summary ?? "(요약 없음)"}</p>
                {l.detail && (
                  <Expander summary="상세">
                    <p>{l.detail}</p>
                  </Expander>
                )}
              </div>
            ))
          )}
        </>
      )}
    </section>
  );
}
