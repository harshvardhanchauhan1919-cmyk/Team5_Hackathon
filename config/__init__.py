"""Model configuration loader (A2). One endpoint, one key, switch by string."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_CFG_PATH = Path(__file__).parent / "models.yaml"
CFG: dict[str, str] = yaml.safe_load(_CFG_PATH.read_text())

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def model_for(role: str):
    """Return a ChatOpenAI client wired to OpenRouter for the given role.

    Import lazily so the schema/graph packages don't require langchain to import.
    """
    from langchain_openai import ChatOpenAI

    model = CFG[role]
    if model == "none":
        raise ValueError(f"role '{role}' is deterministic (no LLM)")
    return ChatOpenAI(
        model=model,
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        temperature=0,
    )
