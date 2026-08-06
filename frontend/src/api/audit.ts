import { apiFetch } from "./client";

export interface BareWordItem {
  token: string;
  count: number;
  is_new: boolean;
  recommend_action: string | null;
  recommend_latex: string | null;
  is_geometry_label: boolean;
}

export interface StructScan {
  box_mismatch: number;
  code_block: number;
  total_questions: number;
}

export interface ScanResponse {
  bare_words: BareWordItem[];
  new_count: number;
  struct: StructScan;
  has_baseline: boolean;
}

export interface StructuralFixResult {
  questions_fixed: number;
  solutions_fixed: number;
  choices_fixed: number;
}

export interface BulkAutoResult {
  mapped: number;
  removed: number;
  ignored: number;
  affected_total: number;
  remaining: number;
  mapped_examples: string[];
  ignored_examples: string[];
}

export interface BulkManualItem {
  token: string;
  action: string;
  latex: string;
}

export interface BulkManualResult {
  done: number;
  affected: number;
  remaining: number;
}

export interface FlaggedItem {
  flag_id: number;
  question_id: number;
  flagged_at: string | null;
  reason: string | null;
  school: string | null;
  year: number | null;
  semester: number | null;
  exam_type: string | null;
  question_number: number | null;
  chapter: string | null;
  question_text: string | null;
}

export interface FixAllFlaggedResult {
  fixed: number;
  failed: number;
}

export interface MessageResponse {
  ok: boolean;
  message: string | null;
}

export function fetchScan(force = false): Promise<ScanResponse> {
  return apiFetch(`/api/audit/scan${force ? "?force=true" : ""}`);
}

export function structuralFix(): Promise<StructuralFixResult> {
  return apiFetch("/api/audit/structural-fix", { method: "POST" });
}

export function bulkAuto(): Promise<BulkAutoResult> {
  return apiFetch("/api/audit/bulk-auto", { method: "POST" });
}

export function bulkManual(items: BulkManualItem[]): Promise<BulkManualResult> {
  return apiFetch("/api/audit/bulk-manual", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export function ignoreRemaining(): Promise<{ ignored: number }> {
  return apiFetch("/api/audit/ignore-remaining", { method: "POST" });
}

export function saveBaseline(): Promise<MessageResponse> {
  return apiFetch("/api/audit/save-baseline", { method: "POST" });
}

export function fetchFlagged(): Promise<FlaggedItem[]> {
  return apiFetch("/api/audit/flagged");
}

export function fixFlagged(flagId: number): Promise<MessageResponse> {
  return apiFetch(`/api/audit/flagged/${flagId}/fix`, { method: "POST" });
}

export function resolveFlagged(flagId: number): Promise<MessageResponse> {
  return apiFetch(`/api/audit/flagged/${flagId}/resolve`, { method: "POST" });
}

export function fixAllFlagged(): Promise<FixAllFlaggedResult> {
  return apiFetch("/api/audit/flagged/fix-all", { method: "POST" });
}
