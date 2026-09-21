"""Tests for findings management and attack chain models."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import (
    AttackChain,
    AttackChainLink,
    CVSSVector,
    Finding,
    FindingStatus,
    RemediationGuidance,
    Severity,
)
from redteam.findings.manager import FindingManager
from redteam.findings.attack_chain import AttackChainManager


@pytest.fixture
def sample_finding() -> Finding:
    return Finding(
        finding_id="FIND-2026-001",
        title="Inconsistent Accounting on Encrypted DNS",
        severity=Severity.HIGH,
        cvss=CVSSVector(
            base_score=7.5,
            vector_string="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N",
        ),
        affected_systems=["BRAS-01", "OCS-01"],
        status=FindingStatus.CONFIRMED,
        description="Encrypted DNS traffic via DoH is not accounted in usage quota.",
        reproduction_steps=["Connect via PPPoE", "Send 10MB via DoH", "Query OCS balance"],
        evidence_ids=["EVI-20260921-0001"],
        scenario_id="SC-DNS-001",
        hypothesis_id="HYP-DNS-001",
        remediation=RemediationGuidance(
            summary="Update BRAS classification rules to match DoH endpoints",
            recommendations=["Add DPI rule for RFC 8484", "Ensure OCS charging trigger matches IP/Port"],
        ),
    )


def test_finding_manager_add_and_get(tmp_path: Path, sample_finding: Finding):
    mgr = FindingManager(storage_dir=tmp_path / "findings")
    mgr.add_finding(sample_finding)

    retrieved = mgr.get_finding("FIND-2026-001")
    assert retrieved is not None
    assert retrieved.title == sample_finding.title
    assert retrieved.severity == Severity.HIGH
    assert retrieved.cvss.base_score == 7.5


def test_finding_manager_filter_by_severity(tmp_path: Path, sample_finding: Finding):
    mgr = FindingManager(storage_dir=tmp_path / "findings")
    mgr.add_finding(sample_finding)

    high_findings = mgr.get_by_severity(Severity.HIGH)
    assert len(high_findings) == 1

    low_findings = mgr.get_by_severity(Severity.LOW)
    assert len(low_findings) == 0


def test_finding_manager_status_update(tmp_path: Path, sample_finding: Finding):
    mgr = FindingManager(storage_dir=tmp_path / "findings")
    mgr.add_finding(sample_finding)

    mgr.update_status("FIND-2026-001", FindingStatus.REMEDIATED)
    retrieved = mgr.get_finding("FIND-2026-001")
    assert retrieved.status == FindingStatus.REMEDIATED


def test_attack_chain_manager(tmp_path: Path):
    mgr = AttackChainManager(storage_dir=tmp_path / "chains")

    chain = AttackChain(
        chain_id="CHN-2026-001",
        name="Pre-Auth to Quota Bypass Chain",
        description="Chained vulnerability from unauthenticated state to persistent free quota",
        links=[
            AttackChainLink(
                step_order=1,
                finding_id="FIND-2026-001",
                description="Use DoH bypass on captive portal",
            ),
            AttackChainLink(
                step_order=2,
                finding_id="FIND-2026-002",
                description="Establish tunnel over DoH to external proxy",
            ),
        ],
        aggregate_severity=Severity.CRITICAL,
    )

    mgr.add_chain(chain)
    retrieved = mgr.get_chain("CHN-2026-001")
    assert retrieved is not None
    assert retrieved.name == "Pre-Auth to Quota Bypass Chain"
    assert len(retrieved.links) == 2
    assert retrieved.aggregate_severity == Severity.CRITICAL
