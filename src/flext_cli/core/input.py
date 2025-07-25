"""FlextCliInput - Input collection using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Consolidated input collection eliminating duplications with flext-core.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult, get_logger
from rich.console import Console
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

# Import centralized helpers to eliminate duplication
from flext_cli.core._helpers import (
    flext_cli_fail as _fail,
    flext_cli_success as _success,
)
from flext_cli.core.validator import FlextCliValidator

logger = get_logger(__name__)


class FlextCliInput:
    """Input collection with validation built on flext-core patterns.

    Eliminates duplications - uses flext-core FlextResult for all operations.
    """

    def __init__(
        self,
        console: Console | None = None,
        validator: FlextCliValidator | None = None,
    ) -> None:
        self.console = console or Console()
        self.validator = validator or FlextCliValidator()

    def text(
        self,
        prompt: str,
        default: str | None = None,
        required: bool = True,
        validator: str | callable | None = None,
    ) -> FlextResult[str]:
        """Collect text input with validation using flext-core patterns."""
        while True:
            try:
                value = Prompt.ask(prompt, default=default, console=self.console)

                # Check required
                if required and not value:
                    self.console.print("[red]This field is required.[/red]")
                    continue

                # Validate if provided
                if validator:
                    temp_validator = FlextCliValidator({"input": validator})
                    result = temp_validator.validate("input", value)
                    if not result.success:
                        self.console.print(f"[red]{result.error}[/red]")
                        continue

                return _success(value)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled.[/yellow]")
                return _fail("Input cancelled by user")
            except Exception as e:
                logger.exception("Text input failed")
                return _fail(f"Input error: {e}")

    def password(self, prompt: str = "Password", confirm: bool = False) -> FlextResult[str]:
        """Collect password with optional confirmation."""
        while True:
            try:
                password = Prompt.ask(prompt, password=True, console=self.console)

                if not password:
                    self.console.print("[red]Password cannot be empty.[/red]")
                    continue

                if confirm:
                    confirm_password = Prompt.ask(
                        "Confirm password", password=True, console=self.console,
                    )
                    if password != confirm_password:
                        self.console.print("[red]Passwords do not match.[/red]")
                        continue

                return _success(password)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled.[/yellow]")
                return _fail("Password input cancelled")
            except Exception as e:
                logger.exception("Password input failed")
                return _fail(f"Password input error: {e}")

    def integer(
        self,
        prompt: str,
        default: int | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> FlextResult[int]:
        """Collect integer with range validation."""
        while True:
            try:
                value = IntPrompt.ask(prompt, default=default, console=self.console)

                if min_value is not None and value < min_value:
                    self.console.print(f"[red]Value must be at least {min_value}.[/red]")
                    continue

                if max_value is not None and value > max_value:
                    self.console.print(f"[red]Value must be at most {max_value}.[/red]")
                    continue

                return _success(value)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled.[/yellow]")
                return _fail("Integer input cancelled")
            except Exception as e:
                logger.exception("Integer input failed")
                return _fail(f"Integer input error: {e}")

    def float_input(
        self,
        prompt: str,
        default: float | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> FlextResult[float]:
        """Collect float with range validation."""
        while True:
            try:
                value = FloatPrompt.ask(prompt, default=default, console=self.console)

                if min_value is not None and value < min_value:
                    self.console.print(f"[red]Value must be at least {min_value}.[/red]")
                    continue

                if max_value is not None and value > max_value:
                    self.console.print(f"[red]Value must be at most {max_value}.[/red]")
                    continue

                return _success(value)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Input cancelled.[/yellow]")
                return _fail("Float input cancelled")
            except Exception as e:
                logger.exception("Float input failed")
                return _fail(f"Float input error: {e}")

    def boolean(self, prompt: str, default: bool = False) -> FlextResult[bool]:
        """Collect boolean input."""
        try:
            value = Confirm.ask(prompt, default=default, console=self.console)
            return _success(value)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled.[/yellow]")
            return _fail("Boolean input cancelled")
        except Exception as e:
            logger.exception("Boolean input failed")
            return _fail(f"Boolean input error: {e}")

    def choice(
        self,
        prompt: str,
        choices: list[str],
        default: str | None = None,
    ) -> FlextResult[str]:
        """Collect choice from predefined options."""
        try:
            value = Prompt.ask(
                prompt,
                choices=choices,
                default=default,
                console=self.console,
            )
            return _success(value)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled.[/yellow]")
            return _fail("Choice input cancelled")
        except Exception as e:
            logger.exception("Choice input failed")
            return _fail(f"Choice input error: {e}")

    def email(self, prompt: str = "Email address", default: str | None = None) -> FlextResult[str]:
        """Collect email with validation."""
        return self.text(prompt, default=default, validator="email")

    def url(self, prompt: str = "URL", default: str | None = None) -> FlextResult[str]:
        """Collect URL with validation."""
        return self.text(prompt, default=default, validator="url")

    def collect_dict(self, schema: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Collect multiple inputs based on schema.

        Raises exception on failure - caller should handle with FlextResult.
        """
        results = {}

        self.console.print("\n[bold cyan]Input Collection[/bold cyan]")

        for field_name, field_config in schema.items():
            field_type = field_config.get("type", str)
            prompt = field_config.get("prompt", field_name.replace("_", " ").title())
            default = field_config.get("default")
            validator = field_config.get("validator")
            required = field_config.get("required", True)

            if field_type is bool:
                result = self.boolean(prompt, default or False)
            elif field_type is int:
                min_val = field_config.get("min_value")
                max_val = field_config.get("max_value")
                result = self.integer(prompt, default, min_val, max_val)
            elif field_type is float:
                min_val = field_config.get("min_value")
                max_val = field_config.get("max_value")
                result = self.float_input(prompt, default, min_val, max_val)
            elif field_config.get("choices"):
                choices = field_config["choices"]
                result = self.choice(prompt, choices, default)
            elif field_config.get("password"):
                confirm = field_config.get("confirm", False)
                result = self.password(prompt, confirm)
            else:
                result = self.text(prompt, default, required, validator)

            if result.success:
                results[field_name] = result.unwrap()
            else:
                msg = f"Failed to collect {field_name}: {result.error}"
                raise RuntimeError(msg)

        return results

    @classmethod
    def create_web_input(cls) -> FlextCliInput:
        """Create input collector for web-related inputs."""
        return cls(validator=FlextCliValidator.create_web_validator())

    @classmethod
    def create_security_input(cls) -> FlextCliInput:
        """Create input collector for security-related inputs."""
        return cls(validator=FlextCliValidator.create_security_validator())

    @classmethod
    def create_network_input(cls) -> FlextCliInput:
        """Create input collector for network-related inputs."""
        return cls(validator=FlextCliValidator.create_network_validator())
