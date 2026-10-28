import { useEffect, useState } from "react";
import { fetchAllTests, type TestListItem } from "../api/tests";
import TestAssignModal from "../components/student-card/TestAssignModal";
import "./WorksheetsPage.css";

// "내 학습지" — 시험지 생성기에서 저장한 학습지를 모아보고, 여기서
// "출제하기"로 반/학생을 골라 배정한다(2026-10-28, 학생관리 안에서
// 즉석 출제하던 흐름을 사용자 피드백으로 뒤집음).
export default function WorksheetsPage() {
  const [tests, setTests] = useState<TestListItem[] | null>(null);
  const [assigningTest, setAssigningTest] = useState<TestListItem | null>(null);

  function reload() {
    fetchAllTests().then((r) => setTests(r.tests)).catch(() => setTests([]));
  }

  useEffect(reload, []);

  return (
    <div className="worksheets-page">
      <h1 className="exam-builder-title">내 학습지</h1>
      <p className="sc-caption">
        문제은행·시험지 탭에서 "학습지로 저장"한 목록입니다. "출제하기"로 반·학생을 골라 배정하세요.
      </p>

      {tests === null ? (
        <p className="sc-empty">불러오는 중...</p>
      ) : tests.length === 0 ? (
        <p className="sc-empty">
          아직 저장된 학습지가 없습니다. "문제은행 · 시험지" 탭에서 문항을 고른 뒤
          STEP2 화면에서 "학습지로 저장"을 눌러주세요.
        </p>
      ) : (
        <div className="worksheets-list">
          {tests.map((t) => (
            <div key={t.test_id} className="worksheet-row">
              <div className="worksheet-row-main">
                <span className="worksheet-title">{t.title}</span>
                <span className="worksheet-meta">
                  {t.chapter_label && <span className="worksheet-chip">{t.chapter_label}</span>}
                  {t.question_count}문항 · {(t.created_at ?? "").slice(0, 10)} ·
                  배정 {t.assigned_count}명
                </span>
              </div>
              <button type="button" className="btn-primary" onClick={() => setAssigningTest(t)}>
                출제하기
              </button>
            </div>
          ))}
        </div>
      )}

      {assigningTest && (
        <TestAssignModal
          testId={assigningTest.test_id}
          testTitle={assigningTest.title}
          onClose={() => setAssigningTest(null)}
          onAssigned={() => { setAssigningTest(null); reload(); }}
        />
      )}
    </div>
  );
}
