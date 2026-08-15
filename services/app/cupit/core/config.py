"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_timeout_seconds: float = 30.0
    ollama_temperature: float = 0.2
    ollama_max_tokens: int = 500
    cors_origin: str = "http://localhost:3000"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        data_root = Path(
            os.getenv(
                "CUPIT_DATA_ROOT",
                str(Path(__file__).resolve().parents[4] / "data"),
            )
        ).resolve()
        configured_data_dir = os.getenv("CUPIT_DATA_DIR")
        if configured_data_dir:
            data_dir = Path(configured_data_dir).resolve()
        else:
            data_dir = cls._active_data_dir(data_root)
        return cls(
            data_dir=data_dir,
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
            ollama_timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30")),
            ollama_temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            ollama_max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "500")),
            cors_origin=os.getenv("CORS_ORIGIN", "http://localhost:3000"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    @staticmethod
    def _active_data_dir(data_root: Path) -> Path:
        pointer = data_root / "ACTIVE_DATASET"
        if not pointer.is_file():
            return data_root / "samples"
        relative = pointer.read_text(encoding="utf-8").strip()
        candidate = (data_root / relative).resolve()
        if not candidate.is_relative_to(data_root):
            raise ValueError("ACTIVE_DATASET must point inside CUPIT_DATA_ROOT")
        return candidate
