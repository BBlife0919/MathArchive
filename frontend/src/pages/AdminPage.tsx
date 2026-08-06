import { useEffect, useState } from "react";
import {
  approveUser, deleteUser, fetchAllUsers, fetchPendingUsers, revokeUser, setAdmin,
  type AdminUser, type PendingUser,
} from "../api/admin";
import { useAuth } from "../context/AuthContext";
import "./AdminPage.css";

export default function AdminPage() {
  const { user: me } = useAuth();
  const [pending, setPending] = useState<PendingUser[] | null>(null);
  const [users, setUsers] = useState<AdminUser[] | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  function loadAll() {
    fetchPendingUsers().then(setPending).catch(() => setPending([]));
    fetchAllUsers().then(setUsers).catch(() => setUsers([]));
  }

  useEffect(() => { loadAll(); }, []);

  async function handleApprove(userId: number, username: string) {
    setBusyId(userId);
    try {
      const res = await approveUser(userId);
      setMessage(
        res.ok
          ? (res.message ? `${username} 승인됨 — ${res.message}` : `${username} 승인 완료 (환영 메일 발송됨)`)
          : `승인 실패: ${res.message}`,
      );
      loadAll();
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(userId: number, username: string) {
    setBusyId(userId);
    try {
      await deleteUser(userId);
      setMessage(`${username} 삭제됨`);
      loadAll();
    } finally {
      setBusyId(null);
    }
  }

  async function handleRevoke(userId: number) {
    setBusyId(userId);
    try {
      await revokeUser(userId);
      loadAll();
    } finally {
      setBusyId(null);
    }
  }

  async function handleSetAdmin(userId: number, isAdmin: boolean) {
    setBusyId(userId);
    try {
      await setAdmin(userId, isAdmin);
      loadAll();
    } finally {
      setBusyId(null);
    }
  }

  if (pending === null || users === null) {
    return <div className="admin-page"><p className="sc-empty">불러오는 중...</p></div>;
  }

  return (
    <div className="admin-page">
      <h1 className="exam-builder-title">관리자</h1>
      <p className="sc-caption">회원 승인 대기열 · 권한 관리 · 회원 목록</p>
      {message && <p className="clinic-success-text">{message}</p>}

      <h2 className="sc-section-title">가입 승인 대기</h2>
      {pending.length === 0 ? (
        <p className="sc-empty">대기 중인 가입 신청이 없습니다.</p>
      ) : (
        pending.map((u) => (
          <div key={u.user_id} className="admin-card">
            <div className="admin-card-info">
              <b>{u.name}</b> <span className="admin-username">({u.username})</span>
              <p className="sc-caption">{u.email}</p>
              <p className="sc-caption">신청일: {u.created_at.slice(0, 10)}</p>
            </div>
            <div className="admin-card-actions">
              <button
                type="button" className="btn-primary" disabled={busyId === u.user_id}
                onClick={() => handleApprove(u.user_id, u.username)}
              >
                승인
              </button>
              <button
                type="button" className="btn-secondary" disabled={busyId === u.user_id}
                onClick={() => handleDelete(u.user_id, u.username)}
              >
                삭제
              </button>
            </div>
          </div>
        ))
      )}

      <hr className="filter-divider" />
      <h2 className="sc-section-title">전체 회원</h2>
      {users.length === 0 ? (
        <p className="sc-empty">회원이 없습니다.</p>
      ) : (
        users.map((u) => {
          const isSelf = me?.user_id === u.user_id;
          return (
            <div key={u.user_id} className="admin-card">
              <div className="admin-card-info">
                <b>{u.name}</b> <span className="admin-username">({u.username})</span>
                <p className="sc-caption">{u.email}</p>
                <p className="sc-caption">
                  {u.approved ? "승인" : "대기"}
                  {u.is_admin ? " · admin" : ""} · {u.created_at.slice(0, 10)}
                </p>
              </div>
              <div className="admin-card-actions">
                {u.is_admin ? (
                  !isSelf && (
                    <button
                      type="button" className="btn-secondary" disabled={busyId === u.user_id}
                      onClick={() => handleSetAdmin(u.user_id, false)}
                    >
                      admin↓
                    </button>
                  )
                ) : (
                  <button
                    type="button" className="btn-secondary" disabled={busyId === u.user_id}
                    onClick={() => handleSetAdmin(u.user_id, true)}
                  >
                    admin↑
                  </button>
                )}
                {u.approved ? (
                  !isSelf && (
                    <button
                      type="button" className="btn-secondary" disabled={busyId === u.user_id}
                      onClick={() => handleRevoke(u.user_id)}
                    >
                      정지
                    </button>
                  )
                ) : (
                  <button
                    type="button" className="btn-primary" disabled={busyId === u.user_id}
                    onClick={() => handleApprove(u.user_id, u.username)}
                  >
                    승인
                  </button>
                )}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
