import { apiFetch } from "./client";

export interface User {
  user_id: number;
  username: string;
  name: string;
  email: string;
  approved: boolean;
  is_admin: boolean;
}

export interface MeResponse {
  logged_in: boolean;
  user: User | null;
}

export interface MessageResponse {
  ok: boolean;
  message: string;
}

export function fetchMe(): Promise<MeResponse> {
  return apiFetch<MeResponse>("/api/auth/me");
}

export function login(username: string, password: string): Promise<MeResponse> {
  return apiFetch<MeResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function signup(
  name: string, username: string, password: string, email: string,
): Promise<MessageResponse> {
  return apiFetch<MessageResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, username, password, email }),
  });
}

export function logout(): Promise<MessageResponse> {
  return apiFetch<MessageResponse>("/api/auth/logout", { method: "POST" });
}

export function requestPasswordReset(email: string): Promise<MessageResponse> {
  return apiFetch<MessageResponse>("/api/auth/request-password-reset", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(
  token: string, newPassword: string,
): Promise<MessageResponse> {
  return apiFetch<MessageResponse>("/api/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}
