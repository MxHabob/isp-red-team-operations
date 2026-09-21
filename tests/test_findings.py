"""Tests for findings management and attack chain models."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import (
    Finding,
    FindingSeverity,
    FindingStatus,
    HypothesisConfidence,
)
from redteam.findings.attack_chain import AttackChain, AttackChainLink
from redteam.findings.manager import FindingManager


def test_finding_manager_lifecycle(tmp_path: Path):
    mgr = FindingManager(findings_dir=tmp_path / "findings")

    # 1. Create draft finding
    finding = mgr.create(
        finding_id="F-ACC-001",
        title="Inconsistent Accounting on Encrypted DNS",
        observation="DoH traffic was not reflected in OCS quota decrease",
        test_ids=["TST-20260921-0001"],
        evidence_ids=["EVI-20260921-0001"],
        severity=FindingSeverity.HIGH,
        impact="Subscribers can consume high bandwidth without quota deduction",
        confidence=HypothesisConfidence.CONFIRMED,
        recommendation="Update BRAS deep packet inspection rules for DoH endpoints",
    )

    assert finding.finding_id == "F-ACC-001"
    assert finding.status == FindingStatus.DRAFT
    assert finding.severity == FindingSeverity.HIGH

    # 2. Update status to validated
    v_finding = mgr.update_status("F-ACC-001", FindingStatus.VALIDATED)
    assert v_finding.status == FindingStatus.VALIDATED

    # 3. Update status to reported
    r_finding = mgr.update_status("F-ACC-001", FindingStatus.REPORTED)
    assert r_finding.status == FindingStatus.REPORTED

    # 4. Update status to remediated
    rem_finding = mgr.update_status("F-ACC-001", FindingStatus.REMEDIATED)
    assert rem_finding.status == FindingStatus.REMEDIATED

    # 5. Update status to closed
    closed = mgr.update_status("F-ACC-001", FindingStatus.CLOSED)
    assert closed.status == FindingStatus.CLOSED

    # Test load from directory
    mgr2 = FindingManager(findings_dir=tmp_path / "findings")
    count = mgr2.load_from_directory()
    assert count == 1
    loaded = mgr2.get("F-ACC-001")
    assert loaded.title == "Inconsistent Accounting on Encrypted DNS"
    assert loaded.status == FindingStatus.CLOSED


def test_attack_chain_building():
    chain = AttackChain(
        chain_id="CHN-2026-001",
        title="Unauthenticated DNS Tunneling to Quota Bypass",
        objective="Demonstrate complete control bypass chain",
    )

    link1 = chain.add_link(
        finding_id="F-AUTH-001",
        stage="authentication",
        description="Captive portal permits port 53 egress to any destination",
    )
    link2 = chain.add_link(
        finding_id="F-ACC-001",
        stage="accounting",
        description="DNS responses not accounted towards subscriber quota",
    )

    assert len(chain.links) == 2
    assert link1.position == 1
    assert link2.position == 2
    assert link1.finding_id == "F-AUTH-001"
    assert link2.finding_id == "F-ACC-001"
