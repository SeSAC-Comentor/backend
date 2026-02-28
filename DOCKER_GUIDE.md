# Commento Docker Compose 사용 가이드

## 사전 준비

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치

## 빠른 시작

### 1. 필요한 파일 준비

프로젝트 루트에 `docker-compose.yml`과 `.env` 두 파일만 있으면 됩니다.

### 2. `.env` 파일 생성

`.env.example`을 복사하고 실제 값을 채워넣으세요.

```bash
cp .env.example .env
```

```env
# 필수
OPENAI_API_KEY=sk-your-openai-api-key
JWT_SECRET=your-secure-random-string-at-least-32-chars

# 소셜 로그인 (선택 - 로그인 기능을 사용할 경우)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAKAO_CLIENT_ID=your-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret

# 리다이렉트 URI (프론트엔드 주소에 맞게 설정)
GOOGLE_REDIRECT_URI=http://localhost:3000
KAKAO_REDIRECT_URI=http://localhost:3000
```

> `OPENAI_API_KEY`와 `JWT_SECRET`은 필수입니다. 소셜 로그인을 사용하지 않는다면 OAuth 관련 값은 비워둬도 됩니다.

### 3. 실행

```bash
docker-compose up
```

첫 실행 시:
- Docker Hub에서 `griotold/commento:2.0.0` 이미지를 자동으로 pull합니다
- PostgreSQL이 먼저 기동되고, DB 마이그레이션이 자동 실행됩니다
- 혐오 표현 분류 모델(~400MB)이 다운로드됩니다 (최초 1회)

서버가 뜨면 아래 로그가 출력됩니다:

```
app-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. 확인

- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/

## 주요 명령어

```bash
# 실행 (포그라운드)
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 로그 확인 (백그라운드 실행 시)
docker-compose logs -f app

# 종료
docker-compose down

# 종료 + DB 데이터 삭제 (초기화)
docker-compose down -v
```

## API 엔드포인트

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| GET | `/` | 없음 | 헬스체크 |
| POST | `/api/review` | 없음 | 혐오 발언 분류 |
| POST | `/api/correct` | 선택적 | 댓글 교정 (로그인 시 히스토리 자동 저장) |
| POST | `/api/feedback` | 없음 | 상세 피드백 |
| POST | `/api/auth/google` | 없음 | Google 로그인 |
| POST | `/api/auth/kakao` | 없음 | Kakao 로그인 |
| POST | `/api/auth/refresh` | 없음 | 토큰 갱신 |
| GET | `/api/auth/me` | 필수 | 현재 사용자 정보 |
| GET | `/api/history` | 필수 | 교정 히스토리 목록 |
| GET | `/api/history/{id}` | 필수 | 히스토리 상세 |
| DELETE | `/api/history/{id}` | 필수 | 히스토리 삭제 |

## API 사용 예시

### 댓글 검토

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"comment": "좋은 영상이네요"}'
```

```json
{"is_problematic": false}
```

### 댓글 교정

```bash
curl -X POST http://localhost:8000/api/correct \
  -H "Content-Type: application/json" \
  -d '{"comment": "여자가 무슨 코딩이야"}'
```

```json
{"corrected_comment": "누구나 코딩을 배울 수 있어요"}
```

### 소셜 로그인 플로우

1. 프론트엔드에서 OAuth 팝업을 열어 인증 코드를 받습니다
2. 받은 코드를 백엔드에 POST합니다

```bash
curl -X POST http://localhost:8000/api/auth/kakao \
  -H "Content-Type: application/json" \
  -d '{"code": "인증코드"}'
```

```json
{"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}
```

3. 이후 요청에 `Authorization: Bearer <access_token>` 헤더를 포함합니다

## 포트 충돌 시

| 서비스 | 기본 포트 | 변경 방법 |
|--------|----------|----------|
| API 서버 | 8000 | `docker-compose.yml`에서 `"8000:8000"` → `"원하는포트:8000"` |
| PostgreSQL | 5432 | `docker-compose.yml`에서 `"5432:5432"` → `"원하는포트:5432"` |
