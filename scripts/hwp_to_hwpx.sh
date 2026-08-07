#!/bin/bash
# HWP → HWPX 배치 변환기 (한컴오피스 한글 Mac 필요)
#
# 사용법:
#   ./scripts/hwp_to_hwpx.sh <소스폴더>
#
# 테스트 모드 (첫 1개만):
#   TEST=1 ./scripts/hwp_to_hwpx.sh <소스폴더>

set -u

SRC_DIR="${1:-}"

if [ -z "$SRC_DIR" ] || [ ! -d "$SRC_DIR" ]; then
    echo "사용법: $0 <소스폴더>"
    exit 1
fi

SRC_DIR="$(cd "$SRC_DIR" && pwd)"
echo "소스: $SRC_DIR"

# 한글 앱 실행
open -a "Hancom Office HWP"
sleep 4

# 변환 대상 수집
shopt -s nullglob
HWP_FILES=("$SRC_DIR"/*.hwp)
TOTAL=${#HWP_FILES[@]}
echo "대상: ${TOTAL}개"
echo ""

count=0
ok=0
fail=0
START=$(date +%s)

for hwp in "${HWP_FILES[@]}"; do
    count=$((count + 1))
    base=$(basename "$hwp" .hwp)
    hwpx="$SRC_DIR/$base.hwpx"

    if [ -f "$hwpx" ]; then
        echo "[$count/$TOTAL] ⏭  이미 존재: $base.hwpx"
        ok=$((ok + 1))
        continue
    fi

    echo -n "[$count/$TOTAL] $base.hwp ... "

    osascript <<APPLESCRIPT 2>/dev/null
tell application "Hancom Office HWP"
    activate
    open POSIX file "$hwp"
end tell
delay 2.5

tell application "System Events"
    tell process "Hancom Office HWP"
        set frontmost to true
        delay 0.3
        click menu item "다른 이름으로 저장하기..." of menu 1 of menu bar item "파일" of menu bar 1
    end tell
end tell
delay 2.5

tell application "System Events"
    tell process "Hancom Office HWP"
        try
            set dlg to window "다른 이름으로 저장하기"
            set sg to splitter group 1 of dlg
            click pop up button 2 of sg
            delay 0.8
            click menu item "한글 표준 문서 (*.hwpx)" of menu 1 of pop up button 2 of sg
            delay 0.5
            click button "저장" of sg
            delay 2
            -- 혹시 추가 확인 팝업 뜨면 Return
            try
                keystroke return
            end try
        end try
    end tell
end tell
delay 2

-- 문서 닫기 (저장된 HWPX 문서)
tell application "System Events"
    tell process "Hancom Office HWP"
        keystroke "w" using {command down}
        delay 0.8
        -- 저장 여부 묻는 팝업이 뜨면 "저장 안 함" (D)
        try
            keystroke "d"
        end try
    end tell
end tell
delay 1
APPLESCRIPT

    if [ -f "$hwpx" ]; then
        echo "✓"
        ok=$((ok + 1))
    else
        echo "✗"
        fail=$((fail + 1))
    fi

    if [ "${TEST:-}" = "1" ]; then
        echo ""
        echo "테스트 모드 종료"
        break
    fi
done

END=$(date +%s)
ELAPSED=$((END - START))
echo ""
echo "========================================"
echo "완료: 성공 $ok / 실패 $fail / 총 $count"
echo "소요: ${ELAPSED}초"
echo "========================================"
