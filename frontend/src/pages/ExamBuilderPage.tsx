import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useSelection } from "../context/SelectionContext";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import {
  fetchFilters, searchQuestionIds, searchQuestions,
  type FiltersResponse, type QuestionCard, type SearchRequest,
} from "../api/questions";
import FilterSidebar, {
  EMPTY_FILTER_STATE, type FilterState,
} from "../components/filters/FilterSidebar";
import QuestionList from "../components/questions/QuestionList";
import Pagination from "../components/questions/Pagination";
import MiniTestPanel from "../components/questions/MiniTestPanel";
import ExamPreviewPanel, { type PdfMode } from "../components/preview/ExamPreviewPanel";
import "./ExamBuilderPage.css";

const PAGE_SIZE = 15;

type Tab = "list" | "preview";

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
  };
}

export default function ExamBuilderPage() {
  const { user, logout } = useAuth();
  const { selectedIds, count, toggle, bulkAdd, replaceAll, clear } = useSelection();

  const [tab, setTab] = useState<Tab>("list");
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
      debouncedKeyword,
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
        <header className="exam-builder-header">
          <h1>문제은행 · 시험지 · 교재 제작</h1>
          <div className="exam-builder-user">
            <span>{user?.name}님</span>
            <button type="button" onClick={() => logout()}>로그아웃</button>
          </div>
        </header>

        <div className="tab-bar">
          <button
            type="button" className={tab === "list" ? "tab-btn active" : "tab-btn"}
            onClick={() => setTab("list")}
          >
            문제 목록
          </button>
          <button
            type="button" className={tab === "preview" ? "tab-btn active" : "tab-btn"}
            onClick={() => setTab("preview")}
          >
            시험지 미리보기{count > 0 ? ` (${count})` : ""}
          </button>
        </div>

        {error && <p className="exam-builder-error">{error}</p>}

        {!error && tab === "list" && (
          <>
            <MiniTestPanel filterState={searchDeps} onGenerated={handleMiniTestGenerated} />
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
          </>
        )}

        {!error && tab === "preview" && (
          <ExamPreviewPanel pdfMode={pdfMode} onPdfModeChange={setPdfMode} />
        )}
      </main>
    </div>
  );
}
