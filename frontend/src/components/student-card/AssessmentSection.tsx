import { useState } from "react";
import {
  addQualitativeAssessment, addQuantityAssessment, type StudentDashboard,
} from "../../api/students";
import { todayLocalISO } from "../../utils/date";
import Expander from "../questions/Expander";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

const GRADE_OPTIONS = ["A", "B", "C", "D"] as const;

export default function AssessmentSection({ sid, dashboard, onUpdate }: Props) {
  const { quantity_grade_counts, latest_qualitative } = dashboard;

  const [aqDate, setAqDate] = useState(todayLocalISO());
  const [aqGrade, setAqGrade] = useState<(typeof GRADE_OPTIONS)[number]>("A");
  const [aqNote, setAqNote] = useState("");
  const [aqSaving, setAqSaving] = useState(false);

  const [alDate, setAlDate] = useState(todayLocalISO());
  const [sl1, setSl1] = useState(3);
  const [sl2, setSl2] = useState(3);
  const [sl3, setSl3] = useState(3);
  const [sl4, setSl4] = useState(3);
  const [alNote, setAlNote] = useState("");
  const [alSaving, setAlSaving] = useState(false);

  async function handleQuantSave() {
    setAqSaving(true);
    try {
      const d = await addQuantityAssessment(sid, { eval_date: aqDate, grade: aqGrade, note: aqNote.trim() || null });
      onUpdate(d);
      setAqNote("");
    } finally {
      setAqSaving(false);
    }
  }

  async function handleQualSave() {
    setAlSaving(true);
    try {
      const d = await addQualitativeAssessment(sid, {
        eval_date: alDate, note_completion: sl1, written_completion: sl2,
        textbook_marking: sl3, second_solve_reason: sl4, note: alNote.trim() || null,
      });
      onUpdate(d);
      setAlNote("");
    } finally {
      setAlSaving(false);
    }
  }

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">5. 과제 정밀평가</h2>
      <p className="sc-caption">
        정량(매일 A/B/C/D)은 처방 갱신 신호, 정성(월 2회 4항목)은 자기학습 자세 추적.
      </p>

      <Expander summary="평가 가이드 (각 항목 의미 + 운영법)">
        <div className="sc-guide">
          <p><b>정량 (매일, A~D)</b> — 그날 숙제 했나</p>
          <ul>
            <li>A 100% 완료 + 풀이 흔적 깔끔</li>
            <li>B 완료했지만 일부 미흡</li>
            <li>C 절반만 풀었거나 풀이 부실</li>
            <li>D 거의 안 함</li>
          </ul>
          <p>→ 3일 연속 C/D 면 보호자 알림. A 80% 이상이면 숙제량 ↑</p>
          <p><b>정성 (월 2회, 1~5점)</b> — 공부 습관이 잡혔나</p>
          <ul>
            <li>① 풀이노트 완성도 — 답만 적혀있으면 1점</li>
            <li>② 서술형 완성도 — ∵∴ 논증 완성 여부</li>
            <li>③ 교재표시 습관 — ★△형광✓ 마킹 시스템</li>
            <li>④ 2차 풀이 후 틀린 이유 작성 — 개념/조건/전략/계산/시간 5종 원인</li>
          </ul>
        </div>
      </Expander>

      <Expander summary="정량 평가 (매일)">
        <div className="sc-form">
          <label>평가일<input type="date" value={aqDate} onChange={(e) => setAqDate(e.target.value)} /></label>
          <div className="sc-radio-row">
            {GRADE_OPTIONS.map((g) => (
              <label key={g}>
                <input type="radio" checked={aqGrade === g} onChange={() => setAqGrade(g)} />
                {g}
              </label>
            ))}
          </div>
          <label>메모 (선택)<input value={aqNote} onChange={(e) => setAqNote(e.target.value)} placeholder="예: 풀이 빈약, 시간 부족" /></label>
          <button type="button" className="btn-primary" disabled={aqSaving} onClick={handleQuantSave}>
            {aqSaving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>

      <Expander summary="정성 평가 (월 2회 · 4항목)">
        <div className="sc-form">
          <label>평가일<input type="date" value={alDate} onChange={(e) => setAlDate(e.target.value)} /></label>
          <div className="sc-slider-grid">
            {([
              ["풀이노트 완성도", sl1, setSl1], ["서술형 완성도", sl2, setSl2],
              ["교재 표시 습관", sl3, setSl3], ["2차 풀이 후 틀린 이유 작성", sl4, setSl4],
            ] as [string, number, (v: number) => void][]).map(([label, val, setter]) => (
              <label key={label} className="sc-slider">
                <span>{label}: {val}</span>
                <input type="range" min={1} max={5} value={val} onChange={(e) => setter(Number(e.target.value))} />
              </label>
            ))}
          </div>
          <label>메모 (선택)<input value={alNote} onChange={(e) => setAlNote(e.target.value)} /></label>
          <button type="button" className="btn-primary" disabled={alSaving} onClick={handleQualSave}>
            {alSaving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>

      {quantity_grade_counts.length === 0 ? (
        <p className="sc-empty">최근 4주 정량 평가 기록 없음.</p>
      ) : (
        <div className="sc-metric-row">
          {quantity_grade_counts.map((g) => (
            <div key={g.grade} className="sc-metric">
              <span>{g.grade} 등급</span>
              <b>{g.count}건</b>
              <small>{g.pct !== null ? `${g.pct.toFixed(0)}%` : "-"}</small>
            </div>
          ))}
        </div>
      )}

      {latest_qualitative && (
        <div className="sc-assessment-latest">
          <p className="sc-caption"><b>최근 정성 평가 ({latest_qualitative.eval_date})</b></p>
          <div className="sc-metric-row">
            <div className="sc-metric"><span>풀이노트</span><b>{latest_qualitative.note_completion}/5</b></div>
            <div className="sc-metric"><span>서술형</span><b>{latest_qualitative.written_completion}/5</b></div>
            <div className="sc-metric"><span>교재 표시</span><b>{latest_qualitative.textbook_marking}/5</b></div>
            <div className="sc-metric"><span>2차 풀이 이유</span><b>{latest_qualitative.second_solve_reason}/5</b></div>
          </div>
          {latest_qualitative.note && <p className="sc-caption">{latest_qualitative.note}</p>}
        </div>
      )}
    </section>
  );
}
