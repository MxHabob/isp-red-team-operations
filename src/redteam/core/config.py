"""Platform configuration loader.

Reads the project root, environment profile, and runtime directories.
All paths to external stores (evidence, telemetry, secrets) are resolved
here so that no other module needs to hard-code filesystem paths.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from redteam.core.errors import ConfigurationError
from redteam.core.types import EnvironmentProfile


def _find_project_root() -> Path:
    """Walk up from CWD to find the project root (contains pyproject.toml)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() and (parent / "AGENTS.md").exists():
            return parent
    raise ConfigurationError(
        "Cannot locate project root (no pyproject.toml + AGENTS.md found in parent directories)"
    )


@dataclass
class PlatformConfig:
    """Resolved platform configuration.

    The project root is the Git repository root.
    Runtime directories (evidence store, telemetry store, secret store) are
    resolved from environment variables or default to paths *outside* the
    repository when possible.
    """

    project_root: Path = field(default_factory=_find_project_root)
    environment: EnvironmentProfile = EnvironmentProfile.LAB

    # External stores — never inside Git for real operations
    evidence_store: Path = field(default=Path(""))
    telemetry_store: Path = field(default=Path(""))
    secret_store: Path = field(default=Path(""))
    runtime_dir: Path = field(default=Path(""))

    def __post_init__(self) -> None:
        env_name = os.environ.get("REDTEAM_ENVIRONMENT", "lab")
        try:
            self.environment = EnvironmentProfile(env_name)
        except ValueError:
            raise ConfigurationError(
                f"Unknown environment profile '{env_name}'. "
                f"Valid profiles: {[e.value for e in EnvironmentProfile]}"
            ) from None

        # Resolve external stores — default to .local/ under project root for
        # lab/dev, but operators SHOULD override via env vars for field use.
        local_base = self.project_root / ".local"

        self.runtime_dir = Path(
            os.environ.get("REDTEAM_RUNTIME_DIR", str(local_base / "runtime"))
        )
        self.evidence_store = Path(
            os.environ.get("REDTEAM_EVIDENCE_STORE", str(local_base / "evidence"))
        )
        self.telemetry_store = Path(
            os.environ.get("REDTEAM_TELEMETRY_STORE", str(local_base / "telemetry"))
        )
        self.secret_store = Path(
            os.environ.get("REDTEAM_SECRET_STORE", str(local_base / "secrets"))
        )

    # ----- Path helpers -----

    @property
    def command_dir(self) -> Path:
        return self.project_root / "command"

    @property
    def scope_file(self) -> Path:
        return self.command_dir / "scope.yaml"

    @property
    def mission_file(self) -> Path:
        return self.command_dir / "mission.yaml"

    @property
    def scenarios_dir(self) -> Path:
        return self.project_root / "scenarios"

    @property
    def config_dir(self) -> Path:
        return self.project_root / "config"

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def lab_dir(self) -> Path:
        return self.project_root / "lab"

    def ensure_runtime_dirs(self) -> None:
        """Create runtime directories if they don't exist."""
        for d in (
            self.runtime_dir,
            self.evidence_store,
            self.telemetry_store,
        ):
            d.mkdir(parents=True, exist_ok=True)
        # Secret store gets restrictive permissions
        self.secret_store.mkdir(parents=True, exist_ok=True)
        try:
            self.secret_store.chmod(0o700)
        except OSError:
            pass  # Windows may not support chmod
