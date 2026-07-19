"""LangChain-like adapter that routes model calls through opencode headless.

Enabled via LLM_BACKEND=opencode (see config/__init__.py:model_for). This lets the
existing graph nodes call model.invoke(messages) without using OpenRouter credentials.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace


class OpenCodeHeadlessModel:
    def __init__(self, role: str) -> None:
        self.role = role
        self.model = os.getenv("OPENCODE_MODEL", "github-copilot/gpt-5.5")
        self.timeout = int(os.getenv("OPENCODE_TIMEOUT", "180"))

    def invoke(self, messages) -> SimpleNamespace:
        prompt = _messages_to_prompt(messages)
        cmd = [
            "opencode",
            "run",
            "--model",
            self.model,
            "--format",
            "json",
            "--title",
            f"pipeline-{self.role}",
            prompt,
        ]
        started = time.strftime("%Y%m%d-%H%M%S")
        proc = subprocess.run(
            cmd,
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        _write_log(started, self.role, prompt, proc.stdout, proc.stderr, proc.returncode)
        if proc.returncode != 0:
            raise RuntimeError(f"opencode exited {proc.returncode}: {proc.stderr.strip()}")
        return SimpleNamespace(content=_extract_text(proc.stdout).strip())


def opencode_model_for(role: str) -> OpenCodeHeadlessModel:
    return OpenCodeHeadlessModel(role)


def _messages_to_prompt(messages) -> str:
    parts: list[str] = []
    for message in messages:
        kind = message.__class__.__name__.replace("Message", "").upper()
        content = getattr(message, "content", str(message))
        parts.append(f"## {kind}\n{content}")
    return "\n\n".join(parts)


def _extract_text(stdout: str) -> str:
    chunks: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part") or {}
        if part.get("type") == "text":
            chunks.append(part.get("text", ""))
    return "".join(chunks)


def _write_log(
    started: str,
    role: str,
    prompt: str,
    stdout: str,
    stderr: str,
    returncode: int,
) -> None:
    log_dir = Path("artifacts") / "opencode_headless"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{started}-{role}.json"
    path.write_text(
        json.dumps(
            {
                "role": role,
                "model": os.getenv("OPENCODE_MODEL", "github-copilot/gpt-5.5"),
                "returncode": returncode,
                "prompt": prompt,
                "stdout": stdout,
                "stderr": stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
