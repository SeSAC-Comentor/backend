from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.core.middlewares.cors import setup_cors
from src.app.core.middlewares.rate_limit import setup_rate_limit
from src.app.routers import comment, auth, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: DB 엔진은 session.py에서 이미 생성됨
    yield
    # shutdown: 엔진 정리
    from src.app.db.session import engine
    await engine.dispose()


app = FastAPI(
    title="Commento API",
    description="""
    한국어 혐오 표현 분류 및 댓글 개선 API

    ## 기능
    - **글 검토**: 혐오 표현 포함 여부 즉시 판정
    - **글 수정**: 부적절한 표현을 적절한 표현으로 수정
    - **피드백**: 문제 유형, 심각도, AI 설명 제공

    ## 분류 카테고리
    - 혐오 (hate)
    - 성차별 (bias_gender)
    - 기타 차별 (bias_others)
    - 욕설/모욕 (offensive)
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

setup_cors(app)
setup_rate_limit(app)

app.include_router(comment.router)
app.include_router(auth.router)
app.include_router(history.router)


@app.get("/")
async def health_check():
    return {"status": "ok"}
