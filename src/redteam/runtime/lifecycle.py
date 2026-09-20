"""Test execution lifecycle state machine.

Defines the ordered phases of a test run and manages transitions:

    PRECHECK → SCOPE_CHECK → SAFETY_CHECK → ENVIRONMENT_CHECK →
    BASELINE → EXECUTION → TELEMETRY → EVIDENCE → ANALYSIS →
    RESULT → CLEANUP

The lifecycle enforces that phases execute in order and that no phase
can be skipped (except CLEANUP, which always runs).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from redteam.core.errors import LifecycleError
from redteam.core.types import TestLifecyclePhase

logger = logging.getLogger(__name__)

# Ordered phases — execution must follow this sequence
PHASE_ORDER: list[TestLifecyclePhase] = [
    TestLifecyclePhase.PRECHECK,
    TestLifecyclePhase.SCOPE_CHECK,
    TestLifecyclePhase.SAFETY_CHECK,
    TestLifecyclePhase.ENVIRONMENT_CHECK,
    TestLifecyclePhase.BASELINE,
    TestLifecyclePhase.EXECUTION,
    TestLifecyclePhase.TELEMETRY,
    TestLifecyclePhase.EVIDENCE,
    TestLifecyclePhase.ANALYSIS,
    TestLifecyclePhase.RESULT,
    TestLifecyclePhase.CLEANUP,
]


@dataclass
class PhaseRecord:
    """Record of a completed lifecycle phase."""

    phase: TestLifecyclePhase
    started_at: datetime
    ended_at: datetime | None = None
    status: str = "pending"  # pending, running, passed, failed, skipped
    message: str = ""


@dataclass
class LifecycleState:
    """Tracks the current state of a test run lifecycle."""

    run_id: str
    current_phase: TestLifecyclePhase = TestLifecyclePhase.PRECHECK
    phase_index: int = 0
    phases: list[PhaseRecord] = field(default_factory=list)
    aborted: bool = False
    abort_reason: str = ""

    def begin_phase(self, phase: TestLifecyclePhase) -> PhaseRecord:
        """Mark a phase as started.

        Raises:
            LifecycleError: If phases are executed out of order.
        """
        expected_index = len(self.phases)
        if expected_index >= len(PHASE_ORDER):
            raise LifecycleError(f"All phases already completed for run {self.run_id}")

        expected = PHASE_ORDER[expected_index]
        if phase != expected:
            raise LifecycleError(
                f"Expected phase {expected.value} but got {phase.value} "
                f"(run {self.run_id})"
            )

        record = PhaseRecord(
            phase=phase,
            started_at=datetime.now(tz=timezone.utc),
            status="running",
        )
        self.phases.append(record)
        self.current_phase = phase
        self.phase_index = expected_index
        logger.info("[%s] Phase started: %s", self.run_id, phase.value)
        return record

    def end_phase(
        self, phase: TestLifecyclePhase, status: str, message: str = ""
    ) -> PhaseRecord:
        """Mark a phase as completed.

        Args:
            phase: The phase being completed.
            status: Result status — ``passed`` or ``failed``.
            message: Optional message explaining the result.

        Raises:
            LifecycleError: If the phase is not the current running phase.
        """
        if not self.phases:
            raise LifecycleError(f"No phase in progress for run {self.run_id}")

        current = self.phases[-1]
        if current.phase != phase:
            raise LifecycleError(
                f"Cannot end phase {phase.value} — current phase is {current.phase.value}"
            )

        current.ended_at = datetime.now(tz=timezone.utc)
        current.status = status
        current.message = message
        logger.info(
            "[%s] Phase ended: %s → %s%s",
            self.run_id,
            phase.value,
            status,
            f" ({message})" if message else "",
        )
        return current

    def abort(self, reason: str) -> None:
        """Abort the lifecycle — skip to CLEANUP."""
        self.aborted = True
        self.abort_reason = reason
        logger.warning("[%s] Lifecycle aborted: %s", self.run_id, reason)

    @property
    def is_complete(self) -> bool:
        """True if all phases have been executed."""
        return len(self.phases) == len(PHASE_ORDER)

    @property
    def all_passed(self) -> bool:
        """True if all completed phases passed."""
        return all(p.status == "passed" for p in self.phases)

    def summary(self) -> str:
        """Human-readable summary of the lifecycle state."""
        lines = [f"Run: {self.run_id}"]
        for p in self.phases:
            duration = ""
            if p.ended_at and p.started_at:
                d = (p.ended_at - p.started_at).total_seconds()
                duration = f" ({d:.1f}s)"
            status_icon = {"passed": "✓", "failed": "✗", "running": "⟳", "skipped": "–"}.get(
                p.status, "?"
            )
            lines.append(f"  {status_icon} {p.phase.value}: {p.status}{duration}")
            if p.message:
                lines.append(f"    {p.message}")
        if self.aborted:
            lines.append(f"  ⚠ ABORTED: {self.abort_reason}")
        return "\n".join(lines)
