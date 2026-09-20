# ISP Red Team Operations

Professional repository scaffold for an auditable ISP/network security assessment and controlled adversary-emulation program.

## Status
Architecture and operating model are being established. No production attack workflow is enabled by default.

## Repository map

- `docs/` — architecture, mission, methodology, glossary, decision records
- `command/` — scope, rules of engagement, approvals, mission control
- `scenarios/` — controlled test scenarios
- `operations/` — runbooks and operator checklists
- `telemetry/` — schemas and collection specifications; raw telemetry is external
- `evidence/` — evidence manifests and integrity metadata; raw evidence is external
- `findings/` — finding records and remediation/retest records
- `reports/` — report templates and generated report metadata
- `scripts/` — safe local validation/bootstrap helpers
- `.github/` — repository governance and CI

## First setup

```bash
git init
git branch -M main
git add .
git commit -m "chore: initialize ISP red team operations repository"
```

Then configure GitHub repository settings:
- branch/ruleset protection
- required pull-request review
- CODEOWNERS
- Dependabot
- secret scanning / push protection where available
- code scanning where appropriate

GitHub documents these controls in its security and repository documentation.

## Important
This repository intentionally separates:
1. mission design,
2. execution procedures,
3. telemetry,
4. evidence,
5. findings,
6. reporting.

Do not put raw PCAPs, credentials, customer records, or production exports into Git.
