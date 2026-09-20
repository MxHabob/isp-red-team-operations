# Config — Configuration Schemas and Profiles

## Responsibility
JSON/YAML schemas for data validation, environment profiles, and example configurations.

## Rules
- Schemas are the authoritative definition for data structures.
- Never store real credentials in example configs.
- Profile configurations that contain secrets must use environment variable references.
