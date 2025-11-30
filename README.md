# Commento Backend
유튜브 댓글을 입력받아 혐오/공격성/차별 표현을 분류하고, 문제가 감지되면 AI가 댓글을 교정 및 교육적 피드백을 제공하는 백엔드 서버입니다.

# 시스템 아키텍쳐
<img width="631" height="528" alt="스크린샷 2025-11-18 오후 2 52 19" src="https://github.com/user-attachments/assets/d2f624b0-e1aa-476c-915e-a5b3a1d84cba" />


```mermaid
graph TB
    subgraph Client["🌐 Client Layer"]
        CE["<b>Chrome Extension</b><br/>유튜브 댓글 UI"]
    end
    
    subgraph FastAPI["<b>⚙️ FastAPI Server (Backend Core)</b>"]
        LC["<b>LangChain</b><br/>오케스트레이션 레이어"]
        
        subgraph Model["<b>🤖 AI Classification Model</b>"]
            KH["<b>beomi/korean-hatespeech-multilabel</b><br/>KcELECTRA-base<br/>다중 라벨 분류기"]
            
            subgraph Data["📊 Training Data"]
                DS["<b>Korean UnSmile Dataset</b><br/>Smilegate AI<br/>LRAP: 0.919"]
            end
        end
        
        subgraph Results["<b>📋 Classification Output</b>"]
            R1["<b>분류 라벨</b><br/>• hate 혐오<br/>• offensive 공격성<br/>• bias_gender 성차별<br/>• bias_others 기타차별"]
            R2["<b>심각도 점수</b><br/>0.0 ~ 1.0"]
        end
    end
    
    subgraph External["<b>☁️ External API</b>"]
        GPT["<b>OpenAI GPT-4.1-mini</b><br/>댓글 교정 & 피드백 생성"]
    end
    
    CE -->|"① 댓글 전송"| LC
    LC -->|"② 분석 요청"| KH
    DS -.->|"학습 데이터"| KH
    KH -->|"③ 분류 수행"| R1
    KH -->|"③ 심각도 측정"| R2
    R1 --> LC
    R2 --> LC
    LC -->|"④ 수정/피드백 요청<br/>(API Call)"| GPT
    GPT -->|"⑤ 교정 댓글<br/>피드백 반환"| LC
    LC -->|"⑥ 최종 결과"| CE
    
    style Client fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    style CE fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000
    
    style FastAPI fill:#fff3e0,stroke:#f57c00,stroke-width:4px,color:#000
    style LC fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000
    
    style Model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000
    style KH fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    
    style Data fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000
    style DS fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    
    style Results fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    style R1 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    style R2 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    
    style External fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style GPT fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000
    
    %% 화살표 스타일 - 파랑색 굵게
    linkStyle 0,1,3,4,5,6,7,8,9 stroke:#1976d2,stroke-width:3px
    linkStyle 2 stroke:#666,stroke-width:2px,stroke-dasharray:5
```

# 서비스 처리 흐름도
- 댓글 분석 프로세스 시퀀스
```mermaid
sequenceDiagram
    participant U as 사용자
    participant CE as Chrome Extension
    participant API as FastAPI Server
    participant LC as LangChain
    participant KH as korean-hatespeech<br/>모델
    participant GPT as GPT-4.1-mini

    U->>CE: 유튜브 댓글 작성/조회
    CE->>API: 댓글 텍스트 전송
    API->>LC: 분석 요청
    
    LC->>KH: 혐오 표현 검출 요청
    KH->>KH: 다중 라벨 분류<br/>(hate, offensive,<br/>bias_gender, bias_others)
    KH-->>LC: 분류 결과 + 심각도
    
    alt 문제 댓글 감지됨
        LC->>GPT: 댓글 수정 요청<br/>(원본 + 분류 결과)
        GPT->>GPT: 교정된 댓글 생성<br/>+ 피드백 작성
        GPT-->>LC: 수정 제안 + 피드백
        LC-->>API: 종합 결과 반환
        API-->>CE: 실시간 피드백 전송
        CE-->>U: 수정 제안 표시<br/>+ 교육적 피드백
    else 정상 댓글
        LC-->>API: 정상 판정
        API-->>CE: 문제없음 전송
        CE-->>U: 댓글 게시
    end
```

