import { apiFetchBlob } from "./client";

export interface ExamPdfRequest {
  question_ids: number[];
  title: string;
  subtitle?: string | null;
  include_source: boolean;
  include_logo: boolean;
}

export function downloadExamPdf(req: ExamPdfRequest): Promise<Blob> {
  return apiFetchBlob("/api/exam/pdf", {
    method: "POST",
    body: JSON.stringify(req),
  });
}
