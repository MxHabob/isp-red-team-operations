"""Custom exception hierarchy for the Red Team platform.

All platform-specific exceptions inherit from :class:`RedTeamError` to
allow callers to catch platform errors without masking unrelated failures.
"""

from __future__ import annotations


class RedTeamError(Exception):
    """Base exception for all Red Team platform errors."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class ConfigurationError(RedTeamError):
    """Invalid or missing configuration."""


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------


class ScopeError(RedTeamError):
    """Base class for scope-related errors."""


class ScopeViolation(ScopeError):
    """An action was attempted outside the authorized scope."""


class ScopeNotLoaded(ScopeError):
    """Scope definition has not been loaded yet."""


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


class SafetyError(RedTeamError):
    """Base class for safety-related errors."""


class SafetyCheckFailed(SafetyError):
    """One or more pre-execution safety checks failed."""


class KillSwitchEngaged(SafetyError):
    """The kill switch has been activated — all execution must stop."""


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------


class AuthorizationError(RedTeamError):
    """Missing or invalid authorization for the requested action."""


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


class EvidenceError(RedTeamError):
    """Base class for evidence-related errors."""


class EvidenceIntegrityError(EvidenceError):
    """Evidence integrity check failed (e.g. hash mismatch)."""


class EvidenceNotFound(EvidenceError):
    """Referenced evidence item does not exist."""


class EvidenceImmutabilityError(EvidenceError):
    """Attempted modification of an immutable evidence record."""


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


class RuntimeError_(RedTeamError):
    """Base class for runtime/execution errors.

    Named with a trailing underscore to avoid shadowing the built-in
    ``RuntimeError``.
    """


class EnvironmentError_(RedTeamError):
    """Environment validation failed.

    Named with a trailing underscore to avoid shadowing the built-in
    ``EnvironmentError``.
    """


class LifecycleError(RedTeamError):
    """Invalid lifecycle state transition."""


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


class ScenarioError(RedTeamError):
    """Base class for scenario-related errors."""


class ScenarioNotFound(ScenarioError):
    """Referenced scenario does not exist."""


class ScenarioValidationError(ScenarioError):
    """Scenario definition failed validation."""


# ---------------------------------------------------------------------------
# IDs
# ---------------------------------------------------------------------------


class IDValidationError(RedTeamError):
    """An identifier does not match the expected format."""
