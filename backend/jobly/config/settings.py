"""Application settings and configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Jobly"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./jobly.db"

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Email Configuration
    gmail_credentials_path: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # LinkedIn Configuration
    linkedin_username: Optional[str] = None
    linkedin_password: Optional[str] = None

    # Rate Limiting
    rate_limit_calls: int = 10
    rate_limit_window: float = 60.0

    # Agent Configuration
    max_agent_retries: int = 3
    agent_timeout: int = 300

    # Storage
    data_dir: str = "./data"
    profile_dir: str = "./data/profiles"
    job_dir: str = "./data/jobs"
    document_dir: str = "./data/documents"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
