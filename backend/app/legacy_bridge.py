"""기존 Streamlit 앱(`app/`)의 프레임워크 비의존 모듈을 그대로 import 하기 위한 부트스트랩.

`app/`은 이번 이관 작업에서 절대 수정하지 않는다 (Streamlit 앱과 병행 운영 중).
이 모듈을 다른 모든 backend 모듈보다 먼저 import 하면 `app/` 이 sys.path 에 들어가
`import db`, `import curriculum`, `import pdf_engine`, `import auth`, `import main`
(원본 Streamlit 파일들) 을 그대로 쓸 수 있다.
"""
from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parents[2] / "app"

if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))
