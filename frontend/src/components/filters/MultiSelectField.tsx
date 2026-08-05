import { useEffect, useRef, useState } from "react";
import "./MultiSelectField.css";

interface Option<T> {
  value: T;
  label: string;
}

interface Props<T extends string | number> {
  label: string;
  options: Option<T>[];
  selected: T[];
  onChange: (next: T[]) => void;
  disabled?: boolean;
}

export default function MultiSelectField<T extends string | number>({
  label, options, selected, onChange, disabled = false,
}: Props<T>) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  function toggle(value: T) {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  }

  const summary = selected.length === 0 ? "전체" : `${selected.length}개 선택`;

  return (
    <div className="ms-field" ref={rootRef}>
      <label className="ms-label">{label}</label>
      <button
        type="button"
        className="ms-trigger"
        disabled={disabled || options.length === 0}
        onClick={() => setOpen((v) => !v)}
      >
        <span>{summary}</span>
        <span className="ms-caret">▾</span>
      </button>
      {open && (
        <div className="ms-dropdown">
          {selected.length > 0 && (
            <button type="button" className="ms-clear" onClick={() => onChange([])}>
              선택 해제
            </button>
          )}
          {options.map((opt) => (
            <label key={String(opt.value)} className="ms-option">
              <input
                type="checkbox"
                checked={selected.includes(opt.value)}
                onChange={() => toggle(opt.value)}
              />
              {opt.label}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
