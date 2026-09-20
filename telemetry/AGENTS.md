# Telemetry — Schemas and Collection Specifications

## Responsibility
Telemetry event schemas, collector specifications, and metadata. Raw telemetry data is stored externally.

## Rules
- Git contains only schemas, specifications, and metadata.
- Raw telemetry files (JSONL, PCAP, logs) belong in the external telemetry store.
- Every event must include operation_id, run_id, test_id, and timestamp.
- Use structured formats (JSON/JSONL) — not free-form text.
