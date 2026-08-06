import { apiFetch } from "./client";

export interface StudentOption {
  student_id: number;
  name: string;
}

export interface DraftItem {
  queue_id: number;
  student_id: number;
  student_name: string;
  target_phone: string;
  ai_draft: string | null;
  instructor_note: string | null;
  scheduled_at: string;
}

export interface ApprovedItem {
  queue_id: number;
  scheduled_at: string;
  student_name: string;
  target_phone: string;
  instructor_note: string | null;
}

export interface SendLogItem {
  queue_id: number;
  status: string;
  student_name: string;
  target_phone: string;
  sent_at: string | null;
  solapi_msg_id: string | null;
  error_log: string | null;
}

export interface MessageResponse {
  ok: boolean;
  message: string | null;
}

export function fetchKakaoStudents(): Promise<StudentOption[]> {
  return apiFetch("/api/kakao/students");
}

export function createDraft(req: {
  student_id: number;
  target_phone: string;
  template_code: string;
  scheduled_at: string;
}): Promise<MessageResponse> {
  return apiFetch("/api/kakao/drafts", { method: "POST", body: JSON.stringify(req) });
}

export function fetchDrafts(): Promise<DraftItem[]> {
  return apiFetch("/api/kakao/drafts");
}

export function approveDraft(queueId: number, instructorNote: string): Promise<MessageResponse> {
  return apiFetch(`/api/kakao/drafts/${queueId}/approve`, {
    method: "POST",
    body: JSON.stringify({ instructor_note: instructorNote }),
  });
}

export function deleteDraft(queueId: number): Promise<MessageResponse> {
  return apiFetch(`/api/kakao/drafts/${queueId}`, { method: "DELETE" });
}

export function fetchApproved(): Promise<ApprovedItem[]> {
  return apiFetch("/api/kakao/approved");
}

export function revertDraft(queueId: number): Promise<MessageResponse> {
  return apiFetch(`/api/kakao/approved/${queueId}/revert`, { method: "POST" });
}

export function fetchSendLogs(): Promise<SendLogItem[]> {
  return apiFetch("/api/kakao/send-logs");
}
