"""Tests for report generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import (
    CVSSVector,
    Environment,
    Finding,
    FindingStatus,
    OperationRecord,
    OperationStatus,
    RemediationGuidance,
    ScenarioDefinition,
    ScenarioStep,
    ScopeDefinition,
    Severity,
)
from redteam.reporting.generator import ReportGenerator


def test_report_generator_produces_markdown(tmp_path: Path):
    generator = ReportGenerator()
    out_file = tmp_path / "report.md"

    op = OperationRecord(
        operation_id="RT-YNET-001",
        name="ISP Security Assessment",
        status=OperationStatus.ACTIVE,
        lead="Security Architect",
    )

    scope = ScopeDefinition(
        operation_id="RT-YNET-001",
        name="Test Scope",
        version="1.0",
        environment=Environment.LAB,
        authorized_assets=["192.0.2.1"],
        authorized_networks=["192.0.2.0/24"],
        allowed_activity=["accounting_validation"],
        status="approved",
    )

    scenario = ScenarioDefinition(
        scenario_id="SC-ACC-001",
        version="1.0",
        objective="Accounting test",
        steps=[ScenarioStep(action="baseline", description="Initial check")],
    )

    finding = Finding(
        finding_id="FIND-2026-001",
        title="Unaccounted Egress",
        severity=Severity.MEDIUM,
        cvss=CVSSVector(base_score=5.3, vector_string="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N"),
        affected_systems=["BRAS-01"],
        status=FindingStatus.CONFIRMED,
        description="Traffic discrepancy observed.",
        remediation=RemediationGuidance(
            summary="Update billing triggers",
            recommendations=["Recalibrate RADIUS interim intervals"],
        ),
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
    assert "FIND-2026-001" in content
    assert "Unaccounted Egress" in content
    assert "EVI-20260921-0001" in content
