from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import os

# Determine the environment type from an environment variable.
# Default to 'dev' if not set.
ENV_TYPE_VALUE = os.getenv('ENV_TYPE', 'dev')

class Settings(BaseSettings):
    """
    Pydantic settings for the application.
    Loads environment variables from a .env file based on the ENV_TYPE.
    """
    # These settings will be loaded from the corresponding .env file.
    LOG_LEVEL: str
    ENV_TYPE: Literal["dev", "prod"]

    # LLM models
    summary_model: str = Field(description="The LLM model name for summarizing retrieved chunks")

    # Paths - not from .env but defined here
    PACKAGE_ROOT: Path = Path(__file__).parent.resolve()
    STATIC_DIR: Path = PACKAGE_ROOT / "STATIC"

    @property
    def SERVER_LOG_FILE(self) -> Path:
        return self.STATIC_DIR / f"{self.ENV_TYPE}_server.log"

    model_config = SettingsConfigDict(
        env_file=f".{ENV_TYPE_VALUE}.env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()