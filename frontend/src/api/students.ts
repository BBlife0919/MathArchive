import { apiFetch } from "./client";

export interface StudentBasic {
  student_id: number;
  name: string;
  school: string | null;
  grade: number | null;
  class_name: string | null;
  note: string | null;
}

export interface PrismScore {
  eval_date: string;
  score_p: number;
  score_r: number;
  score_i: number;
  score_s: number;
  score_m: number;
  note: string | null;
}

export interface ClinicErrorCount {
  code: string;
  label: string;
  count: number;
  category: "이해" | "수행";
}

export interface SelfPredictEntry {
  log_date: string;
  title: string | null;
  predicted: number | null;
  actual: number | null;
  gap: number;
  note: string | null;
}

export interface SelfPredictChartPoint {
  date: string;
  predicted: number | null;
  actual: number | null;
}

export interface ProgressEntry {
  log_date: string;
  category: string;
  chapter: string | null;
  title: string | null;
  planned: string | null;
  actual: string | null;
  score_display: string;
  note: string | null;
}

export interface QuantityGradeCount {
  grade: string;
  count: number;
  pct: number | null;
}

export interface QualitativeEntry {
  eval_date: string;
  note_completion: number;
  written_completion: number;
  textbook_marking: number;
  second_solve_reason: number;
  note: string | null;
}

export interface LogEntry {
  log_date: string;
  log_type: string;
  summary: string | null;
  detail: string | null;
}

export interface StudentDashboard {
  student: StudentBasic;
  clinic_count: number;
  latest_prism: PrismScore | null;
  avg_ris: number | null;
  avg_pm: number | null;
  prism_history: PrismScore[];
  clinic_error_distribution: ClinicErrorCount[];
  self_predict_entries: SelfPredictEntry[];
  self_predict_chart: SelfPredictChartPoint[];
  self_predict_avg_gap: number | null;
  self_predict_over_count: number;
  self_predict_under_count: number;
  progress_entries: ProgressEntry[];
  quantity_grade_counts: QuantityGradeCount[];
  latest_qualitative: QualitativeEntry | null;
  logs: LogEntry[];
}

export interface StudentTemplateItem {
  filename: string;
  label: string;
  available: boolean;
  url: string | null;
}

export function fetchStudents(): Promise<StudentBasic[]> {
  return apiFetch<StudentBasic[]>("/api/students");
}

export function fetchStudentTemplates(): Promise<{ items: StudentTemplateItem[] }> {
  return apiFetch("/api/students/templates");
}

export function fetchStudentDashboard(sid: number): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/dashboard`);
}

export function updateStudentBasic(
  sid: number,
  body: { school: string | null; grade: number; class_name: string | null; note: string | null },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function addPrismEval(
  sid: number,
  body: {
    eval_date: string; score_p: number; score_r: number; score_i: number;
    score_s: number; score_m: number; note: string | null;
  },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/prism`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function addSelfPredict(
  sid: number,
  body: { log_date: string; title: string | null; predicted: number; actual: number; note: string | null },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/self-predict`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function addProgress(
  sid: number,
  body: {
    log_date: string; category: "진도" | "숙제" | "시험"; chapter: string | null;
    title: string | null; planned: string | null; actual: string | null;
    score_raw: number | null; score_max: number | null; note: string | null;
  },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/progress`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function addQuantityAssessment(
  sid: number,
  body: { eval_date: string; grade: "A" | "B" | "C" | "D"; note: string | null },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/assessment/quantity`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function addQualitativeAssessment(
  sid: number,
  body: {
    eval_date: string; note_completion: number; written_completion: number;
    textbook_marking: number; second_solve_reason: number; note: string | null;
  },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/assessment/qualitative`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function addManagementLog(
  sid: number,
  body: { log_date: string; log_type: "보호자" | "출결" | "메모"; summary: string | null; detail: string | null },
): Promise<StudentDashboard> {
  return apiFetch<StudentDashboard>(`/api/students/${sid}/logs`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
