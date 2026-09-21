# ADR-005: Hypothesis-Driven Research Model

## Status
Accepted — 2026-09-21

## Context
The project could approach ISP testing by building bypass tools and then testing them, or by formulating testable hypotheses and designing controlled experiments.

## Decision
Adopt a **hypothesis-driven research model**. Each potential vulnerability class is formulated as a hypothesis (e.g., "Does the ISP correctly account for all IPv6 traffic?"), and a controlled experiment is designed to test it.

The project does NOT assume that "free internet" exists. It tests whether unauthorized service access is possible, and documents the result either way.

## Consequences
- `research/hypotheses/` contains all testable hypotheses
- Each hypothesis maps to one or more scenarios in `scenarios/`
- Negative results (controls working correctly) are documented
- No bypass tools are built — only test harnesses
- Findings must be supported by evidence, not by assumptions
