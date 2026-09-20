"""ID generation and validation for the Red Team platform.

ID conventions:
    Operation:  RT-{CODE}-{NNN}        e.g. RT-YNET-001
    Run:        RUN-{YYYY}-{NNNNNN}    e.g. RUN-2026-000001
    Test:       {CAT}-{NNN}            e.g. ACC-001, DNS-002
    Evidence:   EV-{TEST}-{NNNN}       e.g. EV-ACC-001-0001
    Finding:    F-{TEST}               e.g. F-ACC-001
    Telemetry:  TEL-{TEST}-{NNNN}      e.g. TEL-ACC-001-0001
    Hypothesis: HYP-{CAT}-{NNN}        e.g. HYP-AUTH-001
    Scenario:   SC-{CAT}-{NNN}         e.g. SC-ACC-001
    Approval:   APR-{NNN}              e.g. APR-001
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from redteam.core.errors import IDValidationError

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

_PATTERNS: dict[str, re.Pattern[str]] = {
    "operation": re.compile(r"^RT-[A-Z]+-\d{3}$"),
    "run": re.compile(r"^RUN-\d{4}-\d{6}$"),
    "test": re.compile(r"^[A-Z]+-\d{3}$"),
    "evidence": re.compile(r"^EV-[A-Z]+-\d{3}-\d{4}$"),
    "finding": re.compile(r"^F-[A-Z]+-\d{3}$"),
    "telemetry": re.compile(r"^TEL-[A-Z]+-\d{3}-\d{4}$"),
    "hypothesis": re.compile(r"^HYP-[A-Z]+-\d{3}$"),
    "scenario": re.compile(r"^SC-[A-Z]+-\d{3}$"),
    "approval": re.compile(r"^APR-\d{3}$"),
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_id(value: str, id_type: str) -> str:
    """Validate that *value* matches the pattern for *id_type*.

    Raises :class:`IDValidationError` on mismatch.
    Returns the validated ID unchanged.
    """
    pattern = _PATTERNS.get(id_type)
    if pattern is None:
        raise IDValidationError(f"Unknown ID type: {id_type}")
    if not pattern.match(value):
        raise IDValidationError(
            f"ID '{value}' does not match {id_type} pattern {pattern.pattern}"
        )
    return value


def is_valid_id(value: str, id_type: str) -> bool:
    """Return ``True`` if *value* is a valid ID of *id_type*."""
    pattern = _PATTERNS.get(id_type)
    if pattern is None:
        return False
    return bool(pattern.match(value))


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------

_run_counter: int = 0


def generate_run_id() -> str:
    """Generate a new run ID using current UTC timestamp.

    Format: ``RUN-{YYYY}-{NNNNNN}`` where the counter increments
    within the current process session.
    """
    global _run_counter  # noqa: PLW0603
    _run_counter += 1
    year = datetime.now(tz=timezone.utc).year
    return f"RUN-{year}-{_run_counter:06d}"


def generate_evidence_id(test_id: str, sequence: int) -> str:
    """Generate an evidence ID for a given test.

    Args:
        test_id: The parent test ID (e.g. ``ACC-001``).
        sequence: Sequence number starting from 1.

    Returns:
        Evidence ID string (e.g. ``EV-ACC-001-0001``).
    """
    validate_id(test_id, "test")
    return f"EV-{test_id}-{sequence:04d}"


def generate_telemetry_id(test_id: str, sequence: int) -> str:
    """Generate a telemetry event ID.

    Args:
        test_id: The parent test ID.
        sequence: Sequence number starting from 1.

    Returns:
        Telemetry ID string (e.g. ``TEL-ACC-001-0001``).
    """
    validate_id(test_id, "test")
    return f"TEL-{test_id}-{sequence:04d}"


def reset_run_counter() -> None:
    """Reset the in-process run counter.  For testing only."""
    global _run_counter  # noqa: PLW0603
    _run_counter = 0
