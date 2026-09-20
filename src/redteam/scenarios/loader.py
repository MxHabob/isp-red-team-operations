"""Scenario loader — parse YAML scenario files into typed models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from redteam.core.errors import ScenarioNotFound, ScenarioValidationError
from redteam.core.types import ScenarioDefinition, ScenarioStatus


def load_scenario(scenario_path: Path) -> ScenarioDefinition:
    """Load a scenario from a YAML file.

    Raises:
        ScenarioNotFound: If the file doesn't exist.
        ScenarioValidationError: If the YAML is malformed or missing required fields.
    """
    if not scenario_path.exists():
        raise ScenarioNotFound(f"Scenario file not found: {scenario_path}")

    try:
        raw: dict[str, Any] = yaml.safe_load(
            scenario_path.read_text(encoding="utf-8")
        ) or {}
    except yaml.YAMLError as exc:
        raise ScenarioValidationError(f"Invalid YAML in scenario: {exc}") from exc

    if not isinstance(raw, dict):
        raise ScenarioValidationError("Scenario file must be a YAML mapping")

    scenario_id = raw.get("scenario_id", "")
    if not scenario_id:
        raise ScenarioValidationError("Scenario missing required field 'scenario_id'")

    status_str = raw.get("status", "planned")
    try:
        status = ScenarioStatus(status_str)
    except ValueError:
        status = ScenarioStatus.PLANNED

    return ScenarioDefinition(
        scenario_id=scenario_id,
        version=str(raw.get("version", "1.0")),
        objective=raw.get("objective", ""),
        hypothesis=raw.get("hypothesis", ""),
        risk=raw.get("risk", ""),
        scope_ref=raw.get("scope_ref", "command/scope.yaml"),
        prerequisites=raw.get("prerequisites", []),
        test_identity=raw.get("test_identity", ""),
        steps=raw.get("steps", []),
        expected_behavior=raw.get("expected_behavior", ""),
        measurements=raw.get("measurements", []),
        telemetry=raw.get("telemetry", []),
        evidence=raw.get("evidence", []),
        stop_conditions=raw.get("stop_conditions", []),
        cleanup=raw.get("cleanup", []),
        success_criteria=raw.get("success_criteria", ""),
        failure_criteria=raw.get("failure_criteria", ""),
        status=status,
    )


def load_scenarios_from_directory(scenarios_dir: Path) -> list[ScenarioDefinition]:
    """Load all scenario YAML files from a directory tree.

    Recursively searches for ``*.yaml`` and ``*.yml`` files, skipping
    schema files and the registry.
    """
    scenarios: list[ScenarioDefinition] = []
    skip_names = {"registry.yaml", "registry.yml"}

    for yaml_file in sorted(scenarios_dir.rglob("*.y*ml")):
        if yaml_file.name in skip_names:
            continue
        if "schemas" in yaml_file.parts:
            continue
        try:
            scenario = load_scenario(yaml_file)
            scenarios.append(scenario)
        except (ScenarioNotFound, ScenarioValidationError) as exc:
            # Log but don't fail — allow partial loading
            import logging

            logging.getLogger(__name__).warning("Skipping %s: %s", yaml_file, exc)

    return scenarios
