"""Kill switch — central state machine for emergency stop.

The kill switch has five states::

    ACTIVE → PAUSED → STOP_REQUESTED → STOPPED → ABORTED

Every test runner MUST check the kill switch state before and during
execution.  If the state is anything other than ACTIVE, execution must
not proceed (or must halt immediately if already running).

The kill switch state is persisted to a JSON file in the runtime directory
so that it survives process restarts and is visible to all operators.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.errors import KillSwitchEngaged
from redteam.core.types import KillSwitchState

logger = logging.getLogger(__name__)


class KillSwitch:
    """Central kill switch for the Red Team platform.

    Args:
        state_file: Path to the JSON file storing the kill switch state.
                    If the file doesn't exist, the initial state is ACTIVE.
    """

    def __init__(self, state_file: Path) -> None:
        self._state_file = state_file
        self._state = KillSwitchState.ACTIVE
        self._changed_at: datetime | None = None
        self._changed_by: str = ""
        self._reason: str = ""
        self._load()

    @property
    def state(self) -> KillSwitchState:
        """Current kill switch state (re-reads from file)."""
        self._load()
        return self._state

    @property
    def is_active(self) -> bool:
        """True if execution is allowed."""
        return self.state == KillSwitchState.ACTIVE

    def check(self) -> None:
        """Check whether execution is allowed.

        Raises:
            KillSwitchEngaged: If the kill switch is not in ACTIVE state.
        """
        current = self.state
        if current != KillSwitchState.ACTIVE:
            raise KillSwitchEngaged(
                f"Kill switch is {current.value} "
                f"(by {self._changed_by}, reason: {self._reason})"
            )

    def activate(self, operator: str = "", reason: str = "Resumed") -> None:
        """Set state to ACTIVE — execution is allowed."""
        self._transition(KillSwitchState.ACTIVE, operator, reason)

    def pause(self, operator: str = "", reason: str = "") -> None:
        """Set state to PAUSED — execution should pause."""
        self._transition(KillSwitchState.PAUSED, operator, reason)

    def request_stop(self, operator: str = "", reason: str = "") -> None:
        """Set state to STOP_REQUESTED — execution should stop gracefully."""
        self._transition(KillSwitchState.STOP_REQUESTED, operator, reason)

    def stop(self, operator: str = "", reason: str = "") -> None:
        """Set state to STOPPED — execution has been stopped."""
        self._transition(KillSwitchState.STOPPED, operator, reason)

    def abort(self, operator: str = "", reason: str = "") -> None:
        """Set state to ABORTED — emergency stop."""
        self._transition(KillSwitchState.ABORTED, operator, reason)
        logger.critical("KILL SWITCH ABORTED by %s: %s", operator, reason)

    def _transition(self, new_state: KillSwitchState, operator: str, reason: str) -> None:
        old_state = self._state
        self._state = new_state
        self._changed_at = datetime.now(tz=timezone.utc)
        self._changed_by = operator
        self._reason = reason
        self._save()
        logger.warning(
            "Kill switch: %s → %s (operator=%s, reason=%s)",
            old_state.value,
            new_state.value,
            operator,
            reason,
        )

    def _save(self) -> None:
        """Persist state to the JSON file."""
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "state": self._state.value,
            "changed_at": self._changed_at.isoformat() if self._changed_at else None,
            "changed_by": self._changed_by,
            "reason": self._reason,
        }
        self._state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load(self) -> None:
        """Load state from the JSON file if it exists."""
        if not self._state_file.exists():
            return
        try:
            data = json.loads(self._state_file.read_text(encoding="utf-8"))
            self._state = KillSwitchState(data.get("state", "active"))
            changed_at = data.get("changed_at")
            if changed_at:
                self._changed_at = datetime.fromisoformat(changed_at)
            self._changed_by = data.get("changed_by", "")
            self._reason = data.get("reason", "")
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.error("Failed to load kill switch state: %s", exc)
            # Default to STOPPED on corrupted state for safety
            self._state = KillSwitchState.STOPPED
            self._reason = f"State file corrupted: {exc}"
