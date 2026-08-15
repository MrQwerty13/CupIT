"""Safe Ollama integration that accepts structured analytics only."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cupit.core.exceptions import AiUnavailableError


class AiService:
    prompt_version = "cupit-analyst-v1"

    def __init__(
        self,
        host: str,
        model: str,
        timeout_seconds: float = 30.0,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logging.getLogger(__name__)

    def analyze(self, question: str, analytics: dict[str, Any]) -> str:
        prompt = (
            "Ты аналитик кофейного бизнеса CupIT. Отвечай на русском, кратко и "
            "практично. Используй только предоставленные агрегированные показатели, "
            "не придумывай отсутствующие факты. Сначала сформулируй вывод, затем до "
            "трёх действий.\n\n"
            f"АНАЛИТИКА:\n{json.dumps(analytics, ensure_ascii=False)}\n\n"
            f"ВОПРОС:\n{question}"
        )
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": self.temperature, "num_predict": self.max_tokens},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                result = json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            self.logger.warning("Ollama request failed: %s", exc)
            raise AiUnavailableError() from exc
        answer = result.get("response") if isinstance(result, dict) else None
        if not isinstance(answer, str) or not answer.strip():
            raise AiUnavailableError("Local AI returned an invalid response")
        return answer.strip()
