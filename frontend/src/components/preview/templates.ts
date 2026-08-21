// 학습지 템플릿 드롭다운 골격. 지금은 지금 렌더링 스타일 그대로인 "기본"
// 하나뿐이라 선택해도 요청 바디에는 반영하지 않는다 — 템플릿을 추가할 때
// 이 배열에 옵션만 늘리고, PdfOptionsForm/BookOptionsForm 의 request
// 구성부에서 실제로 그 값을 사용하도록 이어주면 된다.
export type TemplateId = "default";

export const TEMPLATE_OPTIONS: { value: TemplateId; label: string }[] = [
  { value: "default", label: "기본" },
];
