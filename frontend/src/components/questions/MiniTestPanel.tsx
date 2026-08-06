import { useState } from "react";
import { generateMiniTest } from "../../api/questions";
import type { FilterState } from "../filters/FilterSidebar";
import Expander from "./Expander";
import "./MiniTestPanel.css";

interface Props {
  filterState: FilterState;
  onGenerated: (ids: number[]) => void;
}

export default function MiniTestPanel({ filterState, onGenerated }: Props) {
  const [count, setCount] = useState(7);
  const [easyPct, setEasyPct] = useState(40);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);

  async function handleGenerate() {
    setGenerating(true);
    setMessage(null);
    try {
      const res = await generateMiniTest({
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
        mini_count: count,
        mini_easy_pct: easyPct,
      });
      if (res.pool_size === 0) {
        setMessage({ text: "필터 조건에 맞는 문제가 없습니다. 사이드바를 확인하세요.", isError: true });
      } else if (res.question_ids.length === 0) {
        setMessage({ text: "선택 가능한 문제가 부족합니다.", isError: true });
      } else {
        onGenerated(res.question_ids);
        setMessage({
          text: `${res.question_ids.length}문항 자동 선택됨 → '시험지 미리보기' 탭에서 PDF 생성`,
          isError: false,
        });
      }
    } catch {
      setMessage({ text: "미니테스트 생성 중 오류가 발생했습니다.", isError: true });
    } finally {
      setGenerating(false);
    }
  }

  return (
    <Expander summary="미니테스트 자동 생성 (15분 컷, 6~8문항)">
      <p className="mini-test-caption">
        현재 필터(단원/난이도/학교 등) 안에서 난이도 비중에 맞춰 랜덤 추출합니다.
        워밍업 인출 퀴즈·총복습 미니 모의에 활용.
      </p>
      <div className="mini-test-sliders">
        <label className="mini-test-slider">
          <span>문항 수: {count}</span>
          <input
            type="range" min={6} max={8} step={1} value={count}
            onChange={(e) => setCount(Number(e.target.value))}
          />
        </label>
        <label className="mini-test-slider">
          <span>쉬운 문제 비중: {easyPct}%</span>
          <input
            type="range" min={0} max={100} step={10} value={easyPct}
            onChange={(e) => setEasyPct(Number(e.target.value))}
          />
        </label>
      </div>
      <button
        type="button" className="btn-primary" disabled={generating}
        onClick={handleGenerate}
      >
        {generating ? "생성 중..." : "미니테스트 자동 생성"}
      </button>
      {message && (
        <p className={message.isError ? "mini-test-message error" : "mini-test-message"}>
          {message.text}
        </p>
      )}
    </Expander>
  );
}
