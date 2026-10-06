from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    app_name: str = "Intelligent Student Engagement & Dropout Prediction System"
    database_url: str = "sqlite:///./student_engagement.db"
    model_path: str = str(ROOT / "models" / "dropout_model.joblib")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
