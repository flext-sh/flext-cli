"""FLEXT CLI Mixins.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast, override

from flext_core import (
    FlextComparableMixin,
    FlextLoggableMixin,
    FlextResult,
    FlextSerializableMixin,
    FlextValidatableMixin,
    get_logger,
)
from rich.console import Console
from rich.progress import Progress, TaskID

from flext_cli.cli_types import ConfigDict, FlextCliOutputFormat, OutputData

# =============================================================================
# CORE CLI MIXINS - Extending flext-core patterns
# =============================================================================


class CliValidationMixin(FlextValidatableMixin):
    """CLI-specific validation mixin extending flext-core validation.

    Adds CLI-specific validation methods while delegating core validation
    to flext-core FlextValidatableMixin.
    """

    def validate_cli_arguments(self, args: list[str]) -> FlextResult[None]:
        """Validate CLI arguments format and content."""
        # Args is already typed as list[str], so basic validation is minimal
        # We trust the type system but add length validation
        if len(args) == 0:
            return FlextResult[None].ok(None)  # Empty list is valid

        # Check for empty string arguments
        for i, arg in enumerate(args):
            if not arg.strip():
                return FlextResult[None].fail(
                    f"Argument {i} cannot be empty or whitespace-only",
                )

        return FlextResult[None].ok(None)

    def validate_output_format(self, format_type: str) -> FlextResult[None]:
        """Validate CLI output format."""
        valid_formats = [format_value.value for format_value in FlextCliOutputFormat]
        if format_type not in valid_formats:
            return FlextResult[None].fail(
                f"Invalid output format '{format_type}'. Valid formats: {', '.join(valid_formats)}",
            )
        return FlextResult[None].ok(None)


class CliConfigMixin(FlextComparableMixin):
    """CLI-specific configuration mixin extending flext-core configuration.

    Adds CLI-specific configuration methods while delegating core configuration
    to flext-core FlextConfigurableMixin.
    """

    def load_cli_profile(self, profile_name: str) -> FlextResult[ConfigDict]:
        """Load CLI profile configuration."""
        if not profile_name or not profile_name.strip():
            return FlextResult[ConfigDict].fail("Profile name cannot be empty")

        # Simple profile configuration without parent delegation
        # (CliConfigMixin doesn't inherit actual configuration loading)
        profile_config: ConfigDict = {
            "name": profile_name,
            "output_format": "table",
            "debug": False,
        }

        return FlextResult[ConfigDict].ok(profile_config)

    def validate_cli_config(self, config: ConfigDict) -> FlextResult[None]:
        """Validate CLI-specific configuration."""
        # CLI-specific validations only (no parent validation)
        if "output_format" in config:
            output_format = config["output_format"]
            if not isinstance(output_format, str):
                return FlextResult[None].fail("output_format must be a string")

            # Validate against valid formats
            valid_formats = [
                format_value.value for format_value in FlextCliOutputFormat
            ]
            if output_format not in valid_formats:
                return FlextResult[None].fail(
                    f"Invalid output format '{output_format}'. Valid formats: {', '.join(valid_formats)}",
                )

        return FlextResult[None].ok(None)


class CliLoggingMixin(FlextLoggableMixin):
    """CLI-specific logging mixin extending flext-core logging.

    Adds CLI-specific logging methods while delegating core logging
    to flext-core FlextLoggableMixin.
    """

    def log_command_execution(
        self,
        command: str,
        *,
        success: bool,
        duration: float,
    ) -> FlextResult[None]:
        """Log CLI command execution with structured data."""
        logger = get_logger(self.__class__.__name__)

        if success:
            logger.info(
                "Command executed successfully",
                extra={
                    "command": command,
                    "duration_seconds": duration,
                    "status": "success",
                },
            )
        else:
            logger.error(
                "Command execution failed",
                extra={
                    "command": command,
                    "duration_seconds": duration,
                    "status": "failed",
                },
            )

        return FlextResult[None].ok(None)

    def log_cli_error(
        self,
        error_message: str,
        context: Mapping[str, object] | None = None,
    ) -> FlextResult[None]:
        """Log CLI-specific errors with context."""
        logger = get_logger(self.__class__.__name__)

        log_context = dict(context) if context else {}
        log_context.update({"error_type": "cli_error"})

        logger.error(error_message, extra=log_context)
        return FlextResult[None].ok(None)


class CliOutputMixin(FlextSerializableMixin):
    """CLI-specific output formatting mixin extending flext-core serialization.

    Adds CLI-specific output formatting while delegating core serialization
    to flext-core FlextSerializableMixin.
    """

    def format_cli_output(
        self,
        data: OutputData,
        format_type: FlextCliOutputFormat = FlextCliOutputFormat.TABLE,
        **_options: object,
    ) -> FlextResult[str]:
        """Format data for CLI output in specified format."""
        # Validate format without relying on mixin inheritance assumptions
        valid_formats = [fmt.value for fmt in FlextCliOutputFormat]
        if format_type.value not in valid_formats:
            return FlextResult[str].fail(
                f"Invalid output format '{format_type.value}'. Valid formats: {', '.join(valid_formats)}",
            )

        try:
            result: FlextResult[str]
            if format_type == FlextCliOutputFormat.JSON:
                json_result = self.to_json()
                result = FlextResult[str].ok(json_result)
            elif format_type == FlextCliOutputFormat.YAML:
                json_data = self.to_json()
                result = FlextResult[str].ok(
                    "# YAML representation\ndata: " + json_data
                )
            elif format_type == FlextCliOutputFormat.TABLE:
                result = self._format_as_table(data)
            elif format_type == FlextCliOutputFormat.CSV:
                result = self._format_as_csv(data)
            else:
                fallback = str(data)
                result = FlextResult[str].ok(fallback)
            return result
        except Exception as e:
            return FlextResult[str].fail("Output formatting failed: " + str(e))

    def _format_as_table(
        self,
        data: OutputData,
        **_options: object,
    ) -> FlextResult[str]:
        """Format data as table using Rich."""
        # Basic table formatting - can be enhanced
        if isinstance(data, list):
            if not data:
                return FlextResult[str].ok("No data to display")

            # Simple table representation
            rows = [str(item) for item in data]

            return FlextResult[str].ok("\n".join(rows))

        return FlextResult[str].ok(str(data))

    def _format_as_csv(self, data: OutputData, **_options: object) -> FlextResult[str]:
        """Format data as CSV."""
        # Basic CSV formatting - can be enhanced
        if isinstance(data, list):
            if not data:
                return FlextResult[str].ok("")

            # Simple CSV representation
            csv_lines: list[str] = []
            for item in data:
                if isinstance(item, dict):
                    typed_item = cast("dict[str, object]", item)
                    values = [str(v) for v in typed_item.values() if v is not None]
                    csv_lines.append(",".join(values))
                else:
                    csv_lines.append(str(item))

            return FlextResult[str].ok("\n".join(csv_lines))

        return FlextResult[str].ok(str(data))

    # Note: validation logic is provided by CliValidationMixin to avoid duplication


class CliInteractiveMixin:
    """CLI interactive functionality mixin.

    Provides interactive CLI capabilities like prompts, confirmations,
    and progress tracking. This is CLI-specific and doesn't extend
    flext-core as there's no equivalent interactive mixin there.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize interactive mixin."""
        super().__init__(*args, **kwargs)
        self._console: Console | None = None
        self._progress: Progress | None = None

    @property
    def console(self) -> Console:
        """Get or create Rich console instance."""
        if self._console is None:
            self._console = Console()
        return self._console

    def prompt_user(self, message: str, default: str | None = None) -> FlextResult[str]:
        """Prompt user for input with optional default."""
        try:
            prompt_text = f"{message}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "

            user_input = input(prompt_text).strip()
            if not user_input and default:
                user_input = default

            return FlextResult[str].ok(user_input)

        except (EOFError, KeyboardInterrupt):
            return FlextResult[str].fail("User input cancelled")
        except Exception as e:
            return FlextResult[str].fail(f"Input error: {e}")

    def confirm_action(
        self,
        message: str,
        *,
        default: bool = False,
    ) -> FlextResult[bool]:
        """Ask user for confirmation."""
        try:
            default_text = "Y/n" if default else "y/N"
            prompt = f"{message} ({default_text}): "

            response = input(prompt).strip().lower()

            if not response:
                return FlextResult[bool].ok(default)

            if response in {"y", "yes", "true", "1"}:
                confirmed = True
                return FlextResult[bool].ok(confirmed)
            if response in {"n", "no", "false", "0"}:
                confirmed = False
                return FlextResult[bool].ok(confirmed)
            return FlextResult[bool].fail("Please answer 'y' or 'n'")

        except (EOFError, KeyboardInterrupt):
            return FlextResult[bool].fail("User confirmation cancelled")
        except Exception as e:
            return FlextResult[bool].fail(f"Confirmation error: {e}")

    def show_progress(self, description: str) -> FlextResult[TaskID]:
        """Start progress tracking."""
        try:
            if self._progress is None:
                self._progress = Progress()
                self._progress.start()

            task_id = self._progress.add_task(description, total=100)
            return FlextResult[TaskID].ok(task_id)

        except Exception as e:
            return FlextResult[TaskID].fail(f"Progress tracking error: {e}")

    def update_progress(self, task_id: TaskID, advance: int = 1) -> FlextResult[None]:
        """Update progress tracking."""
        try:
            if self._progress:
                self._progress.update(task_id, advance=advance)
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Progress update error: {e}")

    def finish_progress(self) -> FlextResult[None]:
        """Finish progress tracking."""
        try:
            if self._progress:
                self._progress.stop()
                self._progress = None
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Progress finish error: {e}")


