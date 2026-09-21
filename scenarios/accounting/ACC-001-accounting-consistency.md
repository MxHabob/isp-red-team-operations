# ACC-001 — Accounting Consistency

## Hypothesis
For an authorized test account, recorded usage should be consistent with independently measured traffic under the approved test conditions.

## Scope
Use only the test account and destinations explicitly listed in `command/scope.yaml`.

## Measurements
- test start/end timestamps
- bytes observed at the controlled measurement point
- provider-visible usage if legitimately available
- protocol/destination class
- IPv4/IPv6 path
- retransmissions and retries

## Expected result
Measurements are within the agreed tolerance and no unexplained policy difference is observed.

## Stop conditions
Stop if traffic leaves the approved scope or customer data becomes visible.

## Evidence
- measurement log
- packet capture metadata
- screenshots/export supplied by the authorized test environment
- hash manifest

## Analysis
Do not infer implementation details from one observation. Repeat the experiment under controlled conditions and document limitations.
