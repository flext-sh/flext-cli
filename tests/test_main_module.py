"""Basic tests for __main__.py module entry point.

Focus on real functionality testing to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


class TestMainModule:
    """Test __main__.py module entry point."""

    def test_main_module_import(self) -> None:
        """Test that __main__ module can be imported."""
        # Import the __main__ module to trigger coverage
        import flext_cli.__main__

        assert flext_cli.__main__ is not None

    def test_main_function_import(self) -> None:
        """Test that main function can be imported from __main__."""
        # This tests the import line in __main__.py
        from flext_cli.__main__ import main

        assert main is not None
        assert callable(main)

    def test_main_module_execution_help(self) -> None:
        """Test execution via python -m flext_cli --help."""
        # Test that module can be executed and shows help
        result = subprocess.run(
            [sys.executable, "-m", "flext_cli", "--help"],
            check=False,
            cwd=Path(__file__).parent.parent / "src",
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should exit successfully
        assert result.returncode == 0
        # Should contain expected help content
        assert (
            "FLEXT CLI" in result.stdout
            or "Usage:" in result.stdout
            or "usage:" in result.stdout
            or "help" in result.stdout.lower()
        )

    def test_main_module_has_name_main_guard(self) -> None:
        """Test that __main__.py has proper __name__ == '__main__' guard."""
        # Read the file content to verify structure
        main_file = Path(__file__).parent.parent / "src" / "flext_cli" / "__main__.py"
        content = main_file.read_text()

        # Should have the proper guard
        assert 'if __name__ == "__main__"' in content
        assert "main()" in content

    def test_main_module_direct_import_coverage(self) -> None:
        """Test importing __main__ module directly for coverage."""
        # This ensures the import statements in __main__.py are covered
        spec = importlib.util.spec_from_file_location(
            "flext_cli.__main__",
            Path(__file__).parent.parent / "src" / "flext_cli" / "__main__.py",
        )

        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Execute the module to cover the imports
            spec.loader.exec_module(module)
            assert module is not None
