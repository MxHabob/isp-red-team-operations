# Decision Log

| ID | Date | Decision | Rationale | Status |
|---|---|---|---|---|
| [ADR-001](decisions/ADR-001-data-isolation-evidence-storage.md) | 2026-09-21 | Git is source-of-truth for code/docs; raw evidence stays external | Prevent repository bloat and accidental exposure of sensitive data | accepted |
| [ADR-002](decisions/ADR-002-hierarchical-agents-navigation.md) | 2026-09-21 | Use AGENTS.md hierarchy as a map and keep detailed knowledge in docs/ | Better agent context, clear boundaries, and maintainability | accepted |
| [ADR-003](decisions/ADR-003-stable-structured-identifiers.md) | 2026-09-21 | Every artifact and experiment gets a stable regex-validated ID | Reproducibility, evidence correlation, and automated analysis | accepted |
| [ADR-004](decisions/ADR-004-process-centric-not-tool-centric.md) | 2026-09-21 | Process-centric architecture organized by operational lifecycle | Focus on auditable assessment program rather than ad-hoc tools | accepted |
| [ADR-005](decisions/ADR-005-hypothesis-driven-research.md) | 2026-09-21 | Hypothesis-driven research model for vulnerability verification | Scientifically test ISP controls rather than assuming free service | accepted |
| [ADR-006](decisions/ADR-006-lab-before-production.md) | 2026-09-21 | Strict lab-first testing policy before production validation | Ensure safety, zero collateral disruption, and controlled baseline | accepted |
