"""Basic tests for flext-cli."""

from flext_cli import CLISettings, setup_cli


def test_imports() -> None:
    """Test that basic imports work."""
    config = CLISettings()
    assert config.project_name == "flext-cli"


def test_setup_cli() -> None:
    """Test that setup_cli works."""
    result = setup_cli()
    assert result.success
