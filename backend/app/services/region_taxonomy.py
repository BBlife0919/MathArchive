"""학교 지역(questions.region) 데이터 정규화 — 시도→구 2단계 계층 구조.

questions.region 컬럼은 자유 텍스트라 같은 지역이 여러 표기로 중복 적재돼
있고(예: "경기가평"/"경기가평군"/"경기가평시"), 일부는 행정구역상 아예
잘못 분류돼 있다(예: "대구경산시" — 경산시는 실제로는 경북 소속, "서울노원고"
— 지역이 아니라 학교명이 들어간 데이터 오류). DB 원본 값은 건드리지 않고
(원본 파일 추적성 보존), 이 모듈이 "원본 region 문자열 → (시도, 표준 구/시/군
표기)"로 매핑하는 프레젠테이션 레이어 역할만 한다.

- 이미 깨끗한 값(대다수)은 이 딕셔너리에 없어도 _derive_province()로
  시도 접두어만 떼어 자동 처리된다.
- 여기 명시된 항목만 "표준 표기로 교정" 또는 "실제로는 다른 시도 소속으로
  재분류"가 적용된다 (2026-10-22, 사용자 확인: "재분류성 오류는 제 판단대로
  정정" — 전체 118종 실측 후 수작업 분류, HANDOVER 성격의 근거는 아래 주석).
"""
from __future__ import annotations

PROVINCES = [
    "서울", "경기", "강원", "충북", "충남", "전북", "전남",
    "경북", "경남", "대구", "대전", "부산", "인천", "광주", "울산", "세종", "제주",
]

# 구/시/군 세부 정보가 없는 "구 미상" raw row(예: 대구/부산처럼 구 없이 광역시
# 이름만 적힌 값)는 _derive_province()가 canonical == province로 떨어뜨려
# district 목록에 자기 자신이 포함되게만 하면 되므로 별도 룩업 테이블 없이
# province 파생 로직만으로 처리된다.

# raw region → 표준 표기(district만, province 접두어 뗀 형태가 아니라 원본과
# 같은 "시도+구/시/군" 풀 네임으로 유지 — region_schools 등 기존 키 포맷과
# 호환, 검색 SQL에는 raw 값 그대로 돌려써야 하므로 CANONICAL_TO_RAW 로 역매핑).
# 단순 표기 변형(오타/접미사 불일치)과 실제 행정구역 재분류를 구분 없이 같은
# 딕셔너리에 두되, 재분류 항목에는 근거 주석을 남긴다.
RAW_TO_CANONICAL: dict[str, str] = {
    # ── 단순 표기 변형/오타 (같은 지역, 접미사·오타만 다름) ──
    "경기가평": "경기가평군",
    "경기가평시": "경기가평군",
    "경기양평": "경기양평군",
    "경기팽택시": "경기평택시",  # 오타: 팽택→평택
    "경기도용인시": "경기용인시",
    "고양시": "경기고양시",
    "부천": "경기부천시",
    "용인수지구": "경기용인시",  # 용인시 수지구 → 용인시로 합산(구 단위 세분 안 함)
    "경남창녕": "경남창녕군",
    "충남아신시": "충남아산시",  # 오타: 아신→아산
    "충남청양시": "충남청양군",  # 청양은 시가 아니라 군

    # ── 실제 행정구역 재분류 (단순 오타 아님, 사용자 확인 후 정정 2026-10-22) ──
    "대구경산시": "경북경산시",  # 경산시는 대구가 아니라 경북 소속
    "충남평택시": "경기평택시",  # 평택시는 충남이 아니라 경기 소속
    "전남광주담양군": "전남담양군",  # 담양군은 전남 소속, "광주" 접두는 오류로 판단해 제거
    "서울노원고": "서울노원구",  # region 컬럼에 학교명("노원고")이 잘못 들어간 데이터 — 학교 위치(노원구)로 정정
}


def _derive_province(canonical: str) -> str:
    """표준 표기에서 시도를 떼어낸다. "경기가평군"→"경기", "서울강남구"→"서울",
    "대구"→"대구"(구 없는 bare row), "세종"→"세종"."""
    for p in PROVINCES:
        if canonical.startswith(p):
            return p
    return canonical


def canonicalize(raw: str) -> str:
    return RAW_TO_CANONICAL.get(raw, raw)


def build_taxonomy(raw_regions: set[str]) -> dict:
    """load_filter_options() 에서 모은 raw region 전체 집합으로 시도→구
    계층과 canonical→raw 역매핑을 만든다.

    반환:
      - provinces: 실제로 데이터가 있는 시도만, PROVINCES 순서대로
      - province_districts: {시도: [표준 구/시/군 표기, ...]} (시도 자기 자신과
        같은 "구 미상" 항목도 district 목록에 포함될 수 있음)
      - canonical_to_raw: {표준 표기: [원본 raw region, ...]} — 검색 SQL은
        원본 값으로만 매칭되므로, 사용자가 표준 표기를 선택하면 이 역매핑으로
        원본 값 전부를 풀어서 region IN (...) 에 넣어야 한다.
    """
    canonical_to_raw: dict[str, list[str]] = {}
    for raw in raw_regions:
        canon = canonicalize(raw)
        canonical_to_raw.setdefault(canon, []).append(raw)

    province_district_set: dict[str, set[str]] = {}
    for canon in canonical_to_raw:
        province = _derive_province(canon)
        province_district_set.setdefault(province, set()).add(canon)

    provinces = [p for p in PROVINCES if p in province_district_set]
    province_districts = {
        p: sorted(province_district_set[p]) for p in provinces
    }
    return {
        "provinces": provinces,
        "province_districts": province_districts,
        "canonical_to_raw": {c: sorted(r) for c, r in canonical_to_raw.items()},
    }


def expand_canonical_regions(selected: list[str], canonical_to_raw: dict[str, list[str]]) -> list[str]:
    """프론트가 보낸 표준 표기 선택값을 검색 SQL용 원본 raw region 리스트로
    풀어낸다. canonical_to_raw 에 없는 값(혹시 모를 구버전 캐시 등)은 원본
    그대로 1개짜리 취급해 안전하게 통과시킨다."""
    out: list[str] = []
    for c in selected:
        out.extend(canonical_to_raw.get(c, [c]))
    return out
