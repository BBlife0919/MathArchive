import { useEffect, useState } from "react";
import {
  createClinicEntry, downloadPrescriptionPdf, fetchClinicMeta, fetchPendingRetries,
  searchClinicQuestions, type ClinicEntryResponse, type ErrorCodeItem,
  type PendingRetry, type QuestionSearchResult, type SourceMode,
} from "../api/clinic";
import { createStudent, fetchStudents, type StudentBasic } from "../api/students";
import { triggerDownload } from "../utils/download";
import { todayLocalISO } from "../utils/date";
import { ApiError } from "../api/client";
import Expander from "../components/questions/Expander";
import QuestionContent from "../components/content/QuestionContent";
import "./ClinicPage.css";

export default function ClinicPage() {
  const [students, setStudents] = useState<StudentBasic[] | null>(null);
  const [sid, setSid] = useState<number | null>(null);
  const [errorCodes, setErrorCodes] = useState<ErrorCodeItem[]>([]);
  const [pendings, setPendings] = useState<PendingRetry[]>([]);

  // 신규 학생 등록
  const [newName, setNewName] = useState("");
  const [newSchool, setNewSchool] = useState("");
  const [newGrade, setNewGrade] = useState(1);
  const [newClass, setNewClass] = useState("");
  const [registering, setRegistering] = useState(false);

  // 오답 입력 폼
  const [sourceMode, setSourceMode] = useState<SourceMode>("db");
  const [searchKw, setSearchKw] = useState("");
  const [searchResults, setSearchResults] = useState<QuestionSearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [picked, setPicked] = useState<QuestionSearchResult | null>(null);
  const [externalLabel, setExternalLabel] = useState("");
  const [errorCode, setErrorCode] = useState("");
  const [keyword, setKeyword] = useState("");
  const [wrongDate, setWrongDate] = useState(todayLocalISO());
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<ClinicEntryResponse | null>(null);
  const [pdfDownloading, setPdfDownloading] = useState(false);

  function loadPendings() {
    fetchPendingRetries().then(setPendings).catch(() => setPendings([]));
  }

  useEffect(() => {
    fetchStudents()
      .then((list) => {
        setStudents(list);
        if (list.length > 0) setSid(list[0].student_id);
      })
      .catch(() => setStudents([]));
    fetchClinicMeta()
      .then((meta) => {
        setErrorCodes(meta.error_codes);
        if (meta.error_codes.length > 0) setErrorCode(meta.error_codes[0].code);
      })
      .catch(() => setErrorCodes([]));
    loadPendings();
  }, []);

  async function handleRegisterStudent() {
    if (!newName.trim()) return;
    setRegistering(true);
    try {
      const s = await createStudent({
        name: newName.trim(), school: newSchool.trim() || null,
        grade: newGrade, class_name: newClass.trim() || null,
      });
      const list = await fetchStudents();
      setStudents(list);
      setSid(s.student_id);
      setNewName(""); setNewSchool(""); setNewClass(""); setNewGrade(1);
    } finally {
      setRegistering(false);
    }
  }

  async function handleSearch() {
    if (!searchKw.trim()) { setSearchResults([]); return; }
    setSearching(true);
    try {
      const res = await searchClinicQuestions(searchKw.trim());
      setSearchResults(res);
      setPicked(null);
    } finally {
      setSearching(false);
    }
  }

  const canSubmit = sid !== null && (
    (sourceMode === "db" && picked !== null)
    || (sourceMode === "external" && externalLabel.trim().length > 0)
  );

  async function handleSubmit() {
    if (!canSubmit || sid === null) return;
    setSubmitting(true);
    setSubmitError(null);
    setResult(null);
    try {
      const res = await createClinicEntry({
        student_id: sid, source_mode: sourceMode,
        wrong_question_id: sourceMode === "db" ? picked!.question_id : null,
        external_label: sourceMode === "external" ? externalLabel.trim() : null,
        error_code: errorCode, keyword, wrong_date: wrongDate,
      });
      setResult(res);
      loadPendings();
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "처방전 생성 중 오류가 발생했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDownloadPdf() {
    if (!result || result.mode !== "db") return;
    setPdfDownloading(true);
    try {
      const subtitle = `${result.student_name} · 오류코드: ${result.error_code} · ` +
        `재도전: D+3 ${result.schedule.d3} / D+7 ${result.schedule.d7} / ` +
        `D+14 ${result.schedule.d14} / D+30 ${result.schedule.d30}`;
      const blob = await downloadPrescriptionPdf(
        result.prescription_question_ids,
        `처방전 — ${result.student_name} (${wrongDate})`,
        subtitle,
      );
      triggerDownload(blob, `prescription_${result.student_name}_${wrongDate}.pdf`);
    } finally {
      setPdfDownloading(false);
    }
  }

  if (students === null) {
    return <div className="clinic-page"><p className="sc-empty">불러오는 중...</p></div>;
  }

  return (
    <div className="clinic-page">
      <aside className="student-card-sidebar">
        <h2 className="student-card-sidebar-title">학생</h2>
        {students.length === 0 ? (
          <p className="sc-caption">등록된 학생이 없습니다. 아래 폼에서 추가하세요.</p>
        ) : (
          <select value={sid ?? undefined} onChange={(e) => setSid(Number(e.target.value))}>
            {students.map((s) => (
              <option key={s.student_id} value={s.student_id}>
                [{s.school ?? "?"}] {s.name} ({s.grade ?? "?"}학년)
              </option>
            ))}
          </select>
        )}

        <Expander summary="신규 학생 등록">
          <div className="sc-form">
            <label>이름<input value={newName} onChange={(e) => setNewName(e.target.value)} /></label>
            <label>학교<input value={newSchool} onChange={(e) => setNewSchool(e.target.value)} placeholder="예: 광명북중" /></label>
            <label>학년<input type="number" min={1} max={6} value={newGrade} onChange={(e) => setNewGrade(Number(e.target.value))} /></label>
            <label>반<input value={newClass} onChange={(e) => setNewClass(e.target.value)} placeholder="예: 3-2" /></label>
            <button type="button" className="btn-primary" disabled={registering || !newName.trim()} onClick={handleRegisterStudent}>
              {registering ? "등록 중..." : "등록"}
            </button>
          </div>
        </Expander>
      </aside>

      <main className="clinic-main">
        <h1 className="exam-builder-title">수학 클리닉</h1>
        <p className="sc-caption">
          오답 1건 → 즉시 인출 3문항 + D+3/7/14/30 재도전 처방전. PRISM 5스펙트럼 진단으로 오답을 정복 궤도에 올립니다.
        </p>

        {students.length === 0 ? (
          <p className="sc-empty">좌측 사이드바에서 학생을 등록/선택하세요.</p>
        ) : (
          <>
            <h2 className="sc-section-title">오답 입력 → 처방전 생성</h2>

            <div className="sc-radio-row">
              <label>
                <input type="radio" checked={sourceMode === "db"} onChange={() => setSourceMode("db")} />
                DB 검색 (MATHOLOGY 적재 문제)
              </label>
              <label>
                <input type="radio" checked={sourceMode === "external"} onChange={() => setSourceMode("external")} />
                외부 문제 (학교 내신지·시판 교재)
              </label>
            </div>

            {sourceMode === "db" ? (
              <div className="clinic-search-row">
                <div className="clinic-search-col">
                  <label className="sc-form">
                    검색어 (학교명·단원·키워드)
                    <div className="clinic-search-input-row">
                      <input
                        value={searchKw} onChange={(e) => setSearchKw(e.target.value)}
                        placeholder="예: 광명북 / 이차함수 / 인수분해"
                        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                      />
                      <button type="button" className="btn-secondary" onClick={handleSearch} disabled={searching}>
                        {searching ? "검색 중..." : "검색"}
                      </button>
                    </div>
                  </label>
                  {searchKw.trim() && !searching && searchResults.length === 0 && (
                    <p className="clinic-error-text">검색 결과 없음 — 다른 키워드를 시도하거나 '외부 문제' 모드를 사용하세요.</p>
                  )}
                  {searchResults.length > 0 && (
                    <div className="clinic-search-results">
                      <p className="sc-caption">검색 결과 ({searchResults.length}건)</p>
                      {searchResults.map((r) => (
                        <label key={r.question_id} className="clinic-search-result">
                          <input
                            type="radio" checked={picked?.question_id === r.question_id}
                            onChange={() => setPicked(r)}
                          />
                          [{r.school}] {r.question_number}번 · {r.chapter} · {r.difficulty} (id={r.question_id})
                        </label>
                      ))}
                    </div>
                  )}

                  <div className="sc-form">
                    <label>
                      PRISM 오류코드
                      <select value={errorCode} onChange={(e) => setErrorCode(e.target.value)}>
                        {errorCodes.map((c) => <option key={c.code} value={c.code}>{c.display}</option>)}
                      </select>
                    </label>
                    <label>
                      키워드 (학생 작성)
                      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="예: 인수정리 적용 후 조립제법 단계 빼먹음" />
                    </label>
                    <label>
                      오답 발생일
                      <input type="date" value={wrongDate} onChange={(e) => setWrongDate(e.target.value)} />
                    </label>
                  </div>
                </div>
                <div className="clinic-preview-col">
                  {picked && (
                    <>
                      <p className="sc-caption"><b>선택한 오답 미리보기</b></p>
                      <div className="clinic-preview-box">
                        <QuestionContent segments={[{ type: "text", md: picked.text_preview }]} />
                      </div>
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="sc-form">
                <label>
                  외부 문제 라벨
                  <input
                    value={externalLabel} onChange={(e) => setExternalLabel(e.target.value)}
                    placeholder="예: 광명북중 1학기 기말 12번 · 시판 '쎈' p.84 17번"
                  />
                </label>
                <label>
                  PRISM 오류코드
                  <select value={errorCode} onChange={(e) => setErrorCode(e.target.value)}>
                    {errorCodes.map((c) => <option key={c.code} value={c.code}>{c.display}</option>)}
                  </select>
                </label>
                <label>
                  키워드 (학생 작성)
                  <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="예: 부등호 방향 헷갈림" />
                </label>
                <label>
                  오답 발생일
                  <input type="date" value={wrongDate} onChange={(e) => setWrongDate(e.target.value)} />
                </label>
                <p className="sc-caption">외부 문제는 클리닉 기록만 저장됩니다 (인출 3문항·처방전 PDF 미생성).</p>
              </div>
            )}

            <hr className="filter-divider" />

            <button
              type="button" className="btn-primary clinic-submit-btn"
              disabled={!canSubmit || submitting}
              onClick={handleSubmit}
            >
              {submitting ? "처리 중..." : sourceMode === "db" ? "처방전 생성" : "클리닉 기록 저장"}
            </button>

            {submitError && <p className="clinic-error-text">{submitError}</p>}

            {result && (
              <div className="clinic-result">
                <p className="clinic-success-text">클리닉 엔트리 저장됨 (entry_id={result.entry_id})</p>

                {result.mode === "db" ? (
                  <>
                    <button type="button" className="btn-primary" disabled={pdfDownloading} onClick={handleDownloadPdf}>
                      {pdfDownloading ? "PDF 생성 중..." : "처방전 PDF 다운로드"}
                    </button>
                    <p className="sc-caption" style={{ marginTop: 10 }}><b>인출 3문항 (자동 추출)</b></p>
                    <ul className="clinic-similar-list">
                      {result.prescribed_qids.map((qid) => <li key={qid}>id={qid}</li>)}
                    </ul>
                  </>
                ) : (
                  <p className="sc-caption">외부 문제 — {result.external_label}</p>
                )}

                <p className="sc-caption" style={{ marginTop: 10 }}><b>재도전 스케줄</b></p>
                <p className="sc-caption">
                  D+3 ({result.schedule.d3}) · D+7 ({result.schedule.d7}) ·
                  D+14 ({result.schedule.d14}) · D+30 ({result.schedule.d30})
                </p>
              </div>
            )}
          </>
        )}

        <hr className="filter-divider" />
        <h2 className="sc-section-title">오늘 도래한 재도전 (학생 전체)</h2>
        {pendings.length === 0 ? (
          <p className="sc-empty">도래한 재도전이 없습니다.</p>
        ) : (
          pendings.map((p) => (
            <p key={p.entry_id} className="sc-caption">
              · {p.student_name} · 오답 {p.wrong_question_id ? `q=${p.wrong_question_id}` : `외부 · ${p.external_label ?? "-"}`}
              {" "}({p.wrong_date}) · 오류 {p.error_code} · 미완료: {p.due_flags.join(", ")}
            </p>
          ))
        )}
      </main>
    </div>
  );
}
