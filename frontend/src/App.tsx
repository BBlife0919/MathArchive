import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { SelectionProvider } from "./context/SelectionContext";
import AuthPage from "./pages/AuthPage";
import PendingApprovalPage from "./pages/PendingApprovalPage";
import ExamBuilderPage from "./pages/ExamBuilderPage";
import StudentCardPage from "./pages/StudentCardPage";
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
  return (
    <AppShell activePage={page} onNavigate={setPage}>
      {page === "exam" ? (
        <SelectionProvider>
          <ExamBuilderPage />
        </SelectionProvider>
      ) : (
        <StudentCardPage />
      )}
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
