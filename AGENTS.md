# AGENTS.md — ISP Red Team Operations

## Mission
This repository is the source of truth for a professional, auditable Red Team / security-assessment program focused on ISP network behavior, traffic classification, accounting, observability, and controlled adversary emulation.

## Operating principles
- Safety and authorization come before technical execution.
- Keep production-impacting activity out of the repository's default workflows.
- Prefer controlled test accounts, isolated infrastructure, reproducible experiments, and explicit approvals.
- Do not add instructions for evading attribution, hiding activity from a provider, bypassing authentication/accounting on production systems, or destroying evidence.
- Preserve evidence integrity and chain of custody.
- Never commit secrets, customer data, real credentials, or unredacted sensitive identifiers.

## Repository rules
- `docs/` is the system of record for project knowledge.
- `operations/` contains procedures and runbooks.
- `scenarios/` contains test designs, not uncontrolled exploit payloads.
- `evidence/` is metadata-only in Git; raw captures belong in controlled storage.
- `findings/` contains validated observations and remediation evidence.
- Every test must have a unique ID and explicit scope.
- Every material change must update the relevant documentation.
- Prefer small, reviewable commits.
- Use conventional commit style: `type(scope): summary`.
- Do not rewrite history after evidence has been committed unless the evidence repository is explicitly designated as disposable.

## AI-agent behavior
Before changing the repository:
1. Read this file.
2. Read `docs/README.md`, `docs/architecture.md`, and the applicable scenario/runbook.
3. Identify scope and safety constraints.
4. State assumptions when requirements are ambiguous.
5. Make the smallest coherent change.
6. Validate structure, links, YAML/JSON syntax, and tests/checks applicable to the change.
7. Summarize changed files and validation results.

## Security boundary
Detailed offensive actions are permitted only when they are explicitly scoped to owned or authorized systems and test infrastructure. If a requested change would facilitate stealth, anti-forensics, unauthorized access, production abuse, or evasion of monitoring, stop and replace it with an auditable, authorized alternative.

## Directory-specific instructions
Deeper `AGENTS.md` files may add stricter rules for their subtree.
