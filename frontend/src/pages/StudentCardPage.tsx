import { useEffect, useState } from "react";
import {
  fetchStudentDashboard, fetchStudentTemplates,
  type StudentDashboard, type StudentTemplateItem,
} from "../api/students";
import Expander from "../components/questions/Expander";
import ClassTreeSidebar from "../components/student-card/ClassTreeSidebar";
import AccordionSection from "../components/student-card/AccordionSection";
import BasicInfoSection from "../components/student-card/BasicInfoSection";
import TestManagementSection from "../components/student-card/TestManagementSection";
import PrismSection from "../components/student-card/PrismSection";
import SelfPredictSection from "../components/student-card/SelfPredictSection";
import ProgressSection from "../components/student-card/ProgressSection";
import AssessmentSection from "../components/student-card/AssessmentSection";
import ManagementLogSection from "../components/student-card/ManagementLogSection";
import "./StudentCardPage.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string;

export default function StudentCardPage() {
  const [sid, setSid] = useState<number | null>(null);
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [templates, setTemplates] = useState<StudentTemplateItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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

  return (
    <div className="student-card-page">
      <ClassTreeSidebar selectedId={sid} onSelect={setSid} />

      <main className="student-card-main">
        <div className="student-card-main-header">
          <div>
            <h1 className="exam-builder-title">학생관리</h1>
            <p className="sc-caption">
              왼쪽에서 반을 펼쳐 학생을 고르세요. 진도 · PRISM 진단 · 자가예측 ·
              테스트 채점 · 보호자 연락이 한 학생당 한 화면에 누적됩니다.
            </p>
          </div>
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
        </div>

        {error && <p className="exam-builder-error">{error}</p>}
        {loading && !dashboard && <p className="sc-empty">불러오는 중...</p>}
        {sid === null && !loading && (
          <p className="sc-empty">왼쪽에서 반을 펼쳐 학생을 선택하세요.</p>
        )}

        {dashboard && sid !== null && (
          <>
            <AccordionSection title="1. 기본정보" defaultOpen>
              <BasicInfoSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
            <AccordionSection title="2. TEST 관리 — 채점 · 오답 유사문항">
              <TestManagementSection sid={sid} studentName={dashboard.student.name} />
            </AccordionSection>
            <AccordionSection title="3. PRISM — 강사 임상 평가">
              <PrismSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
            <AccordionSection title="4. 자가예측 격차 — 메타인지 추적">
              <SelfPredictSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
            <AccordionSection title="5. 학습 로그 — 진도·숙제·시험">
              <ProgressSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
            <AccordionSection title="6. 과제 정밀평가">
              <AssessmentSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
            <AccordionSection title="7. 관리 로그 — 보호자·출결·메모">
              <ManagementLogSection sid={sid} dashboard={dashboard} onUpdate={setDashboard} />
            </AccordionSection>
          </>
        )}
      </main>
    </div>
  );
}
