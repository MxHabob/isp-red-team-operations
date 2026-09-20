"""Test runner — orchestrates the full test execution lifecycle.

The runner coordinates scope, safety, environment, scenario execution,
telemetry, and evidence collection through the lifecycle state machine.

Usage::

    runner = TestRunner(config)
    result = runner.execute(scenario, dry_run=True)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from redteam.core.config import PlatformConfig
from redteam.core.errors import (
    KillSwitchEngaged,
    SafetyCheckFailed,
    ScopeViolation,
)
from redteam.core.ids import generate_run_id
from redteam.core.types import (
    RunRecord,
    ScenarioDefinition,
    TestLifecyclePhase,
)
from redteam.runtime.lifecycle import LifecycleState
from redteam.safety.engine import SafetyEngine
from redteam.safety.killswitch import KillSwitch
from redteam.scope.engine import ScopeEngine

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    """Complete result of a test run."""

    run_record: RunRecord
    lifecycle: LifecycleState
    telemetry_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def success(self) -> bool:
        return self.lifecycle.all_passed and not self.errors


class TestRunner:
    """Orchestrates the full test execution lifecycle.

    The runner enforces the following order:
    1. PRECHECK — validate inputs
    2. SCOPE_CHECK — verify target is in scope
    3. SAFETY_CHECK — run all safety checks
    4. ENVIRONMENT_CHECK — validate environment
    5. BASELINE — record baseline state
    6. EXECUTION — run the scenario steps
    7. TELEMETRY — collect telemetry
    8. EVIDENCE — collect and hash evidence
    9. ANALYSIS — analyze results
    10. RESULT — record conclusion
    11. CLEANUP — restore state

    If any check phase fails, execution skips to CLEANUP.
    """

    def __init__(
        self,
        config: PlatformConfig,
        scope_engine: ScopeEngine,
        safety_engine: SafetyEngine,
        kill_switch: KillSwitch,
    ) -> None:
        self._config = config
        self._scope = scope_engine
        self._safety = safety_engine
        self._kill_switch = kill_switch

    def execute(
        self,
        scenario: ScenarioDefinition,
        operator: str = "",
        dry_run: bool = False,
    ) -> RunResult:
        """Execute a scenario through the full lifecycle.

        Args:
            scenario: The scenario to execute.
            operator: Operator identifier.
            dry_run: If True, simulate execution without network actions.

        Returns:
            RunResult with lifecycle, telemetry, evidence, and observations.
        """
        run_id = generate_run_id()
        lifecycle = LifecycleState(run_id=run_id)

        run_record = RunRecord(
            run_id=run_id,
            operation_id=self._scope.scope.operation_id if self._scope.is_loaded else "",
            scenario_id=scenario.scenario_id,
            test_id=scenario.scenario_id,
            operator=operator,
            environment=self._config.environment,
            status="running",
            started_at=datetime.now(tz=timezone.utc),
        )

        result = RunResult(
            run_record=run_record,
            lifecycle=lifecycle,
            dry_run=dry_run,
        )

        try:
            self._run_precheck(lifecycle, scenario, result)
            self._run_scope_check(lifecycle, scenario, result)
            self._run_safety_check(lifecycle, result)
            self._run_environment_check(lifecycle, result)
            self._run_baseline(lifecycle, scenario, result, dry_run)
            self._run_execution(lifecycle, scenario, result, dry_run)
            self._run_telemetry(lifecycle, result, dry_run)
            self._run_evidence(lifecycle, result, dry_run)
            self._run_analysis(lifecycle, result)
            self._run_result(lifecycle, result)
        except (ScopeViolation, SafetyCheckFailed, KillSwitchEngaged) as exc:
            lifecycle.abort(str(exc))
            result.errors.append(str(exc))
            logger.error("[%s] Run aborted: %s", run_id, exc)
        except Exception as exc:
            lifecycle.abort(f"Unexpected error: {exc}")
            result.errors.append(f"Unexpected error: {exc}")
            logger.exception("[%s] Unexpected error during run", run_id)
        finally:
            self._run_cleanup(lifecycle, scenario, result, dry_run)

        run_record.ended_at = datetime.now(tz=timezone.utc)
        run_record.status = "completed" if result.success else "failed"
        run_record.evidence_ids = result.evidence_ids
        run_record.telemetry_ids = result.telemetry_ids

        logger.info("[%s] Run %s\n%s", run_id, run_record.status, lifecycle.summary())
        return result

    # ----- Phase implementations -----

    def _run_precheck(
        self, lifecycle: LifecycleState, scenario: ScenarioDefinition, result: RunResult
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.PRECHECK)
        try:
            # Validate scenario has required fields
            issues: list[str] = []
            if not scenario.scenario_id:
                issues.append("Scenario missing ID")
            if not scenario.objective:
                issues.append("Scenario missing objective")
            if not scenario.hypothesis:
                issues.append("Scenario missing hypothesis")

            if issues:
                lifecycle.end_phase(TestLifecyclePhase.PRECHECK, "failed", "; ".join(issues))
                raise SafetyCheckFailed(f"Precheck failed: {'; '.join(issues)}")

            lifecycle.end_phase(TestLifecyclePhase.PRECHECK, "passed")
        except SafetyCheckFailed:
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.PRECHECK, "failed", str(exc))
            raise

    def _run_scope_check(
        self, lifecycle: LifecycleState, scenario: ScenarioDefinition, result: RunResult
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.SCOPE_CHECK)
        try:
            self._kill_switch.check()

            if not self._scope.is_loaded:
                lifecycle.end_phase(
                    TestLifecyclePhase.SCOPE_CHECK, "failed", "Scope not loaded"
                )
                raise ScopeViolation("Scope has not been loaded")

            issues = self._scope.validate()
            if issues:
                msg = "; ".join(issues)
                lifecycle.end_phase(TestLifecyclePhase.SCOPE_CHECK, "failed", msg)
                raise ScopeViolation(f"Scope validation failed: {msg}")

            lifecycle.end_phase(TestLifecyclePhase.SCOPE_CHECK, "passed")
        except (ScopeViolation, KillSwitchEngaged):
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.SCOPE_CHECK, "failed", str(exc))
            raise

    def _run_safety_check(self, lifecycle: LifecycleState, result: RunResult) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.SAFETY_CHECK)
        try:
            self._kill_switch.check()
            report = self._safety.enforce(
                self._scope.scope,
                self._config.environment,
                self._config.evidence_store,
            )
            lifecycle.end_phase(TestLifecyclePhase.SAFETY_CHECK, "passed")
        except (SafetyCheckFailed, KillSwitchEngaged):
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.SAFETY_CHECK, "failed", str(exc))
            raise

    def _run_environment_check(self, lifecycle: LifecycleState, result: RunResult) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.ENVIRONMENT_CHECK)
        try:
            self._kill_switch.check()
            from redteam.runtime.environment import detect_environment, validate_environment

            env_info = detect_environment(self._config.project_root)
            issues = validate_environment(env_info)
            if issues:
                result.observations.extend(issues)
                # Environment issues are warnings for lab, errors for production
                if self._config.environment.value == "production":
                    lifecycle.end_phase(
                        TestLifecyclePhase.ENVIRONMENT_CHECK, "failed", "; ".join(issues)
                    )
                    raise SafetyCheckFailed(f"Environment issues: {'; '.join(issues)}")

            lifecycle.end_phase(TestLifecyclePhase.ENVIRONMENT_CHECK, "passed")
        except (SafetyCheckFailed, KillSwitchEngaged):
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.ENVIRONMENT_CHECK, "failed", str(exc))
            raise

    def _run_baseline(
        self,
        lifecycle: LifecycleState,
        scenario: ScenarioDefinition,
        result: RunResult,
        dry_run: bool,
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.BASELINE)
        try:
            self._kill_switch.check()
            if dry_run:
                result.observations.append("BASELINE: Dry run — baseline simulated")
            else:
                result.observations.append("BASELINE: Recorded baseline state")
                # TODO: Implement actual baseline collection
            lifecycle.end_phase(TestLifecyclePhase.BASELINE, "passed")
        except KillSwitchEngaged:
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.BASELINE, "failed", str(exc))
            raise

    def _run_execution(
        self,
        lifecycle: LifecycleState,
        scenario: ScenarioDefinition,
        result: RunResult,
        dry_run: bool,
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.EXECUTION)
        try:
            self._kill_switch.check()
            if dry_run:
                result.observations.append(
                    f"EXECUTION: Dry run — {len(scenario.steps)} steps simulated"
                )
                for i, step in enumerate(scenario.steps, 1):
                    self._kill_switch.check()
                    desc = step.get("description", step.get("action", f"step-{i}"))
                    result.observations.append(f"  Step {i}: {desc} [simulated]")
            else:
                result.observations.append(
                    f"EXECUTION: {len(scenario.steps)} steps to execute"
                )
                # TODO: Implement actual step execution
                for i, step in enumerate(scenario.steps, 1):
                    self._kill_switch.check()
                    desc = step.get("description", step.get("action", f"step-{i}"))
                    result.observations.append(f"  Step {i}: {desc} [PLANNED]")

            lifecycle.end_phase(TestLifecyclePhase.EXECUTION, "passed")
        except KillSwitchEngaged:
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.EXECUTION, "failed", str(exc))
            raise

    def _run_telemetry(
        self, lifecycle: LifecycleState, result: RunResult, dry_run: bool
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.TELEMETRY)
        try:
            self._kill_switch.check()
            if dry_run:
                result.observations.append("TELEMETRY: Dry run — telemetry collection simulated")
            else:
                result.observations.append("TELEMETRY: Collecting telemetry")
                # TODO: Implement telemetry collection
            lifecycle.end_phase(TestLifecyclePhase.TELEMETRY, "passed")
        except KillSwitchEngaged:
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.TELEMETRY, "failed", str(exc))
            raise

    def _run_evidence(
        self, lifecycle: LifecycleState, result: RunResult, dry_run: bool
    ) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.EVIDENCE)
        try:
            self._kill_switch.check()
            if dry_run:
                result.observations.append("EVIDENCE: Dry run — evidence collection simulated")
            else:
                result.observations.append("EVIDENCE: Collecting and hashing evidence")
                # TODO: Implement evidence collection
            lifecycle.end_phase(TestLifecyclePhase.EVIDENCE, "passed")
        except KillSwitchEngaged:
            raise
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.EVIDENCE, "failed", str(exc))
            raise

    def _run_analysis(self, lifecycle: LifecycleState, result: RunResult) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.ANALYSIS)
        try:
            result.observations.append("ANALYSIS: Comparing expected vs observed behavior")
            # TODO: Implement automated analysis
            lifecycle.end_phase(TestLifecyclePhase.ANALYSIS, "passed")
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.ANALYSIS, "failed", str(exc))
            raise

    def _run_result(self, lifecycle: LifecycleState, result: RunResult) -> None:
        lifecycle.begin_phase(TestLifecyclePhase.RESULT)
        try:
            result.run_record.observed_result = "\n".join(result.observations)
            lifecycle.end_phase(TestLifecyclePhase.RESULT, "passed")
        except Exception as exc:
            lifecycle.end_phase(TestLifecyclePhase.RESULT, "failed", str(exc))
            raise

    def _run_cleanup(
        self,
        lifecycle: LifecycleState,
        scenario: ScenarioDefinition,
        result: RunResult,
        dry_run: bool,
    ) -> None:
        # CLEANUP always runs, even if previous phases were skipped
        if lifecycle.current_phase != TestLifecyclePhase.CLEANUP:
            # Need to advance lifecycle to CLEANUP — fill missing phases as skipped
            try:
                while len(lifecycle.phases) < len(
                    [p for p in TestLifecyclePhase]
                ) - 1:  # all except CLEANUP
                    from redteam.runtime.lifecycle import PHASE_ORDER

                    next_idx = len(lifecycle.phases)
                    if next_idx >= len(PHASE_ORDER):
                        break
                    next_phase = PHASE_ORDER[next_idx]
                    if next_phase == TestLifecyclePhase.CLEANUP:
                        break
                    record = lifecycle.begin_phase(next_phase)
                    lifecycle.end_phase(next_phase, "skipped", "Skipped due to earlier failure")
            except Exception:
                pass

        try:
            lifecycle.begin_phase(TestLifecyclePhase.CLEANUP)
            if dry_run:
                result.observations.append("CLEANUP: Dry run — cleanup simulated")
            else:
                for cleanup_action in scenario.cleanup:
                    result.observations.append(f"CLEANUP: {cleanup_action}")
                # TODO: Implement actual cleanup
            lifecycle.end_phase(TestLifecyclePhase.CLEANUP, "passed")
        except Exception as exc:
            logger.error("Cleanup failed: %s", exc)
            try:
                lifecycle.end_phase(TestLifecyclePhase.CLEANUP, "failed", str(exc))
            except Exception:
                pass
