import { apiFetch, apiFetchBlob } from "./client";

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

export type CoverStyle = "final" | "diagonal";

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
}

export function downloadBookPdf(req: BookPdfRequest): Promise<Blob> {
  return apiFetchBlob("/api/exam/book-pdf", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export interface LayoutPreviewRequest {
  question_ids: number[];
  preserve_order?: boolean;
}

export interface LayoutSlot {
  question_id: number;
  layout: "half" | "full";
}

export interface LayoutColumn {
  slots: LayoutSlot[];
}

export interface LayoutPage {
  columns: LayoutColumn[];
}

export interface LayoutPreviewResponse {
  pages: LayoutPage[];
}

export function fetchLayoutPreview(req: LayoutPreviewRequest): Promise<LayoutPreviewResponse> {
  return apiFetch<LayoutPreviewResponse>("/api/exam/layout-preview", {
    method: "POST",
    body: JSON.stringify(req),
  });
}
