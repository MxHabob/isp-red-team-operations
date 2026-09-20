"""Scope loader — parse command/scope.yaml into typed models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from redteam.core.errors import ConfigurationError, ScopeNotLoaded
from redteam.core.types import AuthorizedAsset, EnvironmentProfile, ScopeDefinition


def load_scope(scope_path: Path) -> ScopeDefinition:
    """Load and parse a scope YAML file into a :class:`ScopeDefinition`.

    Raises:
        ConfigurationError: If the file is missing or malformed.
    """
    if not scope_path.exists():
        raise ConfigurationError(f"Scope file not found: {scope_path}")

    try:
        raw: dict[str, Any] = yaml.safe_load(scope_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in scope file: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigurationError("Scope file must be a YAML mapping")

    operation_id = raw.get("operation_id", "")
    if not operation_id:
        raise ConfigurationError("Scope file missing required field 'operation_id'")

    assets: list[AuthorizedAsset] = []
    for item in raw.get("authorized_assets", []):
        if isinstance(item, dict):
            assets.append(
                AuthorizedAsset(
                    name=item.get("name", ""),
                    type=item.get("type", ""),
                    identifier=item.get("identifier", ""),
                )
            )

    env_str = raw.get("environment", "lab")
    try:
        environment = EnvironmentProfile(env_str)
    except ValueError:
        environment = EnvironmentProfile.LAB

    return ScopeDefinition(
        operation_id=operation_id,
        name=raw.get("name", ""),
        status=raw.get("status", "draft"),
        authorized_assets=assets,
        authorized_networks=raw.get("authorized_networks", []),
        excluded_assets=raw.get("excluded_assets", []),
        allowed_activity=raw.get("allowed_activity", []),
        prohibited_activity=raw.get("prohibited_activity", []),
        operators=raw.get("operators", []),
        approval_ref=raw.get("approval_ref"),
        environment=environment,
    )
