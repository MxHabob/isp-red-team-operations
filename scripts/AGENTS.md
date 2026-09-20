# Scripts — Utility and Validation Scripts

## Responsibility
Repository validation, schema validation, secret scanning, evidence verification, and bootstrap utilities.

## Rules
- Scripts must be safe to run without network access.
- Validation scripts must return non-zero exit code on failure.
- Never execute network operations from validation scripts.
- Use `pathlib` for path handling — avoid shell injection via string formatting.
