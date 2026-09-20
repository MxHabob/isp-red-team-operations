# Baseline Runbook

## Preconditions
- Scope approved
- Test account verified
- Clock synchronized
- Evidence destination available

## Capture
Record:
- timestamp
- test client identity
- access technology
- IPv4/IPv6 state
- DNS configuration
- gateway
- route
- latency/loss
- MTU
- relevant modem/CPE state

## Rule
Do not change network configuration during baseline collection unless the test explicitly requires it.

## Output
Create a baseline record linked to the operation and evidence manifest.
