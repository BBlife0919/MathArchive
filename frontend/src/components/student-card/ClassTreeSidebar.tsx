import { useEffect, useMemo, useState } from "react";
import {
  assignStudentsToClass, createClass, deleteClass, fetchClasses, fetchClassStudents,
  fetchUnassignedStudents, updateClass, type ClassBasic, type ClassStudent,
} from "../../api/classes";
import { createStudent } from "../../api/students";
import Expander from "../questions/Expander";
import "./ClassTreeSidebar.css";

interface Props {
  selectedId: number | null;
  onSelect: (id: number) => void;
  // 바뀔 때마다 트리를 다시 불러온다(학생 삭제 등 사이드바 바깥에서 일어난
  // 변경을 반영).
  refreshKey?: number;
}

// 왼쪽 반→학생 트리 — "학생카드"가 "학생관리"로 리뉴얼되며 추가(2026-10-27).
// 기존엔 전체 학생 flat <select> 였는데, 반 단위로 접고 펼 수 있게 바꾸고,
// 클리닉 페이지에 있던 "신규 학생 등록" 도 여기로 옮겨왔다.
export default function ClassTreeSidebar({ selectedId, onSelect, refreshKey }: Props) {
  const [classes, setClasses] = useState<ClassBasic[] | null>(null);
  const [studentsByClass, setStudentsByClass] = useState<Record<number, ClassStudent[]>>({});
  const [unassigned, setUnassigned] = useState<ClassStudent[]>([]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [search, setSearch] = useState("");

  const [newName, setNewName] = useState("");
  const [newSchool, setNewSchool] = useState("");
  const [newGrade, setNewGrade] = useState(1);
  const [registering, setRegistering] = useState(false);

  const [newClassName, setNewClassName] = useState("");
  const [newClassTeacher, setNewClassTeacher] = useState("");
  const [creatingClass, setCreatingClass] = useState(false);
  const [movingId, setMovingId] = useState<number | null>(null);

  const [editingClassId, setEditingClassId] = useState<number | null>(null);
  const [editClassName, setEditClassName] = useState("");
  const [savingClassId, setSavingClassId] = useState<number | null>(null);
  const [deletingClassId, setDeletingClassId] = useState<number | null>(null);

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

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(reload, [refreshKey]);

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
      onSelect(s.student_id);
    } finally {
      setRegistering(false);
    }
  }

  async function handleCreateClass() {
    if (!newClassName.trim()) return;
    setCreatingClass(true);
    try {
      await createClass(newClassName.trim(), newClassTeacher.trim() || null);
      setNewClassName(""); setNewClassTeacher("");
      reload();
    } finally {
      setCreatingClass(false);
    }
  }

  async function handleMoveStudent(studentId: number, targetClassId: number) {
    setMovingId(studentId);
    try {
      await assignStudentsToClass(targetClassId, [studentId]);
      reload();
    } finally {
      setMovingId(null);
    }
  }

  function startEditClass(c: ClassBasic) {
    setEditingClassId(c.class_id);
    setEditClassName(c.name);
  }

  async function handleRenameClass(classId: number) {
    const name = editClassName.trim();
    if (!name) return;
    setSavingClassId(classId);
    try {
      await updateClass(classId, { name });
      setEditingClassId(null);
      reload();
    } finally {
      setSavingClassId(null);
    }
  }

  async function handleDeleteClass(c: ClassBasic) {
    const ok = window.confirm(
      `"${c.name}" 반을 삭제할까요? 소속 학생 ${c.student_count}명은 삭제되지 않고 미배정으로 이동합니다.`,
    );
    if (!ok) return;
    setDeletingClassId(c.class_id);
    try {
      await deleteClass(c.class_id);
      reload();
    } finally {
      setDeletingClassId(null);
    }
  }

  const searchResults = useMemo(() => {
    const q = search.trim();
    if (!q) return null;
    const out: { student: ClassStudent; className: string }[] = [];
    for (const c of classes ?? []) {
      for (const s of studentsByClass[c.class_id] ?? []) {
        if (s.name.includes(q)) out.push({ student: s, className: c.name });
      }
    }
    for (const s of unassigned) {
      if (s.name.includes(q)) out.push({ student: s, className: "미배정" });
    }
    return out;
  }, [search, classes, studentsByClass, unassigned]);

  if (classes === null) {
    return <aside className="class-tree-sidebar"><p className="sc-empty">불러오는 중...</p></aside>;
  }
  const classList = classes;

  function renderMoveSelect(s: ClassStudent, currentClassId: number | null) {
    return (
      <select
        className="class-tree-move-select"
        value={currentClassId ?? ""}
        disabled={movingId === s.student_id}
        onClick={(e) => e.stopPropagation()}
        onChange={(e) => handleMoveStudent(s.student_id, Number(e.target.value))}
      >
        <option value="" disabled>반 이동</option>
        {classList.map((c) => (
          <option key={c.class_id} value={c.class_id}>{c.name}</option>
        ))}
      </select>
    );
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

      <div className="class-tree-add-row">
        <Expander summary="+ 반 만들기">
          <div className="sc-form">
            <label>반 이름<input value={newClassName} onChange={(e) => setNewClassName(e.target.value)} placeholder="예: 중2 B반" /></label>
            <label>담당 강사 (선택)<input value={newClassTeacher} onChange={(e) => setNewClassTeacher(e.target.value)} /></label>
            <button
              type="button" className="btn-primary"
              disabled={creatingClass || !newClassName.trim()} onClick={handleCreateClass}
            >
              {creatingClass ? "생성 중..." : "반 생성"}
            </button>
          </div>
        </Expander>

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
      </div>

      <div className="class-tree-list">
        {searchResults !== null ? (
          searchResults.length === 0 ? (
            <p className="sc-empty">검색 결과가 없습니다.</p>
          ) : (
            searchResults.map(({ student, className }) => (
              <button
                key={student.student_id}
                type="button"
                className={student.student_id === selectedId
                  ? "class-tree-student active" : "class-tree-student"}
                onClick={() => onSelect(student.student_id)}
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
                {editingClassId === c.class_id ? (
                  <div className="class-tree-class-edit">
                    <input
                      className="class-tree-class-edit-input"
                      value={editClassName}
                      autoFocus
                      onChange={(e) => setEditClassName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleRenameClass(c.class_id);
                        if (e.key === "Escape") setEditingClassId(null);
                      }}
                    />
                    <button
                      type="button" className="class-tree-icon-btn save"
                      disabled={savingClassId === c.class_id || !editClassName.trim()}
                      onClick={() => handleRenameClass(c.class_id)}
                    >
                      저장
                    </button>
                    <button type="button" className="class-tree-icon-btn" onClick={() => setEditingClassId(null)}>
                      취소
                    </button>
                  </div>
                ) : (
                  <div className="class-tree-class-row">
                    <button
                      type="button" className="class-tree-class-btn"
                      onClick={() => toggle(c.class_id)}
                    >
                      <span className="class-tree-caret">{expanded.has(c.class_id) ? "▾" : "▸"}</span>
                      {c.name}
                      <span className="class-tree-count">{c.student_count}명</span>
                    </button>
                    <div className="class-tree-class-actions">
                      <button
                        type="button" className="class-tree-icon-btn" title="반 이름 수정"
                        onClick={() => startEditClass(c)}
                      >
                        ✎
                      </button>
                      <button
                        type="button" className="class-tree-icon-btn danger" title="반 삭제"
                        disabled={deletingClassId === c.class_id}
                        onClick={() => handleDeleteClass(c)}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                )}
                {expanded.has(c.class_id) && (
                  <div className="class-tree-students">
                    {(studentsByClass[c.class_id] ?? []).map((s) => (
                      <div key={s.student_id} className="class-tree-student-row">
                        <button
                          type="button"
                          className={s.student_id === selectedId
                            ? "class-tree-student active" : "class-tree-student"}
                          onClick={() => onSelect(s.student_id)}
                        >
                          {s.name}
                        </button>
                        {renderMoveSelect(s, c.class_id)}
                      </div>
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
                      <div key={s.student_id} className="class-tree-student-row">
                        <button
                          type="button"
                          className={s.student_id === selectedId
                            ? "class-tree-student active" : "class-tree-student"}
                          onClick={() => onSelect(s.student_id)}
                        >
                          {s.name}
                        </button>
                        {classes.length > 0 && renderMoveSelect(s, null)}
                      </div>
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
