# ADR-001: Data Isolation and External Evidence Storage

## Status
Accepted — 2026-09-21

## Context
Security assessment activities generate high-volume artifacts including packet captures (PCAP), subscriber telemetry, logs, and sensitive provider configuration exports. Storing raw artifacts in Git risks credential leakage, privacy violations, and repository bloat.

## Decision
Git serves strictly as the source of truth for code, schemas, configuration templates, documentation, and immutable evidence metadata (hashes, timestamps, manifest records). All raw PCAP, sensitive logs, and subscriber records MUST remain in isolated, external, encrypted storage.

## Consequences
- Zero sensitive data in version control.
- Deterministic verification through cryptographic SHA-256 manifests.
- Compliance with data protection and confidentiality mandates.
