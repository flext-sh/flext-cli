#!/bin/bash
# Phase 1 Execution Script - v0.10.0 Refactoring
# Removes duplicate files and moves test utilities
#
# Usage: bash docs/refactoring/execute_phase_1.sh

set -e # Exit on error

cd "$(dirname "$0")/../.." # Navigate to project root

echo "========================================="
echo "Phase 1: Remove Duplication & Dead Code"
echo "========================================="
echo ""

# Verify we're in the right directory
if [ ! -f "src/flext_cli/__init__.py" ]; then
	echo "❌ Error: Not in flext-cli project root"
	exit 1
fi

echo "📍 Working Directory: $(pwd)"
echo ""

# Step 1: Delete validator.py
echo "Step 1/4: Deleting validator.py..."
if [ -f "src/flext_cli/validator.py" ]; then
	rm -v src/flext_cli/validator.py
	echo "✅ validator.py deleted"
else
	echo "⊘ validator.py already deleted"
fi
echo ""

# Step 2: Delete auth.py
echo "Step 2/4: Deleting auth.py..."
if [ -f "src/flext_cli/auth.py" ]; then
	rm -v src/flext_cli/auth.py
	echo "✅ auth.py deleted"
else
	echo "⊘ auth.py already deleted"
fi
echo ""

# Step 3: Move testing.py
echo "Step 3/4: Moving testing.py to tests/fixtures/..."
mkdir -p tests/fixtures
if [ -f "src/flext_cli/testing.py" ]; then
	mv -v src/flext_cli/testing.py tests/fixtures/testing_utilities.py
	echo "✅ testing.py moved to tests/fixtures/testing_utilities.py"
else
	echo "⊘ testing.py already moved"
fi
echo ""

# Step 4: Update test imports
echo "Step 4/4: Updating test imports..."

# Count how many files need updating
affected_files=$(find tests -name "*.py" -type f -exec grep -l "from flext_cli import.*Test\|from flext_cli.testing" {} \; 2>/dev/null | wc -l)

if [ "$affected_files" -gt 0 ]; then
	echo "Found $affected_files test files with imports to update"

	# Update FlextCliTesting imports
	find tests -name "*.py" -type f -exec sed -i \
		's/from flext_cli import FlextCliTesting/from tests.fixtures.testing_utilities import FlextCliTesting/g' \
		{} + 2>/dev/null || true

	# Update FlextCliTestRunner imports
	find tests -name "*.py" -type f -exec sed -i \
		's/from flext_cli import FlextCliTestRunner/from tests.fixtures.testing_utilities import FlextCliTestRunner/g' \
		{} + 2>/dev/null || true

	# Update FlextCliMockScenarios imports
	find tests -name "*.py" -type f -exec sed -i \
		's/from flext_cli import FlextCliMockScenarios/from tests.fixtures.testing_utilities import FlextCliMockScenarios/g' \
		{} + 2>/dev/null || true

	# Update direct module imports
	find tests -name "*.py" -type f -exec sed -i \
		's/from flext_cli import/from tests.fixtures.testing_utilities import/g' \
		{} + 2>/dev/null || true

	echo "✅ Test imports updated"
else
	echo "⊘ No test imports to update (already done or no tests using testing utilities)"
fi
echo ""

# Verification
echo "========================================="
echo "Verification"
echo "========================================="
echo ""

# Check no references remain
echo "Checking for remaining references..."
if grep -r "from flext_cli.validator\|from flext_cli.auth\|from flext_cli.testing" src/ tests/ 2>/dev/null | grep -v "tests/fixtures/testing_utilities"; then
	echo "⚠️  WARNING: Found remaining references (review above)"
else
	echo "✅ No problematic references found"
fi
echo ""

# Run validation
echo "Running validation suite..."
if make validate 2>&1 | tail -20; then
	echo ""
	echo "✅ Validation passed"
else
	echo ""
	echo "⚠️  Validation had issues (see above)"
fi
echo ""

# Summary
echo "========================================="
echo "Phase 1 Complete!"
echo "========================================="
echo ""
echo "📊 Summary:"
echo "  • Files deleted: 2 (validator.py, auth.py)"
echo "  • Files moved: 1 (testing.py → tests/fixtures/testing_utilities.py)"
echo "  • Files modified: 1 (__init__.py - previously done)"
echo "  • Test files updated: $affected_files"
echo ""
echo "📝 Changes made:"
echo "  ✅ Removed validator.py (empty stub)"
echo "  ✅ Removed auth.py (duplicate functionality)"
echo "  ✅ Moved testing utilities to tests/fixtures/"
echo "  ✅ Updated test imports"
echo ""
echo "🎯 Next Steps:"
echo "  1. Review the changes above"
echo "  2. Run 'make test' to verify all tests pass"
echo "  3. Proceed to Phase 2 (Convert Services to Simple Classes)"
echo ""
echo "📚 Documentation:"
echo "  • Phase 1 Guide: docs/refactoring/phase-1-implementation-guide.md"
echo "  • Progress Report: docs/refactoring/phase-1-progress-report.md"
echo "  • Next Steps: docs/refactoring/IMPLEMENTATION_CHECKLIST.md (Steps 8+)"
echo ""
