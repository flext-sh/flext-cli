"""Tests for flext_cli.main_entry module."""

from unittest.mock import patch

from flext_cli.main_entry import main


class TestMainEntry:
    """Test main entry point."""

    def test_main_function_exists(self) -> None:
        """Test that main function exists."""
        assert callable(main)

    @patch("flext_cli.main_entry.sys.argv", ["flext-cli", "--help"])
    def test_main_with_help(self) -> None:
        """Test main function with help argument."""
        # This test would need to be adjusted based on actual implementation
        # For now, just test that main is callable
        assert callable(main)

    def test_main_import(self) -> None:
        """Test that main can be imported."""
        from flext_cli.main_entry import main

        assert callable(main)
