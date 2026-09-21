# ADR-006: Lab Before Production

## Status
Accepted — 2026-09-21

## Context
Tests could target production ISP infrastructure directly or be developed and validated in a lab environment first.

## Decision
All tests MUST work in a **lab environment** with synthetic data before they can be used against authorized field or production targets.

## Consequences
- `lab/` contains topology, services, and synthetic data
- `data/synthetic/` provides deterministic test data
- Default environment profile is `lab` — production requires explicit override
- Dry-run mode must complete successfully before any real network testing
- The project can be used and developed without any ISP connectivity
