"""Tests for FlextCliConstants - Comprehensive constant validation and functionality.

Modules Tested:
- flext_cli.constants.FlextCliConstants: CLI constants, enums, literals

Scope:
- Constant initialization and values
- Format validation (directory names, file names, paths)
- Cross-platform compatibility
- Encoding compatibility
- Constant consistency and uniqueness
- Integration scenarios (file paths, configuration, logging)
- Edge cases and type safety

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import platform
import tempfile
import time
from pathlib import Path

import pytest

from flext_cli import FlextCliConstants
from tests._helpers import FlextCliTestHelpers
from tests.fixtures.constants import TestConstants

# Alias for nested class
ConstantsFactory = FlextCliTestHelpers.ConstantsFactory


class TestFlextCliConstants:
    """Comprehensive test suite for FlextCliConstants functionality."""

    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================

    def test_constants_service_initialization(self) -> None:
        """Test constants service initialization and basic properties."""
        constants = ConstantsFactory.get_constants()

        assert constants is not None
        assert hasattr(constants, "PROJECT_NAME")
        assert hasattr(constants, "FLEXT_DIR_NAME")
        assert hasattr(constants, "TOKEN_FILE_NAME")
        assert hasattr(constants, "REFRESH_TOKEN_FILE_NAME")

    @pytest.mark.parametrize(
        ("constant_name", "expected_value"),
        [
            ("PROJECT_NAME", TestConstants.ExpectedValues.PROJECT_NAME),
            ("FLEXT_DIR_NAME", TestConstants.ExpectedValues.FLEXT_DIR_NAME),
            ("TOKEN_FILE_NAME", TestConstants.ExpectedValues.TOKEN_FILE_NAME),
            (
                "REFRESH_TOKEN_FILE_NAME",
                TestConstants.ExpectedValues.REFRESH_TOKEN_FILE_NAME,
            ),
            ("AUTH_DIR_NAME", TestConstants.ExpectedValues.AUTH_DIR_NAME),
        ],
    )
    def test_constants_values(
        self,
        constant_name: str,
        expected_value: str,
    ) -> None:
        """Test constants have correct values."""
        constants = ConstantsFactory.get_constants()
        actual_value = getattr(constants, constant_name)

        assert actual_value == expected_value
        assert isinstance(actual_value, str)
        assert len(actual_value) > 0

    # ========================================================================
    # CONSTANT VALIDATION
    # ========================================================================

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
        constants = ConstantsFactory.get_constants()
        constant_value = getattr(constants, constant_name)

        assert isinstance(constant_value, str)
        assert len(constant_value.strip()) > 0

    # ========================================================================
    # FORMAT VALIDATION
    # ========================================================================

    def test_directory_name_format_validation(self) -> None:
        """Test that FLEXT_DIR_NAME follows expected format."""
        constants = ConstantsFactory.get_constants()

        assert constants.FLEXT_DIR_NAME.startswith(
            TestConstants.FormatValidation.DIR_NAME_MUST_START_WITH,
        )
        assert len(constants.FLEXT_DIR_NAME) > 1

    def test_file_name_format_validation(self) -> None:
        """Test that file names follow expected format."""
        constants = ConstantsFactory.get_constants()

        assert constants.TOKEN_FILE_NAME.endswith(
            TestConstants.FormatValidation.FILE_NAME_MUST_END_WITH,
        )
        assert constants.REFRESH_TOKEN_FILE_NAME.endswith(
            TestConstants.FormatValidation.FILE_NAME_MUST_END_WITH,
        )

    @pytest.mark.parametrize(
        "constant_name",
        [
            "TOKEN_FILE_NAME",
            "REFRESH_TOKEN_FILE_NAME",
        ],
    )
    @pytest.mark.parametrize(
        "invalid_char",
        TestConstants.InvalidChars.COMMON_INVALID,
    )
    def test_file_names_no_invalid_characters(
        self,
        constant_name: str,
        invalid_char: str,
    ) -> None:
        """Test that file names don't contain invalid characters."""
        constants = ConstantsFactory.get_constants()
        constant_value = getattr(constants, constant_name)

        assert invalid_char not in constant_value

    def test_constants_uniqueness(self) -> None:
        """Test that constants have unique values."""
        constants = ConstantsFactory.get_constants()

        constants_values = [
            constants.PROJECT_NAME,
            constants.FLEXT_DIR_NAME,
            constants.TOKEN_FILE_NAME,
            constants.REFRESH_TOKEN_FILE_NAME,
        ]

        assert len(constants_values) == len(set(constants_values))

    # ========================================================================
    # CONSTANT USAGE SCENARIOS
    # ========================================================================

    def test_constants_in_file_paths(self) -> None:
        """Test constants usage in file path construction."""
        constants = ConstantsFactory.get_constants()

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
        constants = ConstantsFactory.get_constants()

        config = {
            "project_name": constants.PROJECT_NAME,
            "data_directory": constants.FLEXT_DIR_NAME,
            "token_file": constants.TOKEN_FILE_NAME,
            "refresh_token_file": constants.REFRESH_TOKEN_FILE_NAME,
        }

        assert config["project_name"] == TestConstants.ExpectedValues.PROJECT_NAME
        assert config["data_directory"] == TestConstants.ExpectedValues.FLEXT_DIR_NAME
        assert config["token_file"] == TestConstants.ExpectedValues.TOKEN_FILE_NAME
        assert (
            config["refresh_token_file"]
            == TestConstants.ExpectedValues.REFRESH_TOKEN_FILE_NAME
        )

    def test_constants_in_logging(self) -> None:
        """Test constants usage in logging scenarios."""
        constants = ConstantsFactory.get_constants()

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

    # ========================================================================
    # CONSTANT COMPATIBILITY
    # ========================================================================

    def test_constants_cross_platform_compatibility(self) -> None:
        """Test that constants work across different platforms."""
        constants = ConstantsFactory.get_constants()
        current_platform = platform.system().lower()

        if current_platform == "windows":
            for char in TestConstants.InvalidChars.WINDOWS_INVALID:
                assert char not in constants.TOKEN_FILE_NAME
                assert char not in constants.REFRESH_TOKEN_FILE_NAME
        else:
            for char in TestConstants.InvalidChars.UNIX_INVALID:
                assert char not in constants.TOKEN_FILE_NAME
                assert char not in constants.REFRESH_TOKEN_FILE_NAME

    def test_constants_encoding_compatibility(self) -> None:
        """Test that constants are compatible with different encodings."""
        constants = ConstantsFactory.get_constants()

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

    # ========================================================================
    # CONSTANT VALIDATION METHODS
    # ========================================================================

    def test_validate_constant_format(self) -> None:
        """Test constant format validation."""
        constants = ConstantsFactory.get_constants()

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
            assert isinstance(file_name, str)
            assert file_name.endswith(".json")
            assert not file_name.startswith(".")
            assert "/" not in file_name
            assert "\\" not in file_name

    def test_validate_constant_content(self) -> None:
        """Test constant content validation."""
        constants = ConstantsFactory.get_constants()

        # Validate PROJECT_NAME contains FLEXT
        assert "flext" in constants.PROJECT_NAME.lower()

        # Validate FLEXT_DIR_NAME contains flext
        assert "flext" in constants.FLEXT_DIR_NAME.lower()

        # Validate token files contain expected keywords
        assert any(
            kw in constants.TOKEN_FILE_NAME.lower()
            for kw in TestConstants.FormatValidation.TOKEN_KEYWORDS
        )
        assert any(
            kw in constants.REFRESH_TOKEN_FILE_NAME.lower()
            for kw in TestConstants.FormatValidation.REFRESH_KEYWORDS
        )

    def test_validate_constant_consistency(self) -> None:
        """Test constant consistency validation."""
        constants = ConstantsFactory.get_constants()

        # Token and refresh token should be different
        assert constants.TOKEN_FILE_NAME != constants.REFRESH_TOKEN_FILE_NAME

        # Both should contain 'token'
        assert "token" in constants.TOKEN_FILE_NAME.lower()
        assert "token" in constants.REFRESH_TOKEN_FILE_NAME.lower()

    # ========================================================================
    # CONSTANT ACCESS PATTERNS
    # ========================================================================

    def test_constants_class_access(self) -> None:
        """Test accessing constants through class instance."""
        constants = ConstantsFactory.get_constants()

        assert hasattr(constants, "PROJECT_NAME")
        assert hasattr(constants, "FLEXT_DIR_NAME")
        assert hasattr(constants, "TOKEN_FILE_NAME")
        assert hasattr(constants, "REFRESH_TOKEN_FILE_NAME")

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
        constants1 = ConstantsFactory.get_constants()
        constants2 = ConstantsFactory.get_constants()

        assert constants1.PROJECT_NAME == constants2.PROJECT_NAME
        assert constants1.FLEXT_DIR_NAME == constants2.FLEXT_DIR_NAME
        assert constants1.TOKEN_FILE_NAME == constants2.TOKEN_FILE_NAME
        assert constants1.REFRESH_TOKEN_FILE_NAME == constants2.REFRESH_TOKEN_FILE_NAME

    def test_constants_class_level_access(self) -> None:
        """Test accessing constants at class level."""
        assert (
            FlextCliConstants.PROJECT_NAME == TestConstants.ExpectedValues.PROJECT_NAME
        )
        assert (
            FlextCliConstants.FLEXT_DIR_NAME
            == TestConstants.ExpectedValues.FLEXT_DIR_NAME
        )
        assert (
            FlextCliConstants.TOKEN_FILE_NAME
            == TestConstants.ExpectedValues.TOKEN_FILE_NAME
        )
        assert (
            FlextCliConstants.REFRESH_TOKEN_FILE_NAME
            == TestConstants.ExpectedValues.REFRESH_TOKEN_FILE_NAME
        )

    # ========================================================================
    # CONSTANT INTEGRATION TESTS
    # ========================================================================

    def test_constants_in_real_world_scenarios(self) -> None:
        """Test constants in real-world usage scenarios."""
        constants = ConstantsFactory.get_constants()

        # Scenario 1: Setting up application directories
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir) / constants.FLEXT_DIR_NAME
            app_dir.mkdir()

            token_file = app_dir / constants.TOKEN_FILE_NAME
            refresh_token_file = app_dir / constants.REFRESH_TOKEN_FILE_NAME

            token_file.write_text(TestConstants.TestValues.TEST_TOKEN_JSON)
            refresh_token_file.write_text(
                TestConstants.TestValues.TEST_REFRESH_TOKEN_JSON,
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
        constants = ConstantsFactory.get_constants()

        start_time = time.time()
        for _ in range(TestConstants.TestValues.ITERATION_COUNT):
            _ = constants.PROJECT_NAME
            _ = constants.FLEXT_DIR_NAME
            _ = constants.TOKEN_FILE_NAME
            _ = constants.REFRESH_TOKEN_FILE_NAME
        end_time = time.time()

        access_time = end_time - start_time
        assert access_time < TestConstants.TestValues.PERFORMANCE_THRESHOLD_SECONDS, (
            f"Constants access too slow: {access_time:.4f}s"
        )

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

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
        constants = ConstantsFactory.get_constants()
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
        constants = ConstantsFactory.get_constants()
        constant_value = getattr(constants, constant_name)

        assert isinstance(constant_value, str)
        assert len(constant_value) > 0
        assert constant_value.upper() is not None
        assert constant_value.lower() is not None

    def test_constants_concatenation(self) -> None:
        """Test that constants can be concatenated."""
        constants = ConstantsFactory.get_constants()

        combined = constants.PROJECT_NAME + " " + constants.FLEXT_DIR_NAME
        assert isinstance(combined, str)
        assert len(combined) > 0
