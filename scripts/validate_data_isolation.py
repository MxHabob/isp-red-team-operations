"""Data isolation validation — verify no raw evidence or secrets are in Git."""

from __future__ import annotations

import sys
from pathlib import Path

# Safe terminal encoding setup for cross-platform support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]


def check_data_isolation() -> list[str]:
    """Verify data isolation rules."""
    errors = []

    # 1. No raw evidence directories in Git (except .gitignored ones)
    raw_dirs = ["evidence/raw", "telemetry/raw"]
    for d in raw_dirs:
        path = ROOT / d
        if path.exists() and any(path.iterdir()):
            errors.append(f"Raw data directory has content: {d}")

    # 2. No PCAP files anywhere
    for pcap in ROOT.rglob("*.pcap"):
        if ".git" not in str(pcap) and ".local" not in str(pcap):
            errors.append(f"PCAP file found: {pcap.relative_to(ROOT)}")
    for pcap in ROOT.rglob("*.pcapng"):
        if ".git" not in str(pcap) and ".local" not in str(pcap):
            errors.append(f"PCAPNG file found: {pcap.relative_to(ROOT)}")

    # 3. No credential files
    for ext in ("*.pem", "*.key", "*.p12", "*.pfx"):
        for f in ROOT.rglob(ext):
            if ".git" not in str(f) and ".local" not in str(f):
                errors.append(f"Credential file found: {f.relative_to(ROOT)}")

    # 4. No .env files (except .env.example)
    for env_file in ROOT.rglob(".env"):
        if ".git" not in str(env_file) and ".local" not in str(env_file):
            errors.append(f"Environment file found: {env_file.relative_to(ROOT)}")
    for env_file in ROOT.rglob(".env.*"):
        if ".git" not in str(env_file) and ".local" not in str(env_file):
            if env_file.name != ".env.example":
                errors.append(f"Environment file found: {env_file.relative_to(ROOT)}")

    # 5. Check that .gitignore blocks sensitive files
    gitignore = ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        required_patterns = ["*.pcap", "*.pem", "*.key", ".env", "evidence/raw/", ".local/"]
        for pattern in required_patterns:
            if pattern not in content:
                errors.append(f".gitignore missing pattern: {pattern}")

    return errors


def main() -> int:
    print("=== Data Isolation Validation ===\n")
    errors = check_data_isolation()

    if errors:
        print(f"[FAIL] Data isolation FAILED — {len(errors)} issue(s):\n")
        for err in errors:
            print(f"  * {err}")
        return 1
    else:
        print("[OK] Data isolation validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
