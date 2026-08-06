import type { ReactNode } from "react";
import { useAuth } from "../../context/AuthContext";
import "./AppShell.css";

export type AppPage = "exam" | "student-card" | "clinic" | "admin" | "kakao" | "audit";

const NAV_ITEMS: { page: AppPage; label: string; adminOnly?: boolean }[] = [
  { page: "exam", label: "문제은행 · 시험지" },
  { page: "student-card", label: "학생 카드" },
  { page: "clinic", label: "클리닉" },
  { page: "kakao", label: "카톡 승인 큐", adminOnly: true },
  { page: "audit", label: "검수", adminOnly: true },
  { page: "admin", label: "관리자", adminOnly: true },
];

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
          {NAV_ITEMS.filter((item) => !item.adminOnly || user?.is_admin).map((item) => (
            <button
              key={item.page}
              type="button"
              className={activePage === item.page ? "app-shell-nav-btn active" : "app-shell-nav-btn"}
              onClick={() => onNavigate(item.page)}
            >
              {item.label}
            </button>
          ))}
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
