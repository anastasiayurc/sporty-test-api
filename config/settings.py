"""
Settings — single source of truth for all environment and runtime configuration.

Values are read from environment variables.
A .env file is automatically loaded if present (local dev only).
In CI/CD, vars are injected directly — the .env file is never committed.

Usage:
    from config.settings import settings
    print(settings.api_base_url)

Override for a specific environment:
    ENV=staging API_BASE_URL=https://staging.api.example.com pytest
"""

from __future__ import annotations
from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Loads .env if it exists — silent no-op in CI/CD where vars are set natively
load_dotenv()


@dataclass(frozen=True)
class Settings:
    env: str
    api_base_url: str
    api_timeout: int
    performance_threshold_ms: int

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            env=os.getenv("ENV", "local"),
            api_base_url=os.getenv("API_BASE_URL", "https://api.zippopotam.us"),
            api_timeout=int(os.getenv("API_TIMEOUT", "10")),
            performance_threshold_ms=int(os.getenv("PERFORMANCE_THRESHOLD_MS", "3000")),
        )


# Module-level singleton — import this everywhere instead of reading os.getenv directly
settings = Settings.from_env()
