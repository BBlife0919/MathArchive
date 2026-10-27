import { apiFetch } from "./client";

export interface ClassBasic {
  class_id: number;
  name: string;
  teacher: string | null;
  student_count: number;
}

export interface ClassStudent {
  student_id: number;
  name: string;
  school: string | null;
  grade: number | null;
}

export function fetchClasses(): Promise<{ classes: ClassBasic[] }> {
  return apiFetch<{ classes: ClassBasic[] }>("/api/classes");
}

export function createClass(name: string, teacher?: string | null): Promise<ClassBasic> {
  return apiFetch<ClassBasic>("/api/classes", {
    method: "POST",
    body: JSON.stringify({ name, teacher: teacher ?? null }),
  });
}

export function updateClass(
  classId: number,
  body: { name?: string; teacher?: string | null },
): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/classes/${classId}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function deleteClass(classId: number): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/classes/${classId}`, { method: "DELETE" });
}

export function assignStudentsToClass(
  classId: number,
  studentIds: number[],
): Promise<{ ok: boolean }> {
  return apiFetch<{ ok: boolean }>(`/api/classes/${classId}/assign`, {
    method: "POST",
    body: JSON.stringify({ student_ids: studentIds }),
  });
}

export function fetchClassStudents(classId: number): Promise<{ students: ClassStudent[] }> {
  return apiFetch<{ students: ClassStudent[] }>(`/api/classes/${classId}/students`);
}

export function fetchUnassignedStudents(): Promise<{ students: ClassStudent[] }> {
  return apiFetch<{ students: ClassStudent[] }>("/api/classes/unassigned/students");
}
