import { useAuth } from "../context/AuthContext";
import "./AuthPage.css";

export default function PendingApprovalPage() {
  const { user, logout } = useAuth();

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">승인 대기 중</h1>
        <p className="auth-subtitle">
          {user?.name}님, 가입 신청이 접수되었습니다.
          <br />
          관리자 승인 후 이용하실 수 있습니다.
        </p>
        <button type="button" className="auth-submit" onClick={() => logout()}>
          로그아웃
        </button>
      </div>
    </div>
  );
}
