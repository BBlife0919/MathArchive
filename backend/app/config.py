"""루트 .env 로드 — 기존 Streamlit 앱과 동일한 시크릿 파일을 공유한다.

backend/.env 를 별도로 만들지 않는다 (크리덴셜 이중 관리 방지, 계획 문서 참고).
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ROOT_ENV)

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
