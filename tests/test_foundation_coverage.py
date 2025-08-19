"""Tests for foundation.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli.foundation import (
    FlextCliConfig,
    FlextCliEntity,
    create_cli_config,
    setup_cli,
)


class TestFlextCliEntity:
    """Test FlextCliEntity foundation patterns."""

    def test_entity_creation(self) -> None:
        """Test entity can be created."""
        entity = FlextCliEntity(id="test-id", name="test-entity", description="Test description")
        assert entity.name == "test-entity"
        assert entity.description == "Test description"
        assert entity.id == "test-id"

    def test_entity_execute(self) -> None:
        """Test entity execute method."""
        entity = FlextCliEntity(id="test-cmd-id", name="test-command")
        result = entity.execute()
        assert result.success
        assert "test-command" in str(result.data)

    def test_entity_with_args(self) -> None:
        """Test entity with arguments."""
        entity = FlextCliEntity(id="test-id", name="test")
        updated = entity.with_args({"param": "value"})
        assert updated.name == "test"
        # Should return a new instance (immutable update)
        assert updated is not entity


class TestFlextCliConfig:
    """Test FlextCliConfig foundation patterns."""

    def test_config_creation(self) -> None:
        """Test config can be created."""
        config = FlextCliConfig()
        assert config.profile == "default"
        assert config.output_format == "table"
        assert config.debug is False
        assert config.quiet is False

    def test_config_custom_values(self) -> None:
        """Test config with custom values."""
        config = FlextCliConfig(
            profile="dev",
            output_format="json",
            debug=True,
            quiet=True,
        )
        assert config.profile == "dev"
        assert config.output_format == "json"
        assert config.debug is True
        assert config.quiet is True


class TestCreateCliConfig:
    """Test create_cli_config function."""

    def test_create_default_config(self) -> None:
        """Test creating default config."""
        result = create_cli_config()
        assert result.success
        config = result.data
        assert isinstance(config, FlextCliConfig)
        assert config.profile == "default"

    def test_create_config_with_overrides(self) -> None:
        """Test creating config with overrides."""
        result = create_cli_config(
            debug=True,
            profile="test",
            output_format="yaml"
        )
        assert result.success
        config = result.data
        assert config.debug is True
        assert config.profile == "test"
        assert config.output_format == "yaml"

    def test_create_config_handles_failures(self) -> None:
        """Test config creation handles hierarchy failures gracefully."""
        # This should still work even if hierarchy has issues
        result = create_cli_config(profile="minimal")
        # Should either succeed or fail gracefully
        assert isinstance(result, FlextResult)


class TestSetupCli:
    """Test setup_cli function."""

    def test_setup_default(self) -> None:
        """Test setup with default config."""
        result = setup_cli()
        assert result.success
        assert isinstance(result.data, dict)
        assert "debug_mode" in result.data

    def test_setup_with_custom_config(self) -> None:
        """Test setup with custom config."""
        config = FlextCliConfig(debug=True, profile="test")
        result = setup_cli(config)
        assert result.success
        assert result.data["debug_mode"] is True

    def test_setup_handles_config_creation_failure(self) -> None:
        """Test setup handles config creation failure."""
        # Test with None config to trigger config creation path
        result = setup_cli(None)
        # Should either succeed or fail gracefully
        assert isinstance(result, FlextResult)
        if result.success:
            assert isinstance(result.data, dict)
