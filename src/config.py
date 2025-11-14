import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정"""
    
    # 🔐 API 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_MAX_TOKENS = 150
    OPENAI_TEMPERATURE = 0.7
    
    # 🤖 모델 설정
    HATE_SPEECH_MODEL = "beomi/korean-hatespeech-multilabel"
    DEVICE = -1  # CPU: -1, GPU: 0
    
    # 📊 Threshold 설정
    MIN_THRESHOLD = 0.1
    CONFIDENCE_THRESHOLD = 0.5
    SEVERITY_THRESHOLD = 0.7
    
    # 🌐 서버 설정
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True

class DevelopmentConfig(Config):
    """개발 환경"""
    DEBUG = True

class ProductionConfig(Config):
    """프로덕션 환경"""
    DEBUG = False
    DEVICE = 0  # GPU 사용

# 환경에 따라 선택
ENV = os.getenv("ENV", "development")
config = DevelopmentConfig() if ENV == "development" else ProductionConfig()