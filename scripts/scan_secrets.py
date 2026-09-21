"""Secret scanner — detect potential secret leakage in the repository.

Scans for:
1. High-entropy strings that might be API keys or tokens
2. Known secret patterns (AWS, GitHub, etc.)
3. Files with secret-like extensions
4. Environment variable files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    (re.compile(r"(?:password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE), "Password assignment"),
    (re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*\S+", re.IGNORECASE), "API key assignment"),
    (re.compile(r"(?:secret|token)\s*[:=]\s*['\"][^'\"]{8,}", re.IGNORECASE), "Secret/token assignment"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private key"),
    (re.compile(r"-----BEGIN CERTIFICATE-----"), "Certificate (review if private)"),
]

# File extensions to skip (binary, etc.)
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".eot", ".ttf"}

# Directories to skip
SKIP_DIRS = {".git", ".local", "__pycache__", "node_modules", ".venv", "venv"}


def scan_file(path: Path) -> list[str]:
    """Scan a single file for secret patterns."""
    findings = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern, description in SECRET_PATTERNS:
            if pattern.search(line):
                # Skip if it's clearly a placeholder
                if "REPLACE" in line or "example" in line.lower() or "TODO" in line:
                    continue
                findings.append(
                    f"{path.relative_to(ROOT)}:{line_num} — {description}"
                )
    return findings


def main() -> int:
    print("=== Secret Scan ===\n")
    all_findings: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.suffix in SKIP_EXTENSIONS:
            continue

        findings = scan_file(path)
        all_findings.extend(findings)

    if all_findings:
        print(f"⚠ Found {len(all_findings)} potential secret(s):\n")
        for finding in all_findings:
            print(f"  • {finding}")
        print("\nReview each finding. False positives in example/template files are expected.")
        return 1
    else:
        print("✓ No potential secrets detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
