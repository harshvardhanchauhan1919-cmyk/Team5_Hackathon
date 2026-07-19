"""LangChain-like adapter that routes model calls through the Claude Code CLI's
headless print mode (`claude -p`).

Enabled via LLM_BACKEND=claude (see config/__init__.py:model_for). Mirrors
tools/opencode_llm.py's shape exactly so the two backends are interchangeable.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace


class ClaudeHeadlessModel:
    def __init__(self, role: str) -> None:
        self.role = role
        self.model = os.getenv("CLAUDE_MODEL", "sonnet")
        self.timeout = int(os.getenv("CLAUDE_TIMEOUT", "180"))

    def invoke(self, messages) -> SimpleNamespace:
        system_prompt, user_prompt = _split_messages(messages)
        cmd = [
            "claude",
            "-p",
            user_prompt,
            "--model",
            self.model,
            "--output-format",
            "json",
            # Diagnosis/repair only ever need to return text (JSON or a script) —
            # no tool use, so skip it entirely for speed and to avoid a headless
            # run hanging on a permission prompt it can't answer.
            "--allowedTools",
            "",
        ]
        if system_prompt:
            cmd += ["--system-prompt", system_prompt]

        started = time.strftime("%Y%m%d-%H%M%S")
        proc = subprocess.run(
            cmd,
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        _write_log(started, self.role, user_prompt, proc.stdout, proc.stderr, proc.returncode)
        if proc.returncode != 0:
            raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()}")
        return SimpleNamespace(content=_extract_text(proc.stdout).strip())


def claude_model_for(role: str) -> ClaudeHeadlessModel:
    return ClaudeHeadlessModel(role)


def _split_messages(messages) -> tuple[str, str]:
    """Claude CLI takes the system prompt as its own flag; fold everything else
    (diagnosis/repair's HumanMessage) into the positional prompt."""
    system_parts: list[str] = []
    other_parts: list[str] = []
    for message in messages:
        kind = message.__class__.__name__.replace("Message", "").upper()
        content = getattr(message, "content", str(message))
        if kind == "SYSTEM":
            system_parts.append(content)
        else:
            other_parts.append(f"## {kind}\n{content}")
    return "\n\n".join(system_parts), "\n\n".join(other_parts)


def _extract_text(stdout: str) -> str:
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
    return data.get("result", "")


def _write_log(
    started: str,
    role: str,
    prompt: str,
    stdout: str,
    stderr: str,
    returncode: int,
) -> None:
    log_dir = Path("artifacts") / "claude_headless"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{started}-{role}.json"
    path.write_text(
        json.dumps(
            {
                "role": role,
                "model": os.getenv("CLAUDE_MODEL", "sonnet"),
                "returncode": returncode,
                "prompt": prompt,
                "stdout": stdout,
                "stderr": stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
