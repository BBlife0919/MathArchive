import "./LoadingScreen.css";

export default function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-logo">
        <span className="loading-dot" />
        MATHOLOGY
      </div>
      <div className="loading-bar"><span /></div>
      <p className="loading-caption">불러오는 중...</p>
    </div>
  );
}
