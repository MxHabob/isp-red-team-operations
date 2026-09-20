# Evidence

Do not commit raw PCAPs, credentials, customer records, or sensitive provider exports.

Use an evidence manifest:

```yaml
id: EV-EXAMPLE-001
test_id: EXAMPLE-001
type: pcap
captured_at: "REPLACE_ME"
storage_ref: "external://REPLACE_ME"
sha256: "REPLACE_ME"
classification: restricted
collector: "REPLACE_ME"
```

Evidence should be immutable after collection. If a derived artifact is created, retain its relationship to the original.
