import { useState, type ReactNode } from "react";
import "./Expander.css";

export default function Expander({
  summary, defaultOpen = false, children,
}: {
  summary: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="expander">
      <button type="button" className="expander-summary" onClick={() => setOpen((v) => !v)}>
        <span className="expander-caret">{open ? "▾" : "▸"}</span>
        {summary}
      </button>
      {open && <div className="expander-body">{children}</div>}
    </div>
  );
}
