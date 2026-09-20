"""Scenario engine — validates and coordinates scenario execution."""

from __future__ import annotations

import logging
from pathlib import Path

from redteam.core.errors import ScenarioNotFound, ScenarioValidationError
from redteam.core.types import ScenarioDefinition
from redteam.scenarios.loader import load_scenario, load_scenarios_from_directory

logger = logging.getLogger(__name__)


class ScenarioEngine:
    """Manages the scenario registry and provides access to scenario definitions.

    Usage::

        engine = ScenarioEngine(scenarios_dir=Path("scenarios"))
        engine.load_all()
        scenario = engine.get("SC-ACC-001")
    """

    def __init__(self, scenarios_dir: Path) -> None:
        self._scenarios_dir = scenarios_dir
        self._registry: dict[str, ScenarioDefinition] = {}

    def load_all(self) -> int:
        """Load all scenarios from the scenarios directory.

        Returns the number of scenarios loaded.
        """
        scenarios = load_scenarios_from_directory(self._scenarios_dir)
        self._registry.clear()
        for s in scenarios:
            self._registry[s.scenario_id] = s
        logger.info("Loaded %d scenarios from %s", len(self._registry), self._scenarios_dir)
        return len(self._registry)

    def load_one(self, path: Path) -> ScenarioDefinition:
        """Load a single scenario and add it to the registry."""
        scenario = load_scenario(path)
        self._registry[scenario.scenario_id] = scenario
        return scenario

    def get(self, scenario_id: str) -> ScenarioDefinition:
        """Get a scenario by ID.

        Raises:
            ScenarioNotFound: If the scenario ID is not in the registry.
        """
        if scenario_id not in self._registry:
            raise ScenarioNotFound(
                f"Scenario '{scenario_id}' not found. "
                f"Available: {list(self._registry.keys())}"
            )
        return self._registry[scenario_id]

    def list_all(self) -> list[ScenarioDefinition]:
        """Return all loaded scenarios."""
        return list(self._registry.values())

    def validate(self, scenario: ScenarioDefinition) -> list[str]:
        """Validate a scenario definition for completeness.

        Returns a list of issues found.
        """
        issues: list[str] = []

        if not scenario.scenario_id:
            issues.append("Missing scenario_id")
        if not scenario.objective:
            issues.append("Missing objective")
        if not scenario.hypothesis:
            issues.append("Missing hypothesis")
        if not scenario.steps:
            issues.append("No steps defined")
        if not scenario.stop_conditions:
            issues.append("No stop conditions defined")
        if not scenario.expected_behavior:
            issues.append("Missing expected_behavior")
        if not scenario.measurements:
            issues.append("No measurements defined")
        if not scenario.evidence:
            issues.append("No evidence requirements defined")

        return issues
