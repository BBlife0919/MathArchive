import { useState } from "react";
import { evenDistribute, type EvenDistributeGranularity } from "../../api/questions";
import { EXCLUDE_RECENT_DAYS, type FilterState } from "../filters/FilterSidebar";
import Expander from "./Expander";
import "./EvenDistributePanel.css";

interface Props {
  filterState: FilterState;
  onGenerated: (ids: number[]) => void;
}

const COUNT_PRESETS = [10, 20, 30, 50];
const MAX_COUNT = 150;

export default function EvenDistributePanel({ filterState, onGenerated }: Props) {
  const [count, setCount] = useState(20);
  const [granularity, setGranularity] = useState<EvenDistributeGranularity>("major");
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  function clampCount(n: number) {
    if (Number.isNaN(n)) return 1;
    return Math.min(MAX_COUNT, Math.max(1, Math.round(n)));
  }

  async function handleGenerate() {
    setGenerating(true);
    setMessage(null);
    try {
      const res = await evenDistribute({
        quick_search: filterState.quickSearch,
        regions: filterState.regions,
        schools: filterState.schools,
        grades: filterState.grades,
        years: filterState.years,
        semesters: filterState.semesters,
        exam_types: filterState.examTypes,
        subjects: filterState.subjects,
        majors: filterState.majors,
        minors: filterState.minors,
        difficulties: filterState.difficulties,
        question_type: filterState.questionType,
        keyword: filterState.keyword,
        page: 0,
        page_size: 15,
        exclude_recent_days: filterState.excludeRecentDays ? EXCLUDE_RECENT_DAYS : undefined,
        count,
        granularity,
      });
      if (res.question_ids.length === 0) {
        setMessage({ text: "필터 조건에 맞는 문제가 없습니다. 사이드바를 확인하세요.", isError: true });
      } else {
        const groupCount = res.results.length;
        onGenerated(res.question_ids);
        setMessage({
          text: `${res.question_ids.length}문항 자동 선택됨 (${groupCount}개 단원에 고르게 배분) → '시험지 미리보기' 탭에서 PDF 생성`,
          isError: false,
        });
      }
    } catch {
      setMessage({ text: "균등배분 생성 중 오류가 발생했습니다.", isError: true });
    } finally {
      setGenerating(false);
    }
  }

  return (
    <Expander summary="단원별 균등배분">
      <p className="even-dist-caption">
        현재 필터(범위) 안에서 단원별로 문항 수를 고르게 나눠 랜덤 추출합니다.
      </p>

      <div className="even-dist-count">
        <span className="even-dist-count-label">문제 수: {count}개</span>
        <div className="even-dist-presets">
          {COUNT_PRESETS.map((n) => (
            <button
              key={n}
              type="button"
              className={count === n ? "even-dist-preset active" : "even-dist-preset"}
              onClick={() => setCount(n)}
            >
              {n}
            </button>
          ))}
          <input
            type="number"
            min={1}
            max={MAX_COUNT}
            value={count}
            className="even-dist-count-input"
            onChange={(e) => setCount(clampCount(Number(e.target.value)))}
          />
        </div>
      </div>

      <div className="even-dist-granularity">
        <span className="even-dist-count-label">배분 기준</span>
        <div className="even-dist-granularity-options">
          <label>
            <input
              type="radio" name="even-dist-granularity"
              checked={granularity === "major"}
              onChange={() => setGranularity("major")}
            />
            대단원별
          </label>
          <label>
            <input
              type="radio" name="even-dist-granularity"
              checked={granularity === "minor"}
              onChange={() => setGranularity("minor")}
            />
            중단원별
          </label>
          <label className="even-dist-disabled" title="세부유형 분류 준비 중입니다.">
            <input type="radio" name="even-dist-granularity" disabled />
            유형별 (준비 중)
          </label>
        </div>
      </div>

      <button
        type="button" className="btn-primary" disabled={generating}
        onClick={handleGenerate}
      >
        {generating ? "생성 중..." : "균등배분 자동 생성"}
      </button>
      {message && (
        <p className={message.isError ? "even-dist-message error" : "even-dist-message"}>
          {message.text}
        </p>
      )}
    </Expander>
  );
}
