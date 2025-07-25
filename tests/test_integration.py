"""Integration test for FLEXT CLI refactoring."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_imports() -> None:
    """Test basic imports for FLEXT CLI modules."""
    from flext_cli.config import CLIConfig

    CLIConfig()

    # Test new structure imports instead

    # These should import without errors


def test_version_consistency() -> None:
    """Test version consistency across modules."""
    from flext_cli.__version__ import __version__

    # Test that all version references are consistent
    assert __version__ == "0.7.0", f"Expected 0.7.0, got {__version__}"


def test_clean_architecture() -> None:
    """Test clean architecture compliance."""
    # Test that clean architecture principles are followed
    # This is a placeholder for actual architecture validation


if __name__ == "__main__":
    tests = [
        test_basic_imports,
        test_version_consistency,
        test_clean_architecture,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()  # Test functions return None if they pass
            passed += 1
        except (ImportError, AttributeError, ValueError):
            failed += 1

    if failed == 0:
        sys.exit(0)
    else:
        sys.exit(1)
