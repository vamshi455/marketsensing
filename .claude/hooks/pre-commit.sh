#!/bin/bash
# Pre-commit hook: lint and type-check before committing
set -e

echo "Running ruff check..."
ruff check src/ --fix

echo "Running ruff format..."
ruff format src/ --check

echo "Pre-commit checks passed."
