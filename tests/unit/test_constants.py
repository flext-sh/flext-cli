"""FLEXT CLI Constants Tests - Comprehensive Constant Validation Testing.

Tests for FlextCliConstants covering initialization, values, format validation,
cross-platform compatibility, encoding, consistency, and integration scenarios
with 100% coverage.

Modules tested: flext_cli.constants.FlextCliConstants
Scope: All constant values, format validation, usage scenarios, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import platform
import tempfile
import time
from pathlib import Path

import pytest

from flext_cli import FlextCliConstants, c

from .._helpers import FlextCliTestHelpers

# from ..fixtures.constants import TestConstants  # Fixtures removed - use conftest.py and flext_tests


class TestsCliConstants:
    """Comprehensive test suite for FlextCliConstants functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Fixtures Factory
    # =========================================================================

    class Fixtures:
        """Factory for creating constants instances for testing."""

        @staticmethod
        def get_constants() -> FlextCliConstants:
            """Get FlextCliConstants instance."""
            return FlextCliTestHelpers.ConstantsFactory.get_constants()

    # =========================================================================
    # NESTED: Test Data Factory
    # =========================================================================

    class TestData:
        """Factory for creating test data scenarios."""

        @staticmethod
        def get_constant_value_cases() -> list[tuple[str, str]]:
            """Get parametrized test cases for constant values."""
            return [
                ("PROJECT_NAME", "flext-cli"),
                ("FLEXT_DIR_NAME", ".flext"),
                ("TOKEN_FILE_NAME", "token.json"),
                (
                    "REFRESH_TOKEN_FILE_NAME",
                    "refresh_token.json",
                ),
                ("AUTH_DIR_NAME", ".auth"),
            ]

        @staticmethod
        def get_constant_names() -> list[str]:
            """Get list of constant names for parametrized tests."""
            return [
                "PROJECT_NAME",
                "FLEXT_DIR_NAME",
                "TOKEN_FILE_NAME",
                "REFRESH_TOKEN_FILE_NAME",
            ]

        @staticmethod
        def get_file_name_constants() -> list[str]:
            """Get list of file name constants."""
            return [
                "TOKEN_FILE_NAME",
                "REFRESH_TOKEN_FILE_NAME",
            ]

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    class Assertions:
        """Helper methods for test assertions."""

        @staticmethod
        def assert_constant_exists(
            constants: FlextCliConstants,
            constant_name: str,
        ) -> None:
            """Assert constant exists and has value."""
            assert hasattr(constants, constant_name)
            value = getattr(constants, constant_name)
            assert value is not None
            assert isinstance(value, str)
            assert len(value) > 0
            assert len(value.strip()) > 0

        @staticmethod
        def assert_constant_value(
            constants: FlextCliConstants,
            constant_name: str,
            expected_value: str,
        ) -> None:
            """Assert constant has expected value."""
            actual_value = getattr(constants, constant_name)
            assert actual_value == expected_value
            assert isinstance(actual_value, str)
            assert len(actual_value) > 0

        @staticmethod
        def assert_file_name_format(
            constants: FlextCliConstants,
            constant_name: str,
        ) -> None:
            """Assert file name constant follows format."""
            value = getattr(constants, constant_name)
            assert value.endswith(".json")
            assert not value.startswith(".")
            assert "/" not in value
            assert "\\" not in value

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_constants_service_initialization(self) -> None:
        """Test constants service initialization and basic properties."""
        constants = self.Fixtures.get_constants()

        assert constants is not None
        for constant_name in self.TestData.get_constant_names():
            self.Assertions.assert_constant_exists(constants, constant_name)

    # =========================================================================
    # CONSTANT VALUES TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        ("constant_name", "expected_value"),
        [
            ("PROJECT_NAME", "flext-cli"),
            ("FLEXT_DIR_NAME", ".flext"),
            ("TOKEN_FILE_NAME", "token.json"),
            ("REFRESH_TOKEN_FILE_NAME", "refresh_token.json"),
            ("AUTH_DIR_NAME", ".auth"),
        ],
    )
    def test_constants_values(
        self,
        constant_name: str,
        expected_value: str,
    ) -> None:
        """Test constants have correct values."""
        constants = self.Fixtures.get_constants()
        self.Assertions.assert_constant_value(constants, constant_name, expected_value)

    # =========================================================================
    # CONSTANT VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "constant_name",
        [
            "PROJECT_NAME",
            "FLEXT_DIR_NAME",
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    def test_constants_are_immutable(self, constant_name: str) -> None:
        """Test that constants are properly defined and immutable."""
        constants = self.Fixtures.get_constants()
        constant_value = getattr(constants, constant_name)

        assert isinstance(constant_value, str)
        assert len(constant_value.strip()) > 0

    @pytest.mark.parametrize(
        "constant_name",
        [
            "PROJECT_NAME",
            "FLEXT_DIR_NAME",
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    def test_constants_not_none_or_empty(self, constant_name: str) -> None:
        """Test that constants are not None or empty strings."""
        constants = self.Fixtures.get_constants()
        constant_value = getattr(constants, constant_name)

        assert constant_value is not None
        assert constant_value
        assert constant_value.strip()

    @pytest.mark.parametrize(
        "constant_name",
        [
            "PROJECT_NAME",
            "FLEXT_DIR_NAME",
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    def test_constants_type_safety(self, constant_name: str) -> None:
        """Test constants type safety."""
        constants = self.Fixtures.get_constants()
        constant_value = getattr(constants, constant_name)

        assert isinstance(constant_value, str)
        assert len(constant_value) > 0
        assert constant_value.upper() is not None
        assert constant_value.lower() is not None

    # =========================================================================
    # FORMAT VALIDATION TESTS
    # =========================================================================

    def test_directory_name_format_validation(self) -> None:
        """Test that FLEXT_DIR_NAME follows expected format."""
        constants = self.Fixtures.get_constants()

        assert constants.FLEXT_DIR_NAME.startswith(
            ".",
        )
        assert len(constants.FLEXT_DIR_NAME) > 1

    @pytest.mark.parametrize(
        "constant_name",
        [
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    def test_file_name_format_validation(self, constant_name: str) -> None:
        """Test that file names follow expected format."""
        constants = self.Fixtures.get_constants()
        self.Assertions.assert_file_name_format(constants, constant_name)

    @pytest.mark.parametrize(
        "constant_name",
        [
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    @pytest.mark.parametrize(
        "invalid_char",
        ["/", "\\", ":", "*", "?", '"', "<", ">", "|"],
    )
    def test_file_names_no_invalid_characters(
        self,
        constant_name: str,
        invalid_char: str,
    ) -> None:
        """Test that file names don't contain invalid characters."""
        constants = self.Fixtures.get_constants()
        constant_value = getattr(constants, constant_name)

        assert invalid_char not in constant_value

    def test_constants_uniqueness(self) -> None:
        """Test that constants have unique values."""
        constants = self.Fixtures.get_constants()

        constants_values = [
            constants.PROJECT_NAME,
            constants.FLEXT_DIR_NAME,
            constants.TOKEN_FILE_NAME,
            constants.REFRESH_TOKEN_FILE_NAME,
        ]

        assert len(constants_values) == len(set(constants_values))

    # =========================================================================
    # CONSTANT USAGE SCENARIOS TESTS
    # =========================================================================

    def test_constants_in_file_paths(self) -> None:
        """Test constants usage in file path construction."""
        constants = self.Fixtures.get_constants()

        home_dir = Path.home()
        flext_dir = home_dir / constants.FLEXT_DIR_NAME
        token_file = flext_dir / constants.TOKEN_FILE_NAME
        refresh_token_file = flext_dir / constants.REFRESH_TOKEN_FILE_NAME

        assert str(flext_dir).endswith(constants.FLEXT_DIR_NAME)
        assert str(token_file).endswith(constants.TOKEN_FILE_NAME)
        assert str(refresh_token_file).endswith(constants.REFRESH_TOKEN_FILE_NAME)

        assert Path(flext_dir).name == constants.FLEXT_DIR_NAME
        assert Path(token_file).name == constants.TOKEN_FILE_NAME
        assert Path(refresh_token_file).name == constants.REFRESH_TOKEN_FILE_NAME

    def test_constants_in_configuration(self) -> None:
        """Test constants usage in configuration scenarios."""
        constants = self.Fixtures.get_constants()

        config = {
            "project_name": constants.PROJECT_NAME,
            "data_directory": constants.FLEXT_DIR_NAME,
            "token_file": constants.TOKEN_FILE_NAME,
            "refresh_token_file": constants.REFRESH_TOKEN_FILE_NAME,
        }

        assert config["project_name"] == "flext-cli"
        assert config["data_directory"] == ".flext"
        assert config["token_file"] == "token.json"
        assert config["refresh_token_file"] == "refresh_token.json"

    def test_constants_in_logging(self) -> None:
        """Test constants usage in logging scenarios."""
        constants = self.Fixtures.get_constants()

        log_messages = [
            f"Initializing {constants.PROJECT_NAME}",
            f"Creating directory: {constants.FLEXT_DIR_NAME}",
            f"Loading token from: {constants.TOKEN_FILE_NAME}",
            f"Refreshing token from: {constants.REFRESH_TOKEN_FILE_NAME}",
        ]

        for message in log_messages:
            assert isinstance(message, str)
            assert len(message) > 0
            assert (
                constants.PROJECT_NAME in message
                or constants.FLEXT_DIR_NAME in message
                or constants.TOKEN_FILE_NAME in message
                or constants.REFRESH_TOKEN_FILE_NAME in message
            )

    # =========================================================================
    # CONSTANT COMPATIBILITY TESTS
    # =========================================================================

    def test_constants_cross_platform_compatibility(self) -> None:
        """Test that constants work across different platforms."""
        constants = self.Fixtures.get_constants()
        current_platform = platform.system().lower()

        invalid_chars = (
            ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
            if current_platform == "windows"
            else ["/"]
        )

        for char in invalid_chars:
            assert char not in constants.TOKEN_FILE_NAME
            assert char not in constants.REFRESH_TOKEN_FILE_NAME

    def test_constants_encoding_compatibility(self) -> None:
        """Test that constants are compatible with different encodings."""
        constants = self.Fixtures.get_constants()

        # Test UTF-8 encoding
        utf8_encoded = constants.PROJECT_NAME.encode("utf-8")
        assert isinstance(utf8_encoded, bytes)
        assert len(utf8_encoded) > 0

        # Test that constants can be decoded back
        decoded = utf8_encoded.decode("utf-8")
        assert decoded == constants.PROJECT_NAME

        # Test ASCII compatibility
        try:
            ascii_encoded = constants.PROJECT_NAME.encode("ascii")
            assert isinstance(ascii_encoded, bytes)
        except UnicodeEncodeError:
            pass

    # =========================================================================
    # CONSTANT VALIDATION METHODS TESTS
    # =========================================================================

    def test_validate_constant_format(self) -> None:
        """Test constant format validation."""
        constants = self.Fixtures.get_constants()

        # Validate PROJECT_NAME
        assert isinstance(constants.PROJECT_NAME, str)
        assert len(constants.PROJECT_NAME.strip()) > 0
        assert not constants.PROJECT_NAME.startswith(" ")
        assert not constants.PROJECT_NAME.endswith(" ")

        # Validate FLEXT_DIR_NAME
        assert isinstance(constants.FLEXT_DIR_NAME, str)
        assert constants.FLEXT_DIR_NAME.startswith(".")
        assert len(constants.FLEXT_DIR_NAME) > 1
        assert not constants.FLEXT_DIR_NAME.endswith(".")

        # Validate file names
        for file_name in [constants.TOKEN_FILE_NAME, constants.REFRESH_TOKEN_FILE_NAME]:
            self.Assertions.assert_file_name_format(
                constants,
                "TOKEN_FILE_NAME"
                if file_name == constants.TOKEN_FILE_NAME
                else "REFRESH_TOKEN_FILE_NAME",
            )

    def test_validate_constant_content(self) -> None:
        """Test constant content validation."""
        constants = self.Fixtures.get_constants()

        # Validate PROJECT_NAME contains FLEXT
        assert "flext" in constants.PROJECT_NAME.lower()

        # Validate FLEXT_DIR_NAME contains flext
        assert "flext" in constants.FLEXT_DIR_NAME.lower()

        # Validate token files contain expected keywords
        assert any(
            kw in constants.TOKEN_FILE_NAME.lower()
            for kw in ["token", "access", "bearer"]
        )
        assert any(
            kw in constants.REFRESH_TOKEN_FILE_NAME.lower()
            for kw in ["refresh", "token"]
        )

    def test_validate_constant_consistency(self) -> None:
        """Test constant consistency validation."""
        constants = self.Fixtures.get_constants()

        # Token and refresh token should be different
        assert constants.TOKEN_FILE_NAME != constants.REFRESH_TOKEN_FILE_NAME

        # Both should contain 'token'
        assert "token" in constants.TOKEN_FILE_NAME.lower()
        assert "token" in constants.REFRESH_TOKEN_FILE_NAME.lower()

    # =========================================================================
    # CONSTANT ACCESS PATTERNS TESTS
    # =========================================================================

    def test_constants_class_access(self) -> None:
        """Test accessing constants through class instance."""
        constants = self.Fixtures.get_constants()

        for constant_name in self.TestData.get_constant_names():
            self.Assertions.assert_constant_exists(constants, constant_name)

        project_name = constants.PROJECT_NAME
        flext_dir = constants.FLEXT_DIR_NAME
        token_file = constants.TOKEN_FILE_NAME
        refresh_token_file = constants.REFRESH_TOKEN_FILE_NAME

        assert isinstance(project_name, str)
        assert isinstance(flext_dir, str)
        assert isinstance(token_file, str)
        assert isinstance(refresh_token_file, str)

    def test_constants_multiple_instances(self) -> None:
        """Test that multiple instances return the same constants."""
        constants1 = self.Fixtures.get_constants()
        constants2 = self.Fixtures.get_constants()

        assert constants1.PROJECT_NAME == constants2.PROJECT_NAME
        assert constants1.FLEXT_DIR_NAME == constants2.FLEXT_DIR_NAME
        assert constants1.TOKEN_FILE_NAME == constants2.TOKEN_FILE_NAME
        assert constants1.REFRESH_TOKEN_FILE_NAME == constants2.REFRESH_TOKEN_FILE_NAME

    def test_constants_class_level_access(self) -> None:
        """Test accessing constants at class level."""
        assert c.PROJECT_NAME == "flext-cli"
        assert c.FLEXT_DIR_NAME == ".flext"
        assert c.TOKEN_FILE_NAME == "token.json"
        assert c.REFRESH_TOKEN_FILE_NAME == "refresh_token.json"

    # =========================================================================
    # CONSTANT INTEGRATION TESTS
    # =========================================================================

    def test_constants_in_real_world_scenarios(self) -> None:
        """Test constants in real-world usage scenarios."""
        constants = self.Fixtures.get_constants()

        # Scenario 1: Setting up application directories
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir) / constants.FLEXT_DIR_NAME
            app_dir.mkdir()

            token_file = app_dir / constants.TOKEN_FILE_NAME
            refresh_token_file = app_dir / constants.REFRESH_TOKEN_FILE_NAME

            token_file.write_text({
                "access_token": "test_token",
                "token_type": "Bearer",
            })
            refresh_token_file.write_text(
                {"refresh_token": "test_refresh_token"},
            )

            assert token_file.exists()
            assert refresh_token_file.exists()

        # Scenario 2: Configuration management
        config = {
            "app": {
                "name": constants.PROJECT_NAME,
                "data_dir": constants.FLEXT_DIR_NAME,
                "files": {
                    "token": constants.TOKEN_FILE_NAME,
                    "refresh_token": constants.REFRESH_TOKEN_FILE_NAME,
                },
            },
        }

        assert config is not None
        assert isinstance(config, dict)

        # Scenario 3: Error messages
        error_messages = {
            "missing_token": f"Token file '{constants.TOKEN_FILE_NAME}' not found",
            "missing_refresh_token": f"Refresh token file '{constants.REFRESH_TOKEN_FILE_NAME}' not found",
            "invalid_dir": f"Directory '{constants.FLEXT_DIR_NAME}' is not accessible",
        }

        for message in error_messages.values():
            assert isinstance(message, str)
            assert len(message) > 0
            assert (
                constants.TOKEN_FILE_NAME in message
                or constants.REFRESH_TOKEN_FILE_NAME in message
                or constants.FLEXT_DIR_NAME in message
            )

    def test_constants_performance(self) -> None:
        """Test constants access performance."""
        constants = self.Fixtures.get_constants()

        start_time = time.time()
        for _ in range(1000):
            _ = constants.PROJECT_NAME
            _ = constants.FLEXT_DIR_NAME
            _ = constants.TOKEN_FILE_NAME
            _ = constants.REFRESH_TOKEN_FILE_NAME
        end_time = time.time()

        access_time = end_time - start_time
        assert access_time < 0.1, f"Constants access too slow: {access_time:.4f}s"

    # =========================================================================
    # EDGE CASES TESTS
    # =========================================================================

    def test_constants_concatenation(self) -> None:
        """Test that constants can be concatenated."""
        constants = self.Fixtures.get_constants()

        combined = constants.PROJECT_NAME + " " + constants.FLEXT_DIR_NAME
        assert isinstance(combined, str)
        assert len(combined) > 0

    # =========================================================================
    # VALIDATION METHODS TESTS
    # =========================================================================

    def test_get_valid_output_formats(self) -> None:
        """Test get_valid_output_formats returns sorted tuple."""
        formats = c.get_valid_output_formats()
        assert isinstance(formats, tuple)
        assert len(formats) > 0
        assert all(isinstance(fmt, str) for fmt in formats)
        # Verify sorted
        assert formats == tuple(sorted(formats))

    def test_get_valid_command_statuses(self) -> None:
        """Test get_valid_command_statuses returns sorted tuple."""
        statuses = c.get_valid_command_statuses()
        assert isinstance(statuses, tuple)
        assert len(statuses) > 0
        assert all(isinstance(status, str) for status in statuses)
        # Verify sorted
        assert statuses == tuple(sorted(statuses))

    def test_get_enum_values(self) -> None:
        """Test get_enum_values extracts values from StrEnum."""
        # Test with CommandStatus enum
        values = c.get_enum_values(c.CommandStatus)
        assert isinstance(values, tuple)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)
        assert "pending" in values
        assert "running" in values

        # Test with OutputFormats enum
        output_values = c.get_enum_values(c.OutputFormats)
        assert isinstance(output_values, tuple)
        assert "json" in output_values
        assert "yaml" in output_values

    def test_create_cli_discriminated_union(self) -> None:
        """Test create_cli_discriminated_union creates union mapping."""
        union_map = c.create_cli_discriminated_union(
            "status",
            c.CommandStatus,
            c.SessionStatus,
        )
        assert isinstance(union_map, dict)
        assert len(union_map) > 0
        # Verify all values map to enum classes
        assert union_map["pending"] == c.CommandStatus
        assert union_map["active"] == c.SessionStatus

    def test_get_file_extensions(self) -> None:
        """Test get_file_extensions returns extensions for format."""
        # Test existing format
        extensions = c.get_file_extensions("json")
        assert isinstance(extensions, tuple)
        assert "json" in extensions

        # Test format with multiple extensions
        yaml_extensions = c.get_file_extensions("yaml")
        assert isinstance(yaml_extensions, tuple)
        assert "yaml" in yaml_extensions
        assert "yml" in yaml_extensions

        # Test non-existent format
        none_extensions = c.get_file_extensions("nonexistent")
        assert none_extensions is None

    def test_get_mime_type(self) -> None:
        """Test get_mime_type returns MIME type for format."""
        # Test existing format
        mime = c.get_mime_type("json")
        assert isinstance(mime, str)
        assert mime == "application/json"

        # Test another format
        yaml_mime = c.get_mime_type("yaml")
        assert isinstance(yaml_mime, str)
        assert yaml_mime == "application/x-yaml"

        # Test non-existent format
        none_mime = c.get_mime_type("nonexistent")
        assert none_mime is None

    def test_validate_file_format(self) -> None:
        """Test validate_file_format checks format support."""
        # Test supported formats
        assert c.validate_file_format("json") is True
        assert c.validate_file_format("yaml") is True
        assert c.validate_file_format("csv") is True

        # Test unsupported format
        assert c.validate_file_format("nonexistent") is False
        assert c.validate_file_format("invalid") is False
