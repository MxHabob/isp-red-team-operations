"""Tests for the evidence subsystem."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.errors import EvidenceIntegrityError
from redteam.core.types import DataClassification, EvidenceType
from redteam.evidence.chain import ChainOfCustody
from redteam.evidence.integrity import compute_sha256, compute_sha256_bytes, verify_sha256
from redteam.evidence.store import EvidenceStore


class TestIntegrity:
    def test_compute_sha256(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        digest = compute_sha256(test_file)
        assert len(digest) == 64
        assert digest == compute_sha256(test_file)  # deterministic

    def test_compute_sha256_bytes(self) -> None:
        digest = compute_sha256_bytes(b"test content")
        assert len(digest) == 64

    def test_verify_sha256_success(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        digest = compute_sha256(test_file)
        assert verify_sha256(test_file, digest) is True

    def test_verify_sha256_failure(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        with pytest.raises(EvidenceIntegrityError):
            verify_sha256(test_file, "0" * 64)


class TestChainOfCustody:
    def test_record_and_read(self, tmp_path: Path) -> None:
        chain = ChainOfCustody(tmp_path / "chain.jsonl")
        chain.record("EV-ACC-001-0001", "collected", "operator-1", "abc123")
        chain.record("EV-ACC-001-0001", "verified", "operator-2", "abc123")

        history = chain.get_history("EV-ACC-001-0001")
        assert len(history) == 2
        assert history[0].action == "collected"
        assert history[1].action == "verified"

    def test_integrity_check_passes(self, tmp_path: Path) -> None:
        chain = ChainOfCustody(tmp_path / "chain.jsonl")
        chain.record("EV-ACC-001-0001", "collected", "op", "abc123")
        chain.record("EV-ACC-001-0001", "verified", "op", "abc123")
        assert chain.verify_integrity("EV-ACC-001-0001") is True

    def test_integrity_check_fails_on_tamper(self, tmp_path: Path) -> None:
        chain = ChainOfCustody(tmp_path / "chain.jsonl")
        chain.record("EV-ACC-001-0001", "collected", "op", "abc123")
        chain.record("EV-ACC-001-0001", "verified", "op", "DIFFERENT")

        from redteam.core.errors import EvidenceImmutabilityError

        with pytest.raises(EvidenceImmutabilityError):
            chain.verify_integrity("EV-ACC-001-0001")


class TestEvidenceStore:
    def test_register_and_verify(self, tmp_path: Path) -> None:
        manifests_dir = tmp_path / "manifests"
        raw_store = tmp_path / "raw"
        chain = ChainOfCustody(tmp_path / "chain.jsonl")
        store = EvidenceStore(manifests_dir, raw_store, chain)

        # Create a source file
        source = tmp_path / "source.txt"
        source.write_text("evidence data")

        record = store.register(
            source_file=source,
            test_id="ACC-001",
            operation_id="RT-TEST-001",
            run_id="RUN-2026-000001",
            evidence_type=EvidenceType.LOG,
            operator="test-op",
        )

        assert record.evidence_id == "EV-ACC-001-0001"
        assert record.sha256 != ""
        assert (manifests_dir / "EV-ACC-001-0001.json").exists()

        # Verify
        assert store.verify("EV-ACC-001-0001") is True
