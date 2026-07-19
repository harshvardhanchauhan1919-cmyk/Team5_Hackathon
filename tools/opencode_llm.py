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
        self.bin = os.getenv("OPENCODE_BIN", "opencode")
        self.model = os.getenv("OPENCODE_MODEL", "github-copilot/gpt-5.5")
        self.timeout = int(os.getenv("OPENCODE_TIMEOUT", "180"))

    def invoke(self, messages) -> SimpleNamespace:
        prompt = _messages_to_prompt(messages)
        started = time.strftime("%Y%m%d-%H%M%S")
        prompt_path = _write_prompt_file(started, self.role, prompt)
        cmd = [
            self.bin,
            "run",
            "--model",
            self.model,
            "--format",
            "json",
            "--title",
            f"pipeline-{self.role}",
            f"--file={prompt_path}",
            "Follow the instructions in the attached prompt file exactly. "
            "Respond with the requested output only.",
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            _write_log(started, self.role, prompt, stdout, stderr, -1, cmd, prompt_path)
            raise RuntimeError(
                f"opencode timed out after {self.timeout}s for role={self.role}. "
                f"Prompt was written to {prompt_path}. Increase OPENCODE_TIMEOUT, "
                "set OPENCODE_BIN to a native WSL opencode binary if available, or use USE_MOCK=1."
            ) from exc
        _write_log(started, self.role, prompt, proc.stdout, proc.stderr, proc.returncode)
        if proc.returncode != 0:
            raise RuntimeError(f"opencode exited {proc.returncode}: {proc.stderr.strip()}")
        content = _extract_text(proc.stdout).strip()
        if not content:
            raise RuntimeError("opencode returned no text content")
        return SimpleNamespace(content=content)


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


def _write_prompt_file(started: str, role: str, prompt: str) -> Path:
    prompt_dir = Path("artifacts") / "opencode_headless" / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    path = prompt_dir / f"{started}-{role}.md"
    path.write_text(prompt, encoding="utf-8")
    return path


def _write_log(
    started: str,
    role: str,
    prompt: str,
    stdout: str,
    stderr: str,
    returncode: int,
    cmd: list[str] | None = None,
    prompt_path: Path | None = None,
) -> None:
    log_dir = Path("artifacts") / "opencode_headless"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{started}-{role}.json"
    path.write_text(
        json.dumps(
            {
                "role": role,
                "command": cmd,
                "prompt_path": str(prompt_path) if prompt_path else None,
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
