"""Telemetry collector — structured event collection to JSONL files.

Events are written as append-only JSONL (one JSON object per line).
Each event includes operation, run, and test context for correlation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from redteam.core.ids import generate_telemetry_id
from redteam.core.types import DataClassification, TelemetryEvent, TelemetryEventType

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """Collects structured telemetry events to JSONL files.

    Args:
        output_dir: Directory to write JSONL telemetry files.
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._sequence: dict[str, int] = {}  # test_id → counter

    def _next_sequence(self, test_id: str) -> int:
        current = self._sequence.get(test_id, 0)
        current += 1
        self._sequence[test_id] = current
        return current

    def record(
        self,
        operation_id: str,
        run_id: str,
        test_id: str,
        source: str,
        event_type: TelemetryEventType,
        data: dict | None = None,
        classification: DataClassification = DataClassification.INTERNAL,
        data_reference: str = "",
    ) -> TelemetryEvent:
        """Record a telemetry event.

        The event is appended to a JSONL file named after the run ID.

        Returns:
            The recorded event.
        """
        seq = self._next_sequence(test_id)
        event_id = generate_telemetry_id(test_id, seq)

        event = TelemetryEvent(
            event_id=event_id,
            operation_id=operation_id,
            run_id=run_id,
            test_id=test_id,
            timestamp=datetime.now(tz=timezone.utc),
            source=source,
            type=event_type,
            classification=classification,
            data=data or {},
            data_reference=data_reference,
        )

        self._write_event(event)
        return event

    def _write_event(self, event: TelemetryEvent) -> None:
        """Append an event to the JSONL file."""
        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self._output_dir / f"{event.run_id}.jsonl"

        line = json.dumps(
            {
                "event_id": event.event_id,
                "operation_id": event.operation_id,
                "run_id": event.run_id,
                "test_id": event.test_id,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "type": event.type.value,
                "classification": event.classification.value,
                "data": event.data,
                "data_reference": event.data_reference,
            },
            ensure_ascii=False,
        )

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        logger.debug("Telemetry event: %s (%s)", event.event_id, event.type.value)

    def read_events(self, run_id: str) -> list[TelemetryEvent]:
        """Read all telemetry events for a run.

        Args:
            run_id: The run ID to read events for.

        Returns:
            List of events in chronological order.
        """
        output_file = self._output_dir / f"{run_id}.jsonl"
        if not output_file.exists():
            return []

        events: list[TelemetryEvent] = []
        for line in output_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                events.append(
                    TelemetryEvent(
                        event_id=data["event_id"],
                        operation_id=data["operation_id"],
                        run_id=data["run_id"],
                        test_id=data["test_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        source=data["source"],
                        type=TelemetryEventType(data["type"]),
                        classification=DataClassification(data.get("classification", "internal")),
                        data=data.get("data", {}),
                        data_reference=data.get("data_reference", ""),
                    )
                )
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Skipping corrupted telemetry event: %s", exc)

        return events
