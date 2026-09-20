# Assessment Methodology

## Principles

- Hypothesis-driven rather than tool-driven.
- Measure before modifying.
- Establish a baseline before every materially different experiment.
- Use controlled test identities.
- Keep timestamps synchronized.
- Correlate client telemetry, network telemetry, and provider-visible observations when available.
- Separate observation from interpretation.
- Record negative results as well as positive results.
- Preserve enough context for independent reproduction.

## Analysis dimensions

### Network
Latency, loss, routes, MTU, TCP behavior, transport behavior, IPv4/IPv6.

### DNS
Resolution path, resolver behavior, consistency, failure modes, policy effects.

### TLS
Handshake behavior, protocol negotiation, certificate validation, metadata visibility, policy differences.

### Classification
Determine what observable attributes correlate with policy classification without assuming the implementation.

### Accounting
Compare expected usage against measured/recorded usage on authorized test accounts.

### Monitoring
Determine whether approved test activity produces the expected telemetry and alerts.

## Evidence standard

Every significant conclusion should reference:
- test ID
- timestamp
- environment
- input conditions
- expected behavior
- observed behavior
- evidence IDs
- limitations
