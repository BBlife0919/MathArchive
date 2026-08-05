import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import "katex/dist/katex.min.css";
import "../../styles/questionContent.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string;

export interface ContentSegment {
  type: "text" | "box" | "image";
  md?: string | null;
  url?: string | null;
  ref?: string | null;
}

// 백엔드가 자체 정적 파일(로컬 이미지 폴백)은 origin 없는 상대경로
// (예: /static/images/...) 로 내려준다. R2 원격 URL 은 이미 절대경로라
// 그대로 두고, 상대경로만 API 서버 origin 을 붙여 해석한다.
function resolveImageUrl(url: string): string {
  return url.startsWith("/") ? `${API_BASE}${url}` : url;
}

function Segment({ segment }: { segment: ContentSegment }) {
  if (segment.type === "image") {
    if (segment.url) {
      return (
        <img
          src={resolveImageUrl(segment.url)}
          className="content-image"
          alt={segment.ref ?? "문제 이미지"}
        />
      );
    }
    return (
      <p className="content-image-missing">[이미지: {segment.ref}]</p>
    );
  }

  const md = segment.md ?? "";
  const body = (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex, rehypeRaw]}
    >
      {md}
    </ReactMarkdown>
  );

  if (segment.type === "box") {
    return <div className="content-box">{body}</div>;
  }
  return body;
}

export default function QuestionContent({
  segments,
}: {
  segments: ContentSegment[];
}) {
  return (
    <div className="question-content">
      {segments.map((seg, i) => (
        <Segment key={i} segment={seg} />
      ))}
    </div>
  );
}
