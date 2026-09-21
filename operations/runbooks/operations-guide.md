# Operational Guide & Execution Procedure

This runbook defines the end-to-end operational procedure for executing authorized security assessments and hypothesis testing within the ISP Red Team Operations environment.

---

## 1. Preconditions

- [ ] Operator environment initialized with required dependencies (`pip install -e ".[dev]"`).
- [ ] Active authorization and scope approved in `command/scope.yaml` and `command/roe.md`.
- [ ] Host clock synchronized (NTP).
- [ ] Target environment set to isolated lab / synthetic data environment.
- [ ] Evidence destination storage initialized and writable.

---

## 2. Environment & Repository Validation

Verify repository structure, syntax, and schema integrity:

```powershell
# Validate all files, registries, and syntax
python scripts/validate_repo.py

# Run test suite to verify platform engines
pytest
```

---

## 3. Scope & Safety Pre-Flight Checks

Ensure execution parameters comply strictly with authorized boundaries:

```powershell
# 1. Validate scope configuration
redteam scope validate

# 2. Review authorized assets and network boundaries
redteam scope show

# 3. Perform automated safety checks
redteam safety check

# 4. Verify kill switch status is disarmed / operational
redteam safety killswitch status
```

---

## 4. Scenario Selection & Execution (Lab / Dry Run)

Assessments are conducted through registered, structured scenarios:

```powershell
# List available scenarios
redteam scenario list

# Run pre-flight dry run for a specific scenario (e.g., Accounting Consistency)
redteam run dry-run --scenario SC-ACC-001

# Execute scenario in authorized lab environment
redteam run execute --scenario SC-ACC-001
```

---

## 5. Telemetry & Evidence Collection

Capture immutable telemetry and record evidence hashes:

```powershell
# Verify evidence manifest and SHA-256 integrity
redteam evidence verify

# List and review recorded findings
redteam finding list
```

---

## 6. Cleanup & Emergency Procedures

1. **Normal Cleanup:** Ensure all temporary test states, sessions, and artifacts are purged or finalized.
2. **Emergency Abort (Kill Switch):** In the event of unexpected network behavior or safety anomalies, engage the kill switch immediately:

```powershell
# Activate immediate kill switch
redteam safety killswitch engage
```

---

## 7. Operator Validation & Reporting

- Review generated findings against hypotheses in `research/hypotheses/registry.yaml`.
- Generate the operation summary report:

```powershell
redteam validate all
```
