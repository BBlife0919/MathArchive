import { apiFetch } from "./client";

export interface PendingUser {
  user_id: number;
  username: string;
  name: string;
  email: string;
  created_at: string;
}

export interface AdminUser {
  user_id: number;
  username: string;
  name: string;
  email: string;
  approved: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface MessageResponse {
  ok: boolean;
  message: string | null;
}

export function fetchPendingUsers(): Promise<PendingUser[]> {
  return apiFetch("/api/admin/pending-users");
}

export function fetchAllUsers(): Promise<AdminUser[]> {
  return apiFetch("/api/admin/users");
}

export function approveUser(userId: number): Promise<MessageResponse> {
  return apiFetch(`/api/admin/users/${userId}/approve`, { method: "POST" });
}

export function revokeUser(userId: number): Promise<MessageResponse> {
  return apiFetch(`/api/admin/users/${userId}/revoke`, { method: "POST" });
}

export function deleteUser(userId: number): Promise<MessageResponse> {
  return apiFetch(`/api/admin/users/${userId}`, { method: "DELETE" });
}

export function setAdmin(userId: number, isAdmin: boolean): Promise<MessageResponse> {
  return apiFetch(`/api/admin/users/${userId}/set-admin`, {
    method: "POST",
    body: JSON.stringify({ is_admin: isAdmin }),
  });
}
