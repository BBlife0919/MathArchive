import "./Pagination.css";

// main.py:_page_window() 와 동일한 로직 — 첫·마지막 + 현재±2, 사이가
// 멀면 null('…') 삽입.
function pageWindow(current: number, last: number): (number | null)[] {
  if (last <= 6) {
    return Array.from({ length: last + 1 }, (_, i) => i);
  }
  const pages = new Set<number>([0, last]);
  for (let p = Math.max(0, current - 2); p <= Math.min(last, current + 2); p++) {
    pages.add(p);
  }
  const sorted = Array.from(pages).sort((a, b) => a - b);
  const result: (number | null)[] = [];
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) result.push(null);
    result.push(p);
  });
  return result;
}

interface Props {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ page, pageSize, total, onPageChange }: Props) {
  const maxPage = total > 0 ? Math.floor((total - 1) / pageSize) : 0;
  if (total <= pageSize) return null;

  const pages = pageWindow(page, maxPage);

  return (
    <div className="pagination">
      <button type="button" disabled={page === 0} onClick={() => onPageChange(page - 1)}>
        ◀
      </button>
      {pages.map((p, i) =>
        p === null ? (
          <span key={`ellipsis-${i}`} className="pagination-ellipsis">…</span>
        ) : (
          <button
            key={p}
            type="button"
            className={p === page ? "pagination-current" : ""}
            onClick={() => onPageChange(p)}
          >
            {p + 1}
          </button>
        ),
      )}
      <button type="button" disabled={page >= maxPage} onClick={() => onPageChange(page + 1)}>
        ▶
      </button>
    </div>
  );
}
