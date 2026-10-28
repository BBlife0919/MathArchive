import { useEffect, useMemo, useState } from "react";
import {
  fetchClasses, fetchClassStudents, fetchUnassignedStudents,
  type ClassBasic, type ClassStudent,
} from "../../api/classes";
import { assignTest } from "../../api/tests";
import "./ClassTreeSidebar.css";
import "./TestAssignModal.css";

interface Props {
  testId: number;
  testTitle: string;
  onClose: () => void;
  onAssigned: () => void;
}

// "내 학습지" 목록의 "출제하기" 버튼에서 뜨는 반/학생 피커. ClassTreeSidebar와
// 트리 구조는 비슷하지만, 여기는 여러 명을 한번에 골라 담는 용도라 오른쪽에
// "선택된 학생" 목록을 따로 둔다(2026-10-28 신규).
export default function TestAssignModal({ testId, testTitle, onClose, onAssigned }: Props) {
  const [classes, setClasses] = useState<ClassBasic[] | null>(null);
  const [studentsByClass, setStudentsByClass] = useState<Record<number, ClassStudent[]>>({});
  // "반 통째로 +" 가 classes 는 로드됐지만 studentsByClass 가 아직 안 찬
  // 찰나의 레이스에 눌리면 빈 배열을 담아버리는 문제가 있었다(/근본
  // 1차 검수에서 발견) — 두 로딩이 다 끝난 뒤에야 트리를 보여준다.
  const [studentsLoaded, setStudentsLoaded] = useState(false);
  const [unassigned, setUnassigned] = useState<ClassStudent[]>([]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Map<number, string>>(new Map());
  const [assigning, setAssigning] = useState(false);
  const [done, setDone] = useState<number | null>(null);

  useEffect(() => {
    fetchClasses().then((res) => {
      setClasses(res.classes);
      Promise.all(res.classes.map((c) => fetchClassStudents(c.class_id)
        .then((r) => [c.class_id, r.students] as const)))
        .then((pairs) => {
          setStudentsByClass(Object.fromEntries(pairs));
          setStudentsLoaded(true);
        });
    }).catch(() => { setClasses([]); setStudentsLoaded(true); });
    fetchUnassignedStudents().then((r) => setUnassigned(r.students)).catch(() => setUnassigned([]));
  }, []);

  function toggleExpand(classId: number) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(classId)) next.delete(classId); else next.add(classId);
      return next;
    });
  }

  function addStudent(s: ClassStudent) {
    setSelected((prev) => {
      const next = new Map(prev);
      next.set(s.student_id, s.name);
      return next;
    });
  }

  function addClass(classId: number) {
    const students = studentsByClass[classId] ?? [];
    setSelected((prev) => {
      const next = new Map(prev);
      for (const s of students) next.set(s.student_id, s.name);
      return next;
    });
  }

  function removeStudent(id: number) {
    setSelected((prev) => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }

  const searchResults = useMemo(() => {
    const q = search.trim();
    if (!q) return null;
    const out: ClassStudent[] = [];
    for (const c of classes ?? []) {
      for (const s of studentsByClass[c.class_id] ?? []) {
        if (s.name.includes(q)) out.push(s);
      }
    }
    for (const s of unassigned) {
      if (s.name.includes(q)) out.push(s);
    }
    return out;
  }, [search, classes, studentsByClass, unassigned]);

  async function handleConfirm() {
    if (selected.size === 0) return;
    setAssigning(true);
    try {
      const res = await assignTest(testId, Array.from(selected.keys()));
      setDone(res.assigned_count);
    } finally {
      setAssigning(false);
    }
  }

  return (
    <div className="assign-modal-overlay" onClick={onClose}>
      <div className="assign-modal" onClick={(e) => e.stopPropagation()}>
        <header className="assign-modal-header">
          <div>
            <h2>출제하기</h2>
            <p className="sc-caption">{testTitle}</p>
          </div>
          <button type="button" className="assign-modal-close" onClick={onClose}>✕</button>
        </header>

        {done !== null ? (
          <div className="assign-modal-result">
            <p className="assign-modal-success-text">{done}명에게 새로 출제됐습니다.</p>
            <button type="button" className="btn-primary" onClick={onAssigned}>닫기</button>
          </div>
        ) : classes === null || !studentsLoaded ? (
          <p className="sc-empty">불러오는 중...</p>
        ) : (
          <div className="assign-modal-body">
            <div className="assign-modal-tree-col">
              <input
                className="class-tree-search"
                placeholder="학생이름 혹은 반이름 검색"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <div className="assign-modal-tree">
                {searchResults !== null ? (
                  searchResults.length === 0 ? (
                    <p className="sc-empty">검색 결과가 없습니다.</p>
                  ) : (
                    searchResults.map((s) => (
                      <div key={s.student_id} className="assign-modal-row">
                        <span>{s.name}</span>
                        <button type="button" className="assign-modal-add-btn" onClick={() => addStudent(s)}>+</button>
                      </div>
                    ))
                  )
                ) : (
                  <>
                    {classes.map((c) => (
                      <div key={c.class_id} className="class-tree-group">
                        <div className="assign-modal-row assign-modal-class-row">
                          <button
                            type="button" className="class-tree-class-btn"
                            onClick={() => toggleExpand(c.class_id)}
                          >
                            <span className="class-tree-caret">{expanded.has(c.class_id) ? "▾" : "▸"}</span>
                            {c.name}
                            <span className="class-tree-count">{c.student_count}명</span>
                          </button>
                          <button type="button" className="assign-modal-add-btn" onClick={() => addClass(c.class_id)}>+</button>
                        </div>
                        {expanded.has(c.class_id) && (
                          <div className="class-tree-students">
                            {(studentsByClass[c.class_id] ?? []).map((s) => (
                              <div key={s.student_id} className="assign-modal-row">
                                <span>{s.name}</span>
                                <button type="button" className="assign-modal-add-btn" onClick={() => addStudent(s)}>+</button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                    {unassigned.length > 0 && (
                      <div className="class-tree-group">
                        <button
                          type="button" className="class-tree-class-btn"
                          onClick={() => toggleExpand(-1)}
                        >
                          <span className="class-tree-caret">{expanded.has(-1) ? "▾" : "▸"}</span>
                          미배정
                          <span className="class-tree-count">{unassigned.length}명</span>
                        </button>
                        {expanded.has(-1) && (
                          <div className="class-tree-students">
                            {unassigned.map((s) => (
                              <div key={s.student_id} className="assign-modal-row">
                                <span>{s.name}</span>
                                <button type="button" className="assign-modal-add-btn" onClick={() => addStudent(s)}>+</button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="assign-modal-selected-col">
              <p className="sc-section-title">선택된 학생 {selected.size > 0 ? `${selected.size}명` : ""}</p>
              {selected.size === 0 ? (
                <p className="sc-empty">왼쪽의 + 를 눌러 학생을 선택해 주세요.</p>
              ) : (
                <div className="assign-modal-chips">
                  {Array.from(selected.entries()).map(([id, name]) => (
                    <span key={id} className="assign-modal-chip">
                      {name}
                      <button type="button" onClick={() => removeStudent(id)}>✕</button>
                    </span>
                  ))}
                </div>
              )}
              <button
                type="button" className="btn-primary assign-modal-confirm-btn"
                disabled={selected.size === 0 || assigning}
                onClick={handleConfirm}
              >
                {assigning ? "배정 중..." : "선택 완료"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
