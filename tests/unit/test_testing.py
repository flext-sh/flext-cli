"""Tests for flext_cli.testing module."""

from flext_cli.testing import FlextCliTestRunner


class TestFlextCliTestRunner:
    """Test FlextCliTestRunner class."""

    def test_test_runner_creation(self) -> None:
        """Test test runner instance creation."""
        test_runner = FlextCliTestRunner()
        assert isinstance(test_runner, FlextCliTestRunner)

    def test_test_runner_execute(self) -> None:
        """Test test runner execute method."""
        test_runner = FlextCliTestRunner()
        result = test_runner.execute()
        assert result.is_success

    def test_test_runner_methods(self) -> None:
        """Test test runner methods exist."""
        test_runner = FlextCliTestRunner()

        # Test that test runner methods exist
        assert hasattr(test_runner, "run_tests")
        assert hasattr(test_runner, "run_unit_tests")
        assert hasattr(test_runner, "run_integration_tests")
        assert hasattr(test_runner, "generate_test_report")
