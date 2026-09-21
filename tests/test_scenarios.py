"""Tests for scenario loading and scenario engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import ScenarioStatus
from redteam.scenarios.loader import load_scenario, load_scenarios_from_directory
from redteam.scenarios.engine import ScenarioEngine


ROOT = Path(__file__).resolve().parents[1]


def test_load_all_scenarios_from_directory():
    scenarios_dir = ROOT / "scenarios"
    all_scenarios = load_scenarios_from_directory(scenarios_dir)

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


def test_load_single_scenario():
    scenario_file = ROOT / "scenarios" / "accounting" / "ACC-001-accounting-consistency.yaml"
    sc = load_scenario(scenario_file)

    assert sc.scenario_id == "SC-ACC-001"
    assert sc.status == ScenarioStatus.IMPLEMENTED
    assert len(sc.steps) > 0


def test_scenario_engine_load_and_get():
    engine = ScenarioEngine(scenarios_dir=ROOT / "scenarios")
    count = engine.load_all()
    assert count >= 9

    sc = engine.get("SC-ACC-001")
    assert sc.scenario_id == "SC-ACC-001"
    assert len(sc.steps) > 0

    all_sc = engine.list_all()
    assert len(all_sc) == count
