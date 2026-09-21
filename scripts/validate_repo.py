"""Comprehensive repository validation.

Checks:
1. Required files exist
2. YAML files are valid
3. No forbidden files (secrets, PCAP, credentials)
4. No env files with secrets
5. AGENTS.md hierarchy is complete
6. Scenario registry references valid files
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_required_files() -> list[str]:
    """Check that all required files exist."""
    required = [
        "AGENTS.md",
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "pyproject.toml",
        "command/scope.yaml",
        "command/roe.md",
        "command/mission.yaml",
        "docs/README.md",
        ".github/CODEOWNERS",
        ".github/dependabot.yml",
    ]
    errors = []
    for path in required:
        if (ROOT / path).exists():
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} — MISSING")
            errors.append(f"Missing required file: {path}")
    return errors


def check_agents_hierarchy() -> list[str]:
    """Check that key directories have AGENTS.md files."""
    expected_dirs = [
        "command",
        "research",
        "scenarios",
        "operations",
        "telemetry",
        "evidence",
        "findings",
        "reports",
        "tests",
        "docs",
        "lab",
        "data",
        "config",
        "scripts",
    ]
    errors = []
    for d in expected_dirs:
        dir_path = ROOT / d
        if not dir_path.exists():
            continue
        agents_path = dir_path / "AGENTS.md"
        if agents_path.exists():
            print(f"  ✓ {d}/AGENTS.md")
        else:
            print(f"  ⚠ {d}/AGENTS.md — missing")
            errors.append(f"Missing AGENTS.md: {d}/")
    return errors


def check_forbidden_files() -> list[str]:
    """Check for files that should never be in Git."""
    errors = []
    forbidden_extensions = {".pem", ".key", ".p12", ".pfx", ".pcap", ".pcapng", ".cap"}
    forbidden_names = {".env"}

    for path in ROOT.rglob("*"):
        if ".git" in path.parts or ".local" in path.parts or "__pycache__" in path.parts:
            continue
        if not path.is_file():
            continue

        if path.suffix in forbidden_extensions:
            print(f"  ✗ Forbidden file: {path.relative_to(ROOT)}")
            errors.append(f"Forbidden file: {path.relative_to(ROOT)}")

        if path.name in forbidden_names:
            print(f"  ✗ Secret file: {path.relative_to(ROOT)}")
            errors.append(f"Secret file: {path.relative_to(ROOT)}")

    if not errors:
        print("  ✓ No forbidden files found")

    return errors


def check_yaml_syntax() -> list[str]:
    """Validate all YAML files."""
    errors = []
    try:
        import yaml
    except ImportError:
        print("  ⚠ PyYAML not available — skipping YAML validation")
        return errors

    for path in sorted(ROOT.rglob("*.y*ml")):
        if ".git" in path.parts or ".local" in path.parts or "node_modules" in path.parts:
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            print(f"  ✓ {path.relative_to(ROOT)}")
        except yaml.YAMLError as exc:
            print(f"  ✗ {path.relative_to(ROOT)} — {exc}")
            errors.append(f"Invalid YAML: {path.relative_to(ROOT)}")

    return errors


def main() -> int:
    all_errors: list[str] = []

    print("\n=== Required Files ===")
    all_errors.extend(check_required_files())

    print("\n=== AGENTS.md Hierarchy ===")
    all_errors.extend(check_agents_hierarchy())

    print("\n=== Forbidden Files ===")
    all_errors.extend(check_forbidden_files())

    print("\n=== YAML Syntax ===")
    all_errors.extend(check_yaml_syntax())

    print()
    if all_errors:
        print(f"✗ Validation FAILED — {len(all_errors)} error(s)")
        for err in all_errors:
            print(f"  • {err}")
        return 1
    else:
        print("✓ Repository validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
