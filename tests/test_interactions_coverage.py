"""Tests for interactions.py module to increase coverage."""

from __future__ import annotations

from unittest.mock import Mock

from flext_cli import FlextCliInteractions


class TestFlextCliInteractionsCoverage:
    """Test FlextCliInteractions to increase coverage."""

    def test_interactions_initialization(self) -> None:
        """Test interactions initialization."""
        interactions = FlextCliInteractions()
        assert interactions is not None
        assert hasattr(interactions, "confirm")
        assert hasattr(interactions, "prompt")

    def test_interactions_with_console(self) -> None:
        """Test interactions with custom console."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        assert interactions.console == console

    def test_interactions_quiet_mode(self) -> None:
        """Test interactions in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        assert interactions.quiet is True

    def test_confirm_quiet_mode(self) -> None:
        """Test confirm in quiet mode."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.confirm("Test message", default=True)
        assert result.is_success
        assert result.value is True

    def test_confirm_quiet_mode_false_default(self) -> None:
        """Test confirm in quiet mode with false default."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.confirm("Test message", default=False)
        assert result.is_success
        assert result.value is False

    def test_prompt_quiet_mode_with_default(self) -> None:
        """Test prompt in quiet mode with default."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.value == "default_value"

    def test_prompt_quiet_mode_no_default(self) -> None:
        """Test prompt in quiet mode without default."""
        interactions = FlextCliInteractions(quiet=True)
        result = interactions.prompt("Test message")
        # Should fail because no default provided
        assert result.is_failure

    def test_print_status_info(self) -> None:
        """Test print_status with info."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_status("Test message", status="info")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_status_success(self) -> None:
        """Test print_status with success."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_status("Test message", status="success")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_status_warning(self) -> None:
        """Test print_status with warning."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_status("Test message", status="warning")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_status_error(self) -> None:
        """Test print_status with error."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_status("Test message", status="error")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_status_unknown(self) -> None:
        """Test print_status with unknown status."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_status("Test message", status="unknown")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_success(self) -> None:
        """Test print_success method."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_success("Success message")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_error(self) -> None:
        """Test print_error method."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_error("Error message")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_warning(self) -> None:
        """Test print_warning method."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_warning("Warning message")
        assert result.is_success
        console.print.assert_called_once()

    def test_print_info(self) -> None:
        """Test print_info method."""
        console = Mock()
        interactions = FlextCliInteractions(console=console)
        result = interactions.print_info("Info message")
        assert result.is_success
        console.print.assert_called_once()

    def test_create_progress(self) -> None:
        """Test create_progress method."""
        interactions = FlextCliInteractions()
        result = interactions.create_progress("Test progress")
        assert result.is_success
        assert result.value is not None

    def test_with_progress(self) -> None:
        """Test with_progress method."""
        interactions = FlextCliInteractions()
        items = [1, 2, 3]
        result = interactions.with_progress(items, "Processing")
        assert result.is_success
        assert result.value == items
