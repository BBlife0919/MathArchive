import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import {
  bulkAuto, bulkManual, fetchFlagged, fetchScan, fixAllFlagged,
  fixFlagged, ignoreRemaining, resolveFlagged, saveBaseline, structuralFix,
  type BareWordItem, type FlaggedItem, type ScanResponse,
} from "../api/audit";
import Pagination from "../components/questions/Pagination";
import Expander from "../components/questions/Expander";
import "./AuditPage.css";

const ACTION_LABELS: Record<string, string> = {
  "선택": "선택...",
  ignore: "무시 (도형 라벨/변수 등)",
  map: "→ LaTeX로 매핑",
  remove: "삭제 (스타일 토글 등)",
};

const TOKENS_PER_PAGE = 20;
const EXAM_LABELS: Record<string, string> = { a: "중간", b: "기말" };

export default function AuditPage() {
  const [scan, setScan] = useState<ScanResponse | null>(null);
  const [flagged, setFlagged] = useState<FlaggedItem[] | null>(null);
  const [page, setPage] = useState(0);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ title: string; body: string; kind: string } | null>(null);
  const [manualState, setManualState] = useState<Record<string, { action: string; latex: string }>>({});

  const busy = busyAction !== null;

  function loadScan(force = false) {
    fetchScan(force).then(setScan).catch((e) => showApiError(e));
  }
  function loadFlagged() {
    fetchFlagged().then(setFlagged).catch((e) => showApiError(e));
  }

  useEffect(() => {
    loadScan();
    loadFlagged();
  }, []);

  function showBanner(title: string, body: string, kind = "success") {
    setBanner({ title, body, kind });
  }

  function showApiError(e: unknown) {
    const msg = e instanceof ApiError ? e.message : "네트워크 오류로 요청이 실패했습니다. 잠시 후 다시 시도해주세요.";
    showBanner("처리 실패", msg, "error");
  }

  async function runAction(actionKey: string, fn: () => Promise<void>) {
    setBusyAction(actionKey);
    try {
      await fn();
    } catch (e) {
      showApiError(e);
    } finally {
      setBusyAction(null);
    }
  }

  function handleStructuralFix() {
    return runAction("structural-fix", async () => {
      const res = await structuralFix();
      showBanner(
        "자동 복구 완료",
        `문제 텍스트 ${res.questions_fixed}건, 해설 텍스트 ${res.solutions_fixed}건, ` +
        `선지 ${res.choices_fixed}건 갱신됐습니다. 다음 단계: 알려진 토큰 자동 매핑 버튼을 누르세요.`,
      );
      loadScan(true);
    });
  }

  function handleBulkAuto() {
    return runAction("bulk-auto", async () => {
      const res = await bulkAuto();
      const total = res.mapped + res.removed + res.ignored;
      if (total === 0) {
        showBanner(
          "처리할 토큰 없음",
          "사전/패턴/도형 라벨/그리스 약어로 매칭되는 토큰이 없습니다. " +
          "남은 미상 토큰은 표에서 dropdown으로 수동 처리해주세요.",
          "info",
        );
      } else {
        showBanner(
          "한 방 처리 완료",
          `매핑 ${res.mapped}개, 삭제 ${res.removed}개, 무시 ${res.ignored}개 · ` +
          `DB 문항 변경 ${res.affected_total}건 · 남은 미상 토큰 ${res.remaining}개. ` +
          `다음 단계: 표에 남은 미상 토큰은 dropdown으로 수동 처리 → 미상 dropdown 일괄 적용 → 베이스라인 저장.`,
        );
      }
      loadScan(true);
      setManualState({});
    });
  }

  function handleBulkManual() {
    return runAction("bulk-manual", async () => {
      const items = Object.entries(manualState)
        .filter(([, v]) => v.action && v.action !== "선택")
        .map(([token, v]) => ({ token, action: v.action, latex: v.latex }));
      if (items.length === 0) {
        showBanner("처리할 항목 없음", "dropdown에서 처리 방식을 선택한 토큰이 없습니다.", "warning");
        return;
      }
      const res = await bulkManual(items);
      if (res.done === 0) {
        showBanner("처리할 항목 없음", "dropdown에서 처리 방식을 선택한 토큰이 없습니다.", "warning");
      } else {
        showBanner(
          "미상 dropdown 일괄 적용 완료",
          `처리 토큰 ${res.done}개 · DB 변경 ${res.affected}건 · 남은 미상 토큰 ${res.remaining}개. ` +
          `다음 단계: 베이스라인 저장.`,
        );
      }
      loadScan(true);
      setManualState({});
    });
  }

  function handleIgnoreRemaining() {
    return runAction("ignore-remaining", async () => {
      const res = await ignoreRemaining();
      showBanner(
        "남은 미상 전체 무시 완료",
        `무시 처리 ${res.ignored}개 토큰. DB 변경 0건 (무시는 화이트리스트 등록만). ` +
        `되돌리려면 user_token_mappings 테이블에서 해당 row를 삭제하세요.`,
      );
      loadScan(true);
    });
  }

  function handleSaveBaseline() {
    return runAction("save-baseline", async () => {
      await saveBaseline();
      showBanner(
        "베이스라인 저장 완료",
        "처리된 토큰은 화이트리스트에 반영돼 새로고침 후 사라집니다. 남은 토큰만 표시됩니다.",
      );
      loadScan(true);
    });
  }

  function handleFixAllFlagged() {
    return runAction("fix-all-flagged", async () => {
      const res = await fixAllFlagged();
      showBanner(
        "신고함 한 방 처리 완료",
        `자동 복구 + 처리완료 ${res.fixed}건, 실패 ${res.failed}건. ` +
        `복구된 내용은 검색 페이지에서 확인하세요. 여전히 이상하면 다시 신고하면 됩니다.`,
      );
      loadFlagged();
    });
  }

  function handleFixOne(flagId: number) {
    return runAction(`fix-${flagId}`, async () => {
      await fixFlagged(flagId);
      loadFlagged();
    });
  }

  function handleResolveOne(flagId: number) {
    return runAction(`resolve-${flagId}`, async () => {
      await resolveFlagged(flagId);
      loadFlagged();
    });
  }

  if (scan === null || flagged === null) {
    return (
      <div className="audit-page">
        <p className="audit-empty">
          {banner ? banner.body : "DB 전체 스캔 중... (첫 진입 시 1~2분 걸릴 수 있습니다)"}
        </p>
      </div>
    );
  }

  const struct = scan.struct;
  const bareWords = scan.bare_words;
  const totalTokens = bareWords.length;
  const totalPages = Math.max(1, Math.ceil(totalTokens / TOKENS_PER_PAGE));
  const curPage = Math.min(page, totalPages - 1);
  const start = curPage * TOKENS_PER_PAGE;
  const end = Math.min(start + TOKENS_PER_PAGE, totalTokens);
  const pageTokens = bareWords.slice(start, end);
  const unknownTokens = bareWords.filter((b) => b.recommend_action === null && !b.is_geometry_label);

  return (
    <div className="audit-page">
      <header className="audit-header">
        <h1 className="audit-title">검수 · 데이터 무결성</h1>
        <p className="audit-subtitle">
          누락 토큰 · 구조 오류 · 신고함을 한 화면에서 자동 진단하고 클릭 한 번으로 일괄 처리합니다.
        </p>
      </header>

      {banner && (
        <div className={`audit-banner audit-banner-${banner.kind}`}>
          <div>
            <b>{banner.title}</b>
            <p>{banner.body}</p>
          </div>
          <button type="button" className="btn-ghost" onClick={() => setBanner(null)}>확인</button>
        </div>
      )}

      <section className="audit-card">
        <div className="audit-eyebrow">구조 무결성</div>
        <h2 className="audit-card-title">BOX 짝·코드블록 오인식을 자동으로 복구합니다</h2>
        <div className="audit-stat-row">
          <div className="audit-stat">
            <span className="audit-stat-label">전체 문항</span>
            <span className="audit-stat-value">{struct.total_questions.toLocaleString()}</span>
          </div>
          <div className="audit-stat">
            <span className="audit-stat-label">BOX 짝 어긋남</span>
            <span className="audit-stat-value">{struct.box_mismatch}</span>
          </div>
          <div className="audit-stat">
            <span className="audit-stat-label">코드블록 오인</span>
            <span className="audit-stat-value">{struct.code_block}</span>
          </div>
        </div>
        <button
          type="button" className="btn-primary"
          disabled={busy || (struct.box_mismatch === 0 && struct.code_block === 0)}
          onClick={handleStructuralFix}
        >
          {busyAction === "structural-fix" ? "복구 중..." : "자동 복구"}
        </button>
      </section>

      <section className="audit-card">
        <div className="audit-card-head">
          <div>
            <div className="audit-eyebrow">누락 HWP 토큰</div>
            <h2 className="audit-card-title">수식 안에서 백슬래시 없이 등장하는 단어</h2>
          </div>
          <button type="button" className="btn-ghost" disabled={busy} onClick={() => loadScan(true)}>
            다시 스캔
          </button>
        </div>

        <div className="audit-stat-row">
          <div className="audit-stat">
            <span className="audit-stat-label">현재 누락 토큰</span>
            <span className="audit-stat-value">{totalTokens}</span>
          </div>
          <div className="audit-stat">
            <span className="audit-stat-label">남은 미상 토큰</span>
            <span className="audit-stat-value">{unknownTokens.length}</span>
          </div>
          {scan.new_count > 0 && (
            <div className="audit-stat audit-stat-warn">
              <span className="audit-stat-label">신규 등장</span>
              <span className="audit-stat-value">{scan.new_count}</span>
            </div>
          )}
        </div>

        <div className="audit-toolbar">
          <button type="button" className="btn-primary" disabled={busy} onClick={handleBulkAuto}>
            {busyAction === "bulk-auto" ? "처리 중..." : "① 한 방 처리 (사전+패턴+도형+그리스, 전체)"}
          </button>
          <button type="button" className="btn-secondary" disabled={busy} onClick={handleBulkManual}>
            {busyAction === "bulk-manual" ? "처리 중..." : "③ 미상 dropdown 일괄 적용"}
          </button>
          <button
            type="button" className="btn-secondary" disabled={busy || unknownTokens.length === 0}
            onClick={handleIgnoreRemaining}
          >
            {busyAction === "ignore-remaining" ? "처리 중..." : "남은 미상 전체 무시"}
          </button>
        </div>
        <p className="audit-caption">
          권장 순서: ① 한 방 처리 → ② 남은 미상 토큰은 표에서 dropdown 처리 → ③ 미상 dropdown 일괄 적용 → ④ 베이스라인 저장
        </p>

        <Expander summary="미상 토큰이란? · 처리 가이드">
          <p className="audit-caption">
            미상 토큰 = 사전(SYMBOL_MAP)에도 없고 패턴 인식기(영문 변수 묶음·도형 라벨 등)에도 매칭 안 된 토큰.
          </p>
          <ul>
            <li>수식 토큰(수학 기호로 보이면) → LaTeX로 매핑 선택 + LaTeX 칸에 입력 (예: \prec, \succeq)</li>
            <li>변수/도형 라벨(영문자 묶음) → 무시</li>
            <li>의미 없는 표시 글자(HWP 스타일 토글 등) → 삭제</li>
            <li>모르겠으면 그냥 두기 — 다음에 사전이 업데이트되면 자동 매핑됨</li>
          </ul>
        </Expander>

        <p className="audit-caption audit-page-caption">
          전체 {totalTokens}개 중 {totalTokens ? start + 1 : 0}–{end}번 표시 (페이지 {curPage + 1}/{totalPages})
        </p>
        <Pagination page={curPage} pageSize={TOKENS_PER_PAGE} total={totalTokens} onPageChange={setPage} />

        <div className="audit-table-wrap">
          <table className="audit-token-table">
            <thead>
              <tr><th>토큰</th><th>추천</th><th>처리 방식 (미상 토큰만)</th><th>LaTeX (매핑 시만)</th></tr>
            </thead>
            <tbody>
              {pageTokens.map((b) => (
                <TokenRow
                  key={b.token} item={b}
                  manual={manualState[b.token]}
                  onManualChange={(v) => setManualState((s) => ({ ...s, [b.token]: v }))}
                />
              ))}
            </tbody>
          </table>
        </div>
        <Pagination page={curPage} pageSize={TOKENS_PER_PAGE} total={totalTokens} onPageChange={setPage} />

        <button type="button" className="btn-primary audit-baseline-btn" disabled={busy} onClick={handleSaveBaseline}>
          {busyAction === "save-baseline" ? "저장 중..." : "④ 이번 결과 저장 (베이스라인 갱신)"}
        </button>
      </section>

      <section className="audit-card">
        <div className="audit-card-head">
          <div>
            <div className="audit-eyebrow">신고함</div>
            <h2 className="audit-card-title">검색·시험지에서 사용자가 직접 신고한 문항</h2>
          </div>
          <div className="audit-stat audit-stat-inline">
            <span className="audit-stat-label">미해결 신고</span>
            <span className="audit-stat-value">{flagged.length}</span>
          </div>
        </div>

        {flagged.length === 0 ? (
          <p className="audit-empty">신고된 문항 없음.</p>
        ) : (
          <>
            <div className="audit-toolbar">
              <button type="button" className="btn-primary" disabled={busy} onClick={handleFixAllFlagged}>
                {busyAction === "fix-all-flagged" ? "처리 중..." : `신고함 한 방 처리 (전체 ${flagged.length}건)`}
              </button>
            </div>
            {flagged.slice(0, 20).map((f) => (
              <div key={f.flag_id} className="audit-flag-card">
                <p className="audit-flag-meta">
                  <b>[{f.school}]</b> {f.year}년 {f.semester}학기 {EXAM_LABELS[f.exam_type ?? ""] ?? ""}{" "}
                  {f.question_number}번 · <code>{f.chapter}</code> · qid={f.question_id}
                  <span className="audit-caption"> · 신고일: {f.flagged_at}</span>
                </p>
                <pre className="audit-flag-preview">{(f.question_text ?? "").slice(0, 200)}</pre>
                <div className="audit-flag-actions">
                  <button
                    type="button" className="btn-secondary" disabled={busy}
                    onClick={() => handleFixOne(f.flag_id)}
                  >
                    {busyAction === `fix-${f.flag_id}` ? "복구 중..." : "자동 복구"}
                  </button>
                  <button
                    type="button" className="btn-primary" disabled={busy}
                    onClick={() => handleResolveOne(f.flag_id)}
                  >
                    {busyAction === `resolve-${f.flag_id}` ? "처리 중..." : "처리완료"}
                  </button>
                </div>
              </div>
            ))}
          </>
        )}
      </section>
    </div>
  );
}

