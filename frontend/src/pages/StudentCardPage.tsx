import { useEffect, useState } from "react";
import {
  fetchStudentDashboard, fetchStudents, fetchStudentTemplates,
  type StudentBasic, type StudentDashboard, type StudentTemplateItem,
} from "../api/students";
import Expander from "../components/questions/Expander";
import BasicInfoSection from "../components/student-card/BasicInfoSection";
import PrismSection from "../components/student-card/PrismSection";
import SelfPredictSection from "../components/student-card/SelfPredictSection";
import ProgressSection from "../components/student-card/ProgressSection";
import AssessmentSection from "../components/student-card/AssessmentSection";
import ManagementLogSection from "../components/student-card/ManagementLogSection";
import "./StudentCardPage.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string;

export default function StudentCardPage() {
  const [students, setStudents] = useState<StudentBasic[] | null>(null);
  const [sid, setSid] = useState<number | null>(null);
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [templates, setTemplates] = useState<StudentTemplateItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStudents()
      .then((list) => {
        setStudents(list);
        if (list.length > 0) setSid(list[0].student_id);
      })
      .catch(() => setStudents([]));
    fetchStudentTemplates().then((res) => setTemplates(res.items)).catch(() => setTemplates([]));
  }, []);

  useEffect(() => {
    if (sid === null) return;
    setLoading(true);
    setError(null);
    fetchStudentDashboard(sid)
      .then(setDashboard)
      .catch(() => setError("불러오는 중 오류가 발생했습니다."))
      .finally(() => setLoading(false));
  }, [sid]);

  if (students === null) {
    return <div className="student-card-page"><p className="sc-empty">불러오는 중...</p></div>;
  }

  if (students.length === 0) {
    return (
      <div className="student-card-page">
        <p className="sc-empty">등록된 학생이 없습니다. 클리닉 페이지에서 먼저 등록하세요.</p>
      </div>
    );
  }

  return (
    <div className="student-card-page">
      <aside className="student-card-sidebar">
        <h2 className="student-card-sidebar-title">학생</h2>
        <label className="sc-form">
          <select value={sid ?? undefined} onChange={(e) => setSid(Number(e.target.value))}>
            {students.map((s) => (
              <option key={s.student_id} value={s.student_id}>
                [{s.school ?? "?"}] {s.name} ({s.grade ?? "?"}학년)
              </option>
            ))}
          </select>
        </label>

        <hr className="filter-divider" />
        <p className="sc-caption">
          PRISM 5스펙트럼:<br />
          - <b>P</b> 계산정확성 (Precision)<br />
          - <b>R</b> 조건해석 (Reading)<br />
          - <b>I</b> 개념내재 (Inclusion)<br />
          - <b>S</b> 전략선택 (Strategy)<br />
          - <b>M</b> 시간관리 (Management)<br />
          → 이해(RIS) vs 수행(PM)
        </p>

        <hr className="filter-divider" />
        <Expander summary="학생용 양식 다운로드">
          <p className="sc-caption">매번 같은 양식을 인쇄해서 학생에게 나눠주세요.</p>
          {templates.filter((t) => t.available).map((t) => (
            <a
              key={t.filename}
              className="student-card-template-btn"
              href={`${API_BASE}${t.url}`}
              download={t.filename}
            >
              {t.label}
            </a>
          ))}
        </Expander>
      </aside>

      <main className="student-card-main">
        <h1 className="exam-builder-title">학생 카드</h1>
        <p className="sc-caption">
          한 명 = 한 장. 진도 · PRISM 진단 · 자가예측 · 보호자 연락이 한 화면에 누적되고, 상담·컨설팅 시 바로 꺼내 씁니다.
        </p>

        {error && <p className="exam-builder-error">{error}</p>}
        {loading && !dashboard && <p className="sc-empty">불러오는 중...</p>}

        {dashboard && sid !== null && (
          <>
            <BasicInfoSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            <PrismSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            <SelfPredictSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            <ProgressSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            <AssessmentSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            <ManagementLogSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
          </>
        )}
      </main>
    </div>
  );
}
