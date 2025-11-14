from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI) -> None:
    """
    CORS 미들웨어 설정
    """
    # 모든 오리진 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=False, # True 로 해주려면 origins를 구체적으로 명시해줘야 함.
        allow_methods=["*"],
        allow_headers=["*"],
    )