function TokenRow({
  item, manual, onManualChange,
}: {
  item: BareWordItem;
  manual: { action: string; latex: string } | undefined;
  onManualChange: (v: { action: string; latex: string }) => void;
}) {
  const hasRec = item.recommend_action !== null || item.is_geometry_label;
  const action = manual?.action ?? "선택";
  const latex = manual?.latex ?? "";

  return (
    <tr>
      <td>
        <code>{item.token}</code> ({item.count}건){item.is_new ? " 🆕" : ""}
      </td>
      <td>
        {item.recommend_action === "map" ? (
          <span>📘 <code>{item.recommend_latex}</code></span>
        ) : item.recommend_action === "remove" ? (
          <span>제거</span>
        ) : item.recommend_action === "ignore" ? (
          <span>🚫 무시</span>
        ) : item.is_geometry_label ? (
          <span>🔤 변수</span>
        ) : (
          <span>미상</span>
        )}
      </td>
      <td>
        {hasRec ? (
          <span className="audit-caption">[한 방 처리]로 자동 적용</span>
        ) : (
          <select
            value={action}
            onChange={(e) => onManualChange({ action: e.target.value, latex })}
          >
            {Object.entries(ACTION_LABELS).map(([k, label]) => (
              <option key={k} value={k}>{label}</option>
            ))}
          </select>
        )}
      </td>
      <td>
        {!hasRec && action === "map" ? (
          <input
            type="text" placeholder="예: \prec" value={latex}
            onChange={(e) => onManualChange({ action, latex: e.target.value })}
          />
        ) : (
          <span className="audit-caption">—</span>
        )}
      </td>
    </tr>
  );
}
