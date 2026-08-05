import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import "./AuthPage.css";

type Mode = "login" | "signup";

export default function AuthPage() {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<{ text: string; isError: boolean } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      if (mode === "login") {
        const res = await login(username, password);
        setMessage({ text: res.message, isError: !res.ok });
      } else {
        const res = await signup(name, username, password, email);
        setMessage({ text: res.message, isError: !res.ok });
        if (res.ok) {
          setMode("login");
        }
      }
    } catch (err) {
      const text = err instanceof ApiError ? err.message : "요청 중 오류가 발생했습니다.";
      setMessage({ text, isError: true });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">MATHOLOGY</h1>
        <p className="auth-subtitle">문제은행 · 시험지 · 교재 제작</p>

        <div className="auth-tabs">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => { setMode("login"); setMessage(null); }}
          >
            로그인
          </button>
          <button
            type="button"
            className={mode === "signup" ? "active" : ""}
            onClick={() => { setMode("signup"); setMessage(null); }}
          >
            회원가입
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {mode === "signup" && (
            <input
              type="text" placeholder="이름" value={name}
              onChange={(e) => setName(e.target.value)} required
            />
          )}
          <input
            type="text" placeholder="아이디" value={username}
            onChange={(e) => setUsername(e.target.value)} required
          />
          {mode === "signup" && (
            <input
              type="email" placeholder="이메일" value={email}
              onChange={(e) => setEmail(e.target.value)} required
            />
          )}
          <input
            type="password" placeholder="비밀번호" value={password}
            onChange={(e) => setPassword(e.target.value)} required
          />
          <button type="submit" disabled={submitting} className="auth-submit">
            {submitting ? "처리 중..." : mode === "login" ? "로그인" : "가입 신청"}
          </button>
        </form>

        {message && (
          <p className={message.isError ? "auth-message error" : "auth-message"}>
            {message.text}
          </p>
        )}
      </div>
    </div>
  );
}