# =============================================================================
# COMPOSITE MIXINS - Combining multiple mixins for common patterns
# =============================================================================


class CliCompleteMixin(
    CliValidationMixin,
    CliConfigMixin,
    CliLoggingMixin,
    CliOutputMixin,
    CliInteractiveMixin,
):
    """Complete CLI mixin combining all CLI functionality.

    This composite mixin provides all CLI capabilities in a single
    inheritance. Use this when you need full CLI functionality.
    """

    @override
    def mixin_setup(self) -> None:
        """Set up all mixin components."""
        # Call parent mixin setup (returns None)
        super().mixin_setup()

    def setup_cli_complete(self) -> FlextResult[None]:
        """Set up all mixin components with FlextResult return."""
        try:
            # Initialize all parent mixins
            self.mixin_setup()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Mixin setup failed: {e}")


class CliDataMixin(CliValidationMixin, CliOutputMixin):
    """Data-focused CLI mixin for validation and output formatting."""

    @override
    def mixin_setup(self) -> None:
        """Set up data mixin components."""
        # Call parent mixin setup (returns None)
        super().mixin_setup()


class CliExecutionMixin(CliLoggingMixin, CliInteractiveMixin):
    """Execution-focused CLI mixin for logging and interaction."""

    @override
    def mixin_setup(self) -> None:
        """Set up execution mixin components."""
        # Call parent mixin setup (returns None)
        super().mixin_setup()


class CliUIMixin(CliOutputMixin, CliInteractiveMixin):
    """UI-focused CLI mixin for output and interaction."""

    @override
    def mixin_setup(self) -> None:
        """Set up UI mixin components."""
        # Call parent mixin setup (returns None)
        super().mixin_setup()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CliCompleteMixin",
    "CliConfigMixin",
    "CliDataMixin",
    "CliExecutionMixin",
    "CliInteractiveMixin",
    "CliLoggingMixin",
    "CliOutputMixin",
    "CliUIMixin",
    "CliValidationMixin",
]
