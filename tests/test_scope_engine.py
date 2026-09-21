"""Tests for the scope engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.errors import ConfigurationError, ScopeNotLoaded, ScopeViolation
from redteam.scope.engine import ScopeEngine


class TestScopeEngine:
    def test_load(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        scope = engine.load(tmp_project / "command" / "scope.yaml")
        assert scope.operation_id == "RT-TEST-001"
        assert engine.is_loaded

    def test_not_loaded(self) -> None:
        engine = ScopeEngine()
        with pytest.raises(ScopeNotLoaded):
            _ = engine.scope

    def test_check_target_authorized_network(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        result = engine.check_target("10.0.1.1")
        assert result.allowed is True

    def test_check_target_out_of_scope(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        result = engine.check_target("192.168.1.1")
        assert result.allowed is False

    def test_check_target_excluded(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        result = engine.check_target("customer data")
        assert result.allowed is False

    def test_check_activity_allowed(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        result = engine.check_activity("controlled measurement")
        assert result.allowed is True

    def test_check_activity_prohibited(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        result = engine.check_activity("unauthorized access")
        assert result.allowed is False

    def test_validate_populated(self, tmp_project: Path) -> None:
        engine = ScopeEngine()
        engine.load(tmp_project / "command" / "scope.yaml")
        issues = engine.validate()
        # Status is "approved" and assets are populated, should pass
        assert len(issues) == 0

    def test_missing_scope_file(self, tmp_path: Path) -> None:
        engine = ScopeEngine()
        with pytest.raises(ConfigurationError):
            engine.load(tmp_path / "nonexistent.yaml")
