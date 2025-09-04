"""Basic tests for flext-cli."""

from flext_cli import FlextCliConfig


def test_imports() -> None:
    """Test that basic imports work."""
    config = FlextCliConfig()
    assert config.project_name == "flext-cli"


def test_config_creation() -> None:
    """Test that config creation works."""
    config = FlextCliConfig()
    result = config.ensure_setup()
    assert result.is_success
