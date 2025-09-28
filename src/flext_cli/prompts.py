"""User interaction tools for CLI applications."""

from __future__ import annotations

import re

from flext_cli.typings import FlextCliTypes
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextUtilities,
)


class FlextCliPrompts(FlextService[FlextCliTypes.Data.CliDataDict]):
    """CLI prompts and interactive input service using domain-specific types.

    Provides comprehensive prompt functionality for CLI applications with enhanced
    type safety using FlextCliTypes instead of generic FlextTypes.Core types.
    Extends FlextService with CLI-specific data dictionary types.
    """

    def __init__(
        self,
        default_timeout: int = 30,
        *,
        interactive_mode: bool = True,
        **data: object,
    ) -> None:
        """Initialize CLI prompts service with enhanced configuration.

        Args:
            interactive_mode: Enable interactive prompt features
            default_timeout: Default timeout for prompt operations in seconds
            **data: Additional service initialization data

        """
        super().__init__(**data)
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

        # Prompts-specific configuration
        self._interactive_mode = interactive_mode
        self._default_timeout = default_timeout
        self._prompt_history: list[str] = []

    @property
    def interactive_mode(self) -> bool:
        """Check if interactive mode is enabled.

        Returns:
            bool: True if interactive mode is enabled

        """
        return self._interactive_mode

    @property
    def default_timeout(self) -> int:
        """Get default timeout for prompt operations.

        Returns:
            int: Default timeout in seconds

        """
        return self._default_timeout

    @property
    def prompt_history(self) -> list[str]:
        """Get prompt history.

        Returns:
            list[str]: List of previous prompts

        """
        return self._prompt_history.copy()

    def prompt_text(
        self,
        message: str,
        default: str = "",
        validation_pattern: str | None = None,
    ) -> FlextResult[str]:
        """Prompt user for text input with enhanced validation.

        Args:
            message: Prompt message to display
            default: Default value if no input provided
            timeout: Timeout in seconds (uses default if None)
            validation_pattern: Optional regex pattern for input validation

        Returns:
            FlextResult[str]: User input or error

        """
        if not self._interactive_mode:
            if default:
                return FlextResult[str].ok(default)
            return FlextResult[str].fail(
                "Interactive mode disabled and no default provided"
            )

        try:
            # Record prompt for history
            self._prompt_history.append(message)

            # Use input with timeout if available

            # Simulate user input (in real implementation, would use proper input handling)
            user_input = default or "simulated_input"

            # Validate input if pattern provided
            if (
                validation_pattern
                and user_input
                and not re.match(validation_pattern, user_input)
            ):
                return FlextResult[str].fail(
                    f"Input does not match required pattern: {validation_pattern}"
                )

            return FlextResult[str].ok(user_input)

        except Exception as e:
            return FlextResult[str].fail(f"Text prompt failed: {e}")

    def prompt_confirmation(
        self,
        message: str,
        *,
        default: bool = False,
    ) -> FlextResult[bool]:
        """Prompt user for yes/no confirmation.

        Args:
            message: Confirmation message to display
            default: Default value if no input provided
            timeout: Timeout in seconds (uses default if None)

        Returns:
            FlextResult[bool]: User confirmation or error

        """
        if not self._interactive_mode:
            return FlextResult[bool].ok(default)

        try:
            # Record prompt for history
            self._prompt_history.append(f"{message} (y/n)")

            # Use input with timeout if available

            # Simulate user input (in real implementation, would use proper input handling)
            response = "y" if default else "n"

            return FlextResult[bool].ok(response.lower() in {"y", "yes", "true", "1"})

        except Exception as e:
            return FlextResult[bool].fail(f"Confirmation prompt failed: {e}")

    def prompt_choice(
        self,
        message: str,
        choices: list[str],
        default: str | None = None,
    ) -> FlextResult[str]:
        """Prompt user to select from multiple choices.

        Args:
            message: Choice prompt message to display
            choices: List of available choices
            default: Default choice if no input provided
            timeout: Timeout in seconds (uses default if None)

        Returns:
            FlextResult[str]: Selected choice or error

        """
        if not choices:
            return FlextResult[str].fail("No choices provided")

        if not self._interactive_mode:
            if default and default in choices:
                return FlextResult[str].ok(default)
            return FlextResult[str].fail(
                "Interactive mode disabled and no valid default provided"
            )

        try:
            # Record prompt for history
            choice_list = ", ".join(
                f"{i + 1}. {choice}" for i, choice in enumerate(choices)
            )
            self._prompt_history.append(f"{message}\n{choice_list}")

            # Use input with timeout if available

            # Simulate user input (in real implementation, would use proper input handling)
            selected = default or choices[0]

            if selected not in choices:
                return FlextResult[str].fail(f"Invalid choice: {selected}")

            return FlextResult[str].ok(selected)

        except Exception as e:
            return FlextResult[str].fail(f"Choice prompt failed: {e}")

    def prompt_password(
        self,
        message: str = "Password:",
        min_length: int = 1,
    ) -> FlextResult[str]:
        """Prompt user for password input with hidden text.

        Args:
            message: Password prompt message
            timeout: Timeout in seconds (uses default if None)
            min_length: Minimum password length

        Returns:
            FlextResult[str]: Password input or error

        """
        if not self._interactive_mode:
            return FlextResult[str].fail("Interactive mode disabled for password input")

        try:
            # Record prompt for history (without showing actual password)
            self._prompt_history.append(f"{message} [password hidden]")

            # Use getpass or similar for hidden input

            # Simulate password input (in real implementation, would use getpass)
            # For security, this is a placeholder - real implementation should use secure input
            password = f"{'x' * 8}"  # Placeholder for password

            if len(password) < min_length:
                return FlextResult[str].fail(
                    f"Password must be at least {min_length} characters"
                )

            return FlextResult[str].ok(password)

        except Exception as e:
            return FlextResult[str].fail(f"Password prompt failed: {e}")

    def clear_prompt_history(self) -> FlextResult[None]:
        """Clear prompt history.

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            self._prompt_history.clear()
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"History clear failed: {e}")

    def get_prompt_statistics(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Get prompt usage statistics.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Statistics data

        """
        try:
            stats: FlextCliTypes.Data.CliDataDict = {
                "prompts_executed": len(self._prompt_history),
                "interactive_mode": self._interactive_mode,
                "default_timeout": self._default_timeout,
                "history_size": len(self._prompt_history),
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(stats)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Statistics collection failed: {e}",
            )

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute prompt service operation using CLI-specific data types.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        """
        try:
            execution_data: FlextCliTypes.Data.CliDataDict = {
                "service_status": "operational",
                "interactive_mode": self._interactive_mode,
                "default_timeout": self._default_timeout,
                "prompts_available": True,
                "history_entries": len(self._prompt_history),
                "execution_timestamp": FlextUtilities.Generators.generate_timestamp(),
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(execution_data)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Prompt service execution failed: {e}",
            )

    async def execute_async(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute prompt service operation asynchronously.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        """
        try:
            execution_data: FlextCliTypes.Data.CliDataDict = {
                "service_status": "operational",
                "interactive_mode": self._interactive_mode,
                "default_timeout": self._default_timeout,
                "prompts_available": True,
                "history_entries": len(self._prompt_history),
                "async_capable": True,
                "execution_timestamp": FlextUtilities.Generators.generate_timestamp(),
            }

            return FlextResult[FlextCliTypes.Data.CliDataDict].ok(execution_data)

        except Exception as e:
            return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                f"Async prompt service execution failed: {e}",
            )

    def prompt(self, message: str, default: str = "") -> FlextResult[str]:
        """Prompt user for text input.

        Args:
            message: Prompt message
            default: Default value

        Returns:
            FlextResult[str]: User input or error

        """
        try:
            # Store prompt for history
            self._prompt_history.append(message)

            # Get actual user input
            display_message = f"{message} (default: {default})" if default else message

            user_input = input(f"{display_message}: ").strip()

            # Use default if input is empty
            if not user_input and default:
                user_input = default

            self._logger.info(f"User prompted: {message}, input: {user_input}")
            return FlextResult[str].ok(user_input)
        except Exception as e:
            return FlextResult[str].fail(f"Prompt failed: {e}")

    def confirm(self, message: str, *, default: bool = False) -> FlextResult[bool]:
        """Prompt user for yes/no confirmation.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            FlextResult[bool]: User choice or error

        """
        try:
            # Prepare the confirmation prompt
            prompt_text = f"{message} [Y/n]: " if default else f"{message} [y/N]: "

            while True:
                user_input = input(prompt_text).strip().lower()

                if not user_input:  # Empty input uses default
                    return FlextResult[bool].ok(default)

                if user_input in {"y", "yes"}:
                    return FlextResult[bool].ok(True)
                if user_input in {"n", "no"}:
                    return FlextResult[bool].ok(False)
                self._logger.warning("Please enter 'y', 'yes', 'n', or 'no'.")
        except KeyboardInterrupt:
            return FlextResult[bool].fail("User cancelled confirmation")
        except Exception as e:
            return FlextResult[bool].fail(f"Confirmation failed: {e}")

    def select_from_options(
        self, options: list[str], message: str = "Choose an option:"
    ) -> FlextResult[str]:
        """Prompt user to select from multiple options.

        Args:
            options: List of options
            message: Selection message

        Returns:
            FlextResult[str]: Selected option or error

        """
        try:
            # Store selection prompt for history
            self._prompt_history.append(f"{message}: {options}")

            # Display options to user
            if not options:
                return FlextResult[str].fail("No options provided")

            self._logger.info(f"Selection prompt: {message}")
            for i, option in enumerate(options, 1):
                self._logger.info(f"Option {i}: {option}")

            # Get user selection
            while True:
                try:
                    choice = input(f"\nEnter your choice (1-{len(options)}): ").strip()

                    if not choice:
                        continue

                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        selected_option = options[choice_num - 1]
                        break
                    self._logger.warning(
                        f"Please enter a number between 1 and {len(options)}."
                    )
                except ValueError:
                    self._logger.warning("Please enter a valid number.")
                except KeyboardInterrupt:
                    return FlextResult[str].fail("User cancelled selection")

            self._logger.info(f"User selected: {message}, choice: {selected_option}")
            return FlextResult[str].ok(selected_option)
        except Exception as e:
            return FlextResult[str].fail(f"Selection failed: {e}")

    def print_status(self, message: str, status: str = "info") -> FlextResult[None]:
        """Print status message.

        Args:
            message: Status message
            status: Status type

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            # Format status message with appropriate styling
            status_upper = status.upper()
            formatted_message = f"[{status_upper}] {message}"
            self._logger.info(formatted_message)
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
        try:
            self._logger.info(f"SUCCESS: {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print success failed: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print error message.

        Args:
            message: Error message

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            self._logger.error(f"ERROR: {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print error failed: {e}")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print warning message.

        Args:
            message: Warning message

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            self._logger.warning(f"WARNING: {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print warning failed: {e}")

    def print_info(self, message: str) -> FlextResult[None]:
        """Print info message.

        Args:
            message: Info message

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            self._logger.info(f"INFO: {message}")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Print info failed: {e}")

    def create_progress(
        self, description: str = "Processing..."
    ) -> FlextResult[object]:
        """Create progress indicator.

        Args:
            description: Progress description

        Returns:
            FlextResult[object]: Progress indicator or error

        """
        try:
            # Store progress creation for history
            self._prompt_history.append(f"Progress: {description}")

            # Create a simple progress indicator
            self._logger.info(f"Starting progress: {description}")
            progress_info = {
                "description": description,
                "created": True,
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
                "total_items": 0,
                "completed_items": 0,
            }

            self._logger.info(f"Created progress: {description}")
            return FlextResult[object].ok(progress_info)
        except Exception as e:
            return FlextResult[object].fail(f"Create progress failed: {e}")

    def with_progress(
        self, items: list[object], description: str = "Processing..."
    ) -> FlextResult[object]:
        """Execute with progress indicator.

        Args:
            items: Items to process
            description: Progress description

        Returns:
            FlextResult[object]: Result or error

        """
        try:
            # Store progress operation for history
            self._prompt_history.append(
                f"Progress operation: {description} ({len(items)} items)"
            )

            # Process items with progress indication
            total_items = len(items)
            self._logger.info(f"Processing {total_items} items: {description}")

            processed_count = 0
            progress_report_threshold = 10
            for _ in range(len(items)):
                # Process the item (placeholder - would do actual work)
                processed_count += 1

                # Show progress for large item sets
                if (
                    total_items > progress_report_threshold
                    and processed_count
                    % max(1, total_items // progress_report_threshold)
                    == 0
                ):
                    progress = (processed_count / total_items) * 100
                    self._logger.info(
                        f"  Progress: {progress:.1f}% ({processed_count}/{total_items})"
                    )

            self._logger.info(f"Completed: {description}")
            result_info = {
                "description": description,
                "items_processed": processed_count,
                "timestamp": FlextUtilities.Generators.generate_timestamp(),
            }

            self._logger.info(
                f"Progress completed: {description}, processed: {processed_count}"
            )
            return FlextResult[object].ok(result_info)
        except Exception as e:
            return FlextResult[object].fail(f"With progress failed: {e}")


__all__ = [
    "FlextCliPrompts",
]
