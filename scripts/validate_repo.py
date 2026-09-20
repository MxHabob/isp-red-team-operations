from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    "AGENTS.md",
    "README.md",
    "docs/architecture.md",
    "docs/mission.md",
    "docs/methodology.md",
    "command/scope.yaml",
    "command/roe.md",
    ".github/CODEOWNERS",
    ".github/dependabot.yml",
    "SECURITY.md",
]

missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    print("Missing required files:")
    print("\n".join(f"- {p}" for p in missing))
    sys.exit(1)

print("Repository structure validation: PASS")
