import type { ReactNode } from "react";
import { useAuth } from "../../context/AuthContext";
import "./AppShell.css";

export type AppPage = "exam" | "student-card";

interface Props {
  activePage: AppPage;
  onNavigate: (page: AppPage) => void;
  children: ReactNode;
}

export default function AppShell({ activePage, onNavigate, children }: Props) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-shell-header">
        <nav className="app-shell-nav">
          <span className="app-shell-brand">MATHOLOGY</span>
          <button
            type="button"
            className={activePage === "exam" ? "app-shell-nav-btn active" : "app-shell-nav-btn"}
            onClick={() => onNavigate("exam")}
          >
            문제은행 · 시험지
          </button>
          <button
            type="button"
            className={activePage === "student-card" ? "app-shell-nav-btn active" : "app-shell-nav-btn"}
            onClick={() => onNavigate("student-card")}
          >
            학생 카드
          </button>
        </nav>
        <div className="app-shell-user">
          <span>{user?.name}님</span>
          <button type="button" onClick={() => logout()}>로그아웃</button>
        </div>
      </header>
      <div className="app-shell-body">{children}</div>
    </div>
  );
}
