# ADR-003: Stable Structured Identifier Scheme

## Status
Accepted — 2026-09-21

## Context
Cross-referencing between operations, runs, test executions, scenarios, hypotheses, findings, evidence, and telemetry requires consistent, deterministic, and unambiguous identifiers.

## Decision
Enforce regex-validated ID schemes across the entire platform:
- Operation: `RT-[A-Z0-9]+-\d{3}` (e.g. `RT-YNET-001`)
- Run: `RUN-\d{4}-\d{6}` (e.g. `RUN-2026-000001`)
- Test / Step: `[A-Z]+-\d{3}` (e.g. `TST-001`, `ACC-001`)
- Scenario: `SC-[A-Z]+-\d{3}` (e.g. `SC-ACC-001`)
- Hypothesis: `HYP-[A-Z]+-\d{3}` (e.g. `HYP-ACC-001`)
- Finding: `F-[A-Z]+-\d{3}` (e.g. `F-ACC-001`)
- Evidence: `EV-[A-Z0-9]+-\d{3}-\d{4}` (e.g. `EV-ACC-001-0001`)
- Telemetry: `TEL-[A-Z0-9]+-\d{3}-\d{4}` (e.g. `TEL-TST-001-0001`)

## Consequences
- Automated correlation across SIEM, logs, manifests, and assessment reports.
- Rigorous type and schema validation.
