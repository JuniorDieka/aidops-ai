import os
from typing import Any

from app.config import settings


class TracingManager:
    def __init__(self) -> None:
        self.enabled = settings.enable_tracing
        self.token_tracking_enabled = settings.enable_token_tracking
        self.total_tokens = 0
        self.total_cost = 0.0

        if self.enabled and settings.langsmith_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project

    def track_tokens(self, prompt_tokens: int, completion_tokens: int, model: str) -> dict[str, Any]:
        if not self.token_tracking_enabled:
            return {}

        total = prompt_tokens + completion_tokens
        self.total_tokens += total

        cost = self._calculate_cost(prompt_tokens, completion_tokens, model)
        self.total_cost += cost

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total,
            "estimated_cost_usd": cost,
        }

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        pricing = {
            "gpt-4-turbo-preview": {"prompt": 0.01 / 1000, "completion": 0.03 / 1000},
            "gpt-3.5-turbo": {"prompt": 0.0005 / 1000, "completion": 0.0015 / 1000},
            "claude-3-opus-20240229": {"prompt": 0.015 / 1000, "completion": 0.075 / 1000},
            "claude-3-sonnet-20240229": {"prompt": 0.003 / 1000, "completion": 0.015 / 1000},
        }

        model_pricing = pricing.get(model, {"prompt": 0, "completion": 0})
        return (prompt_tokens * model_pricing["prompt"]) + (
            completion_tokens * model_pricing["completion"]
        )

    def get_stats(self) -> dict[str, Any]:
        return {"total_tokens": self.total_tokens, "total_cost_usd": round(self.total_cost, 4)}


tracing_manager = TracingManager()
