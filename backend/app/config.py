"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # CBORG API Configuration
    anthropic_base_url: str = "https://api.cborg.lbl.gov"
    anthropic_auth_token: str = ""

    # Model Configuration
    llm_model: str = "anthropic/claude-sonnet-4"
    embedding_model: str = "lbl/nomic-embed-text"

    # Database
    database_url: str = "sqlite:///./data/db/opal.db"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:3000"

    @property
    def async_database_url(self) -> str:
        """Return async-compatible database URL."""
        if self.database_url.startswith("sqlite"):
            return self.database_url.replace("sqlite:", "sqlite+aiosqlite:")
        return self.database_url

    @property
    def data_dir(self) -> Path:
        """Return the data directory path."""
        return Path("./data")

    @property
    def pdfs_dir(self) -> Path:
        """Return the PDFs directory path."""
        return self.data_dir / "pdfs"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
