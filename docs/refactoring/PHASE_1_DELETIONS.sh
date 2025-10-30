#!/bin/bash
# Phase 1 File Deletions for v0.10.0 Refactoring
# Run this script after reviewing the changes

set -e

echo "=== Phase 1: File Deletions ==="
echo ""

# Step 4: Delete validator.py (empty stub)
echo "Step 4: Deleting validator.py..."
if [ -f "src/flext_cli/validator.py" ]; then
	rm src/flext_cli/validator.py
	echo "✓ Deleted src/flext_cli/validator.py"
else
	echo "⊘ File already deleted: src/flext_cli/validator.py"
fi

# Step 5: Delete auth.py (duplicate module)
echo ""
echo "Step 5: Deleting auth.py..."
if [ -f "src/flext_cli/auth.py" ]; then
	rm src/flext_cli/auth.py
	echo "✓ Deleted src/flext_cli/auth.py"
else
	echo "⊘ File already deleted: src/flext_cli/auth.py"
fi

echo ""
echo "=== Verification ==="
echo "Checking for remaining references..."

# Verify no imports remain
if grep -r "from flext_cli.validator" . --exclude-dir=docs 2>/dev/null; then
	echo "⚠ WARNING: Found references to validator module!"
	exit 1
fi

if grep -r "from flext_cli.auth" . --exclude-dir=docs 2>/dev/null; then
	echo "⚠ WARNING: Found references to auth module!"
	exit 1
fi

echo "✓ No problematic references found"
echo ""
echo "=== Phase 1 Deletions Complete ==="
echo "Next: Run 'make validate' to verify"
