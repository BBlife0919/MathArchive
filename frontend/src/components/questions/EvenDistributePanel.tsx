import { useState } from "react";
import { evenDistribute, type EvenDistributeGranularity } from "../../api/questions";
import type { FilterState } from "../filters/FilterSidebar";
import { EXCLUDE_RECENT_DAYS } from "../../constants";
import Expander from "./Expander";
import "./EvenDistributePanel.css";

interface Props {
  filterState: FilterState;
  selectedIds: number[];
  onGenerated: (ids: number[]) => void;
  onFillRemaining: (ids: number[]) => void;
}

type PickMode = "auto" | "manual";

const COUNT_PRESETS = [10, 20, 30, 50];
const MAX_COUNT = 150;

export default function EvenDistributePanel({
  filterState, selectedIds, onGenerated, onFillRemaining,
}: Props) {
  const selectedCount = selectedIds.length;
  const [mode, setMode] = useState<PickMode>("auto");
  const [count, setCount] = useState(20);
  const [granularity, setGranularity] = useState<EvenDistributeGranularity>("major");
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  function clampCount(n: number) {
    if (Number.isNaN(n)) return 1;
    return Math.min(MAX_COUNT, Math.max(1, Math.round(n)));
  }

  const remaining = Math.max(0, count - selectedCount);

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
          text: `${res.question_ids.length}문항 자동 선택됨 (${groupCount}개 단원에 고르게 배분) → 아래 '다음' 버튼으로 학습지 설정에서 PDF 생성`,
          isError: false,
        });
      }
    } catch {
      setMessage({ text: "균등배분 생성 중 오류가 발생했습니다.", isError: true });
    } finally {
      setGenerating(false);
    }
  }

  async function handleFillRemaining() {
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
        exclude_ids: selectedIds,
      });
      if (res.question_ids.length === 0) {
        setMessage({ text: "채울 수 있는 문제가 없습니다. 필터 조건을 확인하세요.", isError: true });
      } else {
        onFillRemaining(res.question_ids);
        setMessage({
          text: `${res.question_ids.length}문항 자동으로 채워졌습니다 → 아래 '다음' 버튼으로 학습지 설정에서 PDF 생성`,
          isError: false,
        });
      }
    } catch {
      setMessage({ text: "자동 채우기 중 오류가 발생했습니다.", isError: true });
    } finally {
      setGenerating(false);
    }
  }

  return (
    <Expander summary="문제 고르는 방식 (자동 뽑기 · 직접 고르기)">
      <div className="pick-mode-toggle">
        <button
          type="button"
          className={mode === "auto" ? "pick-mode-btn active" : "pick-mode-btn"}
          onClick={() => setMode("auto")}
        >
          <span className="pick-mode-title">자동으로 뽑기</span>
          <span className="pick-mode-desc">체크한 범위에서 골고루</span>
        </button>
        <button
          type="button"
          className={mode === "manual" ? "pick-mode-btn active" : "pick-mode-btn"}
          onClick={() => setMode("manual")}
        >
          <span className="pick-mode-title">직접 고르기</span>
          <span className="pick-mode-desc">문항을 보고 직접 담기</span>
        </button>
      </div>

      {mode === "manual" && (
        <div className="manual-pick-progress">
          <div className="manual-pick-progress-header">
            <span>직접 고른 문항</span>
            <span className="manual-pick-progress-count">{selectedCount} / {count}</span>
          </div>
          <div className="manual-pick-progress-bar">
            <div
              className="manual-pick-progress-fill"
              style={{ width: `${Math.min(100, (selectedCount / count) * 100)}%` }}
            />
          </div>
          <p className="manual-pick-progress-caption">
            {remaining > 0
              ? `아래 문제 목록에서 '담기'로 직접 고르세요. 모자란 ${remaining}문항은 체크한 범위에서 골고루 채워요.`
              : "목표 문항 수를 채웠습니다. '다음' 버튼으로 학습지 설정으로 이동하세요."}
          </p>
        </div>
      )}

      <p className="even-dist-caption">
        {mode === "auto"
          ? "현재 필터(범위) 안에서 단원별로 문항 수를 고르게 나눠 랜덤 추출합니다."
          : "목표 문항 수를 정하고, 직접 고른 뒤 모자란 만큼만 자동으로 채웁니다."}
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

      {mode === "auto" ? (
        <button
          type="button" className="btn-primary" disabled={generating}
          onClick={handleGenerate}
        >
          {generating ? "생성 중..." : "균등배분 자동 생성"}
        </button>
      ) : (
        <button
          type="button" className="btn-primary" disabled={generating || remaining === 0}
          onClick={handleFillRemaining}
        >
          {generating ? "채우는 중..." : remaining === 0 ? "목표 문항 수 달성" : `모자란 ${remaining}문항 자동 채우기`}
        </button>
      )}
      {message && (
        <p className={message.isError ? "even-dist-message error" : "even-dist-message"}>
          {message.text}
        </p>
      )}
    </Expander>
  );
}
