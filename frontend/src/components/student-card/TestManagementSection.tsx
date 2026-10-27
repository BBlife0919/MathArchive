import { useEffect, useState } from "react";
import { fetchStudentTests, type StudentTestItem } from "../../api/tests";
import { fetchPendingRetries, type PendingRetry } from "../../api/clinic";
import { useSelection } from "../../context/SelectionContext";
import { createTest } from "../../api/tests";
import Expander from "../questions/Expander";
import TestGradingModal from "./TestGradingModal";
import "./TestManagementSection.css";

interface Props {
  sid: number;
  classId: number | null;
  studentName: string;
}

export default function TestManagementSection({ sid, classId, studentName }: Props) {
  const { order } = useSelection();
  const [tests, setTests] = useState<StudentTestItem[] | null>(null);
  const [pendings, setPendings] = useState<PendingRetry[]>([]);
  const [gradingTestId, setGradingTestId] = useState<number | null>(null);
  const [newTitle, setNewTitle] = useState("");
  const [creating, setCreating] = useState(false);

  function reload() {
    fetchStudentTests(sid).then((r) => setTests(r.tests)).catch(() => setTests([]));
    fetchPendingRetries()
      .then((list) => setPendings(list.filter((p) => p.student_id === sid)))
      .catch(() => setPendings([]));
  }

  useEffect(reload, [sid]);

  async function handleCreate() {
    if (!newTitle.trim() || classId === null || order.length === 0) return;
    setCreating(true);
    try {
      await createTest({
        title: newTitle.trim(), class_id: classId, question_ids: order,
      });
      setNewTitle("");
      reload();
    } finally {
      setCreating(false);
    }
  }

  return (
    <>
      {classId === null && (
        <p className="sc-empty">
          이 학생은 아직 반 배정이 안 되어 테스트를 출제할 수 없습니다.
          왼쪽 "미배정"에서 반을 먼저 배정하세요.
        </p>
      )}

      <Expander summary="+ 새 테스트 출제 (현재 선택된 문항 사용)">
        <p className="sc-caption">
          문제은행·시험지 탭에서 먼저 문항을 선택하세요
          (현재 {order.length}문항 선택됨). 같은 반 학생 전체에게 배정됩니다.
        </p>
        <div className="sc-form">
          <label>
            테스트명
            <input
              value={newTitle} onChange={(e) => setNewTitle(e.target.value)}
              placeholder="예: HALF TEST_1(이차함수)"
            />
          </label>
          <button
            type="button" className="btn-primary"
            disabled={creating || !newTitle.trim() || classId === null || order.length === 0}
            onClick={handleCreate}
          >
            {creating ? "등록 중..." : `출제 (${order.length}문항)`}
          </button>
        </div>
      </Expander>

      {tests === null ? (
        <p className="sc-empty">불러오는 중...</p>
      ) : tests.length === 0 ? (
        <p className="sc-empty">배정된 테스트가 없습니다.</p>
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
