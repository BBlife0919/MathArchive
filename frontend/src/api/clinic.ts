import { apiFetch, apiFetchBlob } from "./client";

export interface ErrorCodeItem {
  code: string;
  display: string;
}

export interface QuestionSearchResult {
  question_id: number;
  school: string | null;
  year: number | null;
  semester: number | null;
  exam_type: string | null;
  question_number: number;
  chapter: string | null;
  difficulty: string | null;
  text_preview: string;
}

export type SourceMode = "db" | "external";

export interface ClinicEntryRequest {
  student_id: number;
  source_mode: SourceMode;
  wrong_question_id?: number | null;
  external_label?: string | null;
  error_code: string;
  keyword: string;
  wrong_date: string;
}

export interface RetrySchedule {
  d3: string;
  d7: string;
  d14: string;
  d30: string;
}

export interface ClinicEntryResponse {
  entry_id: number;
  mode: SourceMode;
  prescribed_qids: number[];
  prescription_question_ids: number[];
  schedule: RetrySchedule;
  student_name: string;
  error_code: string;
  external_label: string | null;
}

export interface PendingRetry {
  entry_id: number;
  student_id: number;
  student_name: string;
  wrong_question_id: number | null;
  external_label: string | null;
  wrong_date: string;
  error_code: string;
  due_flags: string[];
}

export function fetchClinicMeta(): Promise<{ error_codes: ErrorCodeItem[] }> {
  return apiFetch("/api/clinic/meta");
}

export function searchClinicQuestions(keyword: string): Promise<QuestionSearchResult[]> {
  return apiFetch(`/api/clinic/search-questions?keyword=${encodeURIComponent(keyword)}`);
}

export function createClinicEntry(req: ClinicEntryRequest): Promise<ClinicEntryResponse> {
  return apiFetch<ClinicEntryResponse>("/api/clinic/entries", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function downloadPrescriptionPdf(
  question_ids: number[], title: string, subtitle: string,
): Promise<Blob> {
  return apiFetchBlob("/api/clinic/prescription-pdf", {
    method: "POST",
    body: JSON.stringify({ question_ids, title, subtitle }),
  });
}

export function fetchPendingRetries(): Promise<PendingRetry[]> {
  return apiFetch("/api/clinic/pending-retries");
}
