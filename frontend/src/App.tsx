import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { SelectionProvider } from "./context/SelectionContext";
import AuthPage from "./pages/AuthPage";
import PendingApprovalPage from "./pages/PendingApprovalPage";
import ExamBuilderPage from "./pages/ExamBuilderPage";
import StudentCardPage from "./pages/StudentCardPage";
import ClinicPage from "./pages/ClinicPage";
import AdminPage from "./pages/AdminPage";
import KakaoQueuePage from "./pages/KakaoQueuePage";
import AppShell, { type AppPage } from "./components/layout/AppShell";
import "./styles/theme.css";

function Gate() {
  const { user, loading } = useAuth();
  const [page, setPage] = useState<AppPage>("exam");

  if (loading) {
    return <div style={{ padding: 24 }}>불러오는 중...</div>;
  }
  if (!user) {
    return <AuthPage />;
  }
  if (!user.approved) {
    return <PendingApprovalPage />;
  }

  let body;
  if (page === "exam") {
    body = (
      <SelectionProvider>
        <ExamBuilderPage />
      </SelectionProvider>
    );
  } else if (page === "student-card") {
    body = <StudentCardPage />;
  } else if (page === "clinic") {
    body = <ClinicPage />;
  } else if (page === "admin" && user.is_admin) {
    // 관리자가 아니면 탭 자체가 안 보이지만, 방어적으로 한 번 더 체크
    // (app/pages/9_관리자.py 의 auth.is_admin() 체크와 동일한 취지).
    body = <AdminPage />;
  } else if (page === "kakao" && user.is_admin) {
    // app/pages/3_카톡승인큐.py 의 auth.is_admin() 체크와 동일한 취지의 방어적 재확인.
    body = <KakaoQueuePage />;
  } else {
    body = <p style={{ padding: 24 }}>이 페이지는 관리자 전용입니다.</p>;
  }

  return (
    <AppShell activePage={page} onNavigate={setPage}>
      {body}
    </AppShell>
  );
}

function App() {
  return (
    <AuthProvider>
      <Gate />
    </AuthProvider>
  );
}

export default App;
