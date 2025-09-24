"""Simple test coverage for FlextCliUtilities module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from pathlib import Path

from flext_cli import FlextCliUtilities


class TestFlextCliUtilitiesSimple:
    """Test FlextCliUtilities class with existing methods only."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.utils = FlextCliUtilities()

    def test_utilities_initialization(self) -> None:
        """Test utilities initialization."""
        utils = FlextCliUtilities()
        assert utils is not None
        assert hasattr(utils, "_container")
        assert hasattr(utils, "_logger")

    def test_execute(self) -> None:
        """Test execute method."""
        result = self.utils.execute()
        assert result.is_success
        assert result.value is None

    def test_logger_property(self) -> None:
        """Test logger property."""
        logger = self.utils.logger
        assert logger is not None

    def test_container_property(self) -> None:
        """Test container property."""
        container = self.utils.container
        assert container is not None

    def test_get_base_config_dict(self) -> None:
        """Test get base config dict."""
        config = FlextCliUtilities.get_base_config_dict()
        assert config is not None
        assert isinstance(config, dict)

    def test_get_strict_config_dict(self) -> None:
        """Test get strict config dict."""
        config = FlextCliUtilities.get_strict_config_dict()
        assert config is not None
        assert isinstance(config, dict)

    def test_home_path(self) -> None:
        """Test home path."""
        path = FlextCliUtilities.home_path()
        assert isinstance(path, Path)
        assert path.is_absolute()

    def test_token_file_path(self) -> None:
        """Test token file path."""
        path = FlextCliUtilities.token_file_path()
        assert isinstance(path, Path)
        assert path.name == "token.json"

    def test_refresh_token_file_path(self) -> None:
        """Test refresh token file path."""
        path = FlextCliUtilities.refresh_token_file_path()
        assert isinstance(path, Path)
        assert path.name == "refresh_token.json"

    def test_get_settings_config_dict(self) -> None:
        """Test get settings config dict."""
        config = FlextCliUtilities.get_settings_config_dict()
        assert config is not None
        assert isinstance(config, dict)
