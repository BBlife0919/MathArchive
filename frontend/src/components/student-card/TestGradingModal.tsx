import { useEffect, useState } from "react";
import { fetchTestDetail, gradeTest, type TestDetail, type GradeTestResult } from "../../api/tests";
import { useSelection } from "../../context/SelectionContext";
import QuestionContent from "../content/QuestionContent";
import Expander from "../questions/Expander";
import "./TestGradingModal.css";

interface Props {
  testId: number;
  sid: number;
  studentName: string;
  onClose: () => void;
  onGraded: () => void;
}

// 적녹색약(정도 심함) 규칙 — 참고 이미지의 빨강/초록 O·X 배색을 그대로
// 쓰지 않고 남색=정답 / 주황=오답 2색만 쓴다.
export default function TestGradingModal({ testId, sid, studentName, onClose, onGraded }: Props) {
  const { bulkAdd } = useSelection();
  const [detail, setDetail] = useState<TestDetail | null>(null);
  const [answers, setAnswers] = useState<Record<number, boolean>>({});
  const [activeIdx, setActiveIdx] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<GradeTestResult | null>(null);
  const [addedToSelection, setAddedToSelection] = useState(false);

  useEffect(() => {
    fetchTestDetail(testId, sid).then((d) => {
      setDetail(d);
      setAnswers(d.existing_answers);
    });
  }, [testId, sid]);

  function setAll(correct: boolean) {
    if (!detail) return;
    const next: Record<number, boolean> = {};
    for (const item of detail.items) next[item.question_id] = correct;
    setAnswers(next);
  }

  const allAnswered = detail !== null && detail.items.every((it) => answers[it.question_id] !== undefined);

  async function handleSubmit() {
    if (!detail || !allAnswered) return;
    setSubmitting(true);
    try {
      const res = await gradeTest(
        testId, sid,
        detail.items.map((it) => ({ question_id: it.question_id, is_correct: answers[it.question_id] })),
      );
      setResult(res);
    } finally {
      setSubmitting(false);
    }
  }

  function handleMakeWorksheet() {
    if (!result || result.prescribed_question_ids.length === 0) return;
    bulkAdd(result.prescribed_question_ids);
    setAddedToSelection(true);
  }

  const active = detail?.items[activeIdx] ?? null;

  return (
    <div className="grading-modal-overlay" onClick={onClose}>
      <div className="grading-modal" onClick={(e) => e.stopPropagation()}>
        <header className="grading-modal-header">
          <div>
            <h2>{detail?.title ?? "채점"}</h2>
            <p className="sc-caption">{studentName} 학생</p>
          </div>
          <button type="button" className="grading-modal-close" onClick={onClose}>✕</button>
        </header>

        {detail === null ? (
          <p className="sc-empty">불러오는 중...</p>
        ) : result ? (
          <div className="grading-result">
            <p className="grading-result-score">{result.score} / {result.total}</p>
            {result.wrong_question_ids.length === 0 ? (
              <p className="sc-caption">전부 정답입니다.</p>
            ) : (
              <>
                <p className="sc-caption">
                  오답 {result.wrong_question_ids.length}문항 ·
                  유사문항 추천 {result.prescribed_question_ids.length}문항
                </p>
                <button
                  type="button" className="btn-primary"
                  disabled={result.prescribed_question_ids.length === 0 || addedToSelection}
                  onClick={handleMakeWorksheet}
                >
                  {addedToSelection ? "선택 목록에 추가됨" : "오답학습지 만들기"}
                </button>
                {addedToSelection && (
                  <p className="sc-caption">
                    유사문항 {result.prescribed_question_ids.length}개가 시험지 생성기 선택
                    목록에 담겼습니다. 상단 "문제은행 · 시험지" 탭에서 이어서 만드세요.
                  </p>
                )}
              </>
            )}
            <button type="button" className="btn-secondary" onClick={onGraded}>닫기</button>
          </div>
        ) : (
          <div className="grading-modal-body">
            <div className="grading-list-col">
              <div className="grading-bulk-row">
                <button type="button" className="grading-bulk-btn correct" onClick={() => setAll(true)}>
                  전체 정답
                </button>
                <button type="button" className="grading-bulk-btn wrong" onClick={() => setAll(false)}>
                  전체 오답
                </button>
              </div>
              <div className="grading-list">
                {detail.items.map((item, idx) => (
                  <div
                    key={item.question_id}
                    className={idx === activeIdx ? "grading-list-row active" : "grading-list-row"}
                  >
                    <button
                      type="button" className="grading-list-num"
                      onClick={() => setActiveIdx(idx)}
                    >
                      {idx + 1}번
                    </button>
                    <div className="grading-toggle-group">
                      <button
                        type="button"
                        className={answers[item.question_id] === true ? "grading-toggle correct active" : "grading-toggle correct"}
                        onClick={() => { setAnswers((p) => ({ ...p, [item.question_id]: true })); setActiveIdx(idx); }}
                      >
                        O
                      </button>
                      <button
                        type="button"
                        className={answers[item.question_id] === false ? "grading-toggle wrong active" : "grading-toggle wrong"}
                        onClick={() => { setAnswers((p) => ({ ...p, [item.question_id]: false })); setActiveIdx(idx); }}
                      >
                        X
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button
                type="button" className="btn-primary grading-submit-btn"
                disabled={!allAnswered || submitting}
                onClick={handleSubmit}
              >
                {submitting ? "저장 중..." : allAnswered ? "채점 저장" : "모든 문항을 O/X로 표시하세요"}
              </button>
            </div>

            <div className="grading-preview-col">
              {active && (
                <>
                  <QuestionContent segments={active.content_segments} />
                  {active.choices_text && (
                    <div className="grading-choices">
                      <QuestionContent segments={[{ type: "text", md: active.choices_text }]} />
                    </div>
                  )}
                  <Expander summary="정답 · 해설">
                    <p className="sc-caption">정답: {active.answer_display ?? active.answer ?? "-"}</p>
                    <QuestionContent segments={active.solution_segments} />
                  </Expander>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
