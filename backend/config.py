from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://mediassist_user:mediassist_pass@db:5432/mediassist_db"

    # JWT
    SECRET_KEY: str = "mediassist-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ML Models
    MODEL_PATH: str = "/app/ml/models/orientation_model.joblib"
    ENCODER_PATH: str = "/app/ml/models/label_encoder.joblib"
    SYMPTOMS_PATH: str = "/app/ml/models/symptom_cols.joblib"

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings():
    return Settings()