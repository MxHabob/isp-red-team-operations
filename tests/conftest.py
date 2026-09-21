"""Pytest fixtures shared across the test suite."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal project structure in a temp directory."""
    # Create essential files
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    (tmp_path / "AGENTS.md").write_text("# Test AGENTS\n")
    (tmp_path / "command").mkdir()
    (tmp_path / "command" / "scope.yaml").write_text(
        """operation_id: RT-TEST-001
name: Test Operation
status: approved
authorized_assets:
  - name: test-account
    type: account
    identifier: TEST-001
authorized_networks:
  - "10.0.0.0/8"
excluded_assets:
  - "customer data"
  - "production systems"
allowed_activity:
  - controlled measurement
  - protocol analysis
prohibited_activity:
  - unauthorized access
  - credential theft
  - destructive actions
"""
    )
    (tmp_path / "command" / "mission.yaml").write_text(
        """operation_id: RT-TEST-001
name: Test Operation
phase: testing
status: active
objectives:
  - test the platform
"""
    )
    (tmp_path / "scenarios").mkdir()
    (tmp_path / "scenarios" / "accounting").mkdir()
    (tmp_path / "scenarios" / "accounting" / "test-scenario.yaml").write_text(
        """scenario_id: SC-TEST-001
version: "1.0"
status: implemented
objective: "Test scenario for unit testing"
hypothesis: "The platform should execute a dry run successfully"
risk: none
scope_ref: command/scope.yaml
test_identity: TEST-ACCOUNT-001
prerequisites:
  - Test environment available
steps:
  - action: test_step
    description: "Simulated test step"
expected_behavior: "Dry run completes without errors"
measurements:
  - execution_time
telemetry:
  - test_execution
evidence:
  - execution_log
stop_conditions:
  - Any unexpected behavior
cleanup:
  - Verify clean state
success_criteria: "All phases complete"
failure_criteria: "Any phase fails"
"""
    )

    # Set environment
    os.environ["REDTEAM_ENVIRONMENT"] = "lab"

    return tmp_path


@pytest.fixture
def project_root() -> Path:
    """Return the real project root."""
    return Path(__file__).resolve().parents[1]
