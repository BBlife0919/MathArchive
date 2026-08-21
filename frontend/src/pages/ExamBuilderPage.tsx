import { useEffect, useMemo, useState } from "react";
import { useSelection } from "../context/SelectionContext";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import {
  fetchFilters, searchQuestionIds, searchQuestions,
  type FiltersResponse, type QuestionCard, type SearchRequest,
} from "../api/questions";
import FilterSidebar, {
  EMPTY_FILTER_STATE, EXCLUDE_RECENT_DAYS, type FilterState,
} from "../components/filters/FilterSidebar";
import QuestionList from "../components/questions/QuestionList";
import Pagination from "../components/questions/Pagination";
import MiniTestPanel from "../components/questions/MiniTestPanel";
import EvenDistributePanel from "../components/questions/EvenDistributePanel";
import ExamPreviewPanel, { type PdfMode } from "../components/preview/ExamPreviewPanel";
import "./ExamBuilderPage.css";

const PAGE_SIZE = 15;

type WizardStep = 1 | 2;

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
  const { selectedIds, count, toggle, bulkAdd, replaceAll, clear } = useSelection();

  const [step, setStep] = useState<WizardStep>(1);
  const [pdfMode, setPdfMode] = useState<PdfMode>("exam");
  const [filters, setFilters] = useState<FiltersResponse | null>(null);
  const [filterState, setFilterState] = useState<FilterState>(EMPTY_FILTER_STATE);
  const [page, setPage] = useState(0);

  const [items, setItems] = useState<QuestionCard[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bulkAdding, setBulkAdding] = useState(false);

  const debouncedKeyword = useDebouncedValue(filterState.keyword, 400);

  useEffect(() => {
    fetchFilters().then(setFilters).catch(() => setFilters(null));
  }, []);

  // 키워드는 디바운스된 값을 기준으로 검색 파라미터를 구성한다.
  const searchDeps = useMemo(
    () => ({ ...filterState, keyword: debouncedKeyword }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      filterState.quickSearch, filterState.regions, filterState.schools,
      filterState.grades, filterState.years, filterState.semesters,
      filterState.examTypes, filterState.subjects, filterState.majors,
      filterState.minors, filterState.difficulties, filterState.questionType,
      filterState.excludeRecentDays, debouncedKeyword,
    ],
  );

  // 필터/검색 조건이 바뀌면 첫 페이지로 리셋.
  useEffect(() => {
    setPage(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchDeps]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    searchQuestions(buildSearchRequest(searchDeps, page))
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch(() => setError("검색 중 오류가 발생했습니다."))
      .finally(() => setLoading(false));
  }, [searchDeps, page]);

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

  const start = total === 0 ? 0 : page * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE + PAGE_SIZE, total);

  return (
    <div className="exam-builder">
      <FilterSidebar
        filters={filters}
        state={filterState}
        onChange={setFilterState}
        selectedCount={count}
        onResetSelection={clear}
      />

      <main className="exam-builder-main">
        <h1 className="exam-builder-title">문제은행 · 시험지 · 교재 제작</h1>

        <div className="wizard-steps">
          <div className={step === 1 ? "wizard-step active" : "wizard-step"}>
            <span className="wizard-step-num">1</span>
            범위·조건 선택
          </div>
          <span className="wizard-step-arrow">→</span>
          <div className={step === 2 ? "wizard-step active" : "wizard-step"}>
            <span className="wizard-step-num">2</span>
            학습지 설정 · 미리보기{count > 0 ? ` (${count}문항)` : ""}
          </div>
        </div>

        {error && <p className="exam-builder-error">{error}</p>}

        {!error && step === 1 && (
          <>
            <MiniTestPanel filterState={searchDeps} onGenerated={handleMiniTestGenerated} />
            <EvenDistributePanel filterState={searchDeps} onGenerated={handleEvenDistributeGenerated} />
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
            <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
            {!loading && total === 0 && (
              <p className="empty-state">필터 조건에 맞는 문제가 없습니다. 사이드바에서 조건을 조정해주세요.</p>
            )}
            <QuestionList items={items} selectedIds={selectedIds} onToggleSelect={toggle} />
            <Pagination page={page} pageSize={PAGE_SIZE} total={total} onPageChange={setPage} />
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
      </main>
    </div>
  );
}
