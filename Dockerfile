# 1단계: 빌드 (멀티스테이지)
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml pdm.lock ./

# PDM 설치 및 의존성 설치
RUN pip install --no-cache-dir pdm && \
    pdm install --prod 

# 2단계: 런타임
FROM python:3.13-slim

WORKDIR /app

# 1단계에서 설치된 패키지들 복사
COPY --from=builder /app/.venv /app/.venv

# 소스 코드 복사
COPY . .

# 환경 변수
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 

# 포트
EXPOSE 8000

# 실행: 마이그레이션 후 서버 기동
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
