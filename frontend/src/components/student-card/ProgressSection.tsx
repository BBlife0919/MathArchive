import { useState } from "react";
import { addProgress, type StudentDashboard } from "../../api/students";
import { todayLocalISO } from "../../utils/date";
import Expander from "../questions/Expander";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

export default function ProgressSection({ sid, dashboard, onUpdate }: Props) {
  const { progress_entries } = dashboard;

  const [logDate, setLogDate] = useState(todayLocalISO());
  const [category, setCategory] = useState<"진도" | "숙제" | "시험">("진도");
  const [chapter, setChapter] = useState("");
  const [title, setTitle] = useState("");
  const [planned, setPlanned] = useState("");
  const [actual, setActual] = useState("");
  const [scoreRaw, setScoreRaw] = useState(0);
  const [scoreMax, setScoreMax] = useState(0);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const d = await addProgress(sid, {
        log_date: logDate, category, chapter: chapter.trim() || null,
        title: title.trim() || null, planned: planned.trim() || null,
        actual: actual.trim() || null,
        score_raw: scoreRaw || null, score_max: scoreMax || null,
        note: note.trim() || null,
      });
      onUpdate(d);
      setChapter(""); setTitle(""); setPlanned(""); setActual(""); setNote("");
      setScoreRaw(0); setScoreMax(0);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">4. 학습 로그 — 진도·숙제·시험</h2>
      <p className="sc-caption">Walk-Run-Fly 트랙 운영을 위해 계획(planned) vs 실제(actual)를 함께 기록합니다.</p>

      <Expander summary="학습 로그 추가">
        <div className="sc-form">
          <label>일자<input type="date" value={logDate} onChange={(e) => setLogDate(e.target.value)} /></label>
          <label>
            카테고리
            <select value={category} onChange={(e) => setCategory(e.target.value as typeof category)}>
              <option value="진도">진도</option>
              <option value="숙제">숙제</option>
              <option value="시험">시험</option>
            </select>
          </label>
          <label>단원/주제<input value={chapter} onChange={(e) => setChapter(e.target.value)} placeholder="예: 인수분해" /></label>
          <label>제목<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="예: 유형 1~10" /></label>
          <div className="sc-form-row">
            <label>계획 (planned)<input value={planned} onChange={(e) => setPlanned(e.target.value)} placeholder="예: 1h / 10문" /></label>
            <label>실제 (actual)<input value={actual} onChange={(e) => setActual(e.target.value)} placeholder="예: 1.2h / 8문" /></label>
          </div>
          <div className="sc-form-row">
            <label>점수 (raw)<input type="number" min={0} value={scoreRaw} onChange={(e) => setScoreRaw(Number(e.target.value))} /></label>
            <label>만점 (max)<input type="number" min={0} value={scoreMax} onChange={(e) => setScoreMax(Number(e.target.value))} /></label>
          </div>
          <label>메모<textarea rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></label>
          <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
            {saving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>

      {progress_entries.length === 0 ? (
        <p className="sc-empty">아직 학습 로그가 없습니다.</p>
      ) : (
        <table className="sc-table">
          <thead>
            <tr><th>날짜</th><th>구분</th><th>단원</th><th>제목</th><th>계획</th><th>실제</th><th>점수</th><th>메모</th></tr>
          </thead>
          <tbody>
            {progress_entries.map((p, i) => (
              <tr key={i}>
                <td>{p.log_date}</td><td>{p.category}</td><td>{p.chapter ?? "-"}</td>
                <td>{p.title ?? "-"}</td><td>{p.planned ?? "-"}</td><td>{p.actual ?? "-"}</td>
                <td>{p.score_display}</td><td>{p.note ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
