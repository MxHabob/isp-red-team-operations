"""Tests for the ID generation and validation module."""

from __future__ import annotations

import pytest

from redteam.core.errors import IDValidationError
from redteam.core.ids import (
    generate_evidence_id,
    generate_run_id,
    generate_telemetry_id,
    is_valid_id,
    reset_run_counter,
    validate_id,
)


class TestValidateId:
    def test_valid_operation_id(self) -> None:
        assert validate_id("RT-YNET-001", "operation") == "RT-YNET-001"

    def test_invalid_operation_id(self) -> None:
        with pytest.raises(IDValidationError):
            validate_id("INVALID", "operation")

    def test_valid_test_id(self) -> None:
        assert validate_id("ACC-001", "test") == "ACC-001"

    def test_valid_evidence_id(self) -> None:
        assert validate_id("EV-ACC-001-0001", "evidence") == "EV-ACC-001-0001"

    def test_valid_finding_id(self) -> None:
        assert validate_id("F-ACC-001", "finding") == "F-ACC-001"

    def test_unknown_type(self) -> None:
        with pytest.raises(IDValidationError, match="Unknown ID type"):
            validate_id("X-001", "unknown_type")


class TestIsValidId:
    def test_valid(self) -> None:
        assert is_valid_id("RT-YNET-001", "operation") is True

    def test_invalid(self) -> None:
        assert is_valid_id("bad", "operation") is False

    def test_unknown_type(self) -> None:
        assert is_valid_id("X-001", "unknown") is False


class TestGenerateRunId:
    def test_format(self) -> None:
        reset_run_counter()
        run_id = generate_run_id()
        assert is_valid_id(run_id, "run")

    def test_increments(self) -> None:
        reset_run_counter()
        id1 = generate_run_id()
        id2 = generate_run_id()
        assert id1 != id2


class TestGenerateEvidenceId:
    def test_format(self) -> None:
        ev_id = generate_evidence_id("ACC-001", 1)
        assert ev_id == "EV-ACC-001-0001"
        assert is_valid_id(ev_id, "evidence")

    def test_invalid_test_id(self) -> None:
        with pytest.raises(IDValidationError):
            generate_evidence_id("bad-id", 1)


class TestGenerateTelemetryId:
    def test_format(self) -> None:
        tel_id = generate_telemetry_id("DNS-002", 5)
        assert tel_id == "TEL-DNS-002-0005"
        assert is_valid_id(tel_id, "telemetry")
