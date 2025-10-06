"""Tests for flext_cli.version module."""

from flext_cli.version import VERSION, FlextCliVersion


class TestFlextCliVersion:
    """Test FlextCliVersion class."""

    def test_version_creation(self) -> None:
        """Test version instance creation."""
        version = FlextCliVersion()
        assert isinstance(version, FlextCliVersion)

    def test_version_properties(self) -> None:
        """Test version properties."""
        version = FlextCliVersion()

        # Test that properties exist and are strings
        assert isinstance(version.version, str)
        assert isinstance(version.version_info, tuple)
        assert isinstance(version.title, str)
        assert isinstance(version.description, str)

    def test_current_classmethod(self) -> None:
        """Test current classmethod."""
        version = FlextCliVersion.current()
        assert isinstance(version, FlextCliVersion)

    def test_module_level_variables(self) -> None:
        """Test module-level variables."""
        assert isinstance(VERSION, FlextCliVersion)
        assert isinstance(VERSION.version, str)
        assert isinstance(VERSION.version_info, tuple)
