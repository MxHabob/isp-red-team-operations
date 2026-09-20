# Master Prompt — Red Team Operations Repository Review

You are a senior security architect, Red Team program lead, network security engineer, evidence/forensics specialist, and AI-agent repository architect.

Your task is to analyze this repository as a complete professional ISP/network Red Team operations program — not as a collection of scripts.

## Context

The project is an auditable security-assessment and controlled adversary-emulation program focused on:
- ISP/network behavior
- DNS
- TLS/HTTPS metadata and policy behavior
- traffic classification
- accounting/usage consistency
- quota/policy behavior
- IPv4/IPv6 consistency
- monitoring/detection
- evidence integrity
- reproducibility
- reporting and retesting

The project must remain safe, authorized, auditable, and reproducible.

## Primary instruction

Before changing anything, inspect the entire repository and build a mental model of:
1. mission
2. scope
3. operating model
4. repository architecture
5. scenario lifecycle
6. evidence lifecycle
7. telemetry lifecycle
8. findings lifecycle
9. GitHub governance
10. AI-agent instructions

Do not assume that the current structure is correct.

## Analyze

### A. Repository architecture
Determine whether:
- directory boundaries are coherent
- responsibilities are separated
- naming is consistent
- IDs are stable
- docs are discoverable
- evidence is separated from source
- raw sensitive data is excluded from Git
- the repository can scale to multiple operations

### B. Red Team methodology
Evaluate:
- authorization
- scope
- ROE
- threat model
- hypotheses
- test scenarios
- stop conditions
- safety controls
- reproducibility
- retesting
- after-action review

Map relevant concepts to established security practice where appropriate. Do not force a framework mapping where it does not add value.

### C. Network assessment model
Evaluate whether the architecture can represent:
- baseline
- DNS
- TLS
- HTTP/HTTPS
- TCP/UDP/QUIC
- traffic classification
- IPv4/IPv6
- accounting
- quota/policy
- monitoring/detection

Do not add unauthorized exploitation or stealth procedures.

### D. Evidence and forensics
Evaluate:
- timestamps
- evidence IDs
- hashes
- chain of custody
- external storage references
- evidence classification
- derived-artifact relationships
- reproducibility

### E. GitHub engineering
Evaluate:
- `AGENTS.md`
- nested agent instructions
- CODEOWNERS
- pull-request governance
- Dependabot
- secret protection
- code scanning
- CI
- issue templates
- release/versioning strategy
- branch/ruleset protection
- repository security

### F. AI-agent readiness
Evaluate whether an AI coding/security agent can:
- understand the project quickly
- locate source-of-truth documents
- know which files it may modify
- understand scope boundaries
- validate changes
- avoid hallucinating architecture
- avoid creating unsafe operational instructions

### G. Missing components
Identify missing:
- documents
- schemas
- configuration
- scripts
- tests
- CI
- evidence manifests
- dashboards
- runbooks
- approval records
- report templates

## Required output

Produce:

### 1. Executive assessment
A concise description of the current architecture and its main strengths/weaknesses.

### 2. Repository tree
Show the recommended final tree.

### 3. Gap analysis
Use:
`CRITICAL / HIGH / MEDIUM / LOW`

Do not use a numeric score or arbitrary ranking.

### 4. Required files
For every required file provide:
- path
- purpose
- owner
- dependencies
- whether it is source-of-truth

### 5. Agent instruction architecture
Recommend:
- root `AGENTS.md`
- nested `AGENTS.md` where needed
- when to use `AGENTS.override.md`
- what belongs in docs instead of AGENTS

### 6. GitHub configuration
Recommend concrete repository configuration for:
- protected main branch/ruleset
- CODEOWNERS
- Dependabot
- secret scanning/push protection
- code scanning
- pull-request requirements
- Actions permissions
- environments/secrets

### 7. CI/CD
Design a minimal CI pipeline that validates:
- Markdown
- YAML
- JSON
- shell scripts
- repository structure
- secret exposure
- links where practical

### 8. Operational architecture
Describe:
- command
- operators
- test clients
- network sensors
- evidence store
- SIEM/observability
- reporting
- communication

### 9. Data model
Define schemas for:
- operation
- scope
- scenario
- test
- telemetry
- evidence
- finding
- retest

### 10. Implementation plan
Give a phased implementation plan:
Phase 0 — repository bootstrap
Phase 1 — governance
Phase 2 — documentation
Phase 3 — schemas
Phase 4 — operational tooling
Phase 5 — scenarios
Phase 6 — telemetry/evidence
Phase 7 — reporting
Phase 8 — validation

For each phase identify exact files to create/change.

## Constraints

- Do not invent authorization.
- Do not recommend hiding activity from a provider.
- Do not provide anti-forensics or attribution-evasion instructions.
- Do not include production exploitation recipes.
- Prefer controlled test environments and authorized test accounts.
- Never place real credentials or sensitive raw evidence in Git.
- Preserve auditability.
- Keep AGENTS.md concise; use `docs/` as the knowledge base.
- Do not modify files until the analysis and proposed change set are explicit.

## Final requirement

End with:

1. `CURRENT_STATE`
2. `TARGET_STATE`
3. `GAPS`
4. `FILES_TO_CREATE`
5. `FILES_TO_MODIFY`
6. `FILES_TO_DELETE`
7. `VALIDATION_PLAN`
8. `RISKS`
9. `OPEN_QUESTIONS`

Do not merely praise the repository. Find structural problems and propose concrete fixes.
