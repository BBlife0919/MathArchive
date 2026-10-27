import { useEffect, useMemo, useState } from "react";
import {
  fetchClasses, fetchClassStudents, fetchUnassignedStudents,
  type ClassBasic, type ClassStudent,
} from "../../api/classes";
import { createStudent } from "../../api/students";
import Expander from "../questions/Expander";
import "./ClassTreeSidebar.css";

interface Props {
  selectedId: number | null;
  onSelect: (id: number, classId: number | null) => void;
}

// 왼쪽 반→학생 트리 — "학생카드"가 "학생관리"로 리뉴얼되며 추가(2026-10-27).
// 기존엔 전체 학생 flat <select> 였는데, 반 단위로 접고 펼 수 있게 바꾸고,
// 클리닉 페이지에 있던 "신규 학생 등록" 도 여기로 옮겨왔다.
export default function ClassTreeSidebar({ selectedId, onSelect }: Props) {
  const [classes, setClasses] = useState<ClassBasic[] | null>(null);
  const [studentsByClass, setStudentsByClass] = useState<Record<number, ClassStudent[]>>({});
  const [unassigned, setUnassigned] = useState<ClassStudent[]>([]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [search, setSearch] = useState("");

  const [newName, setNewName] = useState("");
  const [newSchool, setNewSchool] = useState("");
  const [newGrade, setNewGrade] = useState(1);
  const [registering, setRegistering] = useState(false);

  function reload() {
    fetchClasses().then((res) => {
      setClasses(res.classes);
      // 반 개수가 보통 수십 개 이내라, 한 번에 다 불러와도 검색이
      // 즉시 되고 트리도 바로 펼쳐진다(반별 지연로딩은 더 복잡한 대신
      // 얻는 이득이 적음).
      Promise.all(res.classes.map((c) => fetchClassStudents(c.class_id)
        .then((r) => [c.class_id, r.students] as const)))
        .then((pairs) => setStudentsByClass(Object.fromEntries(pairs)));
    }).catch(() => setClasses([]));
    fetchUnassignedStudents().then((r) => setUnassigned(r.students)).catch(() => setUnassigned([]));
  }

  useEffect(reload, []);

  function toggle(classId: number) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(classId)) next.delete(classId); else next.add(classId);
      return next;
    });
  }

  async function handleRegister() {
    if (!newName.trim()) return;
    setRegistering(true);
    try {
      const s = await createStudent({
        name: newName.trim(), school: newSchool.trim() || null,
        grade: newGrade, class_name: null,
      });
      setNewName(""); setNewSchool(""); setNewGrade(1);
      reload();
      onSelect(s.student_id, null);
    } finally {
      setRegistering(false);
    }
  }

  const searchResults = useMemo(() => {
    const q = search.trim();
    if (!q) return null;
    const out: { student: ClassStudent; className: string; classId: number | null }[] = [];
    for (const c of classes ?? []) {
      for (const s of studentsByClass[c.class_id] ?? []) {
        if (s.name.includes(q)) out.push({ student: s, className: c.name, classId: c.class_id });
      }
    }
    for (const s of unassigned) {
      if (s.name.includes(q)) out.push({ student: s, className: "미배정", classId: null });
    }
    return out;
  }, [search, classes, studentsByClass, unassigned]);

  if (classes === null) {
    return <aside className="class-tree-sidebar"><p className="sc-empty">불러오는 중...</p></aside>;
  }

  return (
    <aside className="class-tree-sidebar">
      <h2 className="student-card-sidebar-title">학생관리</h2>

      <input
        className="class-tree-search"
        placeholder="학생 이름 검색"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <Expander summary="+ 학생 추가">
        <div className="sc-form">
          <label>이름<input value={newName} onChange={(e) => setNewName(e.target.value)} /></label>
          <label>학교<input value={newSchool} onChange={(e) => setNewSchool(e.target.value)} placeholder="예: 광명북중" /></label>
          <label>학년<input type="number" min={1} max={6} value={newGrade} onChange={(e) => setNewGrade(Number(e.target.value))} /></label>
          <button
            type="button" className="btn-primary"
            disabled={registering || !newName.trim()} onClick={handleRegister}
          >
            {registering ? "등록 중..." : "등록 (반은 나중에 배정)"}
          </button>
        </div>
      </Expander>

      <div className="class-tree-list">
        {searchResults !== null ? (
          searchResults.length === 0 ? (
            <p className="sc-empty">검색 결과가 없습니다.</p>
          ) : (
            searchResults.map(({ student, className, classId }) => (
              <button
                key={student.student_id}
                type="button"
                className={student.student_id === selectedId
                  ? "class-tree-student active" : "class-tree-student"}
                onClick={() => onSelect(student.student_id, classId)}
              >
                {student.name}
                <span className="class-tree-student-meta">{className}</span>
              </button>
            ))
          )
        ) : (
          <>
            {classes.map((c) => (
              <div key={c.class_id} className="class-tree-group">
                <button
                  type="button" className="class-tree-class-btn"
                  onClick={() => toggle(c.class_id)}
                >
                  <span className="class-tree-caret">{expanded.has(c.class_id) ? "▾" : "▸"}</span>
                  {c.name}
                  <span className="class-tree-count">{c.student_count}명</span>
                </button>
                {expanded.has(c.class_id) && (
                  <div className="class-tree-students">
                    {(studentsByClass[c.class_id] ?? []).map((s) => (
                      <button
                        key={s.student_id}
                        type="button"
                        className={s.student_id === selectedId
                          ? "class-tree-student active" : "class-tree-student"}
                        onClick={() => onSelect(s.student_id, c.class_id)}
                      >
                        {s.name}
                      </button>
                    ))}
                    {(studentsByClass[c.class_id] ?? []).length === 0 && (
                      <p className="sc-empty">학생 없음</p>
                    )}
                  </div>
                )}
              </div>
            ))}

            {unassigned.length > 0 && (
              <div className="class-tree-group">
                <button
                  type="button" className="class-tree-class-btn"
                  onClick={() => toggle(-1)}
                >
                  <span className="class-tree-caret">{expanded.has(-1) ? "▾" : "▸"}</span>
                  미배정
                  <span className="class-tree-count">{unassigned.length}명</span>
                </button>
                {expanded.has(-1) && (
                  <div className="class-tree-students">
                    {unassigned.map((s) => (
                      <button
                        key={s.student_id}
                        type="button"
                        className={s.student_id === selectedId
                          ? "class-tree-student active" : "class-tree-student"}
                        onClick={() => onSelect(s.student_id, null)}
                      >
                        {s.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
