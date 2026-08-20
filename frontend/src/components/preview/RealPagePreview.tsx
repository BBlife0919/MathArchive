import { useEffect, useState } from "react";
import "./RealPagePreview.css";

// CSS mm 는 고정 물리 단위(1mm = 96/25.4px)라 화면·인쇄 어디서든 동일하게
// 환산된다 — A4 실제 크기 그대로 iframe을 만든 뒤 컨테이너 폭에 맞춰
// transform:scale로 축소 표시한다.
const MM_TO_PX = 96 / 25.4;
const A4_WIDTH_PX = 210 * MM_TO_PX;
const A4_HEIGHT_PX = 297 * MM_TO_PX;
const DEBOUNCE_MS = 400;

interface Props {
  // null 이면(문항 0개 등) 미리보기 자체를 안 그림.
  fetchHtml: (() => Promise<string>) | null;
  // 이 값이 바뀔 때만 재요청 — 제목/부제/문항 구성 등을 JSON.stringify 해서 넘김.
  depsKey: string;
}

export default function RealPagePreview({ fetchHtml, depsKey }: Props) {
  const [html, setHtml] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // useRef 대신 콜백 ref(상태로 보관) — 미리보기가 questionIds 0개↔N개를
  // 오가며 wrap div 가 언마운트/재마운트되는 케이스(문항 전체 제거 후 재추가
  // 등)에도 ResizeObserver 가 새 DOM 노드에 다시 붙도록 하기 위함. useRef +
  // 마운트 1회성 useEffect 조합이면 재마운트 시 재관찰이 안 되는 버그가 있었음.
  const [wrapEl, setWrapEl] = useState<HTMLDivElement | null>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    if (!wrapEl) return;
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width ?? A4_WIDTH_PX;
      setScale(Math.min(1, width / A4_WIDTH_PX));
    });
    observer.observe(wrapEl);
    return () => observer.disconnect();
  }, [wrapEl]);

  useEffect(() => {
    if (!fetchHtml) {
      setHtml("");
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    const timer = setTimeout(() => {
      fetchHtml()
        .then((h) => {
          if (cancelled) return;
          setHtml(h);
          setError(null);
        })
        .catch(() => {
          if (!cancelled) setError("미리보기를 불러오지 못했습니다.");
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, DEBOUNCE_MS);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [depsKey]);

  if (!fetchHtml) return null;

  return (
    <div className="real-preview">
      <p className="real-preview-caption">
        {loading ? "미리보기 갱신 중..." : "실시간 미리보기 (실제 인쇄 페이지 그대로, 여러 쪽이면 안에서 스크롤)"}
      </p>
      {error && <p className="real-preview-error">{error}</p>}
      <div ref={setWrapEl} className="real-preview-wrap" style={{ height: A4_HEIGHT_PX * scale }}>
        <iframe
          title="실물 미리보기"
          className="real-preview-frame"
          srcDoc={html}
          style={{
            width: `${A4_WIDTH_PX}px`,
            height: `${A4_HEIGHT_PX}px`,
            transform: `scale(${scale})`,
          }}
        />
      </div>
    </div>
  );
}
