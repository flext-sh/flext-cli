"""Tests for flext_cli.testing module."""

from flext_cli.testing import FlextCliTesting


class TestFlextCliTesting:
    """Test FlextCliTesting class."""

    def test_test_runner_creation(self) -> None:
        """Test test runner instance creation."""
        test_runner = FlextCliTesting()
        assert isinstance(test_runner, FlextCliTesting)

    def test_test_runner_execute(self) -> None:
        """Test test runner execute method."""
        test_runner = FlextCliTesting()
        result = test_runner.execute()
        assert result.is_success

    def test_test_runner_methods(self) -> None:
        """Test test runner methods exist."""
        test_runner = FlextCliTesting()

        # Test that test runner methods exist
        assert hasattr(test_runner, "run_tests")
        assert hasattr(test_runner, "run_unit_tests")
        assert hasattr(test_runner, "run_integration_tests")
        assert hasattr(test_runner, "generate_test_report")
