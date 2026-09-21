"""Tests for the safety engine and kill switch."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.errors import KillSwitchEngaged, SafetyCheckFailed
from redteam.core.types import EnvironmentProfile, KillSwitchState
from redteam.safety.engine import SafetyEngine
from redteam.safety.killswitch import KillSwitch
from redteam.scope.engine import ScopeEngine


class TestKillSwitch:
    def test_default_state(self, tmp_path: Path) -> None:
        ks = KillSwitch(tmp_path / "ks.json")
        assert ks.state == KillSwitchState.ACTIVE
        assert ks.is_active

    def test_pause(self, tmp_path: Path) -> None:
        ks = KillSwitch(tmp_path / "ks.json")
        ks.pause("test-operator", "testing")
        assert ks.state == KillSwitchState.PAUSED
        assert not ks.is_active

    def test_abort(self, tmp_path: Path) -> None:
        ks = KillSwitch(tmp_path / "ks.json")
        ks.abort("test-operator", "emergency")
        assert ks.state == KillSwitchState.ABORTED

    def test_check_raises_when_not_active(self, tmp_path: Path) -> None:
        ks = KillSwitch(tmp_path / "ks.json")
        ks.stop("test", "testing")
        with pytest.raises(KillSwitchEngaged):
            ks.check()

    def test_persists_state(self, tmp_path: Path) -> None:
        state_file = tmp_path / "ks.json"
        ks1 = KillSwitch(state_file)
        ks1.stop("test", "testing")

        # Load from same file
        ks2 = KillSwitch(state_file)
        assert ks2.state == KillSwitchState.STOPPED

    def test_reactivate(self, tmp_path: Path) -> None:
        ks = KillSwitch(tmp_path / "ks.json")
        ks.stop("test", "testing")
        assert not ks.is_active
        ks.activate("test", "resumed")
        assert ks.is_active


class TestSafetyEngine:
    def test_all_checks_pass(self, tmp_project: Path) -> None:
        scope_engine = ScopeEngine()
        scope_engine.load(tmp_project / "command" / "scope.yaml")

        ks = KillSwitch(tmp_project / ".local" / "ks.json")
        engine = SafetyEngine(ks)

        evidence_store = tmp_project / ".local" / "evidence"
        report = engine.run_checks(
            scope_engine.scope, EnvironmentProfile.LAB, evidence_store
        )
        assert report.passed

    def test_enforce_raises_on_failure(self, tmp_project: Path) -> None:
        scope_engine = ScopeEngine()
        scope_engine.load(tmp_project / "command" / "scope.yaml")

        ks = KillSwitch(tmp_project / ".local" / "ks.json")
        ks.stop("test", "testing")  # Kill switch not active
        engine = SafetyEngine(ks)

        evidence_store = tmp_project / ".local" / "evidence"
        with pytest.raises(SafetyCheckFailed):
            engine.enforce(scope_engine.scope, EnvironmentProfile.LAB, evidence_store)
