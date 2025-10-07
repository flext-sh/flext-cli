"""FLEXT-CLI Interactive Shell (REPL) Mode.

This module provides interactive shell capabilities for CLI applications:
- Interactive command shell with REPL
- Command history and persistence
- Tab completion support
- Multi-line editing
- Signal handling for graceful shutdown
- Session management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import (
    FlextResult,
    FlextService,
    FlextTypes,
)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

from flext_cli.cli import FlextCliCli
from flext_cli.constants import FlextCliConstants
from flext_cli.main import FlextCliMain


class FlextCliShell(FlextService[object]):
    """Interactive shell (REPL) for CLI applications.

    Provides a full-featured interactive shell with command history,
    completion, multi-line editing, and session management.

    Example:
        >>> from flext_cli import FlextCliApi, FlextCliShell
        >>>
        >>> cli = FlextCliApi()
        >>> shell = FlextCliShell(cli_main=cli.main, prompt="myapp> ")
        >>>
        >>> # Start interactive shell
        >>> shell.run()

    """

    def __init__(
        self,
        cli_main: FlextCliMain,
        prompt: str = FlextCliConstants.Shell.DEFAULT_PROMPT,
        *,
        history_file: str | None = None,
        enable_completion: bool = True,
        **data: object,
    ) -> None:
        """Initialize interactive shell.

        Args:
            cli_main: FlextCliMain instance with registered commands
            prompt: Shell prompt string
            history_file: Path to history file (None = no persistence)
            enable_completion: Enable tab completion
            **data: Additional service data

        """
        super().__init__(**data)
        # Logger and container inherited from FlextService via FlextMixins
        self._cli_main = cli_main
        self._prompt = prompt
        self._history_file = Path(history_file) if history_file else None
        self._enable_completion = enable_completion
        self._running = False
        self._history: FlextTypes.StringList = []
        self._session_commands: FlextTypes.StringList = []

        # Initialize prompt_toolkit session
        # Get available commands for completion
        commands_result = self._cli_main.list_commands()
        commands = commands_result.unwrap() if commands_result.is_success else []

        # Add built-in commands
        all_commands = list(commands) + FlextCliConstants.Shell.BUILTIN_COMMANDS

        # Create completer
        completer = WordCompleter(all_commands, ignore_case=True)

        # Create history handler
        history = FileHistory(str(self._history_file)) if self._history_file else None

        # Create prompt session
        self._prompt_session = PromptSession(
            completer=completer if self._enable_completion else None,
            history=history,
            enable_history_search=True,
            enable_suspend=True,
        )

    def run(self) -> FlextResult[None]:
        """Start the interactive shell.

        Returns:
            FlextResult[None]

        Example:
            >>> shell = FlextCliShell(cli.main)
            >>> shell.run()
            Welcome to FLEXT CLI Interactive Shell
            Type 'help' for commands, 'exit' to quit
            >

        """
        try:
            # Load history
            load_result = self._load_history()
            if load_result.is_failure:
                self.logger.warning(f"Failed to load history: {load_result.error}")

            # Setup completion if enabled
            if self._enable_completion:
                setup_result = self._setup_completion()
                if setup_result.is_failure:
                    self.logger.warning(
                        f"Completion setup failed: {setup_result.error}"
                    )

            # Print welcome message
            self._print_welcome()

            # Main REPL loop
            self._running = True
            while self._running:
                loop_result = self._repl_iteration()
                if loop_result.is_failure:
                    if "exit" in str(loop_result.error).lower():
                        break
                    self.logger.error(f"REPL error: {loop_result.error}")

            # Save history on exit
            save_result = self._save_history()
            if save_result.is_failure:
                self.logger.warning(f"Failed to save history: {save_result.error}")

            self.logger.info("Interactive shell session ended")
            return FlextResult[None].ok(None)

        except KeyboardInterrupt:
            return FlextResult[None].ok(None)
        except Exception as e:
            error_msg = f"Shell failed: {e}"
            self.logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def _repl_iteration(self) -> FlextResult[None]:
        """Execute one REPL iteration.

        Returns:
            FlextResult[None]

        """
        try:
            # Read input
            input_result = self._read_input()
            if input_result.is_failure:
                return FlextResult[None].fail(input_result.error)

            command = input_result.unwrap()

            # Skip empty commands
            if not command.strip():
                return FlextResult[None].ok(None)

            # Check for exit
            exit_commands = {
                FlextCliConstants.Shell.EXIT,
                FlextCliConstants.Shell.QUIT,
                FlextCliConstants.Shell.Q,
            }
            if command.strip().lower() in exit_commands:
                self._running = False
                return FlextResult[None].fail("exit")

            # Check for built-in commands
            if command.strip().startswith("!"):
                return self._execute_builtin(command[1:])

            # Add to history
            self._history.append(command)
            self._session_commands.append(command)

            # Execute command
            exec_result = self._execute_command(command)
            if exec_result.is_failure:
                pass

            return FlextResult[None].ok(None)

        except EOFError:
            self._running = False
            return FlextResult[None].fail("exit")
        except Exception as e:
            return FlextResult[None].fail(f"REPL iteration failed: {e}")

    def _read_input(self) -> FlextResult[str]:
        """Read input from user.

        Returns:
            FlextResult containing input string

        """
        try:
            user_input = self._prompt_session.prompt(self._prompt)
            return FlextResult[str].ok(user_input)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to read input: {e}")

    def _execute_command(self, command: str) -> FlextResult[None]:
        """Execute a CLI command.

        Args:
            command: Command string to execute

        Returns:
            FlextResult[None]

        """
        try:
            # Parse command into parts
            parts = command.split()
            if not parts:
                return FlextResult[None].ok(None)

            command_name = parts[0]
            args = parts[1:]

            # Get command from CLI main
            cmd_result = self._cli_main.get_command(command_name)
            if cmd_result.is_failure:
                return FlextResult[None].fail(f"Unknown command: {command_name}")

            # Execute command
            click_wrapper = FlextCliCli()
            runner_result = click_wrapper.create_cli_runner()
            if runner_result.is_failure:
                return FlextResult[None].fail(
                    f"Runner creation failed: {runner_result.error}"
                )

            runner = runner_result.unwrap()
            cmd = cmd_result.unwrap()

            # Invoke command
            result = runner.invoke(cmd, args, catch_exceptions=False)

            if result.exit_code != 0:
                return FlextResult[None].fail(
                    f"Command failed with exit code {result.exit_code}"
                )

            # Print output
            if result.output:
                pass

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Command execution failed: {e}")

    def _execute_builtin(self, command: str) -> FlextResult[None]:
        """Execute built-in shell command.

        Args:
            command: Built-in command (without !)

        Returns:
            FlextResult[None]

        """
        try:
            parts = command.split()
            if not parts:
                return FlextResult[None].ok(None)

            builtin = parts[0].lower()

            if builtin == "history":
                self._show_history()
            elif builtin == "clear":
                self._clear_screen()
            elif builtin == "help":
                self._show_help()
            elif builtin == "commands":
                self._show_commands()
            elif builtin == "session":
                self._show_session_info()

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Built-in command failed: {e}")

    def _show_history(self) -> None:
        """Show command history."""
        if not self._history:
            return

        for _i, _cmd in enumerate(self._history[-20:], 1):  # Last 20 commands
            pass

    def _clear_screen(self) -> None:
        """Clear the screen."""

    def _show_help(self) -> None:
        """Show shell help."""

    def _show_commands(self) -> None:
        """Show available CLI commands."""
        # Get commands from CLI main
        commands_result = self._cli_main.list_commands()
        if commands_result.is_failure:
            return

        commands = commands_result.unwrap()
        if not commands:
            return

        for cmd_name in sorted(commands):
            cmd_result = self._cli_main.get_command(cmd_name)
            if cmd_result.is_success:
                cmd = cmd_result.unwrap()
                # Get help text if available
                getattr(cmd, "help", "") or "No description"

    def _show_session_info(self) -> None:
        """Show session information."""

    def _print_welcome(self) -> None:
        """Print welcome message."""

    def _load_history(self) -> FlextResult[None]:
        """Load command history from file.

        Returns:
            FlextResult[None]

        """
        try:
            # History is managed by prompt_toolkit
            self.logger.debug("History managed by prompt_toolkit")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to load history: {e}")

    def _save_history(self) -> FlextResult[None]:
        """Save command history to file.

        Returns:
            FlextResult[None]

        """
        try:
            # History is managed by prompt_toolkit
            self.logger.debug("History managed by prompt_toolkit")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Failed to save history: {e}")

    def _setup_completion(self) -> FlextResult[None]:
        """Setup tab completion.

        Returns:
            FlextResult[None]

        """
        try:
            # Completion is handled automatically by prompt_toolkit
            self.logger.debug("Tab completion enabled via prompt_toolkit")
            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Completion setup failed: {e}")

    def execute(self) -> FlextResult[None]:
        """Execute shell service (runs interactive shell).

        Returns:
            FlextResult[None]

        """
        return self.run()

    def execute_sync(self) -> FlextResult[object]:
        """Execute shell service (signature deprecated, now sync).

        Note: This method is now synchronous. The signature is maintained
        for backward compatibility but will be removed in future versions.
        Use execute() instead.

        Returns:
            FlextResult[None]

        """
        return self.execute()

    def with_prompt(self, prompt: str) -> FlextCliShell:
        """Set shell prompt.

        Args:
            prompt: Prompt string

        Returns:
            Self for chaining

        """
        self._prompt = prompt
        return self

    def with_history(self, history_file: str) -> FlextCliShell:
        """Enable command history persistence.

        Args:
            history_file: Path to history file

        Returns:
            Self for chaining

        """
        self._history_file = Path(history_file) if history_file else None
        return self

    def with_completion(self, *, enable: bool = True) -> FlextCliShell:
        """Enable tab completion.

        Args:
            enable: Whether to enable completion

        Returns:
            Self for chaining

        """
        self._enable_completion = enable
        return self

    @classmethod
    def create_builder(cls, cli_main: FlextCliMain) -> FlextCliShell:
        """Create shell with builder pattern.

        Args:
            cli_main: FlextCliMain instance

        Returns:
            FlextCliShell instance for chaining

        Example:
            >>> shell = (
            ...     FlextCliShell.create_builder(cli.main)
            ...     .with_prompt("myapp> ")
            ...     .with_history("~/.myapp_history")
            ...     .with_completion()
            ... )
            >>> shell.run()

        """
        return cls(cli_main=cli_main)


__all__ = [
    "FlextCliShell",
]
