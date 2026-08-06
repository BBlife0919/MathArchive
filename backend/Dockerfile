# FastAPI 백엔드 배포용 이미지. Render에서 이 Dockerfile로 빌드한다
# (dockerContext = 레포 루트, dockerfilePath = backend/Dockerfile).
#
# app/(기존 Streamlit 앱)의 순수 로직 모듈(db.py/curriculum.py/pdf_engine.py/
# auth.py/main.py/clinic_logic.py)을 legacy_bridge.py 가 그대로 import 하므로,
# 루트 requirements.txt(streamlit 포함)도 함께 설치해야 한다 — streamlit
# 자체를 실행하진 않지만 import 시점에 패키지가 있어야 함.
FROM python:3.11-slim

WORKDIR /repo

COPY requirements.txt ./requirements.txt
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r backend/requirements.txt

# Playwright Chromium + 필요한 시스템 라이브러리 (PDF 생성용, pdf_engine.py 가 사용)
RUN playwright install --with-deps chromium

# 소스 복사 — .dockerignore 로 images/(24GB)·db/·raw/·parsed/ 등 런타임에
# 불필요한 대용량 디렉터리는 제외됨 (이미지는 R2 URL로 서빙되고, DB는
# SUPABASE_DB_URL 로 Postgres 접속이라 로컬 sqlite 불필요).
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
