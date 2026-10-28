import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { SelectionProvider } from "./context/SelectionContext";
import { BookmarkProvider } from "./context/BookmarkContext";
import AuthPage from "./pages/AuthPage";
import PendingApprovalPage from "./pages/PendingApprovalPage";
import ExamBuilderPage from "./pages/ExamBuilderPage";
import WorksheetsPage from "./pages/WorksheetsPage";
import StudentCardPage from "./pages/StudentCardPage";
import AdminPage from "./pages/AdminPage";
import KakaoQueuePage from "./pages/KakaoQueuePage";
import AuditPage from "./pages/AuditPage";
import AppShell, { type AppPage } from "./components/layout/AppShell";
import LoadingScreen from "./components/LoadingScreen";
import "./styles/theme.css";

function Gate() {
  const { user, loading } = useAuth();
  const [page, setPage] = useState<AppPage>("exam");

  if (loading) {
    return <LoadingScreen />;
  }
  if (!user) {
    return <AuthPage />;
  }
  if (!user.approved) {
    return <PendingApprovalPage />;
  }

  let body;
  if (page === "exam") {
    body = <ExamBuilderPage />;
  } else if (page === "worksheets") {
    body = <WorksheetsPage />;
  } else if (page === "student-card") {
    // TEST 관리의 "오답학습지 만들기"가 useSelection() 으로 시험지
    // 생성기와 같은 선택 상태를 공유해야 해서, SelectionProvider 를 이
    // 페이지에서도 쓸 수 있어야 한다(아래에서 Gate 전체를 감싸는 걸로 통합).
    body = <StudentCardPage />;
  } else if (page === "admin" && user.is_admin) {
    // 관리자가 아니면 탭 자체가 안 보이지만, 방어적으로 한 번 더 체크
    // (app/pages/9_관리자.py 의 auth.is_admin() 체크와 동일한 취지).
    body = <AdminPage />;
  } else if (page === "kakao" && user.is_admin) {
    // app/pages/3_카톡승인큐.py 의 auth.is_admin() 체크와 동일한 취지의 방어적 재확인.
    body = <KakaoQueuePage />;
  } else if (page === "audit" && user.is_admin) {
    // app/pages/5_검수.py 의 auth.is_admin() 체크와 동일한 취지의 방어적 재확인.
    body = <AuditPage />;
  } else {
    body = <p style={{ padding: 24 }}>이 페이지는 관리자 전용입니다.</p>;
  }

  return (
    <SelectionProvider>
      <BookmarkProvider>
        <AppShell activePage={page} onNavigate={setPage}>
          {body}
        </AppShell>
      </BookmarkProvider>
    </SelectionProvider>
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
