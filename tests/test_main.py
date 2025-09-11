"""Tests for __main__.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import flext_cli.__main__
from flext_cli.cli import main


class TestMainModule:
    """Test __main__.py entry point functionality."""

    def test_main_module_import(self) -> None:
        """Test that __main__ module can be imported."""
        # Import should work without errors
        assert flext_cli.__main__ is not None

    def test_main_module_execution(self) -> None:
        """Test execution via python -m flext_cli."""
        # Test that module can be executed (should show help and exit cleanly)
        result = subprocess.run(
            [sys.executable, "-m", "flext_cli", "--help"],
            check=False, cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should exit successfully
        assert result.returncode == 0
        # Should contain expected help content
        assert "FLEXT CLI" in result.stdout or "Usage:" in result.stdout

    def test_main_module_has_correct_imports(self) -> None:
        """Test that __main__ has correct imports."""
        # Should have access to main function
        assert hasattr(flext_cli.__main__, "main")

        # main should be callable
        assert callable(main)
