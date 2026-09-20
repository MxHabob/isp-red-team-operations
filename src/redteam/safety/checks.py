"""Individual safety checks executed before a test run.

Each check function receives the pre-flight context and returns a
:class:`SafetyCheckResult`.  If any check fails, the test runner MUST NOT
proceed to execution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from redteam.core.types import EnvironmentProfile, ScopeDefinition

logger = logging.getLogger(__name__)


@dataclass
class SafetyCheckResult:
    """Result of a single safety check."""

    name: str
    passed: bool
    message: str


def check_authorization(scope: ScopeDefinition) -> SafetyCheckResult:
    """Verify that scope status indicates approval."""
    if scope.status in ("approved", "active"):
        return SafetyCheckResult(
            name="authorization",
            passed=True,
            message=f"Scope status is '{scope.status}'",
        )
    return SafetyCheckResult(
        name="authorization",
        passed=False,
        message=f"Scope status is '{scope.status}' — must be 'approved' or 'active'",
    )


def check_scope_populated(scope: ScopeDefinition) -> SafetyCheckResult:
    """Verify that scope has non-placeholder authorized assets."""
    for asset in scope.authorized_assets:
        if "REPLACE" in asset.identifier:
            return SafetyCheckResult(
                name="scope_populated",
                passed=False,
                message=f"Asset '{asset.name}' has placeholder identifier '{asset.identifier}'",
            )
    if not scope.authorized_assets and not scope.authorized_networks:
        return SafetyCheckResult(
            name="scope_populated",
            passed=False,
            message="No authorized assets or networks defined",
        )
    return SafetyCheckResult(
        name="scope_populated",
        passed=True,
        message="Scope contains populated authorized assets",
    )


def check_environment(
    scope: ScopeDefinition, current_env: EnvironmentProfile
) -> SafetyCheckResult:
    """Verify the current environment is appropriate.

    Production environment requires explicit scope approval.
    """
    if current_env == EnvironmentProfile.PRODUCTION:
        if scope.status != "approved" or scope.environment != EnvironmentProfile.PRODUCTION:
            return SafetyCheckResult(
                name="environment",
                passed=False,
                message="Production environment requires approved scope with explicit production authorization",
            )
    return SafetyCheckResult(
        name="environment",
        passed=True,
        message=f"Environment '{current_env.value}' is acceptable",
    )


def check_evidence_storage(evidence_store: Path) -> SafetyCheckResult:
    """Verify that evidence storage is accessible."""
    if evidence_store.exists() and evidence_store.is_dir():
        return SafetyCheckResult(
            name="evidence_storage",
            passed=True,
            message=f"Evidence store accessible: {evidence_store}",
        )
    # Try to create it
    try:
        evidence_store.mkdir(parents=True, exist_ok=True)
        return SafetyCheckResult(
            name="evidence_storage",
            passed=True,
            message=f"Evidence store created: {evidence_store}",
        )
    except OSError as exc:
        return SafetyCheckResult(
            name="evidence_storage",
            passed=False,
            message=f"Cannot access or create evidence store: {exc}",
        )


def check_prohibited_activity(scope: ScopeDefinition) -> SafetyCheckResult:
    """Verify that prohibited activities are defined (scope is bounded)."""
    if not scope.prohibited_activity:
        return SafetyCheckResult(
            name="prohibited_activity",
            passed=False,
            message="No prohibited activities defined — scope may be dangerously broad",
        )
    return SafetyCheckResult(
        name="prohibited_activity",
        passed=True,
        message=f"{len(scope.prohibited_activity)} prohibited activities defined",
    )
