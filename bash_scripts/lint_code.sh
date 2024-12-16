#!/bin/bash

set -e  # Fail on any error

# Navigate to repo root
SCRIPT_DIR=$(dirname "$0")
REPO_DIR=$(realpath "$SCRIPT_DIR/..")
cd "$REPO_DIR"

# Debugging: Log current directory
echo "Current working directory: $(pwd)"

# Check pylint installation
if ! command -v pylint &> /dev/null; then
  echo "pylint not found. Install it with 'pip install pylint'."
  exit 1
fi

# Debugging: Log all found .py files
echo "Identifying Python files..."
find . -path ./bash\* -prune -o -name "*.py" -print

# Run pylint on each file
echo "Running pylint..."
find . -path ./bash\* -prune -o -name "*.py" -print | while read -r file; do
  echo "Linting $file"
  pylint "$file" || exit 1
done

echo "Linting completed successfully!"
 