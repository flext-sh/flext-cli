"""Interactive Prompts - User Interaction.

Demonstrates auto-configured prompts and FlextResult validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_basic_prompts() -> None:
    """Basic prompts - auto-configured for terminal."""
    # Prompts auto-detect terminal capabilities
    # Example: cli.prompts.confirm("Continue?", default=True)
    cli.formatters.print("✅ Prompts auto-configured for terminal", style="cyan")


def demonstrate_validation() -> None:
    """Prompt validation with FlextResult."""

    def validate_email(email: str) -> FlextResult[str]:
        if "@" not in email:
            return FlextResult[str].fail("Invalid email")
        return FlextResult[str].ok(email)

    cli.formatters.print("\n🔍 Email Validation:", style="bold cyan")

    result = validate_email("user@example.com")
    if result.is_success:
        cli.formatters.print(f"✅ Valid: {result.unwrap()}", style="green")

    result_invalid = validate_email("invalid-email")
    if result_invalid.is_failure:
        cli.formatters.print(f"❌ Invalid: {result_invalid.error}", style="red")


def demonstrate_interactive_workflow() -> None:
    """Complete workflow pattern."""
    # Example workflow:
    # name = cli.prompts.prompt("Project name:")
    # env = cli.prompts.select("Environment:", choices=["dev", "prod"])
    # if cli.prompts.confirm(f"Create {name}?"):
    #     cli.formatters.print(f"Creating {name} in {env}", style="green")
    cli.formatters.print("\n🔄 Interactive workflows auto-configured", style="cyan")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  Interactive Prompts Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_basic_prompts()
    demonstrate_validation()
    demonstrate_interactive_workflow()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All prompt examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()
