# ADR-004: Process-Centric Architecture, Not Tool-Centric

## Status
Accepted — 2026-09-21

## Context
The project could be organized around tools (scripts, scanners, exploits) or around the operational process (mission → scope → hypothesis → test → evidence → finding → report).

## Decision
The project is organized around the **operational lifecycle**, not around tools. Tools serve the process, not the other way around.

## Consequences
- Directory structure reflects process phases (command, research, scenarios, operations, telemetry, evidence, findings, reports)
- Every test must follow the lifecycle: PRECHECK → SCOPE_CHECK → SAFETY_CHECK → ENVIRONMENT_CHECK → BASELINE → EXECUTION → TELEMETRY → EVIDENCE → ANALYSIS → RESULT → CLEANUP
- CLI commands map to process phases, not to individual tools
- Automation serves reproducibility and auditability, not convenience
