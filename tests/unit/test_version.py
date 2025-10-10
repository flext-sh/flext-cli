"""Tests for flext_cli.__version__ module."""

from flext_cli import __version__, __version_info__


class TestFlextCliVersion:
    """Test flext_cli version module."""

    def test_version_string(self) -> None:
        """Test version string is available."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        # Should be in semver format (e.g., "2.0.0")
        assert "." in __version__

    def test_version_info_tuple(self) -> None:
        """Test version_info tuple."""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= 3
        # First three parts should be integers (major.minor.patch)
        for i in range(min(3, len(__version_info__))):
            part = __version_info__[i]
            assert isinstance(part, (int, str))

    def test_version_matches_info(self) -> None:
        """Test that __version__ string matches __version_info__ tuple."""
        version_parts = __version__.split(".")
        # Compare up to the length of version_info
        for i, info_part in enumerate(__version_info__[: len(version_parts)]):
            if isinstance(info_part, int):
                assert int(version_parts[i]) == info_part
            else:
                assert version_parts[i] == info_part
