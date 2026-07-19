"""Model configuration loader (A2). One switch (LLM_BACKEND), three real backends,
one mock. See README.md "Run modes" for the full picture.

  USE_MOCK=1            deterministic FakeModel, no network at all (tests/CI)
  LLM_BACKEND=api        (default) OpenRouter, needs OPENROUTER_API_KEY
  LLM_BACKEND=opencode   headless `opencode` CLI (tools/opencode_llm.py)
  LLM_BACKEND=claude     headless `claude` CLI  (tools/claude_llm.py)

USE_MOCK always wins regardless of LLM_BACKEND — it's the deterministic path tests
depend on, not one of the three "real" run modes.
"""
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

_BACKENDS = ("api", "opencode", "claude")


def model_for(role: str):
    """Return a chat-model client for the given agent role, routed by LLM_BACKEND.

    Import lazily so the schema/graph packages don't require langchain to import.
    """
    if os.getenv("USE_MOCK") == "1":
        from tools.mock_llm import fake_model_for
        return fake_model_for(role)

    backend = os.getenv("LLM_BACKEND", "api").strip().lower()
    if backend not in _BACKENDS:
        raise ValueError(f"LLM_BACKEND={backend!r} is not one of {_BACKENDS}")

    if backend == "opencode":
        from tools.opencode_llm import opencode_model_for
        return opencode_model_for(role)

    if backend == "claude":
        from tools.claude_llm import claude_model_for
        return claude_model_for(role)

    # backend == "api" — OpenRouter, needs OPENROUTER_API_KEY in .env
    from langchain_openai import ChatOpenAI

    model = CFG[role]
    if model == "none":
        raise ValueError(f"role '{role}' is deterministic (no LLM)")
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "LLM_BACKEND=api but OPENROUTER_API_KEY is unset — set it in .env, or "
            "switch to LLM_BACKEND=opencode / LLM_BACKEND=claude instead."
        )
    return ChatOpenAI(
        model=model,
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        temperature=0,
    )
