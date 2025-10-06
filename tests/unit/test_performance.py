"""Tests for flext_cli.performance module."""

from flext_cli.performance import FlextCliPerformance


class TestFlextCliPerformance:
    """Test FlextCliPerformance class."""

    def test_performance_creation(self) -> None:
        """Test performance instance creation."""
        performance = FlextCliPerformance()
        assert isinstance(performance, FlextCliPerformance)

    def test_performance_execute(self) -> None:
        """Test performance execute method."""
        performance = FlextCliPerformance()
        result = performance.execute()
        assert result.is_success

    def test_performance_optimization_methods(self) -> None:
        """Test performance optimization methods exist."""
        performance = FlextCliPerformance()

        # Test that optimization methods exist
        assert hasattr(performance, "optimize_memory")
        assert hasattr(performance, "optimize_cpu")
        assert hasattr(performance, "optimize_io")
        assert hasattr(performance, "get_performance_metrics")
