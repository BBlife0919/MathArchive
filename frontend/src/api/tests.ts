import { apiFetch } from "./client";
import type { QuestionCard } from "./questions";

export interface TestBasic {
  test_id: number;
  title: string;
  class_id: number | null;
  chapter_label: string | null;
  question_count: number;
  created_at: string | null;
}

export interface StudentTestItem {
  test_id: number;
  title: string;
  chapter_label: string | null;
  question_count: number;
  created_at: string | null;
  result_id: number | null;
  score: number | null;
  total: number | null;
  graded_at: string | null;
}

export interface TestDetail {
  test_id: number;
  title: string;
  chapter_label: string | null;
  items: QuestionCard[];
  existing_answers: Record<number, boolean>;
}

export interface GradeTestResult {
  result_id: number;
  score: number;
  total: number;
  wrong_question_ids: number[];
  prescribed_question_ids: number[];
}

export function createTest(body: {
  title: string;
  class_id: number | null;
  question_ids: number[];
  chapter_label?: string | null;
}): Promise<TestBasic> {
  return apiFetch<TestBasic>("/api/tests", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchStudentTests(studentId: number): Promise<{ tests: StudentTestItem[] }> {
  return apiFetch<{ tests: StudentTestItem[] }>(`/api/tests/student/${studentId}`);
}

export function fetchTestDetail(testId: number, studentId?: number): Promise<TestDetail> {
  const qs = studentId != null ? `?student_id=${studentId}` : "";
  return apiFetch<TestDetail>(`/api/tests/${testId}${qs}`);
}

export function gradeTest(
  testId: number,
  studentId: number,
  answers: { question_id: number; is_correct: boolean }[],
): Promise<GradeTestResult> {
  return apiFetch<GradeTestResult>(`/api/tests/${testId}/grade`, {
    method: "POST",
    body: JSON.stringify({ student_id: studentId, answers }),
  });
}
