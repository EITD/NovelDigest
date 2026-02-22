import os

from model.base import ModelClient
from model.gemini_model import GeminiModelClient
from model.openrouter_model import OpenRouterModelClient


def get_model_client() -> ModelClient:
    selected = os.getenv("MODEL_PROVIDER")

    if selected == "gemini":
        return GeminiModelClient()
    if selected == "openrouter":
        return OpenRouterModelClient()

    raise ValueError(
        f"Unsupported MODEL_PROVIDER={selected!r}. Use 'gemini' or 'openrouter'."
    )
