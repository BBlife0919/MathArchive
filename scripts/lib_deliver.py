"""교재 PDF 전달 헬퍼.

빌더는 결과를 리포 output/ 에 저장하지만, 사용자 라이브러리는 ~/교재.
다운로드 폴더는 macOS Gatekeeper 가 quarantine 을 붙여 뷰어 빈화면을 유발하므로
다운로드 밖 ~/교재 로 전달하고 격리 속성을 제거한다.
(다운로드 폴더엔 ~/교재 심볼릭 링크가 있어 한 번 클릭으로 진입 가능)
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

LIBRARY = Path.home() / "교재"


def deliver(pdf_path) -> Path:
    """pdf_path 를 ~/교재 로 복사하고 macOS 격리 속성을 제거. 전달본 경로 반환."""
    src = Path(pdf_path)
    LIBRARY.mkdir(exist_ok=True)
    dst = LIBRARY / src.name
    shutil.copy2(src, dst)
    subprocess.run(["xattr", "-c", str(dst)], check=False)
    print(f"[교재] {dst}")
    return dst


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        deliver(p)
