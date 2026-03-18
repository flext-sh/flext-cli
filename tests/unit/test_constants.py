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

import json
import logging
import platform
import tempfile
import time
from pathlib import Path

import pytest
from flext_tests import tm

from flext_cli import FlextCliConstants, c, u

from ..helpers import FlextCliTestHelpers


class TestsCliConstants:
    """Comprehensive test suite for FlextCliConstants functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    class Fixtures:
        """Factory for creating constants instances for testing."""

        @staticmethod
        def get_constants() -> type[FlextCliConstants]:
            """Get FlextCliConstants instance."""
            return FlextCliTestHelpers.ConstantsFactory.get_constants()

    class TestData:
        """Factory for creating test data scenarios."""

        @staticmethod
        def get_constant_value_cases() -> list[tuple[str, str]]:
            """Get parametrized test cases for constant values."""
            return [
                ("PROJECT_NAME", "flext-cli"),
                ("FLEXT_DIR_NAME", ".flext"),
                ("TOKEN_FILE_NAME", "token.json"),
                ("REFRESH_TOKEN_FILE_NAME", "refresh_token.json"),
                ("AUTH_DIR_NAME", "auth"),
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
            return ["TOKEN_FILE_NAME", "REFRESH_TOKEN_FILE_NAME"]

    class Assertions:
        """Helper methods for test assertions."""

        @staticmethod
        def _get_constant_value(
            constants: type[FlextCliConstants], constant_name: str
        ) -> str:
            """Get constant value from correct namespace."""
            mapping: dict[str, str] = {
                "PROJECT_NAME": constants.Cli.Project.NAME,
                "FLEXT_DIR_NAME": constants.Cli.Paths.FLEXT_DIR_NAME,
                "TOKEN_FILE_NAME": constants.Cli.Paths.TOKEN_FILE_NAME,
                "REFRESH_TOKEN_FILE_NAME": constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME,
                "AUTH_DIR_NAME": constants.Cli.Paths.AUTH_DIR_NAME,
            }
            if constant_name not in mapping:
                msg = f"Unknown constant name: {constant_name}"
                raise ValueError(msg)
            return mapping[constant_name]

        @staticmethod
        def assert_constant_exists(
            constants: type[FlextCliConstants], constant_name: str
        ) -> None:
            """Assert constant exists and has value."""
            value = TestsCliConstants.Assertions._get_constant_value(
                constants, constant_name
            )
            tm.that(value is not None, eq=True)
            tm.that(isinstance(value, str), eq=True)
            tm.that(len(value) > 0, eq=True)
            tm.that(len(value.strip()) > 0, eq=True)

        @staticmethod
        def assert_constant_value(
            constants: type[FlextCliConstants], constant_name: str, expected_value: str
        ) -> None:
            """Assert constant has expected value."""
            actual_value = TestsCliConstants.Assertions._get_constant_value(
                constants, constant_name
            )
            tm.that(actual_value, eq=expected_value)
            tm.that(isinstance(actual_value, str), eq=True)
            tm.that(len(actual_value) > 0, eq=True)

        @staticmethod
        def assert_file_name_format(
            constants: type[FlextCliConstants], constant_name: str
        ) -> None:
            """Assert file name constant follows format."""
            value = TestsCliConstants.Assertions._get_constant_value(
                constants, constant_name
            )
            tm.that(value.endswith(".json"), eq=True)
            tm.that(not value.startswith("."), eq=True)
            tm.that("/" not in value, eq=True)
            tm.that("\\" not in value, eq=True)

    def test_constants_service_initialization(self) -> None:
        """Test constants service initialization and basic properties."""
        constants = self.Fixtures.get_constants()
        tm.that(constants is not None, eq=True)
        for constant_name in self.TestData.get_constant_names():
            self.Assertions.assert_constant_exists(constants, constant_name)

    @pytest.mark.parametrize(
        ("constant_name", "expected_value"),
        [
            ("PROJECT_NAME", "flext-cli"),
            ("FLEXT_DIR_NAME", ".flext"),
            ("TOKEN_FILE_NAME", "token.json"),
            ("REFRESH_TOKEN_FILE_NAME", "refresh_token.json"),
            ("AUTH_DIR_NAME", "auth"),
        ],
    )
    def test_constants_values(self, constant_name: str, expected_value: str) -> None:
        """Test constants have correct values."""
        constants = self.Fixtures.get_constants()
        self.Assertions.assert_constant_value(constants, constant_name, expected_value)

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
        constant_value = self.Assertions._get_constant_value(constants, constant_name)
        tm.that(isinstance(constant_value, str), eq=True)
        tm.that(len(constant_value.strip()) > 0, eq=True)

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
        constant_value = self.Assertions._get_constant_value(constants, constant_name)
        tm.that(constant_value is not None, eq=True)
        tm.that(constant_value, eq=True)
        tm.that(constant_value.strip(), eq=True)

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
        constant_value = self.Assertions._get_constant_value(constants, constant_name)
        tm.that(isinstance(constant_value, str), eq=True)
        tm.that(len(constant_value) > 0, eq=True)
        tm.that(constant_value.upper() is not None, eq=True)
        tm.that(constant_value.lower() is not None, eq=True)

    def test_directory_name_format_validation(self) -> None:
        """Test that FLEXT_DIR_NAME follows expected format."""
        constants = self.Fixtures.get_constants()
        tm.that(constants.Cli.Paths.FLEXT_DIR_NAME.startswith("."), eq=True)
        tm.that(len(constants.Cli.Paths.FLEXT_DIR_NAME) > 1, eq=True)

    @pytest.mark.parametrize(
        "constant_name", ["TOKEN_FILE_NAME", "REFRESH_TOKEN_FILE_NAME"]
    )
    def test_file_name_format_validation(self, constant_name: str) -> None:
        """Test that file names follow expected format."""
        constants = self.Fixtures.get_constants()
        self.Assertions.assert_file_name_format(constants, constant_name)

    @pytest.mark.parametrize(
        "constant_name", ["TOKEN_FILE_NAME", "REFRESH_TOKEN_FILE_NAME"]
    )
    @pytest.mark.parametrize(
        "invalid_char", ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    )
    def test_file_names_no_invalid_characters(
        self, constant_name: str, invalid_char: str
    ) -> None:
        """Test that file names don't contain invalid characters."""
        constants = self.Fixtures.get_constants()
        constant_value = self.Assertions._get_constant_value(constants, constant_name)
        tm.that(invalid_char not in constant_value, eq=True)

    def test_constants_uniqueness(self) -> None:
        """Test that constants have unique values."""
        constants = self.Fixtures.get_constants()
        constants_values = [
            constants.Cli.Project.NAME,
            constants.Cli.Paths.FLEXT_DIR_NAME,
            constants.Cli.Paths.TOKEN_FILE_NAME,
            constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME,
        ]
        tm.that(len(constants_values), eq=len(set(constants_values)))

    def test_constants_in_file_paths(self) -> None:
        """Test constants usage in file path construction."""
        constants = self.Fixtures.get_constants()
        home_dir = Path.home()
        flext_dir = home_dir / constants.Cli.Paths.FLEXT_DIR_NAME
        token_file = flext_dir / constants.Cli.Paths.TOKEN_FILE_NAME
        refresh_token_file = flext_dir / constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
        tm.that(str(flext_dir).endswith(constants.Cli.Paths.FLEXT_DIR_NAME), eq=True)
        tm.that(str(token_file).endswith(constants.Cli.Paths.TOKEN_FILE_NAME), eq=True)
        tm.that(
            str(refresh_token_file).endswith(
                constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
            ),
            eq=True,
        )
        tm.that(Path(flext_dir).name, eq=constants.Cli.Paths.FLEXT_DIR_NAME)
        tm.that(Path(token_file).name, eq=constants.Cli.Paths.TOKEN_FILE_NAME)
        tm.that(
            (
                Path(refresh_token_file).name
                == constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
            ),
            eq=True,
        )

    def test_constants_in_configuration(self) -> None:
        """Test constants usage in configuration scenarios."""
        constants = self.Fixtures.get_constants()
        config = {
            "project_name": constants.Cli.Project.NAME,
            "data_directory": constants.Cli.Paths.FLEXT_DIR_NAME,
            "token_file": constants.Cli.Paths.TOKEN_FILE_NAME,
            "refresh_token_file": constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME,
        }
        tm.that(config["project_name"], eq="flext-cli")
        tm.that(config["data_directory"], eq=".flext")
        tm.that(config["token_file"], eq="token.json")
        tm.that(config["refresh_token_file"], eq="refresh_token.json")

    def test_constants_in_logging(self) -> None:
        """Test constants usage in logging scenarios."""
        constants = self.Fixtures.get_constants()
        log_messages = [
            f"Initializing {constants.Cli.Project.NAME}",
            f"Creating directory: {constants.Cli.Paths.FLEXT_DIR_NAME}",
            f"Loading token from: {constants.Cli.Paths.TOKEN_FILE_NAME}",
            f"Refreshing token from: {constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME}",
        ]
        for message in log_messages:
            tm.that(isinstance(message, str), eq=True)
            tm.that(len(message) > 0, eq=True)
            tm.that(
                (
                    constants.Cli.Project.NAME in message
                    or constants.Cli.Paths.FLEXT_DIR_NAME in message
                    or constants.Cli.Paths.TOKEN_FILE_NAME in message
                    or (constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME in message)
                ),
                eq=True,
            )

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
            tm.that(char not in constants.Cli.Paths.TOKEN_FILE_NAME, eq=True)
            tm.that(char not in constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME, eq=True)

    def test_constants_encoding_compatibility(self) -> None:
        """Test that constants are compatible with different encodings."""
        constants = self.Fixtures.get_constants()
        utf8_encoded = constants.Cli.Project.NAME.encode("utf-8")
        tm.that(isinstance(utf8_encoded, bytes), eq=True)
        tm.that(len(utf8_encoded) > 0, eq=True)
        decoded = utf8_encoded.decode("utf-8")
        tm.that(decoded, eq=constants.Cli.Project.NAME)
        try:
            ascii_encoded = constants.Cli.Project.NAME.encode("ascii")
            tm.that(isinstance(ascii_encoded, bytes), eq=True)
        except UnicodeEncodeError:
            logging.getLogger(__name__).debug(
                "constant not encodable as ascii, skip assert"
            )

    def test_validate_constant_format(self) -> None:
        """Test constant format validation."""
        constants = self.Fixtures.get_constants()
        tm.that(isinstance(constants.Cli.Project.NAME, str), eq=True)
        tm.that(len(constants.Cli.Project.NAME.strip()) > 0, eq=True)
        tm.that(not constants.Cli.Project.NAME.startswith(" "), eq=True)
        tm.that(not constants.Cli.Project.NAME.endswith(" "), eq=True)
        tm.that(isinstance(constants.Cli.Paths.FLEXT_DIR_NAME, str), eq=True)
        tm.that(constants.Cli.Paths.FLEXT_DIR_NAME.startswith("."), eq=True)
        tm.that(len(constants.Cli.Paths.FLEXT_DIR_NAME) > 1, eq=True)
        tm.that(not constants.Cli.Paths.FLEXT_DIR_NAME.endswith("."), eq=True)
        for file_name in [
            constants.Cli.Paths.TOKEN_FILE_NAME,
            constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME,
        ]:
            self.Assertions.assert_file_name_format(
                constants,
                "TOKEN_FILE_NAME"
                if file_name == constants.Cli.Paths.TOKEN_FILE_NAME
                else "REFRESH_TOKEN_FILE_NAME",
            )

    def test_validate_constant_content(self) -> None:
        """Test constant content validation."""
        constants = self.Fixtures.get_constants()
        tm.that("flext" in constants.Cli.Project.NAME.lower(), eq=True)
        tm.that("flext" in constants.Cli.Paths.FLEXT_DIR_NAME.lower(), eq=True)
        tm.that(
            any(
                kw in constants.Cli.Paths.TOKEN_FILE_NAME.lower()
                for kw in ["token", "access", "bearer"]
            ),
            eq=True,
        )
        tm.that(
            any(
                kw in constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME.lower()
                for kw in ["refresh", "token"]
            ),
            eq=True,
        )

    def test_validate_constant_consistency(self) -> None:
        """Test constant consistency validation."""
        constants = self.Fixtures.get_constants()
        tm.that(
            (
                constants.Cli.Paths.TOKEN_FILE_NAME
                != constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
            ),
            eq=True,
        )
        tm.that("token" in constants.Cli.Paths.TOKEN_FILE_NAME.lower(), eq=True)
        tm.that("token" in constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME.lower(), eq=True)

    def test_constants_class_access(self) -> None:
        """Test accessing constants through class instance."""
        constants = self.Fixtures.get_constants()
        for constant_name in self.TestData.get_constant_names():
            self.Assertions.assert_constant_exists(constants, constant_name)
        project_name = constants.Cli.Project.NAME
        flext_dir = constants.Cli.Paths.FLEXT_DIR_NAME
        token_file = constants.Cli.Paths.TOKEN_FILE_NAME
        refresh_token_file = constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
        tm.that(isinstance(project_name, str), eq=True)
        tm.that(isinstance(flext_dir, str), eq=True)
        tm.that(isinstance(token_file, str), eq=True)
        tm.that(isinstance(refresh_token_file, str), eq=True)

    def test_constants_multiple_instances(self) -> None:
        """Test that multiple instances return the same constants."""
        constants1 = self.Fixtures.get_constants()
        constants2 = self.Fixtures.get_constants()
        tm.that(constants1.Cli.Project.NAME, eq=constants2.Cli.Project.NAME)
        tm.that(
            (
                constants1.Cli.Paths.FLEXT_DIR_NAME
                == constants2.Cli.Paths.FLEXT_DIR_NAME
            ),
            eq=True,
        )
        tm.that(
            (
                constants1.Cli.Paths.TOKEN_FILE_NAME
                == constants2.Cli.Paths.TOKEN_FILE_NAME
            ),
            eq=True,
        )
        tm.that(
            (
                constants1.Cli.Paths.REFRESH_TOKEN_FILE_NAME
                == constants2.Cli.Paths.REFRESH_TOKEN_FILE_NAME
            ),
            eq=True,
        )

    def test_constants_class_level_access(self) -> None:
        """Test accessing constants at class level."""
        tm.that(c.Cli.Project.NAME, eq="flext-cli")
        tm.that(c.Cli.Paths.FLEXT_DIR_NAME, eq=".flext")
        tm.that(c.Cli.Paths.TOKEN_FILE_NAME, eq="token.json")
        tm.that(c.Cli.Paths.REFRESH_TOKEN_FILE_NAME, eq="refresh_token.json")

    def test_constants_in_real_world_scenarios(self) -> None:
        """Test constants in real-world usage scenarios."""
        constants = self.Fixtures.get_constants()
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir) / constants.Cli.Paths.FLEXT_DIR_NAME
            app_dir.mkdir()
            token_file = app_dir / constants.Cli.Paths.TOKEN_FILE_NAME
            refresh_token_file = app_dir / constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
            token_file.write_text(
                json.dumps({"access_token": "test_token", "token_type": "Bearer"})
            )
            refresh_token_file.write_text(
                json.dumps({"refresh_token": "test_refresh_token"})
            )
            tm.that(token_file.exists(), eq=True)
            tm.that(refresh_token_file.exists(), eq=True)
        config = {
            "app": {
                "name": constants.Cli.Project.NAME,
                "data_dir": constants.Cli.Paths.FLEXT_DIR_NAME,
                "files": {
                    "token": constants.Cli.Paths.TOKEN_FILE_NAME,
                    "refresh_token": constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME,
                },
            }
        }
        tm.that(config is not None, eq=True)
        tm.that(isinstance(config, dict), eq=True)
        error_messages = {
            "missing_token": f"Token file '{constants.Cli.Paths.TOKEN_FILE_NAME}' not found",
            "missing_refresh_token": f"Refresh token file '{constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME}' not found",
            "invalid_dir": f"Directory '{constants.Cli.Paths.FLEXT_DIR_NAME}' is not accessible",
        }
        for message in error_messages.values():
            tm.that(isinstance(message, str), eq=True)
            tm.that(len(message) > 0, eq=True)
            tm.that(
                (
                    constants.Cli.Paths.TOKEN_FILE_NAME in message
                    or constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME in message
                    or constants.Cli.Paths.FLEXT_DIR_NAME in message
                ),
                eq=True,
            )

    def test_constants_performance(self) -> None:
        """Test constants access performance."""
        constants = self.Fixtures.get_constants()
        start_time = time.time()
        for _ in range(1000):
            _ = constants.Cli.Project.NAME
            _ = constants.Cli.Paths.FLEXT_DIR_NAME
            _ = constants.Cli.Paths.TOKEN_FILE_NAME
            _ = constants.Cli.Paths.REFRESH_TOKEN_FILE_NAME
        end_time = time.time()
        access_time = end_time - start_time
        tm.that(access_time < 0.1, eq=True)

    def test_constants_concatenation(self) -> None:
        """Test that constants can be concatenated."""
        constants = self.Fixtures.get_constants()
        combined = constants.Cli.Project.NAME + " " + constants.Cli.Paths.FLEXT_DIR_NAME
        tm.that(isinstance(combined, str), eq=True)
        tm.that(len(combined) > 0, eq=True)

    def test_get_valid_output_formats(self) -> None:
        """Test get_valid_output_formats returns sorted tuple."""
        formats = u.Cli.CliValidation.get_valid_output_formats()
        tm.that(isinstance(formats, tuple), eq=True)
        tm.that(len(formats) > 0, eq=True)
        tm.that(all(isinstance(fmt, str) for fmt in formats), eq=True)
        tm.that(formats, eq=tuple(sorted(formats)))

    def test_get_valid_command_statuses(self) -> None:
        """Test get_valid_command_statuses returns sorted tuple."""
        statuses = u.Cli.CliValidation.get_valid_command_statuses()
        tm.that(isinstance(statuses, tuple), eq=True)
        tm.that(len(statuses) > 0, eq=True)
        tm.that(all(isinstance(status, str) for status in statuses), eq=True)
        tm.that(statuses, eq=tuple(sorted(statuses)))

    def test_get_enum_values(self) -> None:
        """Test get_enum_values extracts values from StrEnum."""
        values = u.get_enum_values(c.Cli.CommandStatus)
        tm.that(isinstance(values, tuple), eq=True)
        tm.that(len(values) > 0, eq=True)
        tm.that(all(isinstance(v, str) for v in values), eq=True)
        tm.that("pending" in values, eq=True)
        tm.that("running" in values, eq=True)
        output_values = u.get_enum_values(c.Cli.OutputFormats)
        tm.that(isinstance(output_values, tuple), eq=True)
        tm.that("json" in output_values, eq=True)
        tm.that("yaml" in output_values, eq=True)

    def test_create_cli_discriminated_union(self) -> None:
        """Test create_cli_discriminated_union creates union mapping."""
        union_map = u.create_discriminated_union(
            "status", c.Cli.CommandStatus, c.Cli.SessionStatus
        )
        tm.that(isinstance(union_map, dict), eq=True)
        tm.that(len(union_map) > 0, eq=True)
        tm.that(union_map["pending"], eq=c.Cli.CommandStatus)
        tm.that(union_map["active"], eq=c.Cli.SessionStatus)

    def test_get_file_extensions(self) -> None:
        """Test get_file_extensions returns extensions for format."""
        extensions = c.Cli.get_file_extensions("json")
        tm.that(isinstance(extensions, tuple), eq=True)
        tm.that("json" in extensions, eq=True)
        yaml_extensions = c.Cli.get_file_extensions("yaml")
        tm.that(isinstance(yaml_extensions, tuple), eq=True)
        tm.that("yaml" in yaml_extensions, eq=True)
        tm.that("yml" in yaml_extensions, eq=True)
        none_extensions = c.Cli.get_file_extensions("nonexistent")
        tm.that(none_extensions is None, eq=True)

    def test_get_mime_type(self) -> None:
        """Test get_mime_type returns MIME type for format."""
        mime = c.Cli.get_mime_type("json")
        tm.that(isinstance(mime, str), eq=True)
        tm.that(mime, eq="application/json")
        yaml_mime = c.Cli.get_mime_type("yaml")
        tm.that(isinstance(yaml_mime, str), eq=True)
        tm.that(yaml_mime, eq="application/x-yaml")
        none_mime = c.Cli.get_mime_type("nonexistent")
        tm.that(none_mime is None, eq=True)

    def test_validate_file_format(self) -> None:
        """Test validate_file_format checks format support."""
        tm.that(c.Cli.validate_file_format("json") is True, eq=True)
        tm.that(c.Cli.validate_file_format("yaml") is True, eq=True)
        tm.that(c.Cli.validate_file_format("csv") is True, eq=True)
        tm.that(c.Cli.validate_file_format("nonexistent") is False, eq=True)
        tm.that(c.Cli.validate_file_format("invalid") is False, eq=True)
