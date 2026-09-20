# Architecture

## Operational model

```text
Command
  |
  +-- Scope / ROE / Approvals
  |
  +-- Scenarios
  |     +-- Network
  |     +-- DNS
  |     +-- TLS
  |     +-- Traffic classification
  |     +-- Accounting
  |     +-- IPv4/IPv6
  |     +-- Detection/monitoring
  |
  +-- Execution
  |
  +-- Telemetry
  |
  +-- Evidence
  |
  +-- Findings
  |
  +-- Reporting
  |
  +-- Retest
```

## Separation of concerns

- **Command:** what is allowed and why.
- **Scenario:** what hypothesis is being tested.
- **Operations:** how an approved test is executed safely.
- **Telemetry:** what measurements are collected.
- **Evidence:** immutable proof supporting an observation.
- **Findings:** validated security/business observations.
- **Reports:** stakeholder-facing outputs.

## External systems

The project may integrate with:
- GitHub
- a controlled evidence store
- a SIEM
- packet-capture sensors
- test clients
- test CPE/modems
- ATT&CK Navigator
- ticket/case management

Integration credentials must remain outside Git.
