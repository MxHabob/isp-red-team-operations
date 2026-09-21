"""Tests for the test runner and lifecycle."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from redteam.core.config import PlatformConfig
from redteam.core.types import ScenarioDefinition
from redteam.runtime.runner import TestRunner
from redteam.safety.engine import SafetyEngine
from redteam.safety.killswitch import KillSwitch
from redteam.scope.engine import ScopeEngine


class TestTestRunner:
    def _make_runner(self, tmp_project: Path) -> tuple[TestRunner, ScenarioDefinition]:
        os.environ["REDTEAM_ENVIRONMENT"] = "lab"
        os.chdir(tmp_project)

        config = PlatformConfig(project_root=tmp_project)
        scope_engine = ScopeEngine()
        scope_engine.load(tmp_project / "command" / "scope.yaml")

        ks = KillSwitch(tmp_project / ".local" / "runtime" / "ks.json")
        safety_engine = SafetyEngine(ks)

        runner = TestRunner(config, scope_engine, safety_engine, ks)

        scenario = ScenarioDefinition(
            scenario_id="SC-TEST-001",
            objective="Test the runner",
            hypothesis="The runner should complete a dry run",
            steps=[
                {"action": "test", "description": "Test step 1"},
                {"action": "test", "description": "Test step 2"},
            ],
            expected_behavior="Dry run completes",
            measurements=["time"],
            evidence=["log"],
            stop_conditions=["any error"],
        )

        return runner, scenario

    def test_dry_run_succeeds(self, tmp_project: Path) -> None:
        runner, scenario = self._make_runner(tmp_project)
        result = runner.execute(scenario, operator="test-op", dry_run=True)
        assert result.success
        assert result.dry_run
        assert len(result.observations) > 0

    def test_dry_run_with_kill_switch(self, tmp_project: Path) -> None:
        os.environ["REDTEAM_ENVIRONMENT"] = "lab"
        os.chdir(tmp_project)

        config = PlatformConfig(project_root=tmp_project)
        scope_engine = ScopeEngine()
        scope_engine.load(tmp_project / "command" / "scope.yaml")

        ks = KillSwitch(tmp_project / ".local" / "runtime" / "ks.json")
        ks.stop("test", "testing kill switch")
        safety_engine = SafetyEngine(ks)

        runner = TestRunner(config, scope_engine, safety_engine, ks)
        scenario = ScenarioDefinition(
            scenario_id="SC-TEST-001",
            objective="Test",
            hypothesis="Test",
        )

        result = runner.execute(scenario, dry_run=True)
        assert not result.success
        assert len(result.errors) > 0
