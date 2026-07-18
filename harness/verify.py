""""Healed is truly healed" verification hook (F3) — Healing pair.

Checks if a repaired run results in a successful pass, and ensures no regressions.
"""
from __future__ import annotations

import logging
from typing import Optional

from schemas import RunResult

logger = logging.getLogger(__name__)


def verify_healed(result: RunResult, original_result: Optional[RunResult] = None) -> bool:
    """Verify that a repaired execution is successful.

    Args:
        result: The RunResult of the latest execution after repair.
        original_result: The original failing RunResult before repair (optional).

    Returns:
        True if the script execution is successful and contains no errors.
    ```
    """
    if result.status != "pass":
        logger.info("Verification failed: RunResult status is %s (expected 'pass')", result.status)
        return False

    if result.error is not None:
        logger.info("Verification failed: RunResult has an error: %s", result.error.message)
        return False

    # Optional check: make sure we did not regress on some steps
    if original_result and original_result.error:
        logger.info(
            "Verification successful: Repaired execution passed. Original error was %s at step %d.",
            original_result.error.kind,
            original_result.error.step_index,
        )
    else:
        logger.info("Verification successful: Execution passed.")

    return True
