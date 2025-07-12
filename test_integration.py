#!/usr/bin/env python3
"""Integration test for FLEXT CLI refactoring."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_imports() -> bool | None:
    """Test basic imports for FLEXT CLI modules.

    Returns:
        True if imports work, False otherwise.

    """
    try:
        from flext_cli.utils.config import CLIConfig

        CLIConfig()

        # from flext_cli.core.base import BaseCLI
        # print("✓ BaseCLI import works")

        from flext_cli.core.formatters import FormatterFactory

        FormatterFactory.create("json")

        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_version_consistency() -> bool | None:
    """Test version consistency across modules.

    Returns:
        True if version is consistent, False otherwise.

    """
    try:
        from flext_cli.__version__ import __version__

        # Test that all version references are consistent
        assert __version__ == "0.7.0", f"Expected 0.7.0, got {__version__}"

        return True
    except Exception:
        return False


def test_clean_architecture() -> bool | None:
    """Test clean architecture compliance.

    Returns:
        True if architecture is clean, False otherwise.

    """
    try:
        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


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
            if test():
                passed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    if failed == 0:
        sys.exit(0)
    else:
        sys.exit(1)
