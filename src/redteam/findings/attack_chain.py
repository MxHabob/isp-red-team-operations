"""Attack chain — link related findings into an exploitation chain.

An attack chain represents a sequence of findings that, when combined,
demonstrate a compound vulnerability or impact path.  This is used for
analysis and reporting purposes — NOT for building active exploits.

Example conceptual chain:
    INITIAL ACCESS → AUTHENTICATION → AUTHORIZATION → POLICY →
    ACCOUNTING → SERVICE ACCESS → IMPACT
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AttackChainLink:
    """A single link in an attack chain."""

    position: int
    finding_id: str
    stage: str  # e.g. "authentication", "authorization", "accounting"
    description: str = ""
    evidence_ids: list[str] = field(default_factory=list)
    confidence: str = "unconfirmed"


@dataclass
class AttackChain:
    """A chain of linked findings demonstrating a compound vulnerability."""

    chain_id: str
    title: str
    objective: str = ""
    links: list[AttackChainLink] = field(default_factory=list)
    overall_impact: str = ""
    overall_confidence: str = "unconfirmed"
    limitations: str = ""

    def add_link(
        self,
        finding_id: str,
        stage: str,
        description: str = "",
        evidence_ids: list[str] | None = None,
        confidence: str = "unconfirmed",
    ) -> AttackChainLink:
        """Add a new link to the chain."""
        link = AttackChainLink(
            position=len(self.links) + 1,
            finding_id=finding_id,
            stage=stage,
            description=description,
            evidence_ids=evidence_ids or [],
            confidence=confidence,
        )
        self.links.append(link)
        return link

    def summary(self) -> str:
        """Human-readable chain summary."""
        parts = [f"Attack Chain: {self.chain_id} — {self.title}"]
        for link in self.links:
            parts.append(
                f"  {link.position}. [{link.stage}] {link.finding_id}: "
                f"{link.description} (confidence: {link.confidence})"
            )
        if self.overall_impact:
            parts.append(f"  Impact: {self.overall_impact}")
        if self.limitations:
            parts.append(f"  Limitations: {self.limitations}")
        return "\n".join(parts)


def save_attack_chain(chain: AttackChain, output_dir: Path) -> Path:
    """Save an attack chain to a JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{chain.chain_id}.json"

    data = {
        "chain_id": chain.chain_id,
        "title": chain.title,
        "objective": chain.objective,
        "links": [
            {
                "position": link.position,
                "finding_id": link.finding_id,
                "stage": link.stage,
                "description": link.description,
                "evidence_ids": link.evidence_ids,
                "confidence": link.confidence,
            }
            for link in chain.links
        ],
        "overall_impact": chain.overall_impact,
        "overall_confidence": chain.overall_confidence,
        "limitations": chain.limitations,
    }

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
