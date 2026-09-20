"""Environment detection and profile management.

Resolves the active environment profile and validates that the runtime
environment meets the requirements for test execution.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from redteam.core.errors import EnvironmentError_
from redteam.core.types import EnvironmentProfile

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentInfo:
    """Resolved environment information."""

    profile: EnvironmentProfile
    hostname: str
    platform: str
    python_version: str
    project_root: Path
    evidence_store: Path
    telemetry_store: Path


def detect_environment(project_root: Path) -> EnvironmentInfo:
    """Detect the current runtime environment.

    Reads ``REDTEAM_ENVIRONMENT`` to determine the profile. Defaults to
    ``lab`` if not set.
    """
    import platform
    import sys

    env_name = os.environ.get("REDTEAM_ENVIRONMENT", "lab")
    try:
        profile = EnvironmentProfile(env_name)
    except ValueError:
        raise EnvironmentError_(
            f"Unknown environment '{env_name}'. "
            f"Valid: {[e.value for e in EnvironmentProfile]}"
        ) from None

    local_base = Path(os.environ.get("REDTEAM_RUNTIME_DIR", str(project_root / ".local")))

    return EnvironmentInfo(
        profile=profile,
        hostname=platform.node(),
        platform=platform.platform(),
        python_version=sys.version,
        project_root=project_root,
        evidence_store=Path(
            os.environ.get("REDTEAM_EVIDENCE_STORE", str(local_base / "evidence"))
        ),
        telemetry_store=Path(
            os.environ.get("REDTEAM_TELEMETRY_STORE", str(local_base / "telemetry"))
        ),
    )


def validate_environment(env: EnvironmentInfo) -> list[str]:
    """Validate that the environment meets execution requirements.

    Returns a list of issues found (empty if all good).
    """
    issues: list[str] = []

    if env.profile == EnvironmentProfile.PRODUCTION:
        issues.append(
            "WARNING: Production environment detected. "
            "Ensure explicit authorization exists before proceeding."
        )

    if not env.project_root.exists():
        issues.append(f"Project root does not exist: {env.project_root}")

    scope_file = env.project_root / "command" / "scope.yaml"
    if not scope_file.exists():
        issues.append(f"Scope file missing: {scope_file}")

    mission_file = env.project_root / "command" / "mission.yaml"
    if not mission_file.exists():
        issues.append(f"Mission file missing: {mission_file}")

    return issues
