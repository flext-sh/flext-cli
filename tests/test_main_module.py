"""Tests for flext_cli.__main__ module."""

from unittest.mock import MagicMock, patch

import pytest

from flext_cli.__main__ import main
from flext_cli.cli import FlextCli


class TestMainModule:
    """Test cases for main module."""

    @patch("flext_cli.__main__.FlextCli")
    def test_main_function(self, mock_flext_cli_class: MagicMock) -> None:
        """Test main function creates CLI and runs it."""
        # Setup mock
        mock_cli_instance = MagicMock()
        mock_flext_cli_class.return_value = mock_cli_instance

        # Call main function
        main()

        # Verify CLI was created and run_cli was called
        mock_flext_cli_class.assert_called_once()
        mock_cli_instance.run_cli.assert_called_once()

    @patch("flext_cli.__main__.FlextCli")
    def test_main_function_exception_handling(
        self, mock_flext_cli_class: MagicMock
    ) -> None:
        """Test main function handles exceptions."""
        # Setup mock to raise exception
        mock_cli_instance = MagicMock()
        mock_cli_instance.run_cli.side_effect = Exception("Test error")
        mock_flext_cli_class.return_value = mock_cli_instance

        # Call main function - should raise exception since there's no exception handling
        # in the current implementation
        with pytest.raises(Exception, match="Test error"):
            main()

        # Verify CLI was created and run_cli was called
        mock_flext_cli_class.assert_called_once()
        mock_cli_instance.run_cli.assert_called_once()

    def test_main_function_import(self) -> None:
        """Test that main function can be imported."""
        assert callable(main)

    @patch("flext_cli.__main__.FlextCli")
    def test_main_function_multiple_calls(
        self, mock_flext_cli_class: MagicMock
    ) -> None:
        """Test main function can be called multiple times."""
        # Setup mock
        mock_cli_instance = MagicMock()
        mock_flext_cli_class.return_value = mock_cli_instance

        # Call main function multiple times
        main()
        main()
        main()

        # Verify CLI was created and run_cli was called each time
        assert mock_flext_cli_class.call_count == 3
        assert mock_cli_instance.run_cli.call_count == 3

    def test_module_imports(self) -> None:
        """Test that module imports work correctly."""
        # Verify imports work
        assert main is not None
        assert FlextCli is not None

    @patch("flext_cli.__main__.FlextCli")
    def test_main_function_cli_initialization(
        self, mock_flext_cli_class: MagicMock
    ) -> None:
        """Test that main function properly initializes CLI."""
        # Setup mock
        mock_cli_instance = MagicMock()
        mock_flext_cli_class.return_value = mock_cli_instance

        # Call main function
        main()

        # Verify FlextCli was instantiated without arguments
        mock_flext_cli_class.assert_called_once_with()

        # Verify run_cli was called without arguments
        mock_cli_instance.run_cli.assert_called_once_with()

    def test_main_module_execution(self) -> None:
        """Test module execution when run as script."""
        # Import the module to trigger the if __name__ == "__main__" block
        # The module should be importable without errors
