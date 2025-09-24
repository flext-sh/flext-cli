"""Test coverage for __main__.py module execution."""

import subprocess
import sys
from pathlib import Path

from flext_cli import main


def test_main_module_execution() -> None:
    """Test that __main__.py can be executed as a module."""
    # Test running the module directly
    result = subprocess.run(
        [sys.executable, "-m", "flext_cli", "--help"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    # Should not crash, even if it shows help
    assert result.returncode in {0, 2}  # 0 for success, 2 for help shown


def test_main_function_exists() -> None:
    """Test that main function exists and can be imported."""
    assert callable(main)
