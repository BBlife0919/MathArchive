import { useState } from "react";
import { updateStudentBasic, type StudentDashboard } from "../../api/students";
import Expander from "../questions/Expander";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
}

export default function BasicInfoSection({ sid, dashboard, onUpdate }: Props) {
  const { student, clinic_count } = dashboard;
  const [school, setSchool] = useState(student.school ?? "");
  const [grade, setGrade] = useState(student.grade ?? 1);
  const [className, setClassName] = useState(student.class_name ?? "");
  const [note, setNote] = useState(student.note ?? "");
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const d = await updateStudentBasic(sid, {
        school: school.trim() || null,
        grade,
        class_name: className.trim() || null,
        note: note.trim() || null,
      });
      onUpdate(d);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="sc-section">
      <h2 className="sc-section-title">1. 기본정보</h2>
      <div className="sc-metric-row">
        <div className="sc-metric"><span>이름</span><b>{student.name}</b></div>
        <div className="sc-metric"><span>학교</span><b>{student.school ?? "-"}</b></div>
        <div className="sc-metric">
          <span>학년·반</span>
          <b>{student.grade ?? "?"}학년 {student.class_name ?? ""}</b>
        </div>
        <div className="sc-metric"><span>누적 오답</span><b>{clinic_count}건</b></div>
      </div>

      <Expander summary="기본정보 수정">
        <div className="sc-form">
          <label>학교<input value={school} onChange={(e) => setSchool(e.target.value)} /></label>
          <label>
            학년
            <input
              type="number" min={1} max={6} value={grade}
              onChange={(e) => setGrade(Number(e.target.value))}
            />
          </label>
          <label>반<input value={className} onChange={(e) => setClassName(e.target.value)} /></label>
          <label>메모<textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} /></label>
          <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
            {saving ? "저장 중..." : "저장"}
          </button>
        </div>
      </Expander>
    </section>
  );
}
