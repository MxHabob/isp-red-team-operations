# Command — Mission Control

## Responsibility
Mission definition, authorization, scope, rules of engagement, and approvals.

## Rules
- `scope.yaml` is the **authoritative** source for what is in scope.
- Never modify scope during active execution. Create a new scope version.
- Approvals must reference the scope they authorize.
- Do not add placeholder values that could be mistaken for real authorization.
- All placeholders must contain `REPLACE` or be clearly marked as templates.