# 데이터 처리 파이프라인
- AI 모델 처리 과정
```mermaid
graph LR
    subgraph Input["<b>📝 입력</b>"]
        A["<b>유튜브 댓글</b><br/>텍스트"]
    end
    
    subgraph Classification["<b>🤖 혐오 표현 분류 모델</b>"]
        B["<b>beomi/korean-hatespeech-multilabel</b><br/>KcELECTRA-base<br/>Multi-label Classifier"]
    end
    
    subgraph ClassResult["<b>📊 분류 결과</b>"]
        C1["<b>hate</b><br/>혐오"]
        C2["<b>offensive</b><br/>공격성"]
        C3["<b>bias_gender</b><br/>성차별"]
        C4["<b>bias_others</b><br/>기타 차별"]
        C5["<b>심각도 점수</b><br/>0.0 ~ 1.0"]
    end
    
    subgraph Orchestra["<b>⚙️ 오케스트레이션</b>"]
        D["<b>LangChain</b><br/>프롬프트 체인"]
    end
    
    subgraph Correction["<b>✨ 댓글 교정 & 피드백 생성</b>"]
        E["<b>OpenAI GPT-4.1-mini</b>"]
    end
    
    subgraph Output["<b>✅ 출력</b>"]
        F1["<b>수정된 댓글</b>"]
        F2["<b>교육적 피드백</b>"]
        F3["<b>개선 제안</b>"]
    end
    
    A -->|"① 원본 댓글"| B
    B -->|"② 분류 수행"| C1
    B --> C2
    B --> C3
    B --> C4
    B --> C5
    
    C1 --> D
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    
    D -->|"③ 원본+분류결과<br/>전달"| E
    E -->|"④ 생성"| F1
    E -->|"④ 생성"| F2
    E -->|"④ 생성"| F3
    
    style Input fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000
    style A fill:#bbdefb,stroke:#1976d2,stroke-width:2px,color:#000
    
    style Classification fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000
    style B fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    
    style ClassResult fill:#fff9c4,stroke:#f9a825,stroke-width:3px,color:#000
    style C1 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    style C2 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    style C3 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    style C4 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    style C5 fill:#fff59d,stroke:#f9a825,stroke-width:2px,color:#000
    
    style Orchestra fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000
    style D fill:#ffe0b2,stroke:#f57c00,stroke-width:2px,color:#000
    
    style Correction fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style E fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000
    
    style Output fill:#e8f5e9,stroke:#388e3c,stroke-width:3px,color:#000
    style F1 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style F2 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    style F3 fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
    
    %% 화살표 스타일 - 파랑색
    linkStyle default stroke:#1976d2,stroke-width:3px
```
# 실행 방법 - DockerHub Image
## 실행 환경
- Python 3.13
- FastAPI / Uvicorn
- LangChain
- HuggingFace beomi/korean-hatespeech-multilabel
- OpenAI GPT-4.1-mini API

## 환경 변수
- .env 파일을 준비합니다.
```bash
OPENAI_API_KEY=your_api_key
```
- OPENAI_API_KEY 는 필수입니다. 값이 없으면 GPT 피드백 생성 단계에서 오류가 발생합니다.

## Docker 이미지
- Docker Hub Repository: griotold/commento
    - https://hub.docker.com/repository/docker/griotold/commento/general     
- 최신 태그: 1.1.0
- latest 태그가 없으므로 반드시 태그를 명시해야 pull 됩니다.

## 배포 방법
### 1) 서버에 Docker 설치 확인
```bash
docker --version
```
- 설치가 안 되어 있다면 Docker를 먼저 설치합니다.

### 2) .env 파일 생성
- 아래 경로는 예시입니다.
```bash
mkdir -p ~/commento
nano ~/commento/.env
```

내용:
```bash
OPENAI_API_KEY=your_api_key
```
- 저장 후 종료합니다.

### 3) Docker Hub 에서 이미지 pull
```bash
docker pull griotold/commento:1.1.0
```

### 4) 컨테이너 실행
```bash
docker run -d \
  --name commento \
  -p 80:8000 \
  --env-file ~/commento/.env \
  --restart unless-stopped \
  griotold/commento:1.1.0
```

### 5) 배포 확인

```bash
## 컨테이너 상태 확인:
docker ps

## 로그 확인:
docker logs -f commento

## 서버가 정상 실행되면 Swagger 문서로 접속 가능합니다.
http://<PUBLIC_IP>/docs
```

### (선택) 컨테이너 중지/재시작/삭제
중지:
```bash
docker stop commento
```
재시작:
```bash
docker restart commento
```
삭제:
```bash
docker rm -f commento
```

## 트러블 슈팅
### 이미지 pull이 안 될 때
- 태그를 정확히 명시했는지 확인:
```bash
docker pull griotold/commento:1.1.0
```

### OpenAI 관련 에러가 날때
- .env 파일의 OPENAI_API_KEY 값이 올바른지 확인
- 컨테이너에 env가 주입되었느지 확인
```bash
docker exec -it commento printenv | grep OPENAI
```

### 외부 접속이 안 될 때
- 오라클 클라우드 Security List / NSG 에서 인바운드 80 포트가 열려 있는지 확인
