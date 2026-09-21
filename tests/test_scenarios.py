"""Tests for scenario loading and scenario engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.errors import ScenarioError
from redteam.scenarios.loader import ScenarioLoader
from redteam.scenarios.engine import ScenarioEngine


ROOT = Path(__file__).resolve().parents[1]


def test_scenario_loader_loads_all_scenarios():
    loader = ScenarioLoader(scenarios_dir=ROOT / "scenarios")
    all_scenarios = loader.load_all()

    assert len(all_scenarios) >= 9
    scenario_ids = [s.scenario_id for s in all_scenarios]
    assert "SC-ACC-001" in scenario_ids
    assert "SC-AUTH-001" in scenario_ids
    assert "SC-AUTHZ-001" in scenario_ids
    assert "SC-DNS-001" in scenario_ids
    assert "SC-NET-001" in scenario_ids
    assert "SC-TLS-001" in scenario_ids
    assert "SC-SESS-001" in scenario_ids
    assert "SC-QUOTA-001" in scenario_ids
    assert "SC-MON-001" in scenario_ids


def test_scenario_loader_get_by_id():
    loader = ScenarioLoader(scenarios_dir=ROOT / "scenarios")
    sc = loader.get_scenario("SC-ACC-001")
    assert sc is not None
    assert sc.scenario_id == "SC-ACC-001"
    assert sc.status == "implemented"
    assert len(sc.steps) > 0


def test_scenario_loader_get_nonexistent():
    loader = ScenarioLoader(scenarios_dir=ROOT / "scenarios")
    sc = loader.get_scenario("SC-NONEXISTENT-999")
    assert sc is None


def test_scenario_loader_by_category():
    loader = ScenarioLoader(scenarios_dir=ROOT / "scenarios")
    dns_scenarios = loader.get_by_category("dns")
    assert len(dns_scenarios) >= 1
    assert any(s.scenario_id == "SC-DNS-001" for s in dns_scenarios)


def test_scenario_engine_validation():
    loader = ScenarioLoader(scenarios_dir=ROOT / "scenarios")
    sc = loader.get_scenario("SC-ACC-001")
    assert sc is not None

    engine = ScenarioEngine()
    engine.load(sc)
    errors = engine.validate()
    assert errors == []
