"""Tests for report generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import (
    EnvironmentProfile,
    Finding,
    FindingSeverity,
    FindingStatus,
    HypothesisConfidence,
    OperationRecord,
    OperationStatus,
    ScenarioDefinition,
    ScopeDefinition,
)
from redteam.reporting.generator import ReportGenerator


def test_report_generator_produces_markdown(tmp_path: Path):
    generator = ReportGenerator()
    out_file = tmp_path / "report.md"

    op = OperationRecord(
        operation_id="RT-YNET-001",
        name="ISP Security Assessment",
        status=OperationStatus.ACTIVE,
    )

    scope = ScopeDefinition(
        operation_id="RT-YNET-001",
        name="Test Scope",
        status="approved",
        environment=EnvironmentProfile.LAB,
        authorized_assets=[],
        authorized_networks=["192.0.2.0/24"],
        allowed_activity=["accounting_validation"],
    )

    scenario = ScenarioDefinition(
        scenario_id="SC-ACC-001",
        version="1.0",
        objective="Accounting test",
        steps=[{"action": "baseline", "description": "Initial check"}],
    )

    finding = Finding(
        finding_id="F-ACC-001",
        title="Unaccounted Egress",
        severity=FindingSeverity.MEDIUM,
        status=FindingStatus.VALIDATED,
        observation="Traffic discrepancy observed.",
        confidence=HypothesisConfidence.CONFIRMED,
        recommendation="Recalibrate RADIUS interim intervals",
        evidence_ids=["EVI-20260921-0001"],
    )

    result_path = generator.generate(
        output_path=out_file,
        operation=op,
        scope=scope,
        scenarios=[scenario],
        findings=[finding],
        evidence_summary=[{"evidence_id": "EVI-20260921-0001", "type": "measurement_log"}],
        observations=["All tests completed safely."],
        limitations=["Testing performed in synthetic lab environment."],
    )

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "ISP Security Assessment" in content
    assert "RT-YNET-001" in content
    assert "F-ACC-001" in content
    assert "Unaccounted Egress" in content
