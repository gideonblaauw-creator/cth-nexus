from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATA_PLATFORM_ENV: str = "development"
    DB_DIR: Path = Path("./db")
    CPI_LICENCE_ACTIVE: bool = False
    ALLOWED_INTERNAL_IPS: list[str] = ["127.0.0.1", "::1"]
    DATASET_VERSION: str = "1.0.0"
    LAST_UPDATED: str = "2026-05-27"
    JWT_SECRET: str = "dev-secret-change-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def origo_db(self) -> str:
        return str(self.DB_DIR / "origo.db")

    @property
    def apikeys_db(self) -> str:
        return str(self.DB_DIR / "apikeys.db")

    @property
    def provenance_db(self) -> str:
        return str(self.DB_DIR / "provenance.db")


settings = Settings()
