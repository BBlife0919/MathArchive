import { useEffect, useMemo, useState } from "react";
import { useSelection } from "../context/SelectionContext";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import {
  fetchExamPapers, fetchExamPaperIds, fetchFilters, searchQuestionIds, searchQuestions,
  type ExamPaper, type FiltersResponse, type QuestionCard, type SearchRequest,
} from "../api/questions";
import FilterSidebar, {
  EMPTY_FILTER_STATE, EXCLUDE_RECENT_DAYS, type FilterState,
} from "../components/filters/FilterSidebar";
import QuestionList from "../components/questions/QuestionList";
import { QuestionGridSkeleton } from "../components/questions/QuestionCardSkeleton";
import Pagination from "../components/questions/Pagination";
import MiniTestPanel from "../components/questions/MiniTestPanel";
import EvenDistributePanel from "../components/questions/EvenDistributePanel";
import ExamPreviewPanel, { type PdfMode } from "../components/preview/ExamPreviewPanel";
import ExamModeSelect from "../components/mode/ExamModeSelect";
import SchoolTermPicker, {
  EMPTY_SCHOOL_TERM, type SchoolTermValue,
} from "../components/mode/SchoolTermPicker";
import ExamPaperList, { paperKey } from "../components/mode/ExamPaperList";
import "./ExamBuilderPage.css";

const PAGE_SIZE = 15;

type WizardStep = 1 | 2;
type EntryMode = "select" | "type" | "school-term";

function buildSearchRequest(state: FilterState, page: number): SearchRequest {
  return {
    quick_search: state.quickSearch,
    regions: state.regions,
    schools: state.schools,
    grades: state.grades,
    years: state.years,
    semesters: state.semesters,
    exam_types: state.examTypes,
    subjects: state.subjects,
    majors: state.majors,
    minors: state.minors,
    difficulties: state.difficulties,
    question_type: state.questionType,
    keyword: state.keyword,
    page,
    page_size: PAGE_SIZE,
    exclude_recent_days: state.excludeRecentDays ? EXCLUDE_RECENT_DAYS : undefined,
  };
}

