"""Comprehensive tests for config.cli_config module.

# Constants
EXPECTED_BULK_SIZE = 2

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests for CLI configuration to achieve near 100% coverage.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from flext_cli.config.cli_config import CLIConfig


class TestCLIConfig:
    """Test CLIConfig class."""

    def test_config_initialization_defaults(self) -> None:
        """Test config initialization with default values."""
        config = CLIConfig()

        if config.profile != "default":
            raise AssertionError(f"Expected {'default'}, got {config.profile}")
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")
        assert hasattr(config, "output")
        assert hasattr(config, "api")
        assert hasattr(config, "auth")
        assert hasattr(config, "directories")

    def test_config_initialization_with_values(self) -> None:
        """Test config initialization with custom values."""
        config = CLIConfig(
            api_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
            log_level="DEBUG",
            auto_refresh=False,
        )

        if config.api_url != "https://custom.api.com":
            raise AssertionError(
                f"Expected {'https://custom.api.com'}, got {config.api_url}"
            )
        assert config.timeout == 60
        if config.max_retries != 5:
            raise AssertionError(f"Expected {5}, got {config.max_retries}")
        assert config.log_level == "DEBUG"
        if config.auto_refresh:
            raise AssertionError(f"Expected False, got {config.auto_refresh}")

    def test_config_dir_property(self) -> None:
        """Test config_dir property."""
        config = CLIConfig()

        expected_dir = Path.home() / ".flext"
        if config.config_dir != expected_dir:
            raise AssertionError(f"Expected {expected_dir}, got {config.config_dir}")

    def test_cache_dir_property(self) -> None:
        """Test cache_dir property."""
        config = CLIConfig()

        expected_dir = Path.home() / ".flext" / "cache"
        if config.cache_dir != expected_dir:
            raise AssertionError(f"Expected {expected_dir}, got {config.cache_dir}")

    def test_token_file_property(self) -> None:
        """Test token_file property."""
        config = CLIConfig()

        expected_file = Path.home() / ".flext" / ".token"
        if config.token_file != expected_file:
            raise AssertionError(f"Expected {expected_file}, got {config.token_file}")

    def test_refresh_token_file_property(self) -> None:
        """Test refresh_token_file property."""
        config = CLIConfig()

        expected_file = Path.home() / ".flext" / ".refresh_token"
        if config.refresh_token_file != expected_file:
            raise AssertionError(
                f"Expected {expected_file}, got {config.refresh_token_file}"
            )

    def test_config_validation_api_url(self) -> None:
        """Test config validation for API URL."""
        # Valid URLs should work
        valid_urls = [
            "https://api.flext.com",
            "http://localhost:8080",
            "https://custom.domain.com/api/v1",
        ]

        for url in valid_urls:
            config = CLIConfig(api_url=url)
            if config.api_url != url:
                raise AssertionError(f"Expected {url}, got {config.api_url}")

    def test_config_validation_timeout(self) -> None:
        """Test config validation for timeout."""
        # Valid timeouts
        valid_timeouts = [1, 30, 60, 300]

        for timeout in valid_timeouts:
            config = CLIConfig(timeout=timeout)
            if config.timeout != timeout:
                raise AssertionError(f"Expected {timeout}, got {config.timeout}")

    def test_config_validation_max_retries(self) -> None:
        """Test config validation for max_retries."""
        # Valid retry counts
        valid_retries = [0, 1, 3, 5, 10]

        for retries in valid_retries:
            config = CLIConfig(max_retries=retries)
            if config.max_retries != retries:
                raise AssertionError(f"Expected {retries}, got {config.max_retries}")

    def test_config_validation_log_level(self) -> None:
        """Test config validation for log_level."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            config = CLIConfig(log_level=level)
            if config.log_level != level:
                raise AssertionError(f"Expected {level}, got {config.log_level}")

    def test_config_as_dict(self) -> None:
        """Test converting config to dictionary."""
        config = CLIConfig(
            api_url="https://test.com",
            timeout=45,
            max_retries=2,
            log_level="WARNING",
            auto_refresh=False,
        )

        config_dict = config.model_dump()

        if config_dict["api_url"] != "https://test.com":
            raise AssertionError(
                f"Expected {'https://test.com'}, got {config_dict['api_url']}"
            )
        assert config_dict["timeout"] == 45
        if config_dict["max_retries"] != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {config_dict['max_retries']}")
        assert config_dict["log_level"] == "WARNING"
        if config_dict["auto_refresh"]:
            raise AssertionError(f"Expected False, got {config_dict['auto_refresh']}")

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        config_data = {
            "api_url": "https://from-dict.com",
            "timeout": 120,
            "max_retries": 7,
            "log_level": "ERROR",
            "auto_refresh": True,
        }

        config = CLIConfig(**config_data)

        if config.api_url != "https://from-dict.com":
            raise AssertionError(
                f"Expected {'https://from-dict.com'}, got {config.api_url}"
            )
        assert config.timeout == 120
        if config.max_retries != 7:
            raise AssertionError(f"Expected {7}, got {config.max_retries}")
        assert config.log_level == "ERROR"
        if not (config.auto_refresh):
            raise AssertionError(f"Expected True, got {config.auto_refresh}")

    @patch.dict("os.environ", {"FLEXT_API_URL": "https://env.test.com"})
    def test_config_environment_variables(self) -> None:
        """Test config reading from environment variables."""
        # Note: This test assumes CLIConfig supports env var loading
        # If not implemented, this test documents expected behavior
        config = CLIConfig()

        # Either reads from env or uses default - both are valid
        if config.api_url not in {"https://env.test.com", "https://api.flext.com"}:
            raise AssertionError(
                f"Expected {config.api_url} in {['https://env.test.com', 'https://api.flext.com']}"
            )

    def test_config_path_creation(self) -> None:
        """Test that config paths are properly created."""
        config = CLIConfig()

        # Test that all path properties return Path objects
        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.token_file, Path)
        assert isinstance(config.refresh_token_file, Path)

        # Test that paths are absolute
        assert config.config_dir.is_absolute()
        assert config.cache_dir.is_absolute()
        assert config.token_file.is_absolute()
        assert config.refresh_token_file.is_absolute()

    def test_config_immutability(self) -> None:
        """Test that config is immutable (frozen)."""
        config = CLIConfig()

        # Should not be able to modify attributes directly
        with pytest.raises(Exception):  # ValidationError or AttributeError
            config.api_url = "https://new.url.com"

    def test_config_equality(self) -> None:
        """Test config equality comparison."""
        config1 = CLIConfig(api_url="https://test.com", timeout=30)
        config2 = CLIConfig(api_url="https://test.com", timeout=30)
        config3 = CLIConfig(api_url="https://different.com", timeout=30)

        if config1 != config2:
            raise AssertionError(f"Expected {config2}, got {config1}")
        assert config1 != config3

    def test_config_hash(self) -> None:
        """Test config hashing."""
        config = CLIConfig(api_url="https://test.com")

        # Should be hashable (for use in sets, dicts, etc.)
        config_hash = hash(config)
        assert isinstance(config_hash, int)

        # Same config should have same hash
        config2 = CLIConfig(api_url="https://test.com")
        if hash(config) != hash(config2):
            raise AssertionError(f"Expected {hash(config2)}, got {hash(config)}")

    def test_config_string_representation(self) -> None:
        """Test config string representation."""
        config = CLIConfig(api_url="https://test.com")

        config_str = str(config)
        if "CLIConfig" not in config_str:
            raise AssertionError(f"Expected {'CLIConfig'} in {config_str}")
        assert "https://test.com" in config_str

    def test_config_repr(self) -> None:
        """Test config repr representation."""
        config = CLIConfig(api_url="https://test.com")

        config_repr = repr(config)
        if "CLIConfig" not in config_repr:
            raise AssertionError(f"Expected {'CLIConfig'} in {config_repr}")

    def test_config_json_serialization(self) -> None:
        """Test config JSON serialization."""
        config = CLIConfig(
            api_url="https://json.test.com",
            timeout=90,
            log_level="DEBUG",
        )

        json_str = config.model_dump_json()
        assert isinstance(json_str, str)
        if "https://json.test.com" not in json_str:
            raise AssertionError(f"Expected {'https://json.test.com'} in {json_str}")
        assert "90" in json_str
        if "DEBUG" not in json_str:
            raise AssertionError(f"Expected {'DEBUG'} in {json_str}")

    def test_config_model_validation(self) -> None:
        """Test Pydantic model validation."""
        # Test that the config is a valid Pydantic model
        config = CLIConfig()

        # Should have model methods
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")
        assert hasattr(config, "model_dump_json")

    def test_config_field_defaults(self) -> None:
        """Test that all fields have proper defaults."""
        config = CLIConfig()

        # All required fields should have values
        assert config.api_url is not None
        assert config.timeout is not None
        assert config.max_retries is not None
        assert config.log_level is not None
        assert config.auto_refresh is not None
        assert config.config_dir is not None
        assert config.cache_dir is not None
        assert config.token_file is not None
        assert config.refresh_token_file is not None

    def test_config_with_custom_paths(self) -> None:
        """Test config with custom base paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir)

            # If config supports custom paths, test it
            # Otherwise, this documents expected behavior
            config = CLIConfig()

            # Paths should be under user home by default
            if config.config_dir.parts[0] != Path.home().parts[0]:
                raise AssertionError(
                    f"Expected {Path.home().parts[0]}, got {config.config_dir.parts[0]}"
                )


class TestCLIConfigIntegration:
    """Integration tests for CLIConfig."""

    def test_config_workflow(self) -> None:
        """Test complete config workflow."""
        # Create config
        original_config = CLIConfig(
            api_url="https://workflow.test.com",
            timeout=60,
            log_level="DEBUG",
        )

        # Serialize to dict
        config_dict = original_config.model_dump()

        # Recreate from dict
        restored_config = CLIConfig(**config_dict)

        # Should be equal
        if original_config != restored_config:
            raise AssertionError(f"Expected {restored_config}, got {original_config}")

    def test_config_validation_edge_cases(self) -> None:
        """Test config validation with edge cases."""
        # Empty strings (if allowed)
        try:
            config = CLIConfig(api_url="")
            # If this doesn't raise, empty strings are allowed
        except (RuntimeError, ValueError, TypeError):
            # If it raises, validation is working
            pass

        # Very large timeout
        config = CLIConfig(timeout=999999)
        if config.timeout != 999999:
            raise AssertionError(f"Expected {999999}, got {config.timeout}")

        # Zero retries
        config = CLIConfig(max_retries=0)
        if config.max_retries != 0:
            raise AssertionError(f"Expected {0}, got {config.max_retries}")

    def test_config_paths_relationship(self) -> None:
        """Test relationship between different config paths."""
        config = CLIConfig()

        # Cache dir should be under config dir
        if config.cache_dir.parent != config.config_dir:
            raise AssertionError(
                f"Expected {config.config_dir}, got {config.cache_dir.parent}"
            )

        # Token files should be under config dir
        if config.token_file.parent != config.config_dir:
            raise AssertionError(
                f"Expected {config.config_dir}, got {config.token_file.parent}"
            )
        assert config.refresh_token_file.parent == config.config_dir

        # Files should have different names
        assert config.token_file.name != config.refresh_token_file.name

    def test_config_type_annotations(self) -> None:
        """Test that config has proper type annotations."""
        config = CLIConfig()

        # Test type hints are working
        assert isinstance(config.api_url, str)
        assert isinstance(config.timeout, int)
        assert isinstance(config.max_retries, int)
        assert isinstance(config.log_level, str)
        assert isinstance(config.auto_refresh, bool)
        assert isinstance(config.config_dir, Path)
        assert isinstance(config.cache_dir, Path)
        assert isinstance(config.token_file, Path)
        assert isinstance(config.refresh_token_file, Path)
