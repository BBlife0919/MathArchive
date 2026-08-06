import { useState } from "react";
import { addPrismEval, type StudentDashboard } from "../../api/students";
import Expander from "../questions/Expander";
import PrismRadarChart from "../charts/PrismRadarChart";
import ClinicBarChart from "../charts/ClinicBarChart";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

const today = () => new Date().toISOString().slice(0, 10);

export default function PrismSection({ sid, dashboard, onUpdate }: Props) {
  const { latest_prism, avg_ris, avg_pm, prism_history, clinic_error_distribution } = dashboard;

  const [evalDate, setEvalDate] = useState(today());
  const [sp, setSp] = useState(3);
  const [sr, setSr] = useState(3);
  const [si, setSi] = useState(3);
  const [ss, setSs] = useState(3);
  const [sm, setSm] = useState(3);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const d = await addPrismEval(sid, {
        eval_date: evalDate, score_p: sp, score_r: sr, score_i: si,
        score_s: ss, score_m: sm, note: note.trim() || null,
      });
      onUpdate(d);
      setNote("");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">2. PRISM — 강사 임상 평가</h2>
      <p className="sc-caption">
        매주 30초. 숙제 검사 + 평소 인상으로 5영역 결함도를 1~5점 입력. 1=거의 없음 · 3=보통 · 5=매우 두드러짐
      </p>

      <Expander summary="이번 주 PRISM 평가 입력">
        <div className="sc-form">
          <label>평가일<input type="date" value={evalDate} onChange={(e) => setEvalDate(e.target.value)} /></label>
          <div className="sc-slider-grid">
            {([
              ["P 계산정확성", sp, setSp], ["R 조건해석", sr, setSr], ["I 개념내재", si, setSi],
              ["S 전략선택", ss, setSs], ["M 시간관리", sm, setSm],
            ] as [string, number, (v: number) => void][]).map(([label, val, setter]) => (
              <label key={label} className="sc-slider">
                <span>{label}: {val}</span>
                <input type="range" min={1} max={5} value={val} onChange={(e) => setter(Number(e.target.value))} />
              </label>
            ))}
          </div>
          <label>강사 메모 (선택)<textarea rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></label>
          <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
            {saving ? "저장 중..." : "평가 저장"}
          </button>
        </div>
      </Expander>

      {!latest_prism ? (
        <p className="sc-empty">아직 PRISM 평가 없음. 위 폼에서 첫 평가를 입력하세요.</p>
      ) : (
        <>
          <div className="sc-metric-row">
            <div className="sc-metric"><span>이해 RIS 평균</span><b>{avg_ris?.toFixed(1)}/5</b></div>
            <div className="sc-metric"><span>수행 PM 평균</span><b>{avg_pm?.toFixed(1)}/5</b></div>
            <div className="sc-metric"><span>최근 평가일</span><b>{latest_prism.eval_date}</b></div>
          </div>
          <div className="sc-chart-row">
            <PrismRadarChart score={latest_prism} />
            <div className="sc-score-table">
              <p>P 계산정확성: {latest_prism.score_p}/5</p>
              <p>R 조건해석: {latest_prism.score_r}/5</p>
              <p>I 개념내재: {latest_prism.score_i}/5</p>
              <p>S 전략선택: {latest_prism.score_s}/5</p>
              <p>M 시간관리: {latest_prism.score_m}/5</p>
              {latest_prism.note && <p className="sc-caption">{latest_prism.note}</p>}
            </div>
          </div>
        </>
      )}

      {prism_history.length > 1 && (
        <Expander summary={`최근 평가 이력 (${prism_history.length}건)`}>
          <table className="sc-table">
            <thead>
              <tr><th>날짜</th><th>P</th><th>R</th><th>I</th><th>S</th><th>M</th><th>메모</th></tr>
            </thead>
            <tbody>
              {prism_history.map((h, i) => (
                <tr key={i}>
                  <td>{h.eval_date}</td><td>{h.score_p}</td><td>{h.score_r}</td>
                  <td>{h.score_i}</td><td>{h.score_s}</td><td>{h.score_m}</td>
                  <td>{(h.note ?? "").slice(0, 40)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Expander>
      )}

      {clinic_error_distribution.length > 0 && (
        <Expander summary={`참고 — 클리닉 정밀 기록 누적 분포`}>
          <p className="sc-caption">클리닉 페이지에서 입력한 오답 1건씩의 누적 분포 (참고용).</p>
          <ClinicBarChart data={clinic_error_distribution} />
        </Expander>
      )}
    </section>
  );
}
