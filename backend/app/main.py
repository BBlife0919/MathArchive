from __future__ import annotations

# legacy_bridge 는 다른 어떤 backend 모듈보다 먼저 import 되어야 한다
# (app/ 을 sys.path 에 넣어 기존 Streamlit 모듈을 import 가능하게 함).
from . import legacy_bridge  # noqa: F401
from .config import CORS_ORIGINS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import main as legacy_main  # type: ignore  (IMAGE_DIR 재사용 — 로컬 이미지 폴백용)

from .routers import admin, audit, auth, clinic, exam, kakao, meta, questions, students
from .services import similarity_service

app = FastAPI(title="MathDB API")


@app.on_event("startup")
def _warm_similarity_index() -> None:
    # 유사문항 인덱스(256MB)를 백그라운드로 미리 로드 — 첫 클릭이 느려지는
    # 문제를 서버 기동 중에 끝내둔다(backend/app/services/similarity_service.py
    # warm_async() 참고).
    similarity_service.warm_async()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if legacy_main.IMAGE_DIR.exists():
    app.mount(
        "/static/images",
        StaticFiles(directory=str(legacy_main.IMAGE_DIR)),
        name="images",
    )

if students.TEMPLATES_DIR.exists():
    app.mount(
        "/static/student_templates",
        StaticFiles(directory=str(students.TEMPLATES_DIR)),
        name="student_templates",
    )

app.include_router(meta.router)
app.include_router(questions.router)
app.include_router(auth.router)
app.include_router(exam.router)
app.include_router(students.router)
app.include_router(clinic.router)
app.include_router(admin.router)
app.include_router(kakao.router)
app.include_router(audit.router)


@app.get("/api/ping")
def ping():
    return {"ok": True}
