"""Deterministic LLM mock (B3) — Healing pair · usable from hour 0.

Returns canned typed responses so every lane can build without hitting OpenRouter.
Set USE_MOCK=1 in the environment to route model_for() through this.
"""
from __future__ import annotations


class FakeModel:
    def __init__(self, canned: str = "mock-response"):
        self.canned = canned

    def invoke(self, *_args, **_kwargs):
        class _Msg:
            content = self.canned
        return _Msg()


def fake_model_for(_role: str) -> FakeModel:
    return FakeModel()
