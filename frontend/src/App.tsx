import { AuthProvider, useAuth } from "./context/AuthContext";
import { SelectionProvider } from "./context/SelectionContext";
import AuthPage from "./pages/AuthPage";
import PendingApprovalPage from "./pages/PendingApprovalPage";
import ExamBuilderPage from "./pages/ExamBuilderPage";
import "./styles/theme.css";

function Gate() {
  const { user, loading } = useAuth();

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
    <SelectionProvider>
      <ExamBuilderPage />
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
