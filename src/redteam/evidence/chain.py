"""Chain of custody — immutable audit trail for evidence.

Every action on an evidence item (collection, transfer, access, derivation)
is recorded in the chain of custody.  Once recorded, entries cannot be
modified or deleted.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.errors import EvidenceImmutabilityError
from redteam.core.types import ChainOfCustodyEntry

logger = logging.getLogger(__name__)


class ChainOfCustody:
    """Immutable chain of custody for evidence items.

    The chain is stored as a JSONL (JSON Lines) file — one entry per line,
    append-only.  This format ensures that:
    1. Existing entries are never modified
    2. New entries are appended atomically
    3. The file is human-readable and machine-parseable
    """

    def __init__(self, chain_file: Path) -> None:
        self._chain_file = chain_file

    def record(
        self,
        evidence_id: str,
        action: str,
        actor: str,
        sha256: str,
        notes: str = "",
    ) -> ChainOfCustodyEntry:
        """Append a new entry to the chain of custody.

        Args:
            evidence_id: The evidence item ID.
            action: Action performed (collected, transferred, verified, accessed, derived).
            actor: Identity of the person/system performing the action.
            sha256: Current SHA-256 hash of the evidence.
            notes: Optional notes.

        Returns:
            The recorded entry.
        """
        entry = ChainOfCustodyEntry(
            timestamp=datetime.now(tz=timezone.utc),
            action=action,
            actor=actor,
            evidence_id=evidence_id,
            sha256=sha256,
            notes=notes,
        )

        # Append-only write
        self._chain_file.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "timestamp": entry.timestamp.isoformat(),
                "action": entry.action,
                "actor": entry.actor,
                "evidence_id": entry.evidence_id,
                "sha256": entry.sha256,
                "notes": entry.notes,
            },
            ensure_ascii=False,
        )
        with open(self._chain_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        logger.info(
            "Chain of custody: %s %s by %s (sha256=%s...)",
            evidence_id,
            action,
            actor,
            sha256[:16],
        )
        return entry

    def get_history(self, evidence_id: str | None = None) -> list[ChainOfCustodyEntry]:
        """Read chain of custody entries.

        Args:
            evidence_id: If provided, filter to entries for this evidence item.
                         If None, return all entries.

        Returns:
            List of entries in chronological order.
        """
        if not self._chain_file.exists():
            return []

        entries: list[ChainOfCustodyEntry] = []
        for line_num, line in enumerate(
            self._chain_file.read_text(encoding="utf-8").splitlines(), 1
        ):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entry = ChainOfCustodyEntry(
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    action=data["action"],
                    actor=data["actor"],
                    evidence_id=data["evidence_id"],
                    sha256=data["sha256"],
                    notes=data.get("notes", ""),
                )
                if evidence_id is None or entry.evidence_id == evidence_id:
                    entries.append(entry)
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Skipping corrupted chain entry at line %d: %s", line_num, exc)

        return entries

    def verify_integrity(self, evidence_id: str) -> bool:
        """Check that the chain of custody for an evidence item is consistent.

        Verifies that the SHA-256 hash has not changed between entries
        (unless the action is 'derived', which creates a new artifact).

        Returns:
            True if the chain is consistent.

        Raises:
            EvidenceImmutabilityError: If an inconsistency is detected.
        """
        history = self.get_history(evidence_id)
        if not history:
            return True

        # Track the expected hash
        base_hash = history[0].sha256
        for entry in history[1:]:
            if entry.action == "derived":
                # Derived evidence gets a new hash
                base_hash = entry.sha256
                continue
            if entry.sha256 != base_hash:
                raise EvidenceImmutabilityError(
                    f"Evidence {evidence_id} integrity violation at {entry.timestamp}: "
                    f"expected hash {base_hash[:16]}..., got {entry.sha256[:16]}..."
                )

        logger.info("Chain of custody integrity verified for %s", evidence_id)
        return True
