from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[1]
    app_env: str = os.getenv("APP_ENV", "development")
    http_timeout_seconds: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "15"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "1800"))
    max_ontario_projects: int = int(os.getenv("MAX_ONTARIO_PROJECTS", "10000"))
    max_toronto_solicitations: int = int(os.getenv("MAX_TORONTO_SOLICITATIONS", "5000"))

    @property
    def frontend_dir(self) -> Path:
        return self.root_dir / "frontend"

    @property
    def cache_dir(self) -> Path:
        path = self.root_dir / "data" / "cache"
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
