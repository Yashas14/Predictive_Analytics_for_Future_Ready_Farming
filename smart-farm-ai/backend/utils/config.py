"""App config — reads from env vars and .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """All app settings. Env vars override defaults."""

    # Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    model_path: Path = Field(default=Path("models/v1/model.pkl"))
    data_dir: Path = Field(default=Path("data"))
    database_url: str = Field(default="sqlite:///./predictions.db")

    # API Settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default=["*"])

    # ML Settings
    model_version: str = Field(default="1.0.0")
    random_state: int = Field(default=42)
    test_size: float = Field(default=0.2)
    cv_folds: int = Field(default=5)
    n_estimators: int = Field(default=200)

    # Frontend
    backend_url: str = Field(default="http://localhost:8000")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def abs_model_path(self) -> Path:
        if self.model_path.is_absolute():
            return self.model_path
        return self.project_root / self.model_path

    @property
    def abs_data_dir(self) -> Path:
        if self.data_dir.is_absolute():
            return self.data_dir
        return self.project_root / self.data_dir


settings = Settings()
