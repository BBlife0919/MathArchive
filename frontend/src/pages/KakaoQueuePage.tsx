import { useEffect, useState } from "react";
import {
  approveDraft, createDraft, deleteDraft, fetchApproved, fetchDrafts, fetchKakaoStudents,
  fetchSendLogs, revertDraft,
  type ApprovedItem, type DraftItem, type SendLogItem, type StudentOption,
} from "../api/kakao";
import { ApiError } from "../api/client";
import "./KakaoQueuePage.css";

function nextFridayISO(): string {
  // Python 원본: (4 - date.today().weekday()) % 7, weekday() 는 월=0..일=6 (금=4).
  // JS Date.getDay() 는 일=0..토=6 (금=5) 이므로 5 를 기준으로 환산.
  const d = new Date();
  const offset = (5 - d.getDay() + 7) % 7;
  d.setDate(d.getDate() + offset);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export default function KakaoQueuePage() {
  const [students, setStudents] = useState<StudentOption[] | null>(null);
  const [drafts, setDrafts] = useState<DraftItem[]>([]);
  const [approved, setApproved] = useState<ApprovedItem[]>([]);
  const [logs, setLogs] = useState<SendLogItem[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function loadAll() {
    fetchDrafts().then(setDrafts).catch(() => setDrafts([]));
    fetchApproved().then(setApproved).catch(() => setApproved([]));
    fetchSendLogs().then(setLogs).catch(() => setLogs([]));
  }

  useEffect(() => {
    fetchKakaoStudents().then(setStudents).catch(() => setStudents([]));
    loadAll();
  }, []);

  // ── 1. 신규 draft 생성 폼 ──────────────────────────────
  const [selSid, setSelSid] = useState<number | null>(null);
  const [selPhone, setSelPhone] = useState("");
  const [selTemplate, setSelTemplate] = useState("WEEKLY_REPORT_V1");
  const [selScheduled, setSelScheduled] = useState(nextFridayISO());
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (students && students.length > 0 && selSid === null) setSelSid(students[0].student_id);
  }, [students, selSid]);

  async function handleCreateDraft() {
    setError(null);
    setMessage(null);
    if (!selPhone.trim()) {
      setError("학부모 전화번호 입력 필수");
      return;
    }
    if (!selScheduled) {
      setError("발송 예정일 입력 필수");
      return;
    }
    if (selSid === null) return;
    setCreating(true);
    try {
      await createDraft({
        student_id: selSid,
        target_phone: selPhone.trim(),
        template_code: selTemplate.trim(),
        scheduled_at: selScheduled,
      });
      const name = students?.find((s) => s.student_id === selSid)?.name ?? "";
      setMessage(`${name} draft 생성됨`);
      loadAll();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "생성 중 오류가 발생했습니다.");
    } finally {
      setCreating(false);
    }
  }

  if (students === null) {
    return <div className="kakao-page"><p className="sc-empty">불러오는 중...</p></div>;
  }

  return (
    <div className="kakao-page">
      <h1 className="exam-builder-title">카톡 승인 큐</h1>
      <p className="sc-caption">
        AI 가 학생별 데이터로 draft 를 만들고, 강사가 1문장 추가 후 승인하면 금요일 17시 cron 이
        솔라피로 자동 발송합니다.
      </p>
      {message && <p className="clinic-success-text">{message}</p>}
      {error && <p className="kakao-error-text">{error}</p>}

      <section className="sc-section">
        <h2 className="sc-section-title">1. 신규 draft 생성</h2>
        {students.length === 0 ? (
          <p className="sc-empty">등록된 학생이 없습니다. 학생카드 페이지에서 먼저 등록하세요.</p>
        ) : (
          <div className="sc-form">
            <div className="sc-form-row">
              <label>
                학생
                <select value={selSid ?? undefined} onChange={(e) => setSelSid(Number(e.target.value))}>
                  {students.map((s) => (
                    <option key={s.student_id} value={s.student_id}>{s.name}</option>
                  ))}
                </select>
              </label>
              <label>
                학부모 카톡 전화번호
                <input
                  type="text" placeholder="01012345678" value={selPhone}
                  onChange={(e) => setSelPhone(e.target.value)}
                />
              </label>
              <label>
                템플릿 코드
                <input type="text" value={selTemplate} onChange={(e) => setSelTemplate(e.target.value)} />
              </label>
            </div>
            <label>
              발송 예정일
              <input type="date" value={selScheduled} onChange={(e) => setSelScheduled(e.target.value)} />
            </label>
            <button type="button" className="btn-primary" disabled={creating} onClick={handleCreateDraft}>
              {creating ? "생성 중..." : "AI draft 생성 + 큐 적재"}
            </button>
          </div>
        )}
      </section>

      <hr className="filter-divider" />

      <section className="sc-section">
        <h2 className="sc-section-title">2. 승인 대기 (draft) — 강사 1문장 필수</h2>
        {drafts.length === 0 ? (
          <p className="sc-empty">승인 대기 항목이 없습니다.</p>
        ) : (
          drafts.map((d) => <DraftCard key={d.queue_id} draft={d} onChanged={loadAll} />)
        )}
      </section>

      <hr className="filter-divider" />

      <section className="sc-section">
        <h2 className="sc-section-title">3. 승인됨 (approved) — 발송 대기</h2>
        {approved.length === 0 ? (
          <p className="sc-empty">승인된 항목이 없습니다.</p>
        ) : (
          <>
            <table className="sc-table">
              <thead>
                <tr><th>예정일</th><th>학생</th><th>전화번호</th><th>강사 코멘트</th></tr>
              </thead>
              <tbody>
                {approved.map((a) => (
                  <tr key={a.queue_id}>
                    <td>{a.scheduled_at.slice(0, 10)}</td>
                    <td>{a.student_name}</td>
                    <td>{a.target_phone}</td>
                    <td>{(a.instructor_note ?? "").slice(0, 40)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <RevertForm items={approved} onChanged={loadAll} />
          </>
        )}
      </section>

      <hr className="filter-divider" />

      <section className="sc-section">
        <h2 className="sc-section-title">4. 발송 결과 (최근 20건)</h2>
        {logs.length === 0 ? (
          <p className="sc-empty">발송 기록이 없습니다.</p>
        ) : (
          <table className="sc-table">
            <thead>
              <tr><th>상태</th><th>학생</th><th>전화번호</th><th>발송 시각</th><th>솔라피 MSG ID</th><th>에러</th></tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.queue_id}>
                  <td>{l.status === "sent" ? "발송" : "실패"}</td>
                  <td>{l.student_name}</td>
                  <td>{l.target_phone}</td>
                  <td>{l.sent_at ? l.sent_at.slice(0, 19) : "-"}</td>
                  <td>{l.solapi_msg_id ?? "-"}</td>
                  <td>{(l.error_log ?? "").slice(0, 50)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

function DraftCard({ draft, onChanged }: { draft: DraftItem; onChanged: () => void }) {
  const [note, setNote] = useState(draft.instructor_note ?? "");
  const [confirmDel, setConfirmDel] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleApprove() {
    setError(null);
    if (!note.trim()) {
      setError("강사 코멘트가 비어있어 승인할 수 없습니다 (PDF §7-3 룰).");
      return;
    }
    setBusy(true);
    try {
      await approveDraft(draft.queue_id, note.trim());
      onChanged();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "승인 중 오류가 발생했습니다.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    setBusy(true);
    try {
      await deleteDraft(draft.queue_id);
      onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="kakao-draft-card">
      <p className="kakao-draft-card-summary">
        📩 {draft.student_name} · 예정 {draft.scheduled_at.slice(0, 10)} · → {draft.target_phone}
      </p>
      <p className="sc-caption" style={{ fontWeight: 700 }}>AI draft 본문</p>
      <pre className="kakao-draft-body">{draft.ai_draft || "(비어있음)"}</pre>

      <label className="sc-form" style={{ marginTop: 8 }}>
        강사 1문장 (instructor_note) — 미입력 시 승인 불가
        <textarea
          rows={3} value={note} onChange={(e) => setNote(e.target.value)}
          placeholder="예: OO이가 이번 주 인수분해 복합형에서 큰 진전 보였습니다."
        />
      </label>
      {error && <p className="kakao-error-text">{error}</p>}

      <div className="kakao-draft-actions">
        <button type="button" className="btn-primary" disabled={busy} onClick={handleApprove}>승인</button>
        <label className="kakao-confirm-del">
          <input type="checkbox" checked={confirmDel} onChange={(e) => setConfirmDel(e.target.checked)} />
          삭제 확인
        </label>
        {confirmDel && (
          <button type="button" className="btn-secondary" disabled={busy} onClick={handleDelete}>삭제 실행</button>
        )}
      </div>
    </div>
  );
}

function RevertForm({ items, onChanged }: { items: ApprovedItem[]; onChanged: () => void }) {
  const [qid, setQid] = useState<number | "">("");
  const [busy, setBusy] = useState(false);

  async function handleRevert() {
    if (qid === "") return;
    setBusy(true);
    try {
      await revertDraft(qid as number);
      setQid("");
      onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="sc-form-row" style={{ marginTop: 10, alignItems: "flex-end" }}>
      <label>
        승인 취소할 queue_id
        <select value={qid} onChange={(e) => setQid(e.target.value ? Number(e.target.value) : "")}>
          <option value="">선택 안 함</option>
          {items.map((a) => <option key={a.queue_id} value={a.queue_id}>#{a.queue_id}</option>)}
        </select>
      </label>
      <button type="button" className="btn-secondary" disabled={qid === "" || busy} onClick={handleRevert}>
        ↩ draft 로 되돌리기
      </button>
    </div>
  );
}
