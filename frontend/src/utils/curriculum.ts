// app/curriculum.py 의 helper 함수(major_chapters/minor_chapters/expand_to_minors)와
// 동일한 로직의 클라이언트 사이드 포팅. 필터 옵션은 /api/filters 의 curriculum
// 트리를 그대로 쓰므로 서버 왕복 없이 캐스케이딩 가능.
export type CurriculumTree = Record<string, Record<string, string[]>>;

export function majorChapters(tree: CurriculumTree, subjects: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of subjects) {
    for (const major of Object.keys(tree[s] ?? {})) {
      if (!seen.has(major)) {
        seen.add(major);
        out.push(major);
      }
    }
  }
  return out;
}

export function minorChapters(
  tree: CurriculumTree, subjects: string[], majors: string[],
): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const s of subjects) {
    const subjMap = tree[s] ?? {};
    for (const major of majors) {
      for (const minor of subjMap[major] ?? []) {
        if (!seen.has(minor)) {
          seen.add(minor);
          out.push(minor);
        }
      }
    }
  }
  return out;
}

export function allMinorChaptersInSubjects(
  tree: CurriculumTree, subjects: string[],
): string[] {
  return minorChapters(tree, subjects, majorChapters(tree, subjects));
}
