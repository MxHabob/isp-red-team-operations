"""Scope engine — validates actions against the authorized scope.

Every network action, target selection, and test execution MUST pass
through the scope engine before proceeding.  The engine is intentionally
strict: anything not explicitly authorized is denied.
"""

from __future__ import annotations

import ipaddress
import logging
from dataclasses import dataclass, field
from pathlib import Path

from redteam.core.errors import ScopeNotLoaded, ScopeViolation
from redteam.core.types import ScopeDefinition
from redteam.scope.loader import load_scope

logger = logging.getLogger(__name__)


@dataclass
class ScopeCheckResult:
    """Result of a scope validation check."""

    allowed: bool
    reason: str
    scope_ref: str = ""


class ScopeEngine:
    """Enforces the authorized scope for all test activities.

    Usage::

        engine = ScopeEngine()
        engine.load(Path("command/scope.yaml"))

        result = engine.check_target("192.168.1.0/24")
        if not result.allowed:
            raise ScopeViolation(result.reason)
    """

    def __init__(self) -> None:
        self._scope: ScopeDefinition | None = None
        self._loaded_from: str = ""

    @property
    def scope(self) -> ScopeDefinition:
        if self._scope is None:
            raise ScopeNotLoaded("Scope has not been loaded. Call load() first.")
        return self._scope

    @property
    def is_loaded(self) -> bool:
        return self._scope is not None

    def load(self, scope_path: Path) -> ScopeDefinition:
        """Load scope from a YAML file."""
        self._scope = load_scope(scope_path)
        self._loaded_from = str(scope_path)
        logger.info("Scope loaded: %s (operation: %s)", scope_path, self._scope.operation_id)
        return self._scope

    def check_target(self, target: str) -> ScopeCheckResult:
        """Check whether a target (IP, CIDR, hostname, or identifier) is in scope.

        Returns a :class:`ScopeCheckResult` indicating whether the target is
        allowed and the reason.
        """
        scope = self.scope

        # Check against excluded assets first
        for excluded in scope.excluded_assets:
            if target.lower() == excluded.lower() or excluded.lower() in target.lower():
                return ScopeCheckResult(
                    allowed=False,
                    reason=f"Target '{target}' matches excluded asset '{excluded}'",
                    scope_ref=self._loaded_from,
                )

        # Check against authorized assets by identifier
        for asset in scope.authorized_assets:
            if target == asset.identifier or target == asset.name:
                return ScopeCheckResult(
                    allowed=True,
                    reason=f"Target '{target}' matches authorized asset '{asset.name}'",
                    scope_ref=self._loaded_from,
                )

        # Check against authorized networks (CIDR matching)
        for network_str in scope.authorized_networks:
            try:
                network = ipaddress.ip_network(network_str, strict=False)
                target_addr = ipaddress.ip_address(target)
                if target_addr in network:
                    return ScopeCheckResult(
                        allowed=True,
                        reason=f"Target '{target}' is within authorized network '{network_str}'",
                        scope_ref=self._loaded_from,
                    )
            except ValueError:
                # Target or network string is not a valid IP/CIDR — skip
                continue

        return ScopeCheckResult(
            allowed=False,
            reason=f"Target '{target}' is not in the authorized scope",
            scope_ref=self._loaded_from,
        )

    def check_activity(self, activity: str) -> ScopeCheckResult:
        """Check whether an activity type is allowed by the scope."""
        scope = self.scope

        # Check prohibited first
        for prohibited in scope.prohibited_activity:
            if activity.lower() == prohibited.lower():
                return ScopeCheckResult(
                    allowed=False,
                    reason=f"Activity '{activity}' is explicitly prohibited",
                    scope_ref=self._loaded_from,
                )

        # Check allowed
        for allowed in scope.allowed_activity:
            if activity.lower() == allowed.lower():
                return ScopeCheckResult(
                    allowed=True,
                    reason=f"Activity '{activity}' is authorized",
                    scope_ref=self._loaded_from,
                )

        return ScopeCheckResult(
            allowed=False,
            reason=f"Activity '{activity}' is not explicitly authorized",
            scope_ref=self._loaded_from,
        )

    def validate(self) -> list[str]:
        """Validate the loaded scope definition for completeness.

        Returns a list of warnings/issues found.
        """
        scope = self.scope
        issues: list[str] = []

        if scope.status == "draft":
            issues.append("Scope is still in 'draft' status — not approved for execution")

        if not scope.authorized_assets:
            issues.append("No authorized assets defined")

        if not scope.authorized_networks:
            issues.append("No authorized networks defined")

        for asset in scope.authorized_assets:
            if "REPLACE" in asset.identifier:
                issues.append(f"Asset '{asset.name}' still has placeholder identifier")

        for network in scope.authorized_networks:
            if "REPLACE" in network:
                issues.append(f"Network '{network}' is still a placeholder")

        if not scope.prohibited_activity:
            issues.append("No prohibited activities defined — scope may be too broad")

        return issues
