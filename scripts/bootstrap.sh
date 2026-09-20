#!/usr/bin/env bash
set -euo pipefail

git init
git branch -M main
python3 scripts/validate_repo.py
git status --short

echo "Repository bootstrap complete."
echo "Next: replace placeholders in command/scope.yaml and .github/CODEOWNERS."