export default function ExamBuilderPage() {
  const { selectedIds, order, count, toggle, bulkAdd, replaceAll, clear } = useSelection();

  const [entryMode, setEntryMode] = useState<EntryMode>("select");
  const [step, setStep] = useState<WizardStep>(1);
  const [pdfMode, setPdfMode] = useState<PdfMode>("exam");
  const [filters, setFilters] = useState<FiltersResponse | null>(null);

  // "학교·학기별 출제" 모드 — 팝업형 조건 선택 대신 STEP1 자리에 인라인
  // 패널로 띄우고, 검색하면 실제 시험(학교·학년·연도·학기·중간기말) 단위
  // "시험지 카드" 목록을 보여준다. 카드를 고르면 그 시험 문항 전체를
  // 선택에 담고 STEP2로 넘어간다.
  const [termValue, setTermValue] = useState<SchoolTermValue>(EMPTY_SCHOOL_TERM);
  const [papers, setPapers] = useState<ExamPaper[]>([]);
  const [papersLoading, setPapersLoading] = useState(false);
  const [papersSearched, setPapersSearched] = useState(false);
  const [pickingKey, setPickingKey] = useState<string | null>(null);
  // filterState = 사이드바에서 편집 중인 draft. "적용" 버튼을 눌러야
  // appliedFilterState 로 반영되고 그때 비로소 검색이 실행된다 (빠른검색
  // 입력창·키워드 검색은 각자 이미 자체적인 "확정" 동작이 있어 예외로
  // 즉시 반영).
  const [filterState, setFilterState] = useState<FilterState>(EMPTY_FILTER_STATE);
  const [appliedFilterState, setAppliedFilterState] = useState<FilterState>(EMPTY_FILTER_STATE);
  const [page, setPage] = useState(0);

  const [items, setItems] = useState<QuestionCard[]>([]);
  const [total, setTotal] = useState(0);
  // true 로 시작해야 첫 렌더에서 "결과 없음" 문구가 스켈레톤보다 먼저
  // 반짝 노출되는 걸 막을 수 있다 (검색 useEffect 는 첫 페인트 이후 실행됨).
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bulkAdding, setBulkAdding] = useState(false);

  const debouncedKeyword = useDebouncedValue(filterState.keyword, 400);

  useEffect(() => {
    fetchFilters().then(setFilters).catch(() => setFilters(null));
  }, []);

  // 아무 조건도 없이 페이지에 들어오자마자 17만 문항 전체를 무필터로
  // 검색하면 로딩이 걸리고(진짜 체감 느려짐) 결과도 무의미하다. 필터를
  // 하나라도 적용했거나 빠른검색/키워드를 썼을 때만 검색을 실행한다.
  const hasAnyCondition = useMemo(() => {
    const keys: (keyof FilterState)[] = [
      "regions", "schools", "grades", "years", "semesters", "examTypes",
      "subjects", "majors", "minors", "difficulties",
    ];
    return (
      keys.some((k) => (appliedFilterState[k] as unknown[]).length > 0)
      || appliedFilterState.questionType !== "all"
      || appliedFilterState.excludeRecentDays
      || filterState.quickSearch.trim() !== ""
      || debouncedKeyword.trim() !== ""
    );
  }, [appliedFilterState, filterState.quickSearch, debouncedKeyword]);

  // 검색에는 "적용"된 필터(appliedFilterState)를 쓰되, 빠른검색/키워드는
  // 각자의 확정 동작(빠른검색 적용 버튼·키워드 디바운스)이 있으니 draft 값을
  // 그대로 즉시 반영한다.
  const searchDeps = useMemo(
    () => ({ ...appliedFilterState, quickSearch: filterState.quickSearch, keyword: debouncedKeyword }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      appliedFilterState.regions, appliedFilterState.schools,
      appliedFilterState.grades, appliedFilterState.years, appliedFilterState.semesters,
      appliedFilterState.examTypes, appliedFilterState.subjects, appliedFilterState.majors,
      appliedFilterState.minors, appliedFilterState.difficulties, appliedFilterState.questionType,
      appliedFilterState.excludeRecentDays, filterState.quickSearch, debouncedKeyword,
    ],
  );

  // 사이드바 draft가 적용된 필터와 달라졌는지 ("적용" 버튼 강조용).
  // quickSearch/keyword는 각자 즉시 반영되니 비교 대상에서 뺀다.
  const hasPendingFilterChanges = useMemo(() => {
    const keys: (keyof FilterState)[] = [
      "regions", "schools", "grades", "years", "semesters", "examTypes",
      "subjects", "majors", "minors", "difficulties", "questionType", "excludeRecentDays",
    ];
    return keys.some((k) => JSON.stringify(filterState[k]) !== JSON.stringify(appliedFilterState[k]));
  }, [filterState, appliedFilterState]);

  function handleApplyFilters() {
    setAppliedFilterState(filterState);
  }

  // 필터/검색 조건이 바뀌면 첫 페이지로 리셋.
  useEffect(() => {
    setPage(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchDeps]);

  useEffect(() => {
    if (!hasAnyCondition) {
      setItems([]);
      setTotal(0);
      setLoading(false);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    searchQuestions(buildSearchRequest(searchDeps, page))
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch(() => setError("검색 중 오류가 발생했습니다."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchDeps, page, hasAnyCondition]);

  async function handleBulkAdd() {
    setBulkAdding(true);
    try {
      const res = await searchQuestionIds(buildSearchRequest(searchDeps, 0));
      bulkAdd(res.question_ids);
    } catch {
      setError("일괄 담기 중 오류가 발생했습니다.");
    } finally {
      setBulkAdding(false);
    }
  }

  function handleMiniTestGenerated(ids: number[]) {
    // main.py: 미니테스트는 기존 선택을 대체하고 시험지(exam) 모드를 강제한다.
    replaceAll(ids);
    setPdfMode("exam");
  }

  function handleEvenDistributeGenerated(ids: number[]) {
    replaceAll(ids);
    setPdfMode("exam");
  }

  async function handleSearchPapers() {
    setPapersLoading(true);
    setError(null);
    try {
      const res = await fetchExamPapers({
        regions: [],
        schools: termValue.schools,
        grades: termValue.grades,
        years: termValue.years,
        semesters: termValue.semesters,
        exam_types: termValue.examTypes,
        subjects: termValue.subjects,
      });
      setPapers(res.papers);
      setPapersSearched(true);
    } catch {
      setError("시험지를 불러오는 중 오류가 발생했습니다.");
    } finally {
      setPapersLoading(false);
    }
  }

  async function handlePickPaper(paper: ExamPaper) {
    setPickingKey(paperKey(paper));
    setError(null);
    try {
      // search-ids(일반 검색)는 chapter_range를 모른다 — list_exam_papers()는
      // chapter_range까지 GROUP BY 하므로, 나머지 조건이 같아도 chapter_range가
      // 다른 별개 시험지가 섞일 수 있다. 카드와 1:1 대응하는 전용 조회를 쓴다.
      const res = await fetchExamPaperIds({
        school: paper.school, grade: paper.grade, year: paper.year,
        semester: paper.semester, exam_type: paper.exam_type,
        subject: paper.subject, chapter_range: paper.chapter_range,
      });
      bulkAdd(res.question_ids);
      setPdfMode("exam");
      setStep(2);
    } catch {
      setError("시험지를 담는 중 오류가 발생했습니다.");
    } finally {
      setPickingKey(null);
    }
  }

  function handleBackToModeSelect() {
    setEntryMode("select");
    setStep(1);
    setPapers([]);
    setPapersSearched(false);
    setTermValue(EMPTY_SCHOOL_TERM);
  }

  const start = total === 0 ? 0 : page * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE + PAGE_SIZE, total);

  return (
    <div className="exam-builder">
      {entryMode === "type" && (
        <FilterSidebar
          filters={filters}
          state={filterState}
          onChange={setFilterState}
          selectedCount={count}
          onResetSelection={clear}
          onApply={handleApplyFilters}
          hasPendingChanges={hasPendingFilterChanges}
        />
      )}

      <main className="exam-builder-main">
        <h1 className="exam-builder-title">문제은행 · 시험지 · 교재 제작</h1>

        {entryMode === "select" && (
          <ExamModeSelect
            onSelectType={() => setEntryMode("type")}
            onSelectSchoolTerm={() => setEntryMode("school-term")}
          />
        )}

        {entryMode !== "select" && (
          <>
            <button type="button" className="btn-secondary mode-back-btn" onClick={handleBackToModeSelect}>
              ← 다른 방식으로 만들기
            </button>

            <div className="wizard-steps">
              <div className={step === 1 ? "wizard-step active" : "wizard-step"}>
                <span className="wizard-step-num">1</span>
                {entryMode === "type" ? "범위·조건 선택" : "시험 선택"}
              </div>
              <span className="wizard-step-arrow">→</span>
              <div className={step === 2 ? "wizard-step active" : "wizard-step"}>
                <span className="wizard-step-num">2</span>
                학습지 설정 · 미리보기{count > 0 ? ` (${count}문항)` : ""}
              </div>
            </div>

            {error && <p className="exam-builder-error">{error}</p>}

            {!error && step === 1 && entryMode === "school-term" && (
              <>
                <SchoolTermPicker
                  filters={filters ?? { schools: [], regions: [], region_schools: {}, provinces: [], province_districts: {}, years: [], grades: [], semesters: [], exam_types: [], difficulties: [], curriculum: {} }}
                  value={termValue}
                  onChange={setTermValue}
                  onSearch={handleSearchPapers}
                  searching={papersLoading}
                />
                {papersSearched && (
                  <ExamPaperList
                    papers={papers} loading={papersLoading}
                    onPick={handlePickPaper} pickingKey={pickingKey}
                  />
                )}
              </>
            )}

            {!error && step === 1 && entryMode === "type" && (
              <>
                <MiniTestPanel filterState={searchDeps} onGenerated={handleMiniTestGenerated} />
                <EvenDistributePanel
                  filterState={searchDeps}
                  selectedIds={order}
                  onGenerated={handleEvenDistributeGenerated}
                  onFillRemaining={bulkAdd}
                />
                {hasAnyCondition && (
                  <div className="result-bar">
                    <p className="result-caption">
                      {loading ? "검색 중..." : `검색 결과: ${total}문항 · ${start}–${end}번 표시`}
                    </p>
                    {total > 0 && (
                      <button type="button" className="btn-secondary" disabled={bulkAdding} onClick={handleBulkAdd}>
                        {bulkAdding ? "담는 중..." : `전체(${total}) → 시험지`}
                      </button>
                    )}
                  </div>
                )}
                {!hasAnyCondition && (
                  <p className="empty-state">왼쪽에서 조건을 선택하고 "적용"을 눌러주세요. 빠른검색·키워드로 바로 찾을 수도 있습니다.</p>
                )}
                {hasAnyCondition && (
                  <>
                    <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
                    {!loading && total === 0 && (
                      <p className="empty-state">필터 조건에 맞는 문제가 없습니다. 사이드바에서 조건을 조정해주세요.</p>
                    )}
                    {loading && items.length === 0 ? (
                      <QuestionGridSkeleton count={PAGE_SIZE} />
                    ) : (
                      <div className={loading ? "question-list-refreshing" : undefined}>
                        <QuestionList items={items} selectedIds={selectedIds} onToggleSelect={toggle} />
                      </div>
                    )}
                    <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
                  </>
                )}
                <div className="wizard-next-bar">
                  <button
                    type="button" className="btn-primary" disabled={count === 0}
                    onClick={() => setStep(2)}
                  >
                    다음: 학습지 설정{count > 0 ? ` (${count}문항)` : ""} →
                  </button>
                </div>
              </>
            )}

            {!error && step === 1 && entryMode === "school-term" && count > 0 && (
              <div className="wizard-next-bar">
                <button type="button" className="btn-primary" onClick={() => setStep(2)}>
                  다음: 학습지 설정 ({count}문항) →
                </button>
              </div>
            )}

            {!error && step === 2 && (
              <>
                <button
                  type="button" className="btn-secondary wizard-back-btn"
                  onClick={() => setStep(1)}
                >
                  ← 이전 단계로
                </button>
                <ExamPreviewPanel pdfMode={pdfMode} onPdfModeChange={setPdfMode} />
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}
