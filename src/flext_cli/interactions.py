"""FLEXT CLI Interactions - User interaction utilities following flext-core patterns.

Provides FlextCliInteractions class for user prompts, confirmations, and interactive
elements with FlextResult error handling and Rich integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextLogger, FlextResult, FlextTypes


class FlextCliInteractions:
    """User interaction utilities following SOLID principles.

    Single responsibility: User interaction operations.
    Uses FlextLogger for output with FlextResult error handling.
    NO DIRECT RICH IMPORTS - uses flext-core exclusively.
    """

    def __init__(
        self,
        *,
        logger: FlextLogger | None = None,
        quiet: bool = False,
    ) -> None:
        """Initialize interactions manager."""
        self._logger: FlextLogger = logger or FlextLogger(__name__)
        self.quiet: bool = quiet

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Get user confirmation using standard input.

        Returns:
            FlextResult[bool]: Description of return value.

        """
        if self.quiet:
            return FlextResult[bool].ok(default)
        try:
            prompt_text = f"{message} [y/N]: " if not default else f"{message} [Y/n]: "
            response = input(prompt_text).strip().lower()

            if not response:
                return FlextResult[bool].ok(default)

            if response in {"y", "yes", "1", "true"}:
                return FlextResult[bool].ok(data=True)
            if response in {"n", "no", "0", "false"}:
                return FlextResult[bool].ok(data=False)
            self._logger.warning(
                f"Invalid response '{response}', using default {default}",
            )
            return FlextResult[bool].ok(default)

        except KeyboardInterrupt:
            return FlextResult[bool].fail("User interrupted confirmation")
        except EOFError:
            return FlextResult[bool].fail("Input stream ended")
        except Exception as e:
            return FlextResult[bool].fail(f"Confirmation failed: {e}")

    def prompt(self, message: str, *, default: str | None = None) -> FlextResult[str]:
        """Get user text input using standard input.

        Returns:
            FlextResult[str]: Description of return value.

        """
        if self.quiet and default is not None:
            return FlextResult[str].ok(default)
        try:
            prompt_text = (
                f"{message}: " if default is None else f"{message} [{default}]: "
            )

            if not (value := input(prompt_text).strip()):
                return (
                    FlextResult[str].ok(default)
                    if default is not None
                    else FlextResult[str].fail("Empty input is not allowed")
                )

            return FlextResult[str].ok(value)

        except KeyboardInterrupt:
            return FlextResult[str].fail("User interrupted prompt")
        except EOFError:
            return FlextResult[str].fail("Input stream ended")
        except Exception as e:
            return FlextResult[str].fail(f"Prompt failed: {e}")

    def print_status(self, message: str, *, status: str = "info") -> FlextResult[None]:
        """Print status message using FlextLogger.

        Returns:
            FlextResult[None]: Description of return value.

        """
        try:
            if self.quiet and status == "info":
                return FlextResult[None].ok(None)

            # Use match-case for status handling (Python 3.13+)
            match status:
                case "info":
                    self._logger.info(message)
                case "success":
                    self._logger.info(f"SUCCESS: {message}")
                case "warning":
                    self._logger.warning(message)
                case "error":
                    self._logger.error(message)
                case _:
                    self._logger.info(f"{status.upper()}: {message}")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print status failed: {e}")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print success message.

        Returns:
            FlextResult[None]: Description of return value.

        """
        return self.print_status(message, status="success")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message.

        Returns:
            FlextResult[None]: Description of return value.

        """
        return self.print_status(message, status="error")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message.

        Returns:
            FlextResult[None]: Description of return value.

        """
        return self.print_status(message, status="warning")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message.

        Returns:
            FlextResult[None]: Description of return value.

        """
        return self.print_status(message, status="info")

    def create_progress(self, message: str = "") -> FlextResult[str]:
        """Create simple progress tracking message.

        Returns:
            FlextResult[str]: Description of return value.

        """
        try:
            if message and not self.quiet:
                self._logger.info(f"Starting: {message}")
            return FlextResult[str].ok(message)
        except Exception as e:
            return FlextResult[str].fail(f"Progress creation failed: {e}")

    def with_progress(
        self,
        items: FlextTypes.Core.List,
        message: str,
    ) -> FlextResult[FlextTypes.Core.List]:
        """Process items with simple progress tracking.

        Returns:
            FlextResult[FlextTypes.Core.List]: Description of return value.

        """
        try:
            if message and not self.quiet:
                self._logger.info(f"Processing {len(items)} items: {message}")
            return FlextResult[FlextTypes.Core.List].ok(items)
        except Exception as e:
            return FlextResult[FlextTypes.Core.List].fail(
                f"Progress processing failed: {e}",
            )


__all__ = ["FlextCliInteractions"]
