from __future__ import annotations

# legacy_bridge 는 다른 어떤 backend 모듈보다 먼저 import 되어야 한다
# (app/ 을 sys.path 에 넣어 기존 Streamlit 모듈을 import 가능하게 함).
from . import legacy_bridge  # noqa: F401
from .config import CORS_ORIGINS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import main as legacy_main  # type: ignore  (IMAGE_DIR 재사용 — 로컬 이미지 폴백용)

from .routers import admin, auth, clinic, exam, meta, questions, students

app = FastAPI(title="MathDB API")

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


@app.get("/api/ping")
def ping():
    return {"ok": True}
