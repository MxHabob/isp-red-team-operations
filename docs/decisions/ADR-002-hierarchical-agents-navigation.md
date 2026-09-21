# ADR-002: Hierarchical AGENTS.md Navigation and Context Separation

## Status
Accepted — 2026-09-21

## Context
AI agents operating across large repositories need concise, directory-scoped rules to prevent hallucination, scope violations, and architecture erosion.

## Decision
Implement a root `AGENTS.md` defining core safety principles and operational boundaries, accompanied by scoped `AGENTS.md` files in each subsystem directory (`command/`, `research/`, `scenarios/`, `operations/`, `telemetry/`, `evidence/`, `findings/`, `reports/`, `lab/`, `data/`, `config/`, `scripts/`, `docs/`, `tests/`). Comprehensive domain reference documents remain organized under `docs/`.

## Consequences
- Clean agent context windows and deterministic rule enforcement.
- Maintainable and auditable directory boundaries.
