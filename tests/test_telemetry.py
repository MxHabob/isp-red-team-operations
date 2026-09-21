"""Tests for structured telemetry collector."""

from __future__ import annotations

from pathlib import Path

import pytest

from redteam.core.types import DataClassification, TelemetryEventType
from redteam.telemetry.collector import TelemetryCollector


def test_telemetry_collector_record_and_read(tmp_path: Path):
    collector = TelemetryCollector(output_dir=tmp_path / "telemetry")

    event = collector.record(
        operation_id="RT-YNET-001",
        run_id="RUN-2026-000001",
        test_id="TST-001",
        source="client-probe-01",
        event_type=TelemetryEventType.NETWORK,
        data={"bytes_sent": 1048576, "rtt_ms": 14.2},
        classification=DataClassification.INTERNAL,
    )

    assert event.event_id.startswith("TEL-")
    assert event.operation_id == "RT-YNET-001"
    assert event.data["bytes_sent"] == 1048576

    events = collector.read_events("RUN-2026-000001")
    assert len(events) == 1
    assert events[0].event_id == event.event_id


def test_telemetry_collector_sequence_increment(tmp_path: Path):
    collector = TelemetryCollector(output_dir=tmp_path / "telemetry")

    e1 = collector.record(
        operation_id="RT-YNET-001",
        run_id="RUN-2026-000001",
        test_id="TST-001",
        source="client",
        event_type=TelemetryEventType.SESSION,
    )
    e2 = collector.record(
        operation_id="RT-YNET-001",
        run_id="RUN-2026-000001",
        test_id="TST-001",
        source="client",
        event_type=TelemetryEventType.ACCOUNTING,
    )

    assert e1.event_id != e2.event_id
    assert e1.event_id == "TEL-TST-001-0001"
    assert e2.event_id == "TEL-TST-001-0002"

    events = collector.read_events("RUN-2026-000001")
    assert len(events) == 2
