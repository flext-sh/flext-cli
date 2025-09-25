"""User interaction tools for CLI applications."""

from datetime import UTC, datetime

from flext_core import FlextLogger, FlextResult, FlextService, FlextTypes


class FlextCliPrompts(FlextService[None]):
    """User interaction tools for CLI applications.

    Consolidates user interaction functionality from interactions.py.
    Provides confirm, prompt, and status printing with FlextResult error handling.
    NO DIRECT RICH IMPORTS - uses flext-core exclusively.
    """

    def __init__(
        self,
        *,
        logger: FlextLogger | None = None,
        quiet: bool = False,
    ) -> None:
        """Initialize prompts manager."""
        super().__init__()
        self._logger: FlextLogger = logger or FlextLogger(__name__)
        self._quiet: bool = quiet

    def execute(self: object) -> FlextResult[None]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[None].ok(None)

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Get user confirmation using standard input.

        Args:
            message: Confirmation message
            default: Default value if user just presses Enter

        Returns:
            FlextResult[bool]: User confirmation result

        """
        if self._quiet:
            return FlextResult[bool].ok(default)
        try:
            prompt_text = f"{message} [y/N]: " if not default else f"{message} [Y/n]: "
            response = input(prompt_text).strip().lower()

            if not response:
                return FlextResult[bool].ok(default)

            if response in {"y", "yes", "1", "true"}:
                return FlextResult[bool].ok(True)
            if response in {"n", "no", "0", "false"}:
                return FlextResult[bool].ok(False)
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

        Args:
            message: Prompt message
            default: Default value if user just presses Enter

        Returns:
            FlextResult[str]: User input or error

        """
        if self._quiet:
            if default is not None:
                return FlextResult[str].ok(default)
            return FlextResult[str].fail("Empty input is not allowed")

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

        Args:
            message: Status message
            status: Status level (info, success, warning, error)

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            if self._quiet and status == "info":
                return FlextResult[None].ok(None)

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

        Args:
            message: Success message

        Returns:
            FlextResult[None]: Success or error

        """
        return self.print_status(message, status="success")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message.

        Args:
            message: Error message

        Returns:
            FlextResult[None]: Success or error

        """
        return self.print_status(message, status="error")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message.

        Args:
            message: Warning message

        Returns:
            FlextResult[None]: Success or error

        """
        return self.print_status(message, status="warning")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message.

        Args:
            message: Info message

        Returns:
            FlextResult[None]: Success or error

        """
        return self.print_status(message, status="info")

    def create_progress(self, message: str = "") -> FlextResult[str]:
        """Create simple progress tracking message.

        Args:
            message: Progress message

        Returns:
            FlextResult[str]: Progress message or error

        """
        try:
            if message and not self._quiet:
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

        Args:
            items: Items to process
            message: Progress message

        Returns:
            FlextResult[FlextTypes.Core.List]: Items or error

        """
        try:
            if message and not self._quiet:
                self._logger.info(f"Processing {len(items)} items: {message}")
            return FlextResult[FlextTypes.Core.List].ok(items)
        except Exception as e:
            return FlextResult[FlextTypes.Core.List].fail(
                f"Progress processing failed: {e}",
            )

    async def execute_async(self) -> FlextResult[dict[str, object]]:
        """Execute prompts service operation asynchronously."""
        return FlextResult[dict[str, object]].ok({
            "status": "operational",
            "service": "flext-cli-prompts",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "2.0.0",
        })


__all__ = ["FlextCliPrompts"]
