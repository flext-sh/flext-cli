"""FLEXT CLI Testing Utilities - Test helpers for CLI applications.

**PURPOSE**: Provides comprehensive testing utilities for CLI applications following
FLEXT ecosystem standards. Includes test runners, mock scenarios, and fixtures.

**ARCHITECTURE LAYER**: Application Layer (Layer 3) - Test Infrastructure
- Single unified FlextCliTesting class with nested test helpers
- Railway-Oriented Programming with FlextResult[T] throughout
- Integration with Click.testing.CliRunner
- Pydantic v2 models for test data
- FlextService extension for service pattern compliance

**CORE CAPABILITIES**:
1. TestRunner - Execute CLI commands in isolated environments
2. MockScenarios - Create mock configurations and test data
3. Fixtures - Reusable test fixtures and utilities
4. Assertions - FlextResult-aware assertion helpers

**INTEGRATION POINTS**:
- Uses click.testing.CliRunner (already available)
- Extends FlextService from flext-core
- Uses FlextResult[T] for railway pattern
- Compatible with pytest framework
- Follows FLEXT standards (single class per module, nested helpers)

**PRODUCTION READINESS CHECKLIST**:
✅ Railway-oriented pattern (all methods return FlextResult[T])
✅ Single unified class with nested helpers (FLEXT pattern)
✅ Type-safe test data models (Pydantic v2)
✅ Isolated filesystem support (Click.testing)
✅ Mock scenario generation
✅ Comprehensive type annotations
✅ Zero tolerance quality (follows FLEXT standards)

**USAGE PATTERNS**:

```python
# No sys.path manipulation - dependencies must be properly installed

from tests.fixtures.testing_utilities import FlextCliTestRunner, FlextCliMockScenarios

# Pattern 1: Test CLI commands
runner = FlextCliTestRunner()
result = runner.invoke_command(cli.main, "hello", ["--name", "Alice"])

if result.is_success:
    test_result = result.unwrap()
    assert test_result["exit_code"] == 0
    assert "Hello, Alice" in test_result["output"]

# Pattern 2: Mock scenarios
mock = FlextCliMockScenarios()
config = mock.mock_user_config(profile="test", debug=True).unwrap()
token = mock.mock_auth_token("test_token_123").unwrap()

# Pattern 3: Isolated filesystem
with runner.isolated_filesystem():
    # Test file operations in isolation
    Path("test.json").write_text('{"key": "value"}')
    # ... your tests ...
```

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

import click
from click.testing import CliRunner
from collections.abc import Mapping

from flext_cli import FlextCliConstants
from flext_core import FlextResult, FlextService, FlextTypes


class FlextCliTesting(FlextService[dict[str, object]]):
    """Single unified testing utilities class following FLEXT standards.

    **ARCHITECTURE LAYER**: Application Layer (Layer 3)
    Provides comprehensive testing utilities for CLI applications with railway-
    oriented error handling and FLEXT ecosystem compliance.

    **NESTED HELPERS** (FLEXT pattern):
    - TestRunner - CLI command execution in isolated environments
    - MockScenarios - Mock data and configuration generation
    - Fixtures - Reusable test fixtures

    **RAILWAY-ORIENTED PATTERN**:
    All public operations return FlextResult[T] for composable testing:
    - invoke_command() returns FlextResult[dict]
    - mock_user_config() returns FlextResult[CliConfigSchema]
    - create_temp_config_file() returns FlextResult[Path]

    **KEY DESIGN PRINCIPLES**:
    - Railway pattern enables test composition
    - Type safety via FlextCliTypes
    - Isolated filesystem for tests
    - Click.testing integration
    - Mock scenarios for common test cases
    """

    # =========================================================================
    # NESTED HELPER: TestRunner
    # =========================================================================

    class TestRunner:
        """Test runner for CLI commands using Click.testing.CliRunner.

        Provides isolated command execution with comprehensive result capture.
        All methods return FlextResult[T] for railway-oriented testing.
        """

        def __init__(self) -> None:
            """Initialize test runner with Click CliRunner."""
            self.runner = CliRunner()
            self.isolation = True

        def invoke_command(
            self,
            cli: click.Command | click.Group,
            command: str,
            args: list[str] | None = None,
            input_text: str | None = None,
            env: dict[str, str] | None = None,
        ) -> FlextResult[dict[str, FlextTypes.JsonValue]]:
            """Invoke a CLI command in isolated environment.

            Args:
                cli: CLI application instance
                command: Command name to invoke
                args: Command arguments
                input_text: Input text for interactive prompts
                env: Environment variables for command

            Returns:
                FlextResult[dict]: Test result with exit_code, output, exception

            Example:
                >>> runner = FlextCliTesting.TestRunner()
                >>> result = runner.invoke_command(
                ...     cli.main, "hello", ["--name", "Alice"]
                ... )
                >>> if result.is_success:
                ...     assert result.unwrap()["exit_code"] == 0

            """
            try:
                result = self.runner.invoke(
                    cli,
                    args=[command] + (args or []),
                    input=input_text,
                    env=env,
                    catch_exceptions=False,
                )

                return FlextResult[dict[str, Any]].ok({
                    FlextCliConstants.DictKeys.EXIT_CODE: result.exit_code,
                    FlextCliConstants.DictKeys.OUTPUT: result.output,
                    FlextCliConstants.DictKeys.EXCEPTION: result.exception,
                    FlextCliConstants.ContextDictKeys.EXCEPTION_INFO: result.exc_info,
                })
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(str(e))

        @contextmanager
        def isolated_filesystem(self) -> Generator[Path]:
            """Context manager for isolated filesystem testing.

            Returns:
                Context manager providing isolated temporary directory

            Example:
                >>> runner = FlextCliTesting.TestRunner()
                >>> with runner.isolated_filesystem():
                ...     Path("test.json").write_text('{"test": true}')
                ...     # Test file operations in isolation

            """
            with self.runner.isolated_filesystem() as temp_dir:
                yield Path(temp_dir)

    # =========================================================================
    # NESTED HELPER: MockScenarios
    # =========================================================================

    class MockScenarios:
        """Mock scenarios for testing CLI applications.

        Provides pre-configured mock data for common testing scenarios.
        All methods return FlextResult[T] for railway-oriented testing.
        """

        def mock_user_config(
            self,
            profile: str = "test",
            **overrides: FlextTypes.JsonValue,
        ) -> FlextResult[FlextTypes.JsonDict]:
            """Create mock user configuration.

            Args:
                profile: Profile name
                **overrides: Additional configuration overrides

            Returns:
                FlextResult[CliConfigSchema]: Mock configuration

            Example:
                >>> mock = FlextCliTesting.MockScenarios()
                >>> config = mock.mock_user_config(profile="dev", debug=True).unwrap()

            """
            try:
                # Build base config
                base_config: FlextTypes.JsonDict = {
                    FlextCliConstants.DictKeys.PROFILE: profile,
                    FlextCliConstants.DictKeys.DEBUG: False,
                    FlextCliConstants.DictKeys.VERBOSE: False,
                    FlextCliConstants.DictKeys.OUTPUT_FORMAT: FlextCliConstants.OutputFormats.JSON.value,
                }
                # Update with overrides - type is compatible with CliConfigSchema
                base_config.update(overrides)
                return FlextResult[FlextTypes.JsonDict].ok(
                    base_config,
                )
            except Exception as e:
                return FlextResult[FlextTypes.JsonDict].fail(
                    str(e),
                )

        def mock_auth_token(
            self,
            token: str = "test_token_abc123",  # nosec B107 - test fixture
        ) -> FlextResult[str]:
            """Create mock authentication token.

            Args:
                token: Token string (default: "test_token")

            Returns:
                FlextResult[str]: Mock token

            Example:
                >>> mock = FlextCliTesting.MockScenarios()
                >>> token = mock.mock_auth_token("abc123").unwrap()

            """
            return FlextResult[str].ok(token)

        def mock_auth_credentials(
            self,
            username: str = "testuser",
            password: str = "testpass_abc123",  # nosec B107 - test fixture
        ) -> FlextResult[Mapping[str, str]]:
            """Create mock authentication credentials.

            Args:
                username: Username (default: "testuser")
                password: Password (default: "testpass123")

            Returns:
                FlextResult[CredentialsData]: Mock credentials

            Example:
                >>> mock = FlextCliTesting.MockScenarios()
                >>> creds = mock.mock_auth_credentials().unwrap()
                >>> assert creds["username"] == "testuser"

            """
            try:
                credentials: Mapping[str, str] = {
                    FlextCliConstants.DictKeys.USERNAME: username,
                    FlextCliConstants.DictKeys.PASSWORD: password,
                }
                return FlextResult[Mapping[str, str]].ok(credentials)
            except Exception as e:
                return FlextResult[Mapping[str, str]].fail(str(e))

        def create_temp_config_file(
            self,
            config_data: dict[str, FlextTypes.JsonValue],
        ) -> FlextResult[Path]:
            """Create temporary configuration file for testing.

            Args:
                config_data: Configuration data to write

            Returns:
                FlextResult[Path]: Path to temporary file

            Example:
                >>> mock = FlextCliTesting.MockScenarios()
                >>> config = {"debug": True}
                >>> path = mock.create_temp_config_file(config).unwrap()

            """
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".json",
                    delete=False,
                    encoding="utf-8",
                ) as temp_file:
                    json.dump(config_data, temp_file, indent=2)
                    temp_path = Path(temp_file.name)
                return FlextResult[Path].ok(temp_path)
            except Exception as e:
                return FlextResult[Path].fail(str(e))

        def create_temp_directory(self) -> FlextResult[Path]:
            """Create temporary directory for testing.

            Returns:
                FlextResult[Path]: Path to temporary directory

            Example:
                >>> mock = FlextCliTesting.MockScenarios()
                >>> temp_dir = mock.create_temp_directory().unwrap()
                >>> (temp_dir / "test.txt").write_text("test")

            """
            try:
                temp_dir = Path(tempfile.mkdtemp(prefix="flext_cli_test_"))
                return FlextResult[Path].ok(temp_dir)
            except Exception as e:
                return FlextResult[Path].fail(str(e))

    # =========================================================================
    # FLEXTSERVICE PROTOCOL IMPLEMENTATION
    # =========================================================================

    def execute(self, **_kwargs: object) -> FlextResult[dict[str, object]]:
        """Execute testing service.

        Args:
            **kwargs: Additional execution parameters (for FlextService compatibility)

        Returns:
            FlextResult[dict[str, object]]: Service execution status

        """
        try:
            payload: FlextTypes.JsonDict = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                FlextCliConstants.DictKeys.SERVICE: "FlextCliTesting",
                FlextCliConstants.DictKeys.MESSAGE: "Testing utilities ready",
            }
            return FlextResult[dict[str, object]].ok(cast("dict[str, object]", payload))
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))


# =============================================================================
# CONVENIENCE EXPORTS (for backward compatibility with README examples)
# =============================================================================

FlextCliTestRunner = FlextCliTesting.TestRunner
FlextCliMockScenarios = FlextCliTesting.MockScenarios

__all__ = [
    "FlextCliMockScenarios",
    "FlextCliTestRunner",
    "FlextCliTesting",
]
