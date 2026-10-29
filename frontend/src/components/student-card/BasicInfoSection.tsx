import { useState } from "react";
import { deleteStudent, updateStudentBasic, type StudentDashboard } from "../../api/students";
import Expander from "../questions/Expander";
import "./sections.css";

interface Props {
  sid: number;
  dashboard: StudentDashboard;
  onUpdate: (d: StudentDashboard) => void;
  // 학생 삭제 성공 시 부모가 선택을 해제하고 반 트리를 새로고침한다.
  onDeleted?: () => void;
}

export default function BasicInfoSection({ sid, dashboard, onUpdate, onDeleted }: Props) {
  const { student, clinic_count } = dashboard;
  const [name, setName] = useState(student.name);
  const [school, setSchool] = useState(student.school ?? "");
  const [grade, setGrade] = useState(student.grade ?? 1);
  const [className, setClassName] = useState(student.class_name ?? "");
  const [note, setNote] = useState(student.note ?? "");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function handleSave() {
    if (!name.trim()) return;
    setSaving(true);
    try {
      const d = await updateStudentBasic(sid, {
        name: name.trim(),
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

  async function handleDelete() {
    const ok = window.confirm(
      `"${student.name}" 학생을 삭제할까요? 학생관리·반 목록에서 더 이상 보이지 않게 됩니다.`,
    );
    if (!ok) return;
    setDeleting(true);
    try {
      await deleteStudent(sid);
      onDeleted?.();
    } finally {
      setDeleting(false);
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
          <label>이름<input value={name} onChange={(e) => setName(e.target.value)} /></label>
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
          <div className="sc-form-actions">
            <button
              type="button" className="btn-primary"
              disabled={saving || !name.trim()} onClick={handleSave}
            >
              {saving ? "저장 중..." : "저장"}
            </button>
            <button
              type="button" className="btn-danger-ghost"
              disabled={deleting} onClick={handleDelete}
            >
              {deleting ? "삭제 중..." : "학생 삭제"}
            </button>
          </div>
        </div>
      </Expander>
    </section>
  );
}
