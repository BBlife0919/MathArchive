import { apiFetch } from "./client";
import type { ContentSegment } from "../components/content/QuestionContent";

export interface QuestionCard {
  question_id: number;
  meta_short: string;
  meta_full: string;
  school: string | null;
  chapter: string | null;
  difficulty: string | null;
  points: number | null;
  is_subjective: boolean;
  error_note: string | null;
  content_segments: ContentSegment[];
  choices_text: string;
  answer: string | null;
  answer_display: string | null;
  solution_segments: ContentSegment[];
}

export interface FiltersResponse {
  schools: string[];
  regions: string[];
  years: number[];
  grades: number[];
  semesters: number[];
  exam_types: string[];
  difficulties: string[];
  curriculum: Record<string, Record<string, string[]>>;
}

export type QuestionType = "all" | "choice" | "subjective";

export interface SearchRequest {
  quick_search: string;
  regions: string[];
  schools: string[];
  grades: number[];
  years: number[];
  semesters: number[];
  exam_types: string[];
  subjects: string[];
  majors: string[];
  minors: string[];
  difficulties: string[];
  question_type: QuestionType;
  keyword: string;
  page: number;
  page_size: number;
}

export interface SearchResponse {
  total: number;
  page: number;
  page_size: number;
  items: QuestionCard[];
}

export interface ByIdsResponse {
  items: QuestionCard[];
}

export interface SearchIdsResponse {
  question_ids: number[];
}

export interface MiniTestRequest extends SearchRequest {
  mini_count: number;
  mini_easy_pct: number;
}

export interface MiniTestResponse {
  question_ids: number[];
  pool_size: number;
}

export function fetchFilters(): Promise<FiltersResponse> {
  return apiFetch<FiltersResponse>("/api/filters");
}

export function searchQuestions(req: SearchRequest): Promise<SearchResponse> {
  return apiFetch<SearchResponse>("/api/questions/search", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function searchQuestionIds(req: SearchRequest): Promise<SearchIdsResponse> {
  return apiFetch<SearchIdsResponse>("/api/questions/search-ids", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function fetchQuestionsByIds(
  questionIds: number[],
  preserveOrder = false,
): Promise<ByIdsResponse> {
  return apiFetch<ByIdsResponse>("/api/questions/by-ids", {
    method: "POST",
    body: JSON.stringify({ question_ids: questionIds, preserve_order: preserveOrder }),
  });
}

export function generateMiniTest(req: MiniTestRequest): Promise<MiniTestResponse> {
  return apiFetch<MiniTestResponse>("/api/questions/mini-test", {
    method: "POST",
    body: JSON.stringify(req),
  });
}
