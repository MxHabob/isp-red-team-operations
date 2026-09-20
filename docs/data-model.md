# Data Model

## Test record

```yaml
id: ACC-001
operation_id: RT-YNET-001
objective: "Validate accounting consistency for an authorized test account"
status: planned
scope_ref: command/scope.yaml
operator: RT-01
started_at: null
ended_at: null
expected_result: null
observed_result: null
evidence_ids: []
finding_ids: []
```

## Evidence record

```yaml
id: EV-ACC-001-001
test_id: ACC-001
type: pcap
captured_at: null
storage_ref: external://evidence/EV-ACC-001-001
sha256: ""
classification: restricted
```

## Finding record

```yaml
id: F-ACC-001
severity: TBD
status: draft
test_ids: []
evidence_ids: []
title: ""
observation: ""
impact: ""
reproduction_summary: ""
limitations: ""
recommendation: ""
```
