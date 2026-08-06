import { useState } from "react";
import { addSelfPredict, type StudentDashboard } from "../../api/students";
import Expander from "../questions/Expander";
import SelfPredictChart from "../charts/SelfPredictChart";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

const today = () => new Date().toISOString().slice(0, 10);

export default function SelfPredictSection({ sid, dashboard, onUpdate }: Props) {
  const {
    self_predict_entries, self_predict_chart, self_predict_avg_gap,
    self_predict_over_count, self_predict_under_count,
  } = dashboard;

  const [spDate, setSpDate] = useState(today());
  const [title, setTitle] = useState("");
  const [predicted, setPredicted] = useState(80);
  const [actual, setActual] = useState(70);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const d = await addSelfPredict(sid, {
        log_date: spDate, title: title.trim() || null, predicted, actual,
        note: note.trim() || null,
      });
      onUpdate(d);
      setTitle(""); setNote("");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">3. 자가예측 격차 — 메타인지 추적</h2>
      <p className="sc-caption">시험 전 자가예측 점수와 실제 점수의 차이. 격차가 크면 자기평가 능력이 약합니다.</p>

      <Expander summary="자가예측 기록 추가">
        <div className="sc-form">
          <label>시험일<input type="date" value={spDate} onChange={(e) => setSpDate(e.target.value)} /></label>
          <label>시험명<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="예: 인수분해 단원평가" /></label>
          <div className="sc-form-row">
            <label>자가예측 점수<input type="number" min={0} max={100} value={predicted} onChange={(e) => setPredicted(Number(e.target.value))} /></label>
            <label>실제 점수<input type="number" min={0} max={100} value={actual} onChange={(e) => setActual(Number(e.target.value))} /></label>
          </div>
          <label>메모<input value={note} onChange={(e) => setNote(e.target.value)} placeholder="예: 시간관리 실패로 -10" /></label>
          <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
            {saving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>

      {self_predict_entries.length === 0 ? (
        <p className="sc-empty">아직 자가예측 기록이 없습니다.</p>
      ) : (
        <>
          <SelfPredictChart data={self_predict_chart} />
          <div className="sc-metric-row">
            <div className="sc-metric"><span>평균 격차</span><b>{self_predict_avg_gap?.toFixed(1)}점</b></div>
            <div className="sc-metric"><span>과신 (예측&gt;실제)</span><b>{self_predict_over_count}건</b></div>
            <div className="sc-metric"><span>과소 (예측&lt;실제)</span><b>{self_predict_under_count}건</b></div>
          </div>
          <table className="sc-table">
            <thead>
              <tr><th>날짜</th><th>시험</th><th>예측</th><th>실제</th><th>격차</th><th>메모</th></tr>
            </thead>
            <tbody>
              {self_predict_entries.map((e, i) => (
                <tr key={i}>
                  <td>{e.log_date}</td><td>{e.title ?? "-"}</td>
                  <td>{e.predicted}</td><td>{e.actual}</td><td>{e.gap}</td><td>{e.note ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
