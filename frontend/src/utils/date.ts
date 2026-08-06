/** 로컬(브라우저) 기준 오늘 날짜를 YYYY-MM-DD 로 반환.
 *
 * `new Date().toISOString()` 은 UTC 기준이라 한국 새벽 시간대(00~09시)에
 * "어제" 날짜가 나오는 버그가 있었다 — 로컬 시각의 연/월/일을 직접 조합.
 */
export function todayLocalISO(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}
