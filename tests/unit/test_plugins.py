"""Tests for flext_cli.plugins module."""

from flext_cli.plugins import FlextCliPlugins


class TestFlextCliPlugins:
    """Test FlextCliPlugins class."""

    def test_plugin_system_creation(self) -> None:
        """Test plugin system instance creation."""
        plugin_system = FlextCliPlugins()
        assert isinstance(plugin_system, FlextCliPlugins)

    def test_plugin_system_execute(self) -> None:
        """Test plugin system execute method."""
        plugin_system = FlextCliPlugins()
        result = plugin_system.execute()
        assert result.is_success

    def test_plugin_management_methods(self) -> None:
        """Test plugin management methods exist."""
        plugin_system = FlextCliPlugins()

        # Test that plugin management methods exist
        assert hasattr(plugin_system, "discover_plugins")
        assert hasattr(plugin_system, "load_plugin")
        assert hasattr(plugin_system, "initialize_plugin")
        assert hasattr(plugin_system, "unload_plugin")
        assert hasattr(plugin_system, "get_loaded_plugins")
