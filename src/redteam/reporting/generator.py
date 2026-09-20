"""Report generator — produces assessment reports from findings and evidence."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.types import (
    Finding,
    OperationRecord,
    ScenarioDefinition,
    ScopeDefinition,
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates markdown assessment reports.

    The report follows the structure defined in the report template.
    """

    def generate(
        self,
        output_path: Path,
        operation: OperationRecord,
        scope: ScopeDefinition,
        scenarios: list[ScenarioDefinition],
        findings: list[Finding],
        evidence_summary: list[dict],
        observations: list[str] | None = None,
        limitations: list[str] | None = None,
    ) -> Path:
        """Generate a full assessment report.

        Args:
            output_path: Path to write the report.
            operation: Operation record.
            scope: Scope definition.
            scenarios: List of executed scenarios.
            findings: List of findings.
            evidence_summary: Summary of evidence items.
            observations: General observations.
            limitations: Known limitations.

        Returns:
            Path to the generated report.
        """
        sections: list[str] = []

        # Header
        sections.append(f"# Security Assessment Report — {operation.name}")
        sections.append("")
        sections.append(f"**Operation ID:** {operation.operation_id}")
        sections.append(f"**Generated:** {datetime.now(tz=timezone.utc).isoformat()}")
        sections.append(f"**Status:** {operation.status.value}")
        sections.append("")

        # Executive Summary
        sections.append("## 1. Executive Summary")
        sections.append("")
        total_findings = len(findings)
        critical = sum(1 for f in findings if f.severity.value == "critical")
        high = sum(1 for f in findings if f.severity.value == "high")
        medium = sum(1 for f in findings if f.severity.value == "medium")
        low = sum(1 for f in findings if f.severity.value == "low")
        info = sum(1 for f in findings if f.severity.value == "informational")

        sections.append(f"This assessment identified **{total_findings}** findings:")
        sections.append(f"- Critical: {critical}")
        sections.append(f"- High: {high}")
        sections.append(f"- Medium: {medium}")
        sections.append(f"- Low: {low}")
        sections.append(f"- Informational: {info}")
        sections.append("")

        # Authorization and Scope
        sections.append("## 2. Authorization and Scope")
        sections.append("")
        sections.append(f"**Operation:** {scope.name}")
        sections.append(f"**Status:** {scope.status}")
        sections.append(f"**Environment:** {scope.environment.value}")
        sections.append("")
        if scope.authorized_assets:
            sections.append("### Authorized Assets")
            for asset in scope.authorized_assets:
                sections.append(f"- {asset.name} ({asset.type}): `{asset.identifier}`")
            sections.append("")
        if scope.prohibited_activity:
            sections.append("### Prohibited Activities")
            for p in scope.prohibited_activity:
                sections.append(f"- {p}")
            sections.append("")

        # Methodology
        sections.append("## 3. Methodology")
        sections.append("")
        sections.append("Hypothesis-driven assessment using controlled test identities,")
        sections.append("scope-enforced execution, and evidence-based validation.")
        sections.append("")

        # Scenarios
        sections.append("## 4. Scenario Results")
        sections.append("")
        for s in scenarios:
            sections.append(f"### {s.scenario_id}")
            sections.append(f"**Objective:** {s.objective}")
            sections.append(f"**Hypothesis:** {s.hypothesis}")
            sections.append(f"**Status:** {s.status.value}")
            sections.append("")

        # Findings
        sections.append("## 5. Findings")
        sections.append("")
        if not findings:
            sections.append("No findings recorded.")
            sections.append("")
        else:
            for f in findings:
                sections.append(f"### {f.finding_id} — {f.title}")
                sections.append(f"**Severity:** {f.severity.value}")
                sections.append(f"**Status:** {f.status.value}")
                sections.append(f"**Confidence:** {f.confidence.value}")
                sections.append("")
                sections.append(f"**Observation:** {f.observation}")
                sections.append("")
                if f.impact:
                    sections.append(f"**Impact:** {f.impact}")
                    sections.append("")
                if f.limitations:
                    sections.append(f"**Limitations:** {f.limitations}")
                    sections.append("")
                if f.evidence_ids:
                    sections.append("**Evidence:** " + ", ".join(f.evidence_ids))
                    sections.append("")
                if f.recommendation:
                    sections.append(f"**Recommendation:** {f.recommendation}")
                    sections.append("")

        # Evidence Index
        sections.append("## 6. Evidence Index")
        sections.append("")
        if evidence_summary:
            sections.append("| ID | Type | SHA-256 | Classification |")
            sections.append("|---|---|---|---|")
            for ev in evidence_summary:
                sections.append(
                    f"| {ev.get('id', '')} | {ev.get('type', '')} "
                    f"| `{ev.get('sha256', '')[:16]}...` | {ev.get('classification', '')} |"
                )
            sections.append("")
        else:
            sections.append("No evidence collected.")
            sections.append("")

        # Limitations
        sections.append("## 7. Limitations")
        sections.append("")
        if limitations:
            for lim in limitations:
                sections.append(f"- {lim}")
        else:
            sections.append("- Assessment scope limited to authorized test infrastructure")
        sections.append("")

        # Remediation
        sections.append("## 8. Remediation")
        sections.append("")
        recs = [f for f in findings if f.recommendation]
        if recs:
            for f in recs:
                sections.append(f"- **{f.finding_id}:** {f.recommendation}")
        else:
            sections.append("No specific remediation recommendations at this time.")
        sections.append("")

        # Retest
        sections.append("## 9. Retest")
        sections.append("")
        sections.append("Retest should be scheduled after remediation is applied.")
        sections.append("")

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(sections)
        output_path.write_text(content, encoding="utf-8")
        logger.info("Report generated: %s", output_path)
        return output_path
