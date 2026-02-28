# 작업 로그 — 2026-02-28

## 목표

기존 stateless Commento API에 PostgreSQL + 소셜 로그인 + 교정 히스토리 기능 추가

---

## 새로 생성한 파일

### DB 레이어
- `src/app/db/__init__.py`
- `src/app/db/base.py` — SQLAlchemy DeclarativeBase
- `src/app/db/session.py` — async engine, sessionmaker, `get_db` 의존성

### ORM 모델
- `src/app/models/user.py` — User 테이블 (provider+provider_id 유니크, email 없음)
- `src/app/models/correction_history.py` — CorrectionHistory 테이블 (user_id FK, JSON problem_types)

### 인증
- `src/app/auth/__init__.py`
- `src/app/auth/jwt.py` — JWT access/refresh 토큰 생성·검증 (HS256)
- `src/app/auth/dependencies.py` — `get_current_user` (필수), `get_optional_user` (선택적) FastAPI Depends
- `src/app/auth/oauth.py` — Google/Kakao OAuth code exchange + 프로필 조회

### 라우터
- `src/app/routers/__init__.py`
- `src/app/routers/comment.py` — 기존 3개 엔드포인트(`/api/review`, `/api/correct`, `/api/feedback`) 이동
- `src/app/routers/auth.py` — `POST /api/auth/google`, `POST /api/auth/kakao`, `POST /api/auth/refresh`, `GET /api/auth/me`
- `src/app/routers/history.py` — `GET /api/history`, `DELETE /api/history/{id}`

### 스키마
- `src/app/schemas/auth.py` — OAuthCodeRequest, TokenResponse, RefreshTokenRequest, UserResponse
- `src/app/schemas/history.py` — HistoryResponse, HistoryListResponse

### 서비스
- `src/app/services/history_service.py` — save, list_by_user (페이지네이션), delete_by_id

### 테스트 (36개, 전부 통과)
- `tests/__init__.py`
- `tests/conftest.py` — aiosqlite in-memory DB fixture, ML 모델 mock, TestClient, test_user/auth_headers fixture
- `tests/test_jwt.py` (7개) — 토큰 생성, 검증, 만료, 잘못된 타입
- `tests/test_auth_endpoints.py` (9개) — 소셜 로그인(POST), 토큰 갱신, /me
- `tests/test_history_service.py` (6개) — 저장, 조회, 페이지네이션, 삭제, 접근 제어
- `tests/test_history_endpoints.py` (6개) — GET/DELETE 엔드포인트, 401 검증
- `tests/test_comment_endpoints.py` (8개) — 기존 엔드포인트 회귀 + 인증 시 히스토리 자동 저장

### 인프라
- `alembic.ini` — Alembic 설정 (DB URL은 env.py에서 주입)
- `alembic/env.py` — async 마이그레이션 설정
- `alembic/versions/3802a276101a_initial_users_and_correction_histories.py` — 초기 마이그레이션
- `docker-compose.yml` — PostgreSQL + app 서비스
- `.env.example` — 환경변수 템플릿

---

## 수정한 기존 파일

| 파일 | 변경 내용 |
|------|----------|
| `pyproject.toml` | sqlalchemy, asyncpg, alembic, PyJWT 의존성 추가. dev 의존성(pytest, pytest-asyncio, aiosqlite) 추가. pytest 설정, `pdm run test` 스크립트 추가 |
| `src/main.py` | lifespan 핸들러 추가, 인라인 라우트 제거 → `app.include_router()` 방식으로 리팩토링 |
| `src/config.py` | DATABASE_URL, JWT_*, GOOGLE_*, KAKAO_* 설정 추가 |
| `src/app/services/comment_service.py` | `correct()` 반환값에 `classification` dict 포함 (히스토리 저장용) |
| `Dockerfile` | CMD에 `alembic upgrade head` 추가 (마이그레이션 후 서버 기동) |

---

## 설계 결정

- **소셜 로그인은 POST 방식**: Extension이 OAuth 팝업을 열어 authorization code를 받고, `POST /api/auth/google` (또는 `/kakao`)에 `{"code": "..."}` 전송 → JSON으로 토큰 응답
- **email 컬럼 제거**: 카카오는 비즈 앱이 아니면 이메일 수집 불가하므로 User 모델에서 email 필드 삭제
- **JSON 컬럼**: `problem_types`에 PostgreSQL ARRAY 대신 JSON 사용 — SQLite 테스트 호환
- **aiosqlite 테스트**: PostgreSQL 없이 CI/로컬에서 실행 가능
- **선택적 인증**: `/api/correct`만 `get_optional_user` 적용 — 로그인 시 히스토리 자동 저장, 비로그인 시 기존과 동일

---

## 테스트 실행

```bash
pdm run test
```
