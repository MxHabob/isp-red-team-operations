"""Evidence store — registration, storage, and retrieval of evidence items.

The evidence store manages evidence metadata (manifests) in Git and
raw evidence in an external directory.  It enforces immutability:
once registered, an evidence record cannot be modified.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.errors import (
    EvidenceImmutabilityError,
    EvidenceNotFound,
)
from redteam.core.ids import generate_evidence_id
from redteam.core.types import DataClassification, EvidenceRecord, EvidenceType
from redteam.evidence.chain import ChainOfCustody
from redteam.evidence.integrity import compute_sha256

logger = logging.getLogger(__name__)


class EvidenceStore:
    """Manages evidence registration, storage, and retrieval.

    Args:
        manifests_dir: Directory for evidence manifest YAML/JSON files (in Git).
        raw_store: Directory for raw evidence files (outside Git).
        chain: Chain of custody instance.
    """

    def __init__(
        self,
        manifests_dir: Path,
        raw_store: Path,
        chain: ChainOfCustody,
    ) -> None:
        self._manifests_dir = manifests_dir
        self._raw_store = raw_store
        self._chain = chain
        self._registry: dict[str, EvidenceRecord] = {}

    def register(
        self,
        source_file: Path,
        test_id: str,
        operation_id: str,
        run_id: str,
        evidence_type: EvidenceType,
        operator: str,
        classification: DataClassification = DataClassification.RESTRICTED,
        parent_evidence_id: str | None = None,
        metadata: dict | None = None,
    ) -> EvidenceRecord:
        """Register a new evidence item.

        1. Computes SHA-256 hash of the source file
        2. Copies the file to the raw evidence store
        3. Creates an evidence manifest
        4. Records the collection in the chain of custody

        Args:
            source_file: Path to the evidence file to register.
            test_id: Parent test ID.
            operation_id: Parent operation ID.
            run_id: Parent run ID.
            evidence_type: Type of evidence.
            operator: Operator who collected the evidence.
            classification: Data classification level.
            parent_evidence_id: If derived, the parent evidence ID.
            metadata: Additional metadata.

        Returns:
            The registered evidence record.
        """
        if not source_file.exists():
            raise EvidenceNotFound(f"Source file not found: {source_file}")

        # Generate ID
        sequence = len([
            r for r in self._registry.values() if r.test_id == test_id
        ]) + 1
        evidence_id = generate_evidence_id(test_id, sequence)

        # Compute hash
        sha256 = compute_sha256(source_file)

        # Copy to raw store
        self._raw_store.mkdir(parents=True, exist_ok=True)
        dest_dir = self._raw_store / evidence_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / source_file.name
        shutil.copy2(source_file, dest_file)

        # Create record
        record = EvidenceRecord(
            evidence_id=evidence_id,
            test_id=test_id,
            operation_id=operation_id,
            run_id=run_id,
            type=evidence_type,
            captured_at=datetime.now(tz=timezone.utc),
            storage_ref=f"evidence-store://{evidence_id}/{source_file.name}",
            sha256=sha256,
            classification=classification,
            collector=operator,
            operator=operator,
            parent_evidence_id=parent_evidence_id,
            metadata=metadata or {},
        )

        self._registry[evidence_id] = record

        # Save manifest
        self._save_manifest(record)

        # Record in chain of custody
        action = "derived" if parent_evidence_id else "collected"
        self._chain.record(
            evidence_id=evidence_id,
            action=action,
            actor=operator,
            sha256=sha256,
            notes=f"Source: {source_file.name}, Type: {evidence_type.value}",
        )

        logger.info(
            "Evidence registered: %s (sha256=%s..., type=%s)",
            evidence_id,
            sha256[:16],
            evidence_type.value,
        )
        return record

    def get(self, evidence_id: str) -> EvidenceRecord:
        """Retrieve an evidence record by ID.

        Raises:
            EvidenceNotFound: If the evidence ID is not registered.
        """
        if evidence_id not in self._registry:
            raise EvidenceNotFound(f"Evidence '{evidence_id}' not found")
        return self._registry[evidence_id]

    def verify(self, evidence_id: str) -> bool:
        """Verify the integrity of a stored evidence item.

        Checks that the raw file still matches the recorded SHA-256 hash
        and that the chain of custody is consistent.

        Returns:
            True if integrity is verified.

        Raises:
            EvidenceIntegrityError: If integrity check fails.
            EvidenceNotFound: If the evidence is not registered.
        """
        record = self.get(evidence_id)

        # Find the raw file
        raw_dir = self._raw_store / evidence_id
        if not raw_dir.exists():
            logger.warning("Raw evidence directory not found: %s", raw_dir)
            return False

        raw_files = list(raw_dir.iterdir())
        if not raw_files:
            logger.warning("No raw files in evidence directory: %s", raw_dir)
            return False

        # Verify hash of the first file
        current_hash = compute_sha256(raw_files[0])
        if current_hash != record.sha256:
            from redteam.core.errors import EvidenceIntegrityError

            raise EvidenceIntegrityError(
                f"Evidence {evidence_id} hash mismatch: "
                f"expected {record.sha256[:16]}..., got {current_hash[:16]}..."
            )

        # Verify chain of custody
        self._chain.verify_integrity(evidence_id)

        # Record the verification
        self._chain.record(
            evidence_id=evidence_id,
            action="verified",
            actor="system",
            sha256=current_hash,
        )

        return True

    def list_all(self) -> list[EvidenceRecord]:
        """Return all registered evidence records."""
        return list(self._registry.values())

    def _save_manifest(self, record: EvidenceRecord) -> None:
        """Save evidence manifest to the manifests directory."""
        self._manifests_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = self._manifests_dir / f"{record.evidence_id}.json"

        data = {
            "evidence_id": record.evidence_id,
            "test_id": record.test_id,
            "operation_id": record.operation_id,
            "run_id": record.run_id,
            "type": record.type.value,
            "captured_at": record.captured_at.isoformat() if record.captured_at else None,
            "storage_ref": record.storage_ref,
            "sha256": record.sha256,
            "classification": record.classification.value,
            "collector": record.collector,
            "operator": record.operator,
            "parent_evidence_id": record.parent_evidence_id,
            "metadata": record.metadata,
        }

        manifest_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
