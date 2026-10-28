import { useEffect, useState } from "react";
import { fetchStudentTests, type StudentTestItem } from "../../api/tests";
import { fetchPendingRetries, type PendingRetry } from "../../api/clinic";
import Expander from "../questions/Expander";
import TestGradingModal from "./TestGradingModal";
import "./TestManagementSection.css";

interface Props {
  sid: number;
  studentName: string;
}

// 출제(학습지 생성+배정)는 "문제은행·시험지" → "학습지로 저장" → "내 학습지"
// → "출제하기" 흐름으로 옮겨갔다(2026-10-28, 학생관리 안에서 즉석 출제하던
// 걸 사용자 피드백으로 뒤집음). 여기는 이 학생에게 배정된 테스트 목록과
// 채점만 다룬다.
export default function TestManagementSection({ sid, studentName }: Props) {
  const [tests, setTests] = useState<StudentTestItem[] | null>(null);
  const [pendings, setPendings] = useState<PendingRetry[]>([]);
  const [gradingTestId, setGradingTestId] = useState<number | null>(null);

  function reload() {
    fetchStudentTests(sid).then((r) => setTests(r.tests)).catch(() => setTests([]));
    fetchPendingRetries()
      .then((list) => setPendings(list.filter((p) => p.student_id === sid)))
      .catch(() => setPendings([]));
  }

  useEffect(reload, [sid]);

  return (
    <>
      {tests === null ? (
        <p className="sc-empty">불러오는 중...</p>
      ) : tests.length === 0 ? (
        <p className="sc-empty">
          배정된 테스트가 없습니다. "내 학습지" 탭에서 학습지를 출제하면 여기에 뜹니다.
        </p>
      ) : (
        <div className="test-mgmt-list">
          {tests.map((t) => (
            <div key={t.test_id} className="test-mgmt-row">
              <div className="test-mgmt-row-main">
                <span className="test-mgmt-title">{t.title}</span>
                <span className="test-mgmt-meta">
                  {t.chapter_label && <span className="test-mgmt-chip">{t.chapter_label}</span>}
                  {t.question_count}문항 · {(t.created_at ?? "").slice(0, 10)}
                </span>
              </div>
              {t.result_id === null ? (
                <button type="button" className="btn-primary" onClick={() => setGradingTestId(t.test_id)}>
                  채점하기
                </button>
              ) : (
                <div className="test-mgmt-score-group">
                  <span className="test-mgmt-score">{t.score}/{t.total}</span>
                  <button type="button" className="btn-secondary" onClick={() => setGradingTestId(t.test_id)}>
                    재채점
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {pendings.length > 0 && (
        <Expander summary={`오늘 도래한 재도전 (${pendings.length}건)`}>
          {pendings.map((p) => (
            <p key={p.entry_id} className="sc-caption">
              · 오답 {p.wrong_question_id ? `id=${p.wrong_question_id}` : `외부 · ${p.external_label ?? "-"}`}
              {" "}({p.wrong_date}) · 오류 {p.error_code} · 미완료: {p.due_flags.join(", ")}
            </p>
          ))}
        </Expander>
      )}

      {gradingTestId !== null && (
        <TestGradingModal
          testId={gradingTestId}
          sid={sid}
          studentName={studentName}
          onClose={() => setGradingTestId(null)}
          onGraded={() => { setGradingTestId(null); reload(); }}
        />
      )}
    </>
  );
}
