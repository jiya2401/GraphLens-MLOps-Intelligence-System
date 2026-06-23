"""
Centralized configuration for GraphLens backend.

Uses Pydantic BaseSettings which automatically reads from:
1. Environment variables
2. .env file
3. Default values defined here

Interview Q: "What is Pydantic BaseSettings and why use it?"
Answer: It provides type-safe configuration that validates at startup.
If someone sets PORT="abc", Pydantic raises a clear error immediately
instead of crashing at runtime when you try to bind the socket.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


# Resolve project root (one level up from backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Each field maps to an env var with the GRAPHLENS_ prefix.
    For example, 'data_dir' reads from GRAPHLENS_DATA_DIR.
    """

    # --- Paths ---
    data_dir: str = str(PROJECT_ROOT / "data" / "json")
    synthetic_dir: str = str(PROJECT_ROOT / "data" / "synthetic")
    config_path: str = str(PROJECT_ROOT / "configs" / "dataset_config.yaml")

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    model_config = {
        "env_prefix": "GRAPHLENS_",
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
    }

    @property
    def data_path(self) -> Path:
        """Resolved Path object for the JSON data directory."""
        path = Path(self.data_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()

    @property
    def synthetic_path(self) -> Path:
        """Resolved Path object for the synthetic CSV directory."""
        path = Path(self.synthetic_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()


# Singleton — import this everywhere
settings = Settings()
