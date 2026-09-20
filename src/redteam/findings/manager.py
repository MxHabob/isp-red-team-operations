"""Finding manager — create, validate, and manage findings.

A finding is a validated observation with security/business significance.
The lifecycle is: draft → validated → reported → remediated → retested → closed.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.errors import RedTeamError
from redteam.core.types import (
    Finding,
    FindingSeverity,
    FindingStatus,
    HypothesisConfidence,
)

logger = logging.getLogger(__name__)


class FindingManager:
    """Manages finding records.

    Args:
        findings_dir: Directory to store finding JSON files.
    """

    def __init__(self, findings_dir: Path) -> None:
        self._findings_dir = findings_dir
        self._registry: dict[str, Finding] = {}

    def create(
        self,
        finding_id: str,
        title: str,
        observation: str,
        test_ids: list[str] | None = None,
        evidence_ids: list[str] | None = None,
        severity: FindingSeverity = FindingSeverity.INFORMATIONAL,
        impact: str = "",
        confidence: HypothesisConfidence = HypothesisConfidence.UNCONFIRMED,
        limitations: str = "",
        recommendation: str = "",
    ) -> Finding:
        """Create a new finding in DRAFT status.

        A finding MUST have an observation.  Hypothesis → Finding conversion
        requires evidence.
        """
        if not observation:
            raise RedTeamError("Finding must have an observation")

        finding = Finding(
            finding_id=finding_id,
            title=title,
            status=FindingStatus.DRAFT,
            severity=severity,
            observation=observation,
            impact=impact,
            confidence=confidence,
            limitations=limitations,
            evidence_ids=evidence_ids or [],
            test_ids=test_ids or [],
            recommendation=recommendation,
        )

        self._registry[finding_id] = finding
        self._save(finding)
        logger.info("Finding created: %s — %s", finding_id, title)
        return finding

    def update_status(self, finding_id: str, new_status: FindingStatus) -> Finding:
        """Update a finding's lifecycle status."""
        finding = self.get(finding_id)
        old_status = finding.status
        finding.status = new_status
        self._save(finding)
        logger.info(
            "Finding %s: %s → %s", finding_id, old_status.value, new_status.value
        )
        return finding

    def get(self, finding_id: str) -> Finding:
        """Retrieve a finding by ID."""
        if finding_id not in self._registry:
            raise RedTeamError(f"Finding '{finding_id}' not found")
        return self._registry[finding_id]

    def list_all(self) -> list[Finding]:
        """Return all findings."""
        return list(self._registry.values())

    def _save(self, finding: Finding) -> None:
        """Save finding to a JSON file."""
        self._findings_dir.mkdir(parents=True, exist_ok=True)
        path = self._findings_dir / f"{finding.finding_id}.json"

        data = {
            "finding_id": finding.finding_id,
            "title": finding.title,
            "status": finding.status.value,
            "severity": finding.severity.value,
            "observation": finding.observation,
            "analysis": finding.analysis,
            "hypothesis": finding.hypothesis,
            "impact": finding.impact,
            "confidence": finding.confidence.value,
            "limitations": finding.limitations,
            "evidence_ids": finding.evidence_ids,
            "test_ids": finding.test_ids,
            "recommendation": finding.recommendation,
            "retest_id": finding.retest_id,
            "retest_result": finding.retest_result,
        }

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_from_directory(self) -> int:
        """Load all findings from the findings directory.

        Returns the number of findings loaded.
        """
        if not self._findings_dir.exists():
            return 0

        count = 0
        for json_file in sorted(self._findings_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                finding = Finding(
                    finding_id=data["finding_id"],
                    title=data.get("title", ""),
                    status=FindingStatus(data.get("status", "draft")),
                    severity=FindingSeverity(data.get("severity", "informational")),
                    observation=data.get("observation", ""),
                    analysis=data.get("analysis", ""),
                    hypothesis=data.get("hypothesis", ""),
                    impact=data.get("impact", ""),
                    confidence=HypothesisConfidence(data.get("confidence", "unconfirmed")),
                    limitations=data.get("limitations", ""),
                    evidence_ids=data.get("evidence_ids", []),
                    test_ids=data.get("test_ids", []),
                    recommendation=data.get("recommendation", ""),
                    retest_id=data.get("retest_id"),
                    retest_result=data.get("retest_result", ""),
                )
                self._registry[finding.finding_id] = finding
                count += 1
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Skipping corrupted finding %s: %s", json_file.name, exc)

        return count
