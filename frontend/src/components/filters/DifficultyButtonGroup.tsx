import "./DifficultyButtonGroup.css";

// 표시 순서는 사용자가 명시한 "킬상중하" 순서를 그대로 따른다.
const DIFFICULTY_ORDER = ["킬", "상", "중", "하"];

interface Props {
  options: string[];
  selected: string[];
  onChange: (next: string[]) => void;
}

export default function DifficultyButtonGroup({ options, selected, onChange }: Props) {
  const known = new Set(options);
  const ordered = DIFFICULTY_ORDER.filter((d) => known.has(d));
  // 혹시 모를 신규 난이도 값은 뒤에 그대로 붙여 누락 없이 표시.
  const rest = options.filter((d) => !DIFFICULTY_ORDER.includes(d));

  function toggle(value: string) {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  }

  return (
    <div className="diff-btn-field">
      <label className="ms-label">난이도</label>
      <div className="diff-btn-group">
        {[...ordered, ...rest].map((value) => (
          <button
            key={value}
            type="button"
            className={selected.includes(value) ? "diff-btn active" : "diff-btn"}
            onClick={() => toggle(value)}
          >
            {value}
          </button>
        ))}
      </div>
    </div>
  );
}
