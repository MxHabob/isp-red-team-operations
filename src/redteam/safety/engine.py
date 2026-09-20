"""Safety engine — orchestrates all pre-execution safety validations.

The safety engine runs all safety checks and the kill switch verification
before any test execution is allowed.  If ANY check fails, execution MUST
NOT proceed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from redteam.core.errors import SafetyCheckFailed
from redteam.core.types import EnvironmentProfile, ScopeDefinition
from redteam.safety.checks import (
    SafetyCheckResult,
    check_authorization,
    check_environment,
    check_evidence_storage,
    check_prohibited_activity,
    check_scope_populated,
)
from redteam.safety.killswitch import KillSwitch

logger = logging.getLogger(__name__)


@dataclass
class SafetyReport:
    """Aggregated results of all safety checks."""

    checks: list[SafetyCheckResult] = field(default_factory=list)
    kill_switch_active: bool = False

    @property
    def passed(self) -> bool:
        """True only if ALL checks passed AND kill switch is active."""
        return self.kill_switch_active and all(c.passed for c in self.checks)

    @property
    def failed_checks(self) -> list[SafetyCheckResult]:
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        lines = []
        for c in self.checks:
            status = "✓" if c.passed else "✗"
            lines.append(f"  {status} {c.name}: {c.message}")
        ks_status = "✓" if self.kill_switch_active else "✗"
        lines.append(f"  {ks_status} kill_switch: {'active' if self.kill_switch_active else 'NOT ACTIVE'}")
        return "\n".join(lines)


class SafetyEngine:
    """Orchestrates safety validation before test execution.

    Usage::

        safety = SafetyEngine(kill_switch=ks)
        report = safety.run_checks(scope, env, evidence_path)
        if not report.passed:
            raise SafetyCheckFailed(report.summary())
    """

    def __init__(self, kill_switch: KillSwitch) -> None:
        self._kill_switch = kill_switch

    def run_checks(
        self,
        scope: ScopeDefinition,
        environment: EnvironmentProfile,
        evidence_store: Path,
    ) -> SafetyReport:
        """Run all safety checks and return the aggregated report."""
        report = SafetyReport()

        # Kill switch check
        report.kill_switch_active = self._kill_switch.is_active

        # Individual checks
        report.checks.append(check_authorization(scope))
        report.checks.append(check_scope_populated(scope))
        report.checks.append(check_environment(scope, environment))
        report.checks.append(check_evidence_storage(evidence_store))
        report.checks.append(check_prohibited_activity(scope))

        if report.passed:
            logger.info("Safety checks PASSED\n%s", report.summary())
        else:
            logger.warning("Safety checks FAILED\n%s", report.summary())

        return report

    def enforce(
        self,
        scope: ScopeDefinition,
        environment: EnvironmentProfile,
        evidence_store: Path,
    ) -> SafetyReport:
        """Run checks and raise if any fail.

        Raises:
            SafetyCheckFailed: If one or more checks fail.
        """
        report = self.run_checks(scope, environment, evidence_store)
        if not report.passed:
            raise SafetyCheckFailed(
                f"Safety checks failed:\n{report.summary()}"
            )
        return report
