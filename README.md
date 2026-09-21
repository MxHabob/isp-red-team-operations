# ISP Red Team Operations

Professional, auditable Red Team security research environment for ISP network assessment.

## Mission

Test the hypothesis: **Do vulnerabilities or misconfigurations exist in ISP security controls that could allow unauthorized service access or incorrect accounting?**

This is NOT a tool collection. It is a process-driven, hypothesis-based security research platform where every test is:

- **Authorized** — explicit scope and approval required
- **Controlled** — safety engine and kill switch enforce boundaries
- **Isolated** — lab environment with synthetic data by default
- **Auditable** — full evidence chain of custody with SHA-256 integrity
- **Reproducible** — structured scenarios with deterministic execution
- **Documented** — findings, evidence, and reports are linked and traceable

## Quick Start

```bash
# Install the platform
pip install -e ".[dev]"

# Verify the repository
python scripts/validate_repo.py

# Check the scope
redteam scope validate

# Run safety checks
redteam safety check

# Execute a dry run
redteam run dry-run --scenario SC-ACC-001

# Manage the kill switch
redteam safety killswitch status
```

## Repository Structure

| Directory | Purpose |
|---|---|
| `command/` | Mission control — scope, ROE, approvals |
| `research/` | Hypothesis registry and vulnerability research |
| `scenarios/` | Structured test scenario definitions (YAML) |
| `operations/` | Runbooks, checklists, kill switch |
| `src/redteam/` | Python runtime — engines, CLI, telemetry, evidence |
| `tests/` | Python test suite |
| `telemetry/` | Telemetry schemas (raw data is external) |
| `evidence/` | Evidence manifests and chain of custody (raw data is external) |
| `findings/` | Finding records and remediation tracking |
| `reports/` | Report templates and generated reports |
| `lab/` | Lab topology, services, synthetic data |
| `data/` | Test fixtures and synthetic data |
| `config/` | Configuration schemas and environment profiles |
| `scripts/` | Validation and utility scripts |
| `docs/` | Architecture, methodology, ADRs, security |

## Key Principles

1. **Process over tools** — the operational lifecycle is the center, not scripts
2. **Hypothesis-driven** — test whether vulnerabilities exist, don't assume they do
3. **Lab first** — all tests must work in lab before touching real infrastructure
4. **Evidence integrity** — SHA-256 hashing, chain of custody, immutable records
5. **Safety by default** — scope engine, safety engine, and kill switch enforce boundaries

## Data Isolation

Git contains **only**: source code, schemas, documentation, scenario definitions, evidence metadata, and finding metadata.

Git **never** contains: raw PCAP, credentials, customer data, production exports, secrets, or sensitive logs.

## Documentation

See `docs/README.md` for the documentation index.
