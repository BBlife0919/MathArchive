import { apiFetchBlob, apiFetchText } from "./client";

export interface ExamPdfRequest {
  question_ids: number[];
  title: string;
  subtitle?: string | null;
  include_source: boolean;
  include_logo: boolean;
  preserve_order?: boolean;
}

export function downloadExamPdf(req: ExamPdfRequest): Promise<Blob> {
  return apiFetchBlob("/api/exam/pdf", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// 실물 미리보기용 — Playwright 없이 실제 PDF와 같은 HTML을 그대로 받아
// iframe에 넣는다(다운로드 집계에 안 잡히도록 별도 엔드포인트).
export function fetchExamHtmlPreview(req: ExamPdfRequest): Promise<string> {
  return apiFetchText("/api/exam/html-preview", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export type CoverStyle = "final" | "diagonal";
export type BookMode = "chapter" | "flat";
export type FlatLayout = "half" | "full";

export interface BookPdfRequest {
  question_ids: number[];
  title: string;
  subtitle?: string | null;
  include_source: boolean;
  include_logo: boolean;
  cover_style: CoverStyle;
  cover_kicker?: string | null;
  cover_big_word?: string | null;
  cover_footer_main?: string | null;
  cover_footer_sub?: string | null;
  dcov_subject?: string | null;
  dcov_level?: string | null;
  kicker_mark?: string | null;
  kicker_text?: string | null;
  divider_meta_top?: string | null;
  divider_footer_title?: string | null;
  divider_footer_sub?: string | null;
  book_mode?: BookMode;
  flat_layout?: FlatLayout;
}

export function downloadBookPdf(req: BookPdfRequest): Promise<Blob> {
  return apiFetchBlob("/api/exam/book-pdf", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function fetchBookHtmlPreview(req: BookPdfRequest): Promise<string> {
  return apiFetchText("/api/exam/book-html-preview", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